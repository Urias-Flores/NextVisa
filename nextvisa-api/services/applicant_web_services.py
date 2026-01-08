import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
import time
import re
from xmlrpc.client import DateTime

import requests
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from lib.webdriver import get_driver, get_main_url
from models.applicant import ApplicantBase
from services import re_schedule_services, applicant_services, configuration_services, re_schedule_log_services
from models.re_schedule import ReScheduleUpdate, ScheduleStatus
from models.re_schedule_log import ReScheduleLogCreate, LogState
from lib import security
from lib.pushhover import PushHover

logger = logging.getLogger(__name__)
pushhover = PushHover()

def test_credentials(email: str, password: str) -> Dict[str, Optional[str]]:
    """
    Test applicant credentials by attempting login and extracting schedule number.

    Args:
        email: Applicant's email
        password: Applicant's password

    Returns:
        Dict with keys: success (bool), schedule (str|None), error (str|None)
    """
    driver = None
    try:
        driver = get_driver()
        
        # Attempt login
        config = configuration_services.get_configuration()
        
        if not config or not config.base_url:
            raise Exception("Configuration missing base URL")

        login_url = f"{config.base_url}/users/sign_in"
        __do_login(driver, login_url, email, password)
        
        logger.info("Login successful for credentials - extracting schedule number")

        # Extract schedule number from URL
        current_url = driver.current_url
        logger.info(f"Current URL: {current_url}")

        # Look for schedule number in URL pattern: /schedule/{SCHEDULE}/
        schedule_match = re.search(r'/schedule/(\d+)/', current_url)
        if schedule_match:
            schedule_number = schedule_match.group(1)
            logger.info(f"Extracted schedule number: {schedule_number}")
            return {
                "success": True,
                "schedule": schedule_number,
                "error": None
            }
        else:
            # Try to navigate to an appointment page to get schedule from URL
            try:
                # Look for an appointment or continue button
                continue_btn = driver.find_element(By.CSS_SELECTOR, ".button.primary.small")
                continue_btn.click()
                time.sleep(2)

                current_url = driver.current_url
                schedule_match = re.search(r'/schedule/(\d+)/', current_url)
                if schedule_match:
                    schedule_number = schedule_match.group(1)
                    logger.info(f"Extracted schedule number: {schedule_number}")
                    return {
                        "success": True,
                        "schedule": schedule_number,
                        "error": None
                    }
            except Exception as e:
                logger.warning(f"Could not navigate to get schedule: {e}")

            logger.warning("Could not extract schedule number from URL")
            return {
                "success": True,
                "schedule": None,
                "error": "Login successful but could not extract schedule number"
            }

    except Exception as e:
        logger.error(f"Error testing credentials: {e}", exc_info=True)
        return {
            "success": False,
            "schedule": None,
            "error": f"Error: {str(e)}"
        }
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as ex:
                logger.warning("Could not quit Selenium driver", ex)

def process_re_schedule(re_schedule_id: int):
    driver = None
    try:
        # Mark as PROCESSING and set the start time
        re_schedule_services.update_re_schedule(
            re_schedule_id,
            ReScheduleUpdate(status=ScheduleStatus.PROCESSING)
        )
        logger.info(f"Processing re-schedule {re_schedule_id}")

        rs = re_schedule_services.get_re_schedule_by_id(re_schedule_id)
        applicant_id = rs.get('applicant')
        if not applicant_id:
            raise Exception("Missing applicant id")

        applicant = applicant_services.get_applicant_with_password(applicant_id)
        email = applicant.get('email')
        password = security.decrypt_password(applicant.get('password'))
        schedule_number = applicant.get('schedule')

        if not email or not password or not schedule_number:
            raise Exception("Applicant email, password or schedule missing")

        config = configuration_services.get_configuration()

        # Build base URLs from configuration
        logger.info(f"Using configuration: {config}")
        base_url = config.base_url
        hub_address = config.hub_address

        if not hub_address or not base_url:
            raise Exception("Selenium hub address missing")

        appointment_url = f"{base_url}/schedule/{schedule_number}/appointment"
        days_url = f"{base_url}/schedule/{schedule_number}/appointment/days/143.json?appointments[expedite]=false"
        times_url_tmpl = f"{base_url}/schedule/{schedule_number}/appointment/times/143.json?date=%s&appointments[expedite]=false"

        driver = get_driver()
        login_url = f"{base_url}/users/sign_in"
        log_re_schedule(re_schedule_id, "Trying to login in platform", LogState.INFO)
        __do_login(driver, login_url, email, password)
        log_re_schedule(re_schedule_id, "Login successful", LogState.INFO)

        # TODO: add email or password invalid validation
        Wait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".button.primary.small")))

        # Redirect to re-schedule page
        log_re_schedule(re_schedule_id, "Redirecting to re-schedule page", LogState.INFO)
        driver.get(appointment_url)
        if driver.find_elements(By.NAME, "confirmed_limit_message"):
            Wait(driver, 2).until(EC.presence_of_element_located((By.NAME, 'confirmed_limit_message')))
            driver.find_element(By.CSS_SELECTOR, '.icheckbox').click()
            time.sleep(2)
            driver.find_element(By.NAME, 'commit').click()

        re_schudule_completed = False
        datetime_found = False
        
        # Parse end_datetime once to avoid repeated parsing
        end_datetime = datetime.strptime(str(rs.get('end_datetime')).replace("T", " "), "%Y-%m-%d %H:%M:%S")
        logger.info(f"Starting re-schedule loop for {re_schedule_id} until {end_datetime}")
        log_re_schedule(re_schedule_id, f"Starting re-schedule monitoring until {end_datetime}", LogState.INFO)
        
        # Continue while current time is BEFORE end_datetime AND process not completed
        while datetime.now() < end_datetime and not re_schudule_completed:
            time.sleep(config.sleep_time)
            logger.info(f"Re-schedule {re_schedule_id}: Checking for available appointments...")

            # Check session before getting dates
            if __is_session_expired(driver):
                logger.warning(f"Session expired before checking dates for re-schedule {re_schedule_id}")
                if not __attempt_relogin_with_retry(driver, login_url, email, password, re_schedule_id):
                    # Failed to recover session - terminate process
                    raise Exception("Session expired and could not be recovered after 3 attempts")
                
                # After successful re-login, navigate back to appointment page
                logger.info(f"Navigating back to appointment page after re-login")
                driver.get(appointment_url)
                time.sleep(2)

            # Get available dates via requests with Selenium cookies
            log_re_schedule(re_schedule_id, "Checking for available dates", LogState.INFO)
            dates = __get_dates(driver, appointment_url, days_url, re_schedule_id)
            
            # Handle empty response
            if not dates:
                logger.info(f"No dates available for re-schedule {re_schedule_id} - will retry in next iteration")
                log_re_schedule(re_schedule_id, "No dates available at this time", LogState.WARNING)
                continue
            
            # Extract dates list from response (can be dict or list)
            if isinstance(dates, dict):
                dates_list: List[dict] = dates.get('available_dates') or dates.get('dates') or []
            elif isinstance(dates, list):
                dates_list = dates
            else:
                logger.warning(f"Unexpected dates format for re-schedule {re_schedule_id}: {type(dates)}")
                log_re_schedule(re_schedule_id, f"Unexpected dates format received", LogState.WARNING)
                continue
            
            # Check if we actually have dates
            if not dates_list or len(dates_list) == 0:
                logger.info(f"No dates in list for re-schedule {re_schedule_id} - will retry")
                log_re_schedule(re_schedule_id, "No dates available at this time", LogState.WARNING)
                continue
            
            # Log the earliest available date
            earliest_date = dates_list[0].get('date') if isinstance(dates_list[0], dict) else dates_list[0]
            logger.info(f"Earlier date available: {earliest_date}")
            log_re_schedule(re_schedule_id, f"Earlier date available: {earliest_date}", LogState.INFO)

            # Check session before getting times
            if __is_session_expired(driver):
                logger.warning(f"Session expired before checking times for re-schedule {re_schedule_id}")
                if not __attempt_relogin_with_retry(driver, login_url, email, password, re_schedule_id):
                    raise Exception("Session expired and could not be recovered after 3 attempts")
                driver.get(appointment_url)
                time.sleep(2)

            # Get time for chosen date
            log_re_schedule(re_schedule_id, f"Checking available times for {chosen_date}", LogState.INFO)
            available_times = __get_times(driver, appointment_url, times_url_tmpl % chosen_date, re_schedule_id)
            
            # Handle empty response or unexpected format
            if not available_times:
                logger.info(f"No times available for date {chosen_date} - will retry")
                log_re_schedule(re_schedule_id, f"No times available for {chosen_date}", LogState.WARNING)
                continue
            
            # Validate that we have a list with items
            if not isinstance(available_times, list) or len(available_times) == 0:
                logger.info(f"Invalid times format or empty list for {chosen_date} - will retry")
                log_re_schedule(re_schedule_id, f"Invalid times data received for {chosen_date}", LogState.WARNING)
                continue
                
            time_slot = available_times[-1]
            logger.info(f"Selected time slot: {time_slot} for date {chosen_date}")
            log_re_schedule(re_schedule_id, f"Selected appointment: {chosen_date} at {time_slot}", LogState.INFO)

            datetime_found = True
            
            # Check session before performing reschedule
            if __is_session_expired(driver):
                logger.warning(f"Session expired before performing reschedule for re-schedule {re_schedule_id}")
                if not __attempt_relogin_with_retry(driver, login_url, email, password, re_schedule_id):
                    raise Exception("Session expired and could not be recovered after 3 attempts")
                driver.get(appointment_url)
                time.sleep(2)

            # Perform reschedule via POST with cookies
            log_re_schedule(re_schedule_id, "Attempting to perform reschedule with selected date and time", LogState.INFO)
            rescheduled = __perform_reschedule(driver, appointment_url, chosen_date, time_slot, re_schedule_id)
            
            if rescheduled:
                re_schuduel_completed = True
                logger.info(f"Re-schedule {re_schedule_id} completed successfully!")
                re_schedule_services.update_re_schedule(
                    re_schedule_id,
                    ReScheduleUpdate(status=ScheduleStatus.COMPLETED, error=None, end_datetime=datetime.now())
                )
                log_re_schedule(
                    re_schedule_id, 
                    f"Re-schedule completed successfully! New appointment: {chosen_date} at {time_slot}", 
                    LogState.SUCCESS
                )
                pushhover.send_message(f"Successfully Rescheduled for {applicant.get('name')} {applicant.get('last_name')} on {chosen_date} at {time_slot}")
                
                # Exit loop - process completed successfully
                break
            else:
                # If POST failed, stop the process immediately (fail-fast)
                error_msg = "Reschedule POST request failed. Stopping process for safety."
                logger.error(f"{error_msg} Re-schedule ID: {re_schedule_id}")
                log_re_schedule(re_schedule_id, error_msg, LogState.ERROR)
                re_schedule_services.update_re_schedule(
                    re_schedule_id,
                    ReScheduleUpdate(status=ScheduleStatus.FAILED, error=error_msg, end_datetime=datetime.now())
                )
                raise Exception(error_msg)
        
        if not datetime_found:
            logger.info(f"No suitable date found within time window for re-schedule {re_schedule_id}")
            re_schedule_services.update_re_schedule(
                re_schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.NOT_FOUND, end_datetime=datetime.now(), error="No suitable date found")
            )
            log_re_schedule(re_schedule_id, "Time window expired without finding suitable appointment", LogState.ERROR)

    except Exception as e:
        logger.error(f"Error processing re-schedule {re_schedule_id}: {e}", exc_info=True)
        log_re_schedule(re_schedule_id, f"Critical error during re-schedule process: {str(e)}", LogState.ERROR)
        
        try:
            re_schedule_services.update_re_schedule(
                re_schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.FAILED, end_datetime=datetime.now(), error=str(e))
            )
        except Exception as ex:
            logger.exception("Error updating re-schedule status", ex,  exc_info=True)
    finally:
        # Always ensure driver is properly cleaned up
        __safe_quit_driver(driver)

def __perform_reschedule(driver, appointment_url: str, date_str: str, time_slot: str, re_schedule_id: int) -> bool:
    data = {
        "utf8": driver.find_element(By.NAME, 'utf8').get_attribute('value'),
        "authenticity_token": driver.find_element(By.NAME, 'authenticity_token').get_attribute('value'),
        "confirmed_limit_message": driver.find_element(By.NAME, 'confirmed_limit_message').get_attribute('value'),
        "use_consulate_appointment_capacity": driver.find_element(By.NAME, 'use_consulate_appointment_capacity').get_attribute('value'),
        "appointments[consulate_appointment][facility_id]": "143", # Tegucigalpa
        "appointments[consulate_appointment][date]": date_str,
        "appointments[consulate_appointment][time]": time_slot,
    }

    # CSRF
    try:
        csrf_meta = driver.find_element(By.CSS_SELECTOR, 'meta[name="csrf-token"]').get_attribute('content')
    except Exception as ex:
        logger.warning(f"Could not find CSRF token: {ex}")
        csrf_meta = data.get("authenticity_token")

    session = requests.Session()
    __copy_cookies(driver, session)
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
        "Referer": appointment_url,
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRF-Token": csrf_meta,
    }
    session.headers.update(headers)
    try:
        r = session.post(appointment_url, data=data, allow_redirects=True)

        if r.status_code == 200:
            log_re_schedule(re_schedule_id, "Reschedule performed successfully", LogState.INFO)
            return True
        
        log_re_schedule(re_schedule_id, f"Could not perform reschedule[{r.status_code}]: {r.text}", LogState.ERROR)
        logger.warning(f"Could not perform reschedule[{r.status_code}]: {r.text}")
        return False
    except Exception as ex:
        log_re_schedule(re_schedule_id, f"Could not perform reschedule: {ex}", LogState.ERROR)
        logger.warning(f"Could not perform reschedule: something went wrong")
        return False

