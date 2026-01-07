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
        while datetime.strptime(str(rs.get('end_datetime')).replace("T", " "), "%Y-%m-%d %H:%M:%S") <= datetime.now() or not re_schudule_completed:
            time.sleep(config.sleep_time)

            # Get available dates via requests with Selenium cookies
            dates = __get_dates(driver, appointment_url, days_url)
            if len(dates) == 0:
                logger.info(f"No dates available for re-schedule {re_schedule_id}")
                re_schedule_services.update_re_schedule(
                    re_schedule_id,
                    ReScheduleUpdate(error="No dates available")
                )
                log_re_schedule(re_schedule_id, "No dates available", LogState.ERROR)
                continue
            
            logger.info(f"Earlier date available: {dates[0]}")
            log_re_schedule(re_schedule_id, f"Earlier date available: {dates[0]}", LogState.INFO)
            if isinstance(dates, dict):
                dates_list: List[dict] = dates.get('available_dates') or dates.get('dates') or []
            elif isinstance(dates, list):
                dates_list = dates
            else:
                dates_list = []

            chosen_date = __get_available_date(dates_list, applicant)
            if not chosen_date:
                logger.info(f"No suitable date found for re-schedule {re_schedule_id}")
                re_schedule_services.update_re_schedule(
                    re_schedule_id,
                    ReScheduleUpdate(error="No suitable date found")
                )
                log_re_schedule(re_schedule_id, "No suitable date found.", LogState.ERROR)
                continue

            # Get time for chosen a date
            available_times = __get_times(driver, appointment_url, times_url_tmpl % chosen_date)
            if not available_times:
                logger.info(f"No times available for date {chosen_date}")
                re_schedule_services.update_re_schedule(
                    re_schedule_id,
                    ReScheduleUpdate(error="No suitable time found")
                )
                log_re_schedule(re_schedule_id, "No suitable time found.", LogState.ERROR)
                continue
            time_slot = available_times[-1]

            datetime_found = True
            # Perform reschedule via POST with cookies
            log_re_schedule(re_schedule_id, "Performing reschedule. A date and time has been selected.", LogState.INFO)
            rescheduled = __perform_reschedule(driver, appointment_url, chosen_date, time_slot, re_schedule_id)
            log_re_schedule(re_schedule_id, f"Reschedule performed. result: {rescheduled}", LogState.INFO)

            if rescheduled:
                re_schuduel_completed = True
                re_schedule_services.update_re_schedule(
                    re_schedule_id,
                    ReScheduleUpdate(status=ScheduleStatus.COMPLETED, error=None, end_datetime=datetime.now())
                )
                pushhover.send_message(f"Successfully Rescheduled for {applicant.get('name')} {applicant.get('last_name')} on {chosen_date} at {time_slot}")
            else:
                # If POST failed, leave processing to retry later
                logger.warning(f"Reschedule POST failed for {re_schedule_id}, will retry")
        
        if not datetime_found:
            logger.info(f"No suitable date found for re-schedule {re_schedule_id}")
            re_schedule_services.update_re_schedule(
                re_schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.NOT_FOUND, end_datetime=datetime.now(), error="No suitable date found")
            )
            log_re_schedule(re_schedule_id, "No suitable date found.", LogState.ERROR)

    except Exception as e:
        logger.error(f"Error processing re-schedule {re_schedule_id}: {e}", exc_info=True)
        try:
            re_schedule_services.update_re_schedule(
                re_schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.FAILED, end_datetime=datetime.now(), error=str(e))
            )
        except Exception as ex:
            logger.exception("Error updating re-schedule status", ex,  exc_info=True)
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as ex:
            logger.warning("Could not quit Selenium driver", ex)

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
    Wait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".button.primary.small"))
    )

def __copy_cookies(driver, session):
    for c in driver.get_cookies():
        session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path', '/'))

def __get_dates(driver, appointment_url: str, date_url: str):
    session = requests.Session()
    __copy_cookies(driver, session)

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": appointment_url,
        "User-Agent": driver.execute_script("return navigator.userAgent;")
    }

    r = session.get(date_url, headers=headers, allow_redirects=True, timeout=15)
    logger.info(f"status: {r.status_code}")
    logger.info(f"text (start): {r.text[:200]}")

    try:
        data = r.json()
        return data
    except ValueError:
        log_re_schedule(re_schedule_id, f"The request did not return JSON. status: {r.status_code}", LogState.ERROR)
        logger.warning("The request did not return JSON")
        return r.text

def __get_times(driver, appointment_url: str, time_url: str):
    session = requests.Session()
    __copy_cookies(driver, session)

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": appointment_url,
        "User-Agent": driver.execute_script("return navigator.userAgent;")
    }

    r = session.get(time_url, headers=headers, allow_redirects=True, timeout=15)
    logger.info(f"status: {r.status_code}")
    logger.info(f"text (start): {r.text[:200]}")

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

def log_re_schedule(re_schedule_id: int, content: str, state: LogState):
    try:
        re_schedule_log_services.create_re_schedule_log(ReScheduleLogCreate(re_schedule=re_schedule_id, state=state, content=content))
    except Exception as e:
        # Don't call log_re_schedule here to avoid infinite recursion
        logger.error(f"Error logging re-schedule: {e}")