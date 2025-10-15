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
        
        # Anti-detection: Remove WebDriver traces to avoid Akamai bot detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional anti-fingerprinting for Akamai
        options.add_argument('--disable-web-security')
        options.add_argument('--lang=pl-PL,pl,en-US,en')
        options.add_experimental_option('prefs', {
            'intl.accept_languages': 'pl-PL,pl,en-US,en',
            'profile.default_content_setting_values.notifications': 2,
        })

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
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        # Execute CDP commands to hide automation and bypass Akamai fingerprinting
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // Hide webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Spoof plugins to look like real browser
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Spoof languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pl-PL', 'pl', 'en-US', 'en']
                });
                
                // Override chrome property
                window.chrome = {
                    runtime: {}
                };
                
                // Override permissions query
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Canvas fingerprinting protection
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    if (type === 'image/png' && this.width === 16 && this.height === 16) {
                        return originalToDataURL.apply(this, arguments);
                    }
                    const context = this.getContext('2d');
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] = imageData.data[i] ^ 1;
                    }
                    context.putImageData(imageData, 0, 0);
                    return originalToDataURL.apply(this, arguments);
                };
                
                // WebGL fingerprinting protection
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };
                
                // Timezone spoofing for Warsaw
                Date.prototype.getTimezoneOffset = function() {
                    return -60; // UTC+1 (Warsaw winter time)
                };
            '''
        })
        
        # Set timezone to Europe/Warsaw via CDP
        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
            'timezoneId': 'Europe/Warsaw'
        })
        
        # Set locale
        driver.execute_cdp_cmd('Emulation.setLocaleOverride', {
            'locale': 'pl-PL'
        })
        
        return driver
