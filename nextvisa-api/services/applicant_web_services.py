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
from services import re_schedule_services, applicant_services, configuration_services
from models.re_schedule import ReScheduleUpdate, ScheduleStatus
from lib import security

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

def __pick_available_date(dates: List[dict], applicant: dict) -> Optional[str]:
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

def perform_reschedule(driver, appointment_url: str, date_str: str, time_slot: str) -> bool:
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
    __copy_cookies(driver, session)
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

def _visit_login(driver, main_url: str):
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
        logger.info("Logged in successfully")
    except Exception:
        pass

def _do_login_action(driver, email: str, password: str):
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
    logger.info(f"Submitting login for credentials. email: {email}")
    time.sleep(random.randint(1, 3))

def copy_cookies_from_selenium_to_session(driver, session):
    for c in driver.get_cookies():
        session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path', '/'))

def get_date_via_requests_using_selenium_cookies(driver, appointment_url: str, date_url: str):
    session = requests.Session()
    copy_cookies_from_selenium_to_session(driver, session)

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": appointment_url,
        "User-Agent": driver.execute_script("return navigator.userAgent;")
    }

    r = session.get(date_url, headers=headers, allow_redirects=True, timeout=15)
    print("status:", r.status_code)
    print("text (start):", r.text[:200])

    # intentar parsear JSON si viene JSON
    try:
        data = r.json()
        print("JSON keys:", data.keys())
        return data
    except ValueError:
        print("No devolvió JSON (posible HTML de error).")
        return r.text

def date_available_is_valid(min_date: DateTime, max_date: DateTime, date_available: DateTime) -> bool:
    return min_date <= date_available <= max_date

def get_available_date(dates, applicant: ApplicantBase):
    global last_seen
    print("getting available dates")
    def is_earlier(date):
        print("is_earlier")
        return datetime.strptime(applicant.schedule_date, "%Y-%m-%d") > datetime.strptime(date, "%Y-%m-%d")

    for d in dates:
        date = d.get('date')
        if is_earlier(date) and date != last_seen:
            _, month, day = date.split('-')
            if date_available_is_valid(DateTime(applicant.min_date), DateTime(applicant.max_date), d):
                last_seen = date
                return date
    return None

def process_re_schedule(re_schedule_id: int):
    driver = None
    try:
        # Mark as PROCESSING and set the start time
        re_schedule_services.update_re_schedule(
            re_schedule_id,
            ReScheduleUpdate(status=ScheduleStatus.PROCESSING, start_datetime=datetime.now())
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

        main_url = base_url
        appointment_url = f"{base_url}/schedule/{schedule_number}/appointment"
        days_url = f"{base_url}/schedule/{schedule_number}/appointment/days/143.json?appointments[expedite]=false"
        times_url_tmpl = f"{base_url}/schedule/{schedule_number}/appointment/times/143.json?date=%s&appointments[expedite]=false"

        driver = get_driver()

        # Navigate and login
        return password
        _visit_login(driver, main_url)
        _do_login_action(driver, email, password)

        # Ensure logged in
        print(driver.page_source)
        # TODO: add email or password invalid validation
        Wait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".button.primary.small")))

        # Get available dates via requests with Selenium cookies
        dates = get_date_via_requests_using_selenium_cookies(driver, appointment_url, days_url)
        logger.info(f"Dates available: {dates}")
        return
        if isinstance(dates, dict):
            dates_list: List[dict] = dates.get('available_dates') or dates.get('dates') or []
        elif isinstance(dates, list):
            dates_list = dates
        else:
            dates_list = []

        chosen_date = get_available_date(dates_list, applicant)
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
        # rescheduled = _perform_reschedule(driver, appointment_url, chosen_date, time_slot)

        rescheduled = True
        if rescheduled:
            re_schedule_services.update_re_schedule(
                re_schedule_id,
                ReScheduleUpdate(status=ScheduleStatus.COMPLETED, end_datetime=datetime.now(), error=None)
            )
            # _send_push(f"Successfully Rescheduled to {chosen_date} at {time_slot}")
            # _remove_job(re_schedule_id)
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
        # _remove_job(re_schedule_id)
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass

def _perform_reschedule(driver, date, appointment_url: str, date_found, time_slot):
    global EXIT
    logger.info("Start Reschedule")

    # Extrae valores del formulario (ya lo hacías)
    data = {
        "utf8": driver.find_element(By.NAME, 'utf8').get_attribute('value'),
        "authenticity_token": driver.find_element(By.NAME, 'authenticity_token').get_attribute('value'),
        "confirmed_limit_message": driver.find_element(By.NAME, 'confirmed_limit_message').get_attribute('value'),
        "use_consulate_appointment_capacity": driver.find_element(By.NAME,
                                                                  'use_consulate_appointment_capacity').get_attribute(
            'value'),
        "appointments[consulate_appointment][facility_id]": "108",
        "appointments[consulate_appointment][date]": date_found,
        "appointments[consulate_appointment][time]": time_slot,
    }

    # Extrae CSRF token (meta tag) si está presente
    try:
        csrf_meta = driver.find_element(By.CSS_SELECTOR, 'meta[name="csrf-token"]').get_attribute('content')
    except:
        csrf_meta = None

    # Crear sesión requests y copiar cookies de Selenium
    session = requests.Session()
    copy_cookies_from_selenium_to_session(driver, session)

    # Construir headers; las cookies ya las maneja session
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
        "Referer": appointment_url,
        "X-Requested-With": "XMLHttpRequest",
    }
    # Añadir X-CSRF-Token si lo encontramos
    if csrf_meta:
        headers["X-CSRF-Token"] = csrf_meta
    else:
        # alternativa: intentar obtenerlo desde el input hidden (ya lo tienes en authenticity_token)
        headers["X-CSRF-Token"] = data.get("authenticity_token")

    session.headers.update(headers)

    # Hacer la petición POST
    r = session.post(appointment_url, data=data, allow_redirects=True)

    # Depuración opcional:
    print("POST status:", r.status_code)
    # print("Response headers:", r.headers)
    # print("Response text:", r.text[:1000])

    if r.text.find('Successfully Scheduled') != -1:
        logger.info("Successfully Rescheduled")
    else:
        logger.info("ReScheduled Fail")