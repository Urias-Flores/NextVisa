import time
import json
import random
import platform
from datetime import datetime
from pickle import GLOBAL

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By

USERNAME = 'vasquezlopezmaobelia@gmail.com'
PASSWORD = 'Lopezmaobelia123*'
SCHEDULE = '71480241'

PUSH_TOKEN = 'a54n8t4kdpt73wi66wwxgdri7q9k36'
PUSH_USER = 'umcsd812b43tjize7dcmmmotd1a3f8'

MY_SCHEDULE_DATE = "2026-03-25"  # 2020-12-02
# MY_CONDITION = lambda month,day: int(month) == 11 or (int(month) == 12 and int(day) <=5)
MY_CONDITION = lambda month, day: int(month) == 2 and int(day) <= 5

SLEEP_TIME = 10  # recheck time interval
MAIN_URL = "https://ais.usvisa-info.com/en-hn/niv"
DATE_URL = f"{MAIN_URL}/schedule/{SCHEDULE}/appointment/days/143.json?appointments[expedite]=false"
TIME_URL = f"{MAIN_URL}/schedule/{SCHEDULE}/appointment/times/143.json?date=%%s&appointments[expedite]=false"
APPOINTMENT_URL = f"{MAIN_URL}/schedule/{SCHEDULE}/appointment"
HUB_ADDRESS = 'http://localhost:4444/wd/hub'
EXIT = False


def send(msg):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSH_TOKEN,
        "user": PUSH_USER,
        "message": msg
    }
    requests.post(url, data)


def get_drive():
    local_use = platform.system() == 'Darwin'
    if local_use:
        service = Service('./chromedriver')
        dr = webdriver.Chrome(service=service)
    else:
        options = Options()
        dr = webdriver.Remote(
            command_executor=HUB_ADDRESS,
            options=options
        )
    return dr


driver = get_drive()


def login():
    # Bypass reCAPTCHA
    print(f"visit login page on: {MAIN_URL}")
    driver.get(MAIN_URL)
    time.sleep(1)
    a = driver.find_element(By.XPATH,'//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    print("start sign")
    href = driver.find_element(By.XPATH,'//*[@id="header"]/nav/div[1]/div[1]/div[2]/div[1]/ul/li[3]/a')
    href.click()
    time.sleep(1)
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))

    print("click bounce")
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    do_login_action()


def do_login_action():
    print("input email")
    user = driver.find_element(By.ID, 'user_email')
    user.send_keys(USERNAME)
    time.sleep(random.randint(1, 3))

    print("input pwd")
    pw = driver.find_element(By.ID,'user_password')
    pw.send_keys(PASSWORD)
    time.sleep(random.randint(1, 3))

    print("click privacy")
    box = driver.find_element(By.CLASS_NAME,'icheckbox')
    box.click()
    time.sleep(random.randint(1, 3))

    print("commit")
    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(random.randint(1, 3))

    Wait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".button.primary.small")))
    print("Login successfully! ")


def get_date():
    # driver.get(DATE_URL)
    dates_found = get_date_via_requests_using_selenium_cookies(driver)
    print("get date")
    if not is_logined():
        print("re trying login")
        login()
        return get_date()
    else:
        print("getting dates")
        # content = driver.find_element(By.TAG_NAME, 'pre').text
        # date = json.loads(content)
        print(f"date: {date}")
        return dates_found


def get_time(date):
    time_url = TIME_URL % date
    driver.get(time_url)
    content = driver.find_element(By.TAG_NAME,'pre').text
    data = json.loads(content)
    time = data.get("available_times")[-1]
    print("Get time successfully!")
    return time

# def copy_cookies_from_selenium_to_session(driver, session):
#     # Copia cookies visibles por Selenium a requests.Session
#     for c in driver.get_cookies():
#         cookie = {
#             'domain': c.get('domain'),
#             'name': c.get('name'),
#             'value': c.get('value'),
#             'path': c.get('path', '/'),
#             'secure': c.get('secure', False),
#             'rest': {'HttpOnly': c.get('httpOnly', False)}
#         }
#         session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])

def copy_cookies_from_selenium_to_session(driver, session):
    for c in driver.get_cookies():
        session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path', '/'))

def get_date_via_requests_using_selenium_cookies(driver):
    session = requests.Session()
    copy_cookies_from_selenium_to_session(driver, session)

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": APPOINTMENT_URL,  # o MAIN_URL según convenga
        "User-Agent": driver.execute_script("return navigator.userAgent;")
    }

    r = session.get(DATE_URL, headers=headers, allow_redirects=True, timeout=15)
    print("status:", r.status_code)
    # imprime hasta 2000 chars para no saturar consola
    print("text (start):", r.text[:200])

    # intentar parsear JSON si viene JSON
    try:
        data = r.json()
        print("JSON keys:", data.keys())
        return data
    except ValueError:
        print("No devolvió JSON (posible HTML de error).")
        return r.text

def reschedule(date):
    global EXIT
    print("Start Reschedule")

    time_slot = get_time(date)  # tu función ya existente
    driver.get(APPOINTMENT_URL)

    # Extrae valores del formulario (ya lo hacías)
    data = {
        "utf8": driver.find_element(By.NAME, 'utf8').get_attribute('value'),
        "authenticity_token": driver.find_element(By.NAME, 'authenticity_token').get_attribute('value'),
        "confirmed_limit_message": driver.find_element(By.NAME, 'confirmed_limit_message').get_attribute('value'),
        "use_consulate_appointment_capacity": driver.find_element(By.NAME,
                                                                  'use_consulate_appointment_capacity').get_attribute(
            'value'),
        "appointments[consulate_appointment][facility_id]": "108",
        "appointments[consulate_appointment][date]": date,
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
        "Referer": APPOINTMENT_URL,
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
    r = session.post(APPOINTMENT_URL, data=data, allow_redirects=True)

    # Depuración opcional:
    print("POST status:", r.status_code)
    # print("Response headers:", r.headers)
    # print("Response text:", r.text[:1000])

    if r.text.find('Successfully Scheduled') != -1:
        print("Successfully Rescheduled")
        send("Successfully Rescheduled")
        EXIT = True
    else:
        print("ReScheduled Fail")
        send("ReScheduled Fail")


def is_logined():
    content = driver.page_source
    print("is_logined")
    print(content)
    if content.find("error") != -1:
        print("An error occured")
        EXIT = True
        return False
    return True


def print_date(dates):
    for d in dates:
        print("%s \t business_day: %s" % (d.get('date'), d.get('business_day')))
    print()


last_seen = None


def get_available_date(dates):
    global last_seen
    print("getting available dates")
    def is_earlier(date):
        print("is_earlier")
        return datetime.strptime(MY_SCHEDULE_DATE, "%Y-%m-%d") > datetime.strptime(date, "%Y-%m-%d")

    for d in dates:
        date = d.get('date')
        if is_earlier(date) and date != last_seen:
            _, month, day = date.split('-')
            if MY_CONDITION(month, day):
                last_seen = date
                return date
    return None


def push_notification(dates):
    msg = "date: "
    for d in dates:
        msg = msg + d.get('date') + '; '
    send(msg)


if __name__ == "__main__":
    login()
    retry_count = 0
    while 1:
        if retry_count > 6:
            break
        try:
            print(datetime.today())
            print("------------------")

            dates = get_date()[:5]
            print_date(dates)
            date = get_available_date(dates)
            if date:
                reschedule(date)
                push_notification(dates)

            if (EXIT):
                break

            time.sleep(SLEEP_TIME)
        except:
            retry_count += 1
            time.sleep(60 * 5)

    if not EXIT:
        send("HELP! Crashed.")