import time
import re
import platform
import logging
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)

HUB_ADDRESS = 'http://localhost:4444/wd/hub'
MAIN_URL = "https://ais.usvisa-info.com/en-hn/niv"

def get_driver():
    """Initialize and return a Selenium WebDriver"""
    local_use = platform.system() in ['Darwin', 'Windows']
    if local_use:
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        dr = webdriver.Chrome(options=options)
    else:
        options = Options()
        dr = webdriver.Remote(
            command_executor=HUB_ADDRESS,
            options=options
        )
    return dr

def test_applicant_credentials(email: str, password: str) -> Dict[str, Optional[str]]:
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
        logger.info(f"Testing credentials for {email}")
        driver = get_driver()
        
        # Navigate to login page
        logger.info(f"Navigating to {MAIN_URL}")
        driver.get(MAIN_URL)
        time.sleep(2)
        
        # Handle potential bounce page or direct login
        try:
            # Try to find the login form directly first
            driver.find_element(By.ID, 'user_email')
        except:
            # If not found, click through to login page
            try:
                a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
                a.click()
                time.sleep(1)
                href = driver.find_element(By.XPATH, '//*[@id="header"]/nav/div[1]/div[1]/div[2]/div[1]/ul/li[3]/a')
                href.click()
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Could not find bounce elements: {e}")
        
        # Wait for login form
        Wait(driver, 30).until(EC.presence_of_element_located((By.ID, 'user_email')))
        
        logger.info("Entering credentials")
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
        logger.info("Submitting login")
        btn = driver.find_element(By.NAME, 'commit')
        btn.click()
        time.sleep(3)
        
        # Wait for either success or error
        try:
            # Wait for successful login indicator
            Wait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".button.primary.small"))
            )
            logger.info("Login successful!")
            
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
                # Try to navigate to appointment page to get schedule from URL
                try:
                    # Look for appointment or continue button
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
            # Check if there's an error message
            page_source = driver.page_source
            if "error" in page_source.lower() or "invalid" in page_source.lower():
                logger.error("Login failed - invalid credentials")
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Invalid email or password"
                }
            else:
                logger.error(f"Login timeout or unexpected error: {e}")
                return {
                    "success": False,
                    "schedule": None,
                    "error": "Login timeout or unexpected error"
                }
                
    except Exception as e:
        logger.error(f"Error testing credentials: {e}")
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
