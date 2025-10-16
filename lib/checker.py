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
            # Check for Akamai iframe
            captcha_iframes = self.config.browser.find_elements(By.CSS_SELECTOR, "iframe[src*='akamai']")
            if captcha_iframes:
                msg = '⚠️ AKAMAI CAPTCHA DETECTED! Please solve manually in VNC within 2 minutes'
                logging.warning(msg)
                self.config.messenger.send_message(msg)
                time.sleep(120)  # Wait 2 minutes for manual solving
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

    # Updated selector from selectors.md
    x_appointment_button = '//button[.//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]]'

    def open_case_page(self):
        self.config.browser.get(self.case_page_url(self.config.case_id))
        time.sleep(rand.uniform(2, 5))  # Increased delay 2-5 seconds
        
        # Check for captcha
        self.detect_captcha()
        
        if len(self.config.browser.find_elements(by=By.XPATH, value=self.x_appointment_button)) == 0:
            logging.error('Appointment button not found')
            return False
        self.waiter.until(EC.visibility_of_element_located((By.XPATH, self.x_appointment_button)))
        return True

    def expand_appointment_panel(self):
        logging.info('expand appointment panel')
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
        x_appointment_block = '//button[.//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]]/following-sibling::div[contains(@class,"accordion__more")]'
        try:
            appointment_block = self.config.browser.find_element(by=By.XPATH, value=x_appointment_block)
            if not appointment_block.is_displayed():
                time.sleep(rand.uniform(1, 3))
                x_appointment_button_el = self.config.browser.find_element(by=By.XPATH, value=self.x_appointment_button)
                _, _ = x_appointment_button_el.location_once_scrolled_into_view
                self.human.human_click(x_appointment_button_el)
        except Exception as e:
            logging.warning(f'Error expanding appointment panel: {e}')

    def expand_locations(self):
        logging.info('expand list of locations')
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
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
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
        x_location_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        location_option = self.config.browser.find_element(by=By.XPATH, value=x_location_selector(location_name))
        self.human.human_click(location_option)
        self.wait_spinner()

    def expand_queues(self):
        logging.info('open list of queues')
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
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
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
        x_queue_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        queue_option = self.config.browser.find_element(by=By.XPATH, value=x_queue_selector(queue_name))
        self.human.human_click(queue_option)
        self.wait_spinner()

    def day_checker_full(self, location, queue, months_to_check=3):
        x_enabled_cells = '//mat-calendar[contains(@class,"reservation-calander")]/div/mat-month-view/table/tbody/tr/td[@role="gridcell" and not(contains(@class,"disabled"))]'
        x_month_year = '//button[contains(@class,"mat-calendar-period-button")]/span/span'
        x_next_month = '//button[contains(@class,"mat-calendar-next-button")]'
        x_reservations_hours = '//div[@class="reservation__hours"]/div/div[@class="row"]/*'

        day_counter = 0
        month_counter = months_to_check
        while True:
            month_year_text = self.config.browser.find_element(by=By.XPATH, value=x_month_year).text
            enabled_cells = self.config.browser.find_elements(by=By.XPATH, value=x_enabled_cells)
            logging.info(f'{len(enabled_cells)} enabled cells in {month_year_text}')

            for enabled_cell in enabled_cells:
                date_text = enabled_cell.text
                logging.info(f'check {date_text} {month_year_text}')
                time.sleep(rand.uniform(2, 5))  # Increased delay
                self.human.human_click(enabled_cell)
                day_counter += 1
                self.wait_spinner()

                # TODO: Found better test
                if len(self.config.browser.find_elements(by=By.XPATH, value=x_reservations_hours)) != 0:
                    msg = f'slot found {date_text} {month_year_text}: {location} - {queue}'
                    logging.info(msg)
                    self.config.messenger.send_message(msg)

            month_counter -= 1
            if month_counter == 0:
                return

            logging.info('go to next month')
            time.sleep(rand.uniform(2, 5))  # Increased delay
            next_month_btn = self.config.browser.find_element(by=By.XPATH, value=x_next_month)
            self.human.human_click(next_month_btn)
            self.wait_spinner()

    def check_one_location(self, location_number):
        self.config.browser.get(self.case_page_url(self.config.case_id))
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
        # Check for captcha
        self.detect_captcha()

        logging.info('expand appointment panel')
        x_appointment_button = '//button[.//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]]'
        WebDriverWait(self.config.browser, self.config.page_load_timeout).until(
            EC.visibility_of_element_located((By.XPATH, x_appointment_button)))
        x_appointment_block = '//button[.//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]]/following-sibling::div[contains(@class,"accordion__more")]'
        appointment_block = self.config.browser.find_element(by=By.XPATH, value=x_appointment_block)
        if not appointment_block.is_displayed():
            time.sleep(rand.uniform(1, 3))
            button_el = self.config.browser.find_element(by=By.XPATH, value=x_appointment_button)
            self.human.human_click(button_el)
        _, _ = self.config.browser.find_element(
            by=By.XPATH,
            value=x_appointment_button).location_once_scrolled_into_view

        logging.info('expand list of locations')
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
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
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
        x_location_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        location_option = self.config.browser.find_element(by=By.XPATH, value=x_location_selector(location_name))
        self.human.human_click(location_option)
        self.wait_spinner()

        # TODO: Find better way to wait list of queues

        logging.info('open list of queues')
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
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
        time.sleep(rand.uniform(2, 5))  # Increased delay
        
        x_queue_selector = lambda text: f'//mat-option/span[@class="mat-option-text" and contains(text(),"{text}")]'
        queue_option = self.config.browser.find_element(by=By.XPATH, value=x_queue_selector(queue_name))
        self.human.human_click(queue_option)
        self.wait_spinner()

        x_calendar = '//mat-calendar[contains(@class,"reservation-calander")]'
        x_enabled_cells = '//mat-calendar[contains(@class,"reservation-calander")]/div/mat-month-view/table/tbody/tr/td[@role="gridcell" and not(contains(@class,"disabled"))]'
        x_month_year = '//button[contains(@class,"mat-calendar-period-button")]/span/span'
        x_next_month = '//button[contains(@class,"mat-calendar-next-button")]'
        x_reservations_hours = '//div[@class="reservation__hours"]/div/div[@class="row"]/*'

        day_counter = 0
        month_counter = 0
        while True:
            month_year_text = self.config.browser.find_element(by=By.XPATH, value=x_month_year).text
            enabled_cells = self.config.browser.find_elements(by=By.XPATH, value=x_enabled_cells)
            logging.info(f'{len(enabled_cells)} enabled cells in {month_year_text}')

            for enabled_cell in enabled_cells:
                date_text = enabled_cell.text
                logging.info(f'check {date_text} {month_year_text}')
                time.sleep(rand.uniform(2, 5))  # Increased delay
                self.human.human_click(enabled_cell)
                day_counter += 1
                self.wait_spinner()
                # TODO: Found better marker
                if len(self.config.browser.find_elements(by=By.XPATH, value=x_reservations_hours)) != 0:
                    msg = f'slot found {date_text} {month_year_text} {location_name}'
                    logging.info(msg)
                    self.config.messenger.send_message(msg)

            if month_counter >= 4:
                break

            logging.info('go to next month')
            time.sleep(rand.uniform(2, 5))  # Increased delay
            month_counter += 1
            next_month_button = self.config.browser.find_element(by=By.XPATH, value=x_next_month)
            self.human.human_click(next_month_button)
            self.wait_spinner()

        logging.info('end')
