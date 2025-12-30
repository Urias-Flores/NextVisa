from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

from services import configuration_services

logger = logging.getLogger(__name__)

def get_driver():
    """
    Get a Chrome WebDriver instance using remote Selenium hub.
    Always uses the hub_address from configuration.
    """
    configuration = configuration_services.get_configuration()
    
    if not configuration or not configuration.hub_address:
        raise Exception("Selenium hub address not configured. Please set hub_address in configuration.")
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    logger.info(f"Connecting to remote Selenium hub: {configuration.hub_address}")
    
    try:
        dr = webdriver.Remote(
            command_executor=configuration.hub_address,
            options=options
        )
        logger.info("Successfully connected to Selenium hub")
        return dr
    except Exception as e:
        logger.error(f"Failed to connect to Selenium hub: {e}")
        raise Exception(f"Could not connect to Selenium hub at {configuration.hub_address}: {str(e)}")

def get_main_url() -> str:
    configuration = configuration_services.get_configuration()
    return configuration.base_url