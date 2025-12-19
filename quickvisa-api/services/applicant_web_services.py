import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
import time
import re
import requests
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from lib.webdriver import get_driver, get_main_url
from services import re_schedule_services, applicant_services
from models.re_schedule import ReScheduleUpdate, ScheduleStatus

logger = logging.getLogger(__name__)

def __do_login(driver, email: str, password: str):
    main_url = get_main_url()
    logger.info(f"Testing credentials for {email}")

    driver.get(main_url)
    time.sleep(1)

    try:
        driver.find_element(By.ID, 'user_email')
    except:
        try:
            a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
            a.click()
            time.sleep(1)
            href = driver.find_element(By.XPATH, '//*[@id="header"]/nav/div[1]/div[1]/div[2]/div[1]/ul/li[3]/a')
            href.click()
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Could not find bounce elements: {e}")

    # Wait for a login form
    Wait(driver, 30).until(EC.presence_of_element_located((By.ID, 'user_email')))

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
        __do_login(driver, email, password)
        
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
            except:
                pass

def _pick_available_date(dates: List[dict], applicant: dict) -> Optional[str]:
    schedule_date = applicant.get('schedule_date')
    min_date = applicant.get('min_date')
    max_date = applicant.get('max_date')

    # Normalize to YYYY-MM-DD strings from API
    def in_range(d: str) -> bool:
        if min_date and d < min_date:
            return False
        if max_date and d > max_date:
            return False
        return True

    def earlier_than_schedule(d: str) -> bool:
        if schedule_date:
            return d < schedule_date
        return True

    for d in dates:
        date_str = d.get('date')
        if not date_str:
            continue
        if (min_date or max_date):
            if in_range(date_str):
                return date_str
        else:
            if earlier_than_schedule(date_str):
                return date_str
    return None

def __copy_cookies(driver, session):
    for c in driver.get_cookies():
        session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path', '/'))

def perform_reschedule(self, driver, appointment_url: str, date_str: str, time_slot: str) -> bool:
    driver.get(appointment_url)

    data = {
        "utf8": driver.find_element(By.NAME, 'utf8').get_attribute('value'),
        "authenticity_token": driver.find_element(By.NAME, 'authenticity_token').get_attribute('value'),
        "confirmed_limit_message": driver.find_element(By.NAME, 'confirmed_limit_message').get_attribute('value'),
        "use_consulate_appointment_capacity": driver.find_element(By.NAME, 'use_consulate_appointment_capacity').get_attribute('value'),
        "appointments[consulate_appointment][facility_id]": "108",
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
    self.__copy_cookies(driver, session)
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
        "Referer": appointment_url,
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRF-Token": csrf_meta,
    }
    session.headers.update(headers)
    r = session.post(appointment_url, data=data, allow_redirects=True)
    if 'Successfully Scheduled' in r.text:
        return True
    return False

def visit_login(self, driver, main_url: str):
    driver.get(main_url)
    time.sleep(1)
    try:
        a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
        a.click()
        time.sleep(1)
    except Exception:
        pass
    try:
        href = driver.find_element(By.XPATH, '//*[@id="header"]/nav/div[1]/div[1]/div[2]/div[1]/ul/li[3]/a')
        href.click()
        time.sleep(1)
    except Exception:
        pass
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))
    try:
        a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
        a.click()
        time.sleep(1)
    except Exception:
        pass

def do_login_action(self, driver, email: str, password: str):
    user = driver.find_element(By.ID, 'user_email')
    user.clear()
    user.send_keys(email)
    time.sleep(random.randint(1, 3))

    pw = driver.find_element(By.ID, 'user_password')
    pw.clear()
    pw.send_keys(password)
    time.sleep(random.randint(1, 3))

    try:
        box = driver.find_element(By.CLASS_NAME, 'icheckbox')
        box.click()
        time.sleep(random.randint(1, 3))
    except Exception as ex:
        logger.warning(f"Could not find privacy checkbox: {ex}")
        pass

    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(random.randint(1, 3))

def process_re_schedule(self, re_schedule_id: int):
    driver = None
    try:
        # Mark as PROCESSING and set start time
        re_schedule_services.update_re_schedule(
            re_schedule_id,
            ReScheduleUpdate(status=ScheduleStatus.PROCESSING, start_datetime=datetime.now())
        )

        rs = re_schedule_services.get_re_schedule_by_id(re_schedule_id)
        applicant_id = rs.get('applicant')
        if not applicant_id:
            raise Exception("Missing applicant id")

        applicant = applicant_services.get_applicant_with_password(applicant_id)
        email = applicant.get('email')
        password = applicant.get('password')
        schedule_number = applicant.get('schedule')

        if not email or not password or not schedule_number:
            raise Exception("Applicant email, password or schedule missing")

        # Build base URLs from configuration
        base_url = self.config.base_url
        hub_address = self.config.hub_address

        if not hub_address or not base_url:
            raise Exception("Selenium hub address missing")

        main_url = base_url
        appointment_url = f"{base_url}/schedule/{schedule_number}/appointment"
        days_url = f"{base_url}/schedule/{schedule_number}/appointment/days/143.json?appointments[expedite]=false"
        times_url_tmpl = f"{base_url}/schedule/{schedule_number}/appointment/times/143.json?date=%s&appointments[expedite]=false"

        driver = self._get_driver(hub_address)

        # Navigate and login
        self._visit_login(driver, main_url)
        self._do_login_action(driver, email, password)

        # Ensure logged in
        Wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".button.primary.small")))

        # Get available dates via requests with Selenium cookies
        dates = self._get_dates_via_requests(driver, days_url, appointment_url)
        if isinstance(dates, dict):
            dates_list: List[dict] = dates.get('available_dates') or dates.get('dates') or []
        elif isinstance(dates, list):
            dates_list = dates
        else:
            dates_list = []

        chosen_date = self._pick_available_date(dates_list, applicant)
        if not chosen_date:
            logger.info(f"No suitable date found for re-schedule {re_schedule_id}")
            # Keep job running; do not mark as failed
            return

        # Get time for chosen date
        driver.get(times_url_tmpl % chosen_date)
        content = driver.find_element(By.TAG_NAME, 'pre').text
        data = json.loads(content) if content else {}
        available_times = data.get("available_times") or []
        if not available_times:
            logger.info(f"No times available for date {chosen_date}")
            return
        time_slot = available_times[-1]

        # Perform reschedule via POST with cookies
        rescheduled = self._perform_reschedule(driver, appointment_url, chosen_date, time_slot)

        if rescheduled:
            re_schedule_services.update_re_schedule(
                re_schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.COMPLETED, end_datetime=datetime.now(), error=None)
            )
            self._send_push(f"Successfully Rescheduled to {chosen_date} at {time_slot}")
            self._remove_job(re_schedule_id)
        else:
            # If POST failed, leave processing to retry later
            logger.warning(f"Reschedule POST failed for {re_schedule_id}, will retry")

    except Exception as e:
        logger.error(f"Error processing re-schedule {re_schedule_id}: {e}", exc_info=True)
        try:
            re_schedule_services.update_re_schedule(
                re_schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.FAILED, end_datetime=datetime.now(), error=str(e))
            )
        except Exception:
            pass
        self._remove_job(re_schedule_id)
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass