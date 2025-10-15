import logging
import os
import tempfile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.remote_connection import LOGGER as webdriver_logger
from urllib3.connectionpool import log as urllib_logger


class BrowserFactory:
    def __init__(self, log_level=logging.WARNING):
        webdriver_logger.setLevel(log_level)
        urllib_logger.setLevel(log_level)

    def create(
        self,
        maximized: bool = False,
        window_size: str = '1920,1080',
        service_log_path: str | None = None,
    ):
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--remote-allow-origins=*')
        options.add_argument(f'--window-size={window_size}')
        if maximized:
            options.add_argument('--start-maximized')
        
        # Generate unique user-data-dir to avoid "directory is already in use" error
        profile_path = os.environ.get('PROFILE_PATH')
        if profile_path:
            # If PROFILE_PATH is set, use it with PID to make it unique
            user_data_dir = f'{profile_path}-{os.getpid()}'
        else:
            # Otherwise create temporary directory
            user_data_dir = tempfile.mkdtemp(prefix='chrome-profile-')
        
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        # Headless mode support
        headless_mode = os.environ.get('HEADLESS', 'false').lower() == 'true'
        if headless_mode:
            options.add_argument('--headless=new')

        binary_path = os.environ.get('CHROME_BINARY')
        if binary_path:
            options.binary_location = binary_path

        service: ChromeService | None = None
        driver_path = os.environ.get('CHROMEDRIVER_PATH')
        if driver_path:
            service = ChromeService(executable_path=driver_path, log_path=service_log_path)

        # Create Chrome WebDriver with standard selenium
        if service:
            return webdriver.Chrome(service=service, options=options)
        else:
            return webdriver.Chrome(options=options)
