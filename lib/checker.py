import logging
import random as rand
import time
from random import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from lib.checker_config import CheckerConfig
from lib.human_behavior import HumanBehavior


class Checker:
    def __init__(self, config: CheckerConfig):
        self.config = config
        self.human = HumanBehavior(config.browser)
    
    def detect_captcha(self):
        """Detect Akamai captcha and wait for manual solving."""
        try:
            captcha_detected = False
            detection_reason = ""
            
            # Method 1: Check for VISIBLE Akamai iframe
            captcha_iframes = self.config.browser.find_elements(By.CSS_SELECTOR, "iframe[src*='akamai']")
            for iframe in captcha_iframes:
                if iframe.is_displayed():
                    try:
                        size = iframe.size
                        if size['width'] > 100 and size['height'] > 100:  # Must be reasonably sized
                            captcha_detected = True
                            detection_reason = 'Akamai iframe (visible and sized)'
                            logging.debug(f'Captcha detected: {detection_reason}')
                            break
                    except:
                        pass
            
            # Method 2: Check for VISIBLE Akamai div overlay with proper size
            if not captcha_detected:
                # More specific selectors based on real Akamai structure
                akamai_selectors = [
                    "div[id^='sec-if-cpt']",  # starts with
                    "div[id^='sec-cpt']",
                    "div.behavioral-content",
                    "div[class*='akamai']"
                ]
                
                for selector in akamai_selectors:
                    try:
                        containers = self.config.browser.find_elements(By.CSS_SELECTOR, selector)
                        for container in containers:
                            if container.is_displayed():
                                size = container.size
                                # Overlay должен быть достаточно большим (минимум 200x200px)
                                if size['width'] > 200 and size['height'] > 200:
                                    # Проверяем что элемент действительно видим (не прозрачный)
                                    opacity = container.value_of_css_property('opacity')
                                    if opacity and float(opacity) > 0.5:
                                        captcha_detected = True
                                        detection_reason = f'Akamai overlay ({selector}, size: {size["width"]}x{size["height"]})'
                                        logging.debug(f'Captcha detected: {detection_reason}')
                                        break
                    except Exception as e:
                        logging.debug(f'Error checking {selector}: {e}')
                        continue
                    
                    if captcha_detected:
                        break
            
            # Method 3: Check for VISIBLE captcha text in modal/dialog
            if not captcha_detected:
                try:
                    # Ищем только ВИДИМЫЙ текст капчи в модальном окне или диалоге
                    captcha_text_xpaths = [
                        "//div[contains(@class, 'modal') or contains(@class, 'dialog') or contains(@class, 'popup')]//*[contains(text(), 'Potwierdź') or contains(text(), 'człowiekiem') or contains(text(), 'robot')]",
                        "//*[contains(@id, 'captcha')]//*[contains(text(), 'Potwierdź') or contains(text(), 'człowiekiem')]"
                    ]
                    
                    for xpath in captcha_text_xpaths:
                        elements = self.config.browser.find_elements(By.XPATH, xpath)
                        for el in elements:
                            if el.is_displayed():
                                captcha_detected = True
                                detection_reason = f'Captcha text in modal/dialog: "{el.text[:50]}"'
                                logging.debug(f'Captcha detected: {detection_reason}')
                                break
                        if captcha_detected:
                            break
                except Exception as e:
                    logging.debug(f'Text element search error: {e}')
            
            # If captcha detected, notify and wait
            if captcha_detected:
                msg = f'🚨 AKAMAI CAPTCHA DETECTED!\n'
                msg += f'📍 Detection: {detection_reason}\n\n'
                msg += '⏰ Bot paused for 2 minutes\n'
                msg += '🔗 VNC: http://localhost:6080 (password: password)\n'
                msg += '✅ Please solve the captcha manually\n\n'
                msg += '⚠️ If not solved in 2 min, bot will try to continue'
                
                logging.warning(f'CAPTCHA DETECTED ({detection_reason}) - pausing for 2 minutes')
                self.config.messenger.send_message(msg)
                
                # Wait 2 minutes for manual solving
                logging.info('Waiting 120 seconds for captcha to be solved manually...')
                time.sleep(120)
                
                logging.info('Resuming after captcha wait period')
                return True
                
        except Exception as e:
            logging.debug(f'Captcha detection error: {e}')
        
        return False

    @property
    def waiter(self):
        return WebDriverWait(self.config.browser, self.config.page_load_timeout)

    def login_page_url(self):
        return 'https://inpol.mazowieckie.pl/login'

    def case_page_url(self, case_id):
        return f'https://inpol.mazowieckie.pl/home/cases/{case_id}'

    def login(self):
        self.config.browser.get(self.login_page_url())
        
        # Simulate page load time (human reading)
        self.human.simulate_reading(1.5, 3.0)

        sign_in = self.waiter.until(
            EC.visibility_of_element_located((By.XPATH, '//button[contains(@class, "btn--submit")]')))

        # Handle cookie banner with human-like behavior
        x_cookie = '//a[contains(@aria-label,"cookie") and contains(@aria-label,"dismiss")]'
        try:
            cookie_block = self.config.browser.find_element(by=By.XPATH, value=x_cookie)
            if cookie_block.is_displayed():
                self.human.human_click(cookie_block)
        except:
            pass

        # Type email slowly like a human
        email_el = self.config.browser.find_element(by=By.XPATH, value='//input[@formcontrolname="email"]')
        self.human.slow_type(email_el, self.config.email)
        
        # Random delay before password (thinking time)
        self.human.random_delay(0.5, 1.2)

        # Type password slowly
        password_el = self.config.browser.find_element(by=By.XPATH, value='//input[@formcontrolname="password"]')
        self.human.slow_type(password_el, self.config.password)

        # Random delay before clicking sign in
        self.human.random_delay(0.8, 1.5)
        
        logging.info('sign in')
        self.human.human_click(sign_in)
        
        # Wait for response with random mouse movement
        self.human.random_mouse_movement()
        time.sleep(2)

        x_error = '//mat-error[contains(text(),"Incorrect email")]'
        if len(self.config.browser.find_elements(by=By.XPATH, value=x_error)) != 0:
            logging.error('Wrong password or maintenance hours')
            return False
        self.waiter.until(
            EC.visibility_of_element_located((By.XPATH, '//a[@routerlink="/home/cases-choose" and @class="btn"]')))
        return True

    def random_sleep(self, min_period=0.3, max_period=0.9):
        time.sleep(random() * (max_period - min_period) + min_period)

    def wait_spinner(self):
        self.random_sleep(min_period=0.3, max_period=0.5)
        x_progress_bar = '//mat-spinner[@role="progressbar"]'
        self.waiter.until_not(EC.visibility_of_element_located((By.XPATH, x_progress_bar)))

    # Language-independent selector - find accordion with "appointment" class or structure
    # Look for the accordion section that contains location/queue dropdowns
    x_appointment_section = '//div[contains(@class,"accordion")]//mat-select[@name="location"]'

    def open_case_page(self):
        self.config.browser.get(self.case_page_url(self.config.case_id))
        time.sleep(rand.uniform(1, 2))  # Faster page load
        
        # Check for captcha
        self.detect_captcha()
        
        # Look for location dropdown (it's inside the appointment section)
        # This is language-independent
        try:
            self.waiter.until(EC.presence_of_element_located((By.XPATH, self.x_appointment_section)))
            logging.info('Appointment section found (detected location dropdown)')
            return True
        except Exception as e:
            logging.error(f'Appointment section not found: {e}')
            # Debug: print page structure
            all_buttons = self.config.browser.find_elements(by=By.XPATH, value='//button')
            logging.error(f'Found {len(all_buttons)} buttons on page')
            return False

    def expand_appointment_panel(self):
        logging.info('check if appointment panel needs expanding')
        time.sleep(rand.uniform(2, 4))  # Human-like delay
        
        # Language-independent: find location dropdown and check if visible
        x_location_dropdown = '//mat-select[@name="location"]'
        
        try:
            # Check if location dropdown is already visible first
            dropdown_elements = self.config.browser.find_elements(by=By.XPATH, value=x_location_dropdown)
            
            if len(dropdown_elements) > 0 and dropdown_elements[0].is_displayed():
                logging.info('Panel already expanded (location dropdown visible)')
                return
            
            # Multi-language XPath for appointment section button
            # Finds h3 heading with any language variant and gets the accordion button after it
            x_appointment_button = '//h3[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "appointment") or contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "wizyt") or contains(translate(text(), "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"), "зустріч") or contains(translate(text(), "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"), "встречу")]/following::button[contains(@class, "btn--accordion")][1]'
            
            logging.debug('Looking for appointment accordion button with multi-language selector')
            button_elements = self.config.browser.find_elements(by=By.XPATH, value=x_appointment_button)
            
            if len(button_elements) == 0:
                logging.warning('Appointment accordion button not found with multi-language selector')
                # Fallback: check if dropdown is visible anyway
                dropdown_elements = self.config.browser.find_elements(by=By.XPATH, value=x_location_dropdown)
                if len(dropdown_elements) > 0 and dropdown_elements[0].is_displayed():
                    logging.info('Panel already expanded (no button needed)')
                return
            
            # Panel is collapsed, click the accordion button to expand
            logging.info('Panel collapsed, clicking appointment accordion button to expand')
            time.sleep(rand.uniform(1, 2))  # Human thinking time
            button_el = button_elements[0]
            
            # Scroll into view with human-like behavior
            _, _ = button_el.location_once_scrolled_into_view
            time.sleep(rand.uniform(0.5, 1.0))
            
            # Use JavaScript click as it's more reliable for accordion buttons
            logging.debug('Clicking accordion button via JavaScript')
            self.config.browser.execute_script("arguments[0].click();", button_el)
            time.sleep(rand.uniform(2, 3))  # Wait for animation with human-like delay
            logging.info('Panel expanded successfully')
        except Exception as e:
            logging.debug(f'Error expanding panel (likely already expanded): {e}')
            # Panel is probably already expanded, continue anyway

    def expand_locations(self):
        logging.info('expand list of locations')
        time.sleep(rand.uniform(0.5, 1.0))  # Faster dropdown
        
        x_show_location_button = '//mat-select[@name="location"]'
        self.waiter.until(EC.visibility_of_element_located((By.XPATH, x_show_location_button)))
        location_dropdown = self.config.browser.find_element(by=By.XPATH, value=x_show_location_button)
        self.human.human_click(location_dropdown)

    def get_locations(self):
        logging.info('get a list of locations')
        x_location_elements = '//mat-option/span[@class="mat-option-text"]'
        self.waiter.until(EC.visibility_of_element_located((By.XPATH, x_location_elements)))
        location_elements = self.config.browser.find_elements(by=By.XPATH, value=x_location_elements)
        location = list(map(lambda el: el.text, location_elements))
        location = list(filter(lambda s: s.strip() != '-', location))
        return location

    def select_location(self, location_name):
        logging.info(f'location selection ({location_name})')
        # ВАЖНО: Не добавляем задержку здесь - dropdown уже открыт и может закрыться!
        
        x_location_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        
        try:
            # Ждем что элемент видим и кликабелен (dropdown должен быть открыт)
            location_option = WebDriverWait(self.config.browser, 3).until(
                EC.element_to_be_clickable((By.XPATH, x_location_selector(location_name)))
            )
            self.human.human_click(location_option)
            self.wait_spinner()
        except Exception as e:
            logging.error(f'Failed to select location "{location_name}": {e}')
            # Попытка найти похожие элементы для отладки
            all_options = self.config.browser.find_elements(By.XPATH, '//mat-option/span[@class="mat-option-text"]')
            logging.debug(f'Available location options: {[opt.text for opt in all_options]}')
            raise

    def expand_queues(self):
        logging.info('open list of queues')
        time.sleep(rand.uniform(0.5, 1.0))  # Faster dropdown
        
        x_show_queue_button = '//mat-select[@name="queueName"]'
        self.waiter.until(EC.visibility_of_element_located((By.XPATH, x_show_queue_button)))
        queue_dropdown = self.config.browser.find_element(by=By.XPATH, value=x_show_queue_button)
        self.human.human_click(queue_dropdown)
        self.wait_spinner()

    def get_queues(self):
        logging.info('get list of queues')
        x_queue_elements = '//mat-option/span[@class="mat-option-text"]'
        self.waiter.until(EC.visibility_of_element_located((By.XPATH, x_queue_elements)))
        queue_elements = self.config.browser.find_elements(by=By.XPATH, value=x_queue_elements)
        queues = list(map(lambda el: el.text, queue_elements))
        queues = list(filter(lambda s: s.strip() != '-', queues))
        return queues

    def select_queue(self, queue_name):
        logging.info(f'queue selection ({queue_name})')
        # ВАЖНО: Не добавляем задержку здесь - dropdown уже открыт и может закрыться!
        
        # Ищем элемент очереди в открытом dropdown
        x_queue_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        
        try:
            # Ждем что элемент видим (dropdown должен быть открыт)
            queue_option = WebDriverWait(self.config.browser, 3).until(
                EC.element_to_be_clickable((By.XPATH, x_queue_selector(queue_name)))
            )
            self.human.human_click(queue_option)
            self.wait_spinner()
        except Exception as e:
            logging.error(f'Failed to select queue "{queue_name}": {e}')
            # Попытка найти похожие элементы для отладки
            all_options = self.config.browser.find_elements(By.XPATH, '//mat-option/span[@class="mat-option-text"]')
            logging.debug(f'Available options: {[opt.text for opt in all_options]}')
            raise
    
    def select_first_queue_atomic(self):
        """
        Атомарная операция: открыть dropdown очередей и выбрать первую очередь.
        Минимизирует время между открытием dropdown и кликом.
        """
        logging.info('open list of queues (atomic operation)')
        time.sleep(rand.uniform(0.3, 0.8))  # Quick but human-like
        
        x_show_queue_button = '//mat-select[@name="queueName"]'
        x_queue_elements = '//mat-option/span[@class="mat-option-text"]'
        
        # Открываем dropdown
        self.waiter.until(EC.visibility_of_element_located((By.XPATH, x_show_queue_button)))
        queue_dropdown = self.config.browser.find_element(by=By.XPATH, value=x_show_queue_button)
        self.human.human_click(queue_dropdown)
        
        # СРАЗУ получаем список и кликаем по первой очереди
        try:
            # Ждем появления опций
            self.waiter.until(EC.visibility_of_element_located((By.XPATH, x_queue_elements)))
            
            # Получаем все опции
            queue_elements = self.config.browser.find_elements(by=By.XPATH, value=x_queue_elements)
            queues = [el.text for el in queue_elements if el.text.strip() != '-']
            
            if len(queues) == 0:
                logging.warning('No queues found in dropdown')
                return None
            
            # Берем первую очередь
            queue_name = queues[0]
            logging.info(f'Found queue: {queue_name}')
            
            # СРАЗУ кликаем по ней (dropdown еще открыт!)
            x_queue_selector = f'//mat-option/span[@class="mat-option-text" and contains(text(),"{queue_name}")]'
            
            # Находим элемент среди уже полученных (чтобы не искать заново)
            for el in queue_elements:
                if el.text == queue_name:
                    logging.info(f'queue selection ({queue_name})')
                    self.human.human_click(el)
                    self.wait_spinner()
                    
                    # Check for captcha after queue selection
                    self.detect_captcha()
                    
                    return queue_name
            
            # Если не нашли среди старых элементов, пробуем найти заново
            queue_option = self.config.browser.find_element(by=By.XPATH, value=x_queue_selector)
            logging.info(f'queue selection ({queue_name})')
            self.human.human_click(queue_option)
            self.wait_spinner()
            
            # Check for captcha after queue selection
            self.detect_captcha()
            
            return queue_name
            
        except Exception as e:
            logging.error(f'Failed in atomic queue selection: {e}')
            # Debug info
            try:
                all_options = self.config.browser.find_elements(By.XPATH, x_queue_elements)
                logging.debug(f'Available options: {[opt.text for opt in all_options]}')
            except:
                pass
            raise

    def day_checker_full(self, location, queue, months_to_check=3):
        # Updated Material Design calendar selectors
        x_calendar = '//mat-calendar[contains(@class,"reservation-calander")]'
        x_enabled_cells = '//mat-calendar[contains(@class,"reservation-calander")]/div/mat-month-view/table/tbody/tr/td[@role="gridcell" and not(contains(@class,"disabled"))]//div[contains(@class,"mat-calendar-body-cell-content")]'
        x_month_year = '//button[contains(@class,"mat-calendar-period-button")]/span'
        x_next_month = '//button[contains(@class,"mat-calendar-next-button")]'
        x_prev_month = '//button[contains(@class,"mat-calendar-previous-button")]'
        # Time slots container - updated selector from selectors.md
        x_reservations_hours = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]'
        x_time_slots = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]//*[contains(@class,"tile")]'

        # Wait for calendar to appear after queue selection
        logging.info('waiting for calendar to load...')
        time.sleep(rand.uniform(2, 4))
        
        try:
            WebDriverWait(self.config.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, x_calendar))
            )
            logging.info('Calendar loaded successfully')
        except Exception as e:
            logging.warning(f'Calendar did not load for "{location}" - "{queue}" - skipping this combination')
            return  # Skip this location/queue combo

        day_counter = 0
        month_counter = months_to_check
        empty_months_in_row = 0  # Track consecutive empty months
        
        while True:
            # Check for captcha before each month
            self.detect_captcha()
            
            try:
                month_year_text = self.config.browser.find_element(by=By.XPATH, value=x_month_year).text
                enabled_cells = self.config.browser.find_elements(by=By.XPATH, value=x_enabled_cells)
                logging.info(f'{len(enabled_cells)} enabled cells in {month_year_text}')
            except Exception as e:
                logging.error(f'Error accessing calendar: {e}')
                break  # Exit if calendar not accessible

            # If no dates available in this month
            if len(enabled_cells) == 0:
                empty_months_in_row += 1
                logging.warning(f'No available dates in {month_year_text} (empty month {empty_months_in_row}/2)')
                
                # If 2 months in a row are empty, no point checking further
                if empty_months_in_row >= 2:
                    logging.warning(f'2 consecutive empty months - stopping check for this location/queue')
                    return
                
                # Try next month
                month_counter -= 1
                if month_counter == 0:
                    return
                
                logging.info('go to next month')
                time.sleep(rand.uniform(0.5, 1.0))  # Quick skip to next month
                next_month_btn = self.config.browser.find_element(by=By.XPATH, value=x_next_month)
                self.human.human_click(next_month_btn)
                self.wait_spinner()
                continue
            
            # Reset counter if we found dates
            empty_months_in_row = 0

            for enabled_cell in enabled_cells:
                date_text = enabled_cell.text
                logging.info(f'check {date_text} {month_year_text}')
                time.sleep(rand.uniform(0.5, 1.5))  # Faster but still human-like
                self.human.human_click(enabled_cell)
                day_counter += 1
                self.wait_spinner()

                # Check if time slots container appears (improved detection)
                slots_container = self.config.browser.find_elements(by=By.XPATH, value=x_reservations_hours)
                if len(slots_container) != 0:
                    # Double-check for actual time slot elements
                    time_slots = self.config.browser.find_elements(by=By.XPATH, value=x_time_slots)
                    if len(time_slots) > 0:
                        msg = f'🎯 SLOT FOUND! {date_text} {month_year_text}: {location} - {queue} ({len(time_slots)} slots available)'
                        logging.info(msg)
                        self.config.messenger.send_message(msg)
                    else:
                        logging.debug(f'Container found but no time slots for {date_text}')
                
                # Check for captcha every 10 dates (early detection)
                if day_counter % 10 == 0:
                    self.detect_captcha()

            month_counter -= 1
            if month_counter == 0:
                return

            logging.info('go to next month')
            time.sleep(rand.uniform(0.5, 1.0))  # Faster month switching
            next_month_btn = self.config.browser.find_element(by=By.XPATH, value=x_next_month)
            self.human.human_click(next_month_btn)
            self.wait_spinner()

    def check_one_location(self, location_number):
        self.config.browser.get(self.case_page_url(self.config.case_id))
        time.sleep(rand.uniform(1, 2))  # Faster page load
        
        # Check for captcha
        self.detect_captcha()

        logging.info('check if appointment panel needs expanding')
        # Language-independent selectors
        x_location_dropdown = '//mat-select[@name="location"]'
        # Multi-language XPath for appointment section button (same as expand_appointment_panel)
        x_accordion_button = '//h3[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "appointment") or contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "wizyt") or contains(translate(text(), "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"), "зустріч") or contains(translate(text(), "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"), "встречу")]/following::button[contains(@class, "btn--accordion")][1]'
        
        # Wait for page to load with human-like delay
        time.sleep(rand.uniform(1, 2))
        
        # Check if accordion is already expanded
        dropdown_elements = self.config.browser.find_elements(by=By.XPATH, value=x_location_dropdown)
        if len(dropdown_elements) > 0 and dropdown_elements[0].is_displayed():
            logging.info('Panel already expanded (location dropdown visible)')
        else:
            # Panel collapsed, click to expand with multi-language selector
            button_elements = self.config.browser.find_elements(by=By.XPATH, value=x_accordion_button)
            if len(button_elements) > 0:
                logging.info('Panel collapsed, clicking appointment accordion button to expand')
                time.sleep(rand.uniform(1, 2))
                button_el = button_elements[0]
                _, _ = button_el.location_once_scrolled_into_view
                time.sleep(rand.uniform(0.5, 1.0))
                self.config.browser.execute_script("arguments[0].click();", button_el)
                time.sleep(rand.uniform(2, 3))  # Wait for animation
            else:
                logging.warning('Appointment accordion button not found with multi-language selector')

        logging.info('expand list of locations')
        time.sleep(rand.uniform(0.5, 1.0))  # Faster dropdown
        
        x_show_location_button = '//mat-select[@name="location"]'
        WebDriverWait(self.config.browser, self.config.page_load_timeout).until(
            EC.visibility_of_element_located((By.XPATH, x_show_location_button)))
        location_dropdown = self.config.browser.find_element(by=By.XPATH, value=x_show_location_button)
        self.human.human_click(location_dropdown)

        logging.info('get a list of locations')
        x_location_elements = '//mat-option/span[@class="mat-option-text"]'
        WebDriverWait(self.config.browser, self.config.page_load_timeout).until(
            EC.visibility_of_element_located((By.XPATH, x_location_elements)))
        location_elements = self.config.browser.find_elements(by=By.XPATH, value=x_location_elements)
        location = list(map(lambda el: el.text, location_elements))
        location = list(filter(lambda s: s.strip() != '-', location))

        if len(location) != self.config.count_of_locations:
            msg = f'wrong list of locations {location}'
            logging.warning(msg)
            self.config.messenger.send_message(msg)
            if location_number > len(location) - 1:
                return  # TODO: исчезнование одного из location не повод падать
        location_name = location[location_number]

        logging.info(f'location selection ({location_name})')
        time.sleep(rand.uniform(0.5, 1.0))  # Faster selection
        
        x_location_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        location_option = self.config.browser.find_element(by=By.XPATH, value=x_location_selector(location_name))
        self.human.human_click(location_option)
        self.wait_spinner()

        # TODO: Find better way to wait list of queues

        logging.info('open list of queues')
        time.sleep(rand.uniform(0.5, 1.0))  # Faster dropdown
        
        x_show_queue_button = '//mat-select[@name="queueName"]'
        WebDriverWait(self.config.browser, self.config.page_load_timeout).until(
            EC.visibility_of_element_located((By.XPATH, x_show_queue_button)))
        queue_dropdown = self.config.browser.find_element(by=By.XPATH, value=x_show_queue_button)
        self.human.human_click(queue_dropdown)
        self.wait_spinner()

        logging.info('get list of queues')
        x_queue_elements = '//mat-option/span[@class="mat-option-text"]'
        WebDriverWait(self.config.browser, self.config.page_load_timeout).until(
            EC.visibility_of_element_located((By.XPATH, x_queue_elements)))
        queue_elements = self.config.browser.find_elements(by=By.XPATH, value=x_queue_elements)
        queues = list(map(lambda el: el.text, queue_elements))
        queues = list(filter(lambda s: s.strip() != '-', queues))

        if len(queues) != 1:
            msg = f'wrong list of queues {queues} for location "{location_name}"'
            logging.warning(msg)
            self.config.messenger.send_message(msg)
            if len(queues) == 0:
                return  # TODO: выходим если ни одной очереди нет
        queue_number = 0
        queue_name = queues[queue_number]

        logging.info(f'queue selection ({queue_name})')
        time.sleep(rand.uniform(0.5, 1.0))  # Faster selection
        
        x_queue_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        queue_option = self.config.browser.find_element(by=By.XPATH, value=x_queue_selector(queue_name))
        self.human.human_click(queue_option)
        self.wait_spinner()

        # Wait for calendar to load (up to 5 seconds)
        logging.info('waiting for calendar to load...')
        time.sleep(rand.uniform(2, 4))
        
        # Updated Material Design calendar selectors
        x_calendar = '//mat-calendar[contains(@class,"reservation-calander")]'
        x_enabled_cells = '//mat-calendar[contains(@class,"reservation-calander")]/div/mat-month-view/table/tbody/tr/td[@role="gridcell" and not(contains(@class,"disabled"))]//div[contains(@class,"mat-calendar-body-cell-content")]'
        x_month_year = '//button[contains(@class,"mat-calendar-period-button")]/span'
        x_next_month = '//button[contains(@class,"mat-calendar-next-button")]'
        x_prev_month = '//button[contains(@class,"mat-calendar-previous-button")]'
        # Time slots container - updated selector from selectors.md
        x_reservations_hours = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]'
        x_time_slots = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]//*[contains(@class,"tile")]'

        # Check if calendar loaded
        try:
            WebDriverWait(self.config.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, x_calendar))
            )
            logging.info('Calendar loaded successfully')
        except Exception as e:
            logging.warning(f'Calendar did not load for location "{location_name}" queue "{queue_name}" - skipping')
            return  # Skip to next location

        day_counter = 0
        month_counter = 0
        while True:
            # Check for captcha before each month
            self.detect_captcha()
            
            try:
                month_year_text = self.config.browser.find_element(by=By.XPATH, value=x_month_year).text
                enabled_cells = self.config.browser.find_elements(by=By.XPATH, value=x_enabled_cells)
                logging.info(f'{len(enabled_cells)} enabled cells in {month_year_text}')
            except Exception as e:
                logging.error(f'Error getting calendar data: {e}')
                break  # Exit calendar check loop

            for enabled_cell in enabled_cells:
                date_text = enabled_cell.text
                logging.info(f'check {date_text} {month_year_text}')
                time.sleep(rand.uniform(0.5, 1.5))  # Faster but still human-like
                self.human.human_click(enabled_cell)
                day_counter += 1
                self.wait_spinner()
                
                # Check if time slots container appears (improved detection)
                slots_container = self.config.browser.find_elements(by=By.XPATH, value=x_reservations_hours)
                if len(slots_container) != 0:
                    # Double-check for actual time slot elements
                    time_slots = self.config.browser.find_elements(by=By.XPATH, value=x_time_slots)
                    if len(time_slots) > 0:
                        msg = f'🎯 SLOT FOUND! {date_text} {month_year_text} {location_name} ({len(time_slots)} slots available)'
                        logging.info(msg)
                        self.config.messenger.send_message(msg)
                    else:
                        logging.debug(f'Container found but no time slots for {date_text}')
                
                # Check for captcha every 10 dates (early detection)
                if day_counter % 10 == 0:
                    self.detect_captcha()

            if month_counter >= 4:
                break

            logging.info('go to next month')
            time.sleep(rand.uniform(0.5, 1.0))  # Faster month switching
            month_counter += 1
            next_month_button = self.config.browser.find_element(by=By.XPATH, value=x_next_month)
            self.human.human_click(next_month_button)
            self.wait_spinner()

        logging.info('end')