def __do_login(driver, login_url, email: str, password: str):
    logger.info(f"Testing credentials for {email}")

    driver.get(login_url)
    # Wait for a login form
    Wait(driver, 5).until(EC.presence_of_element_located((By.ID, 'user_email')))

    # Enter email
    user = driver.find_element(By.ID, 'user_email')
    user.clear()
    user.send_keys(email)
    time.sleep(1)

    # Enter password
    pw = driver.find_element(By.ID, 'user_password')
    pw.clear()
    pw.send_keys(password)
    time.sleep(1)

    # Click privacy checkbox
    try:
        box = driver.find_element(By.CLASS_NAME, 'icheckbox')
        box.click()
        time.sleep(1)
    except Exception as e:
        logger.warning(f"Could not find privacy checkbox: {e}")

    # Submit login
    logger.info(f"Submitting login for credentials. email: {email}")
    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(3)

    # Wait for login success indicator
    Wait(driver, 7).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".button.primary.small"))
    )

def __copy_cookies(driver, session):
    for c in driver.get_cookies():
        session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path', '/'))

def __get_dates(driver, appointment_url: str, date_url: str, re_schedule_id: int):
    session = requests.Session()
    __copy_cookies(driver, session)

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": appointment_url,
        "User-Agent": driver.execute_script("return navigator.userAgent;")
    }

    try:
        r = session.get(date_url, headers=headers, allow_redirects=True, timeout=15)
        logger.info(f"Get dates - status: {r.status_code}")
        logger.debug(f"Get dates - response preview: {r.text[:200]}")
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout getting dates for re-schedule {re_schedule_id} - server took too long to respond")
        log_re_schedule(re_schedule_id, "Timeout while fetching available dates - will retry", LogState.WARNING)
        return []
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"Connection error getting dates for re-schedule {re_schedule_id}: {e}")
        log_re_schedule(re_schedule_id, "Network connection error while fetching dates - will retry", LogState.WARNING)
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting dates for re-schedule {re_schedule_id}: {e}")
        log_re_schedule(re_schedule_id, f"Error fetching dates: {str(e)}", LogState.ERROR)
        return []

    try:
        data = r.json()
        return data
    except ValueError:
        log_re_schedule(re_schedule_id, f"The request did not return JSON. status: {r.status_code}", LogState.ERROR)
        logger.warning("The request did not return JSON")
        return r.text

def __get_times(driver, appointment_url: str, time_url: str, re_schedule_id: int):
    session = requests.Session()
    __copy_cookies(driver, session)

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": appointment_url,
        "User-Agent": driver.execute_script("return navigator.userAgent;")
    }

    try:
        r = session.get(time_url, headers=headers, allow_redirects=True, timeout=15)
        logger.info(f"Get times - status: {r.status_code}")
        logger.debug(f"Get times - response preview: {r.text[:200]}")
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout getting times for re-schedule {re_schedule_id} - server took too long to respond")
        log_re_schedule(re_schedule_id, "Timeout while fetching available times - will retry", LogState.WARNING)
        return []
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"Connection error getting times for re-schedule {re_schedule_id}: {e}")
        log_re_schedule(re_schedule_id, "Network connection error while fetching times - will retry", LogState.WARNING)
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting times for re-schedule {re_schedule_id}: {e}")
        log_re_schedule(re_schedule_id, f"Error fetching times: {str(e)}", LogState.ERROR)
        return []

    try:
        data = r.json()
        available_times = data.get("available_times") or []
        return available_times
    except ValueError:
        log_re_schedule(re_schedule_id, f"The request did not return JSON. status: {r.status_code}", LogState.ERROR)
        logger.warning("The request did not return JSON")
        return r.text

def __get_available_date(dates: List[dict], applicant: dict) :
    min_date: datetime = datetime.strptime(applicant.get('min_date'), '%Y-%m-%d')
    max_date: datetime = datetime.strptime(applicant.get('max_date'), '%Y-%m-%d')

    if not min_date or not max_date:
        log_re_schedule(
            re_schedule_id,
            "Applicant missing date boundaries.",
            LogState.ERROR
        )

        logger.warning(f"Applicant {applicant.get('id')} missing date boundaries.")
        return None

    for d in dates:
        current_date: datetime = datetime.strptime(d.get('date'), '%Y-%m-%d')

        if current_date >= min_date and current_date <= max_date:
            logger.info(f"Match found: {current_date}")
            return current_date.strftime('%Y-%m-%d')
    return None


def __safe_quit_driver(driver):
    """
    Safely quit the Selenium driver to prevent zombie processes.
    
    Args:
        driver: Selenium WebDriver instance
    """
    if driver:
        try:
            logger.info("Attempting to quit Selenium driver")
            driver.quit()
            logger.info("Driver quit successfully")
        except Exception as e:
            logger.warning(f"Error quitting driver (may already be closed): {e}")
            try:
                # Force kill if quit failed
                driver.close()
                logger.info("Driver forcefully closed")
            except:
                logger.warning("Could not close driver - may be already terminated")


def __is_session_expired(driver) -> bool:
    """
    Check if the Selenium session has expired.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if session appears expired, False otherwise
    """
    try:
        # Check if we're on the login page
        current_url = driver.current_url
        if '/users/sign_in' in current_url or '/login' in current_url:
            logger.warning("Session expired - redirected to login page")
            return True
            
        # Check if login form elements are present (indicates session expired)
        login_elements = driver.find_elements(By.ID, 'user_email')
        if login_elements:
            logger.warning("Session expired - login form detected")
            return True
            
        return False
    except Exception as e:
        logger.error(f"Error checking session status: {e}")
        # Assume session is valid if we can't determine
        return False


def __attempt_relogin_with_retry(driver, login_url: str, email: str, password: str, 
                                  re_schedule_id: int, max_retries: int = 3) -> bool:
    """
    Attempt to re-login after session expiration, with retry logic.
    
    Args:
        driver: Selenium WebDriver instance
        login_url: URL for login page
        email: User email
        password: User password
        re_schedule_id: ID of the re-schedule process
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if login successful, False if all attempts failed
    """
    logger.warning(f"Session expired for re-schedule {re_schedule_id}. Attempting to re-login...")
    log_re_schedule(re_schedule_id, "Session expired during process. Attempting automatic re-login.", LogState.WARNING)
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Re-login attempt {attempt}/{max_retries} for re-schedule {re_schedule_id}")
            log_re_schedule(
                re_schedule_id, 
                f"Re-login attempt {attempt} of {max_retries}", 
                LogState.INFO
            )
            
            # Attempt login
            __do_login(driver, login_url, email, password)
            
            # Verify login was successful
            time.sleep(2)
            if not __is_session_expired(driver):
                logger.info(f"Re-login successful on attempt {attempt}/{max_retries}")
                log_re_schedule(
                    re_schedule_id, 
                    f"Successfully re-logged in after {attempt} attempt(s)", 
                    LogState.INFO
                )
                return True
            else:
                logger.warning(f"Re-login attempt {attempt} appeared to fail - still on login page")
                
        except Exception as e:
            logger.error(f"Re-login attempt {attempt}/{max_retries} failed: {e}", exc_info=True)
            log_re_schedule(
                re_schedule_id, 
                f"Re-login attempt {attempt} failed: {str(e)}", 
                LogState.ERROR
            )
        
        # Wait before next retry (unless this was the last attempt)
        if attempt < max_retries:
            logger.info(f"Waiting 2 seconds before retry attempt {attempt + 1}")
            time.sleep(2)
    
    # All attempts failed
    logger.error(f"All {max_retries} re-login attempts failed for re-schedule {re_schedule_id}")
    log_re_schedule(
        re_schedule_id, 
        f"Failed to re-login after {max_retries} attempts. Session cannot be recovered.", 
        LogState.ERROR
    )
    return False


def log_re_schedule(re_schedule_id: int, content: str, state: LogState):

    try:
        re_schedule_log_services.create_re_schedule_log(ReScheduleLogCreate(re_schedule=re_schedule_id, state=state, content=content))
    except Exception as e:
        # Don't call log_re_schedule here to avoid infinite recursion
        logger.error(f"Error logging re-schedule: {e}")