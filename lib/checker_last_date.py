# New method to check ONLY the last available date
# This will be inserted into checker.py

def check_last_date_only(self, location, queue):
    """
    Check ONLY the last available date in calendar.
    Skip weekends (Sat/Sun).
    If dates extend to end of month, check next month too.
    """
    import calendar as cal
    from datetime import datetime
    
    # Calendar selectors
    x_calendar = '//mat-calendar[contains(@class,"reservation-calander")]'
    x_enabled_cells = '//mat-calendar[contains(@class,"reservation-calander")]/div/mat-month-view/table/tbody/tr/td[@role="gridcell" and not(contains(@class,"disabled"))]//div[contains(@class,"mat-calendar-body-cell-content")]'
    x_month_year = '//button[contains(@class,"mat-calendar-period-button")]/span'
    x_next_month = '//button[contains(@class,"mat-calendar-next-button")]'
    x_prev_month = '//button[contains(@class,"mat-calendar-previous-button")]'
    x_reservations_hours = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]'
    x_time_slots = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]//*[contains(@class,"tile")]'

    # Wait for calendar
    logging.info('waiting for calendar to load...')
    time.sleep(rand.uniform(0.5, 1.0))
    
    try:
        WebDriverWait(self.config.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, x_calendar))
        )
        logging.info('Calendar loaded successfully')
    except Exception as e:
        logging.warning(f'Calendar did not load for "{location}" - "{queue}" - skipping')
        return None
    
    def is_weekend(date_text, month_year_text):
        """Check if date is Saturday or Sunday"""
        try:
            # Parse month/year (e.g., "PAŹ 2025" -> October 2025)
            months_pl = {
                'STY': 1, 'LUT': 2, 'MAR': 3, 'KWI': 4, 'MAJ': 5, 'CZE': 6,
                'LIP': 7, 'SIE': 8, 'WRZ': 9, 'PAŹ': 10, 'LIS': 11, 'GRU': 12
            }
            
            parts = month_year_text.split()
            if len(parts) >= 2:
                month_str = parts[0]
                year = int(parts[1])
                month = months_pl.get(month_str, 1)
                day = int(date_text)
                
                # Get weekday (0=Mon, 6=Sun)
                weekday = datetime(year, month, day).weekday()
                
                # Saturday=5, Sunday=6
                return weekday >= 5
        except Exception as e:
            logging.debug(f'Error checking weekend: {e}')
            return False
        
        return False
    
    def is_end_of_month(date_text, month_year_text):
        """Check if date is close to end of month (last 5 days)"""
        try:
            parts = month_year_text.split()
            if len(parts) >= 2:
                months_pl = {
                    'STY': 1, 'LUT': 2, 'MAR': 3, 'KWI': 4, 'MAJ': 5, 'CZE': 6,
                    'LIP': 7, 'SIE': 8, 'WRZ': 9, 'PAŹ': 10, 'LIS': 11, 'GRU': 12
                }
                month_str = parts[0]
                year = int(parts[1])
                month = months_pl.get(month_str, 1)
                day = int(date_text)
                
                # Get last day of month
                last_day = cal.monthrange(year, month)[1]
                
                # If within last 5 days of month
                return (last_day - day) <= 5
        except Exception as e:
            logging.debug(f'Error checking end of month: {e}')
            return False
        
        return False
    
    # Get current month info
    try:
        month_year_text = self.config.browser.find_element(by=By.XPATH, value=x_month_year).text
        enabled_cells = self.config.browser.find_elements(by=By.XPATH, value=x_enabled_cells)
        logging.info(f'{len(enabled_cells)} enabled cells in {month_year_text}')
    except Exception as e:
        logging.error(f'Error accessing calendar: {e}')
        return None
    
    if len(enabled_cells) == 0:
        logging.warning(f'No available dates in {month_year_text}')
        return None
    
    # Filter out weekends
    valid_cells = []
    for cell in enabled_cells:
        date_text = cell.text
        if not is_weekend(date_text, month_year_text):
            valid_cells.append(cell)
        else:
            logging.debug(f'Skipping weekend: {date_text} {month_year_text}')
    
    if len(valid_cells) == 0:
        logging.warning(f'No non-weekend dates in {month_year_text}')
        return None
    
    # Take LAST date (excluding weekends)
    last_cell = valid_cells[-1]
    last_date_text = last_cell.text
    
    logging.info(f'✅ Checking LAST available date: {last_date_text} {month_year_text}')
    time.sleep(rand.uniform(0.15, 0.5))  # Very fast delay
    
    # Click on last date
    self.human.human_click(last_cell)
    self.wait_spinner()
    
    # IMMEDIATELY check for captcha after click!
    captcha_appeared = self.detect_captcha()
    if captcha_appeared:
        logging.info('Captcha was solved, continuing...')
        time.sleep(rand.uniform(1, 2))  # Extra wait after captcha
    
    # Check for time slots
    slots_found = False
    slots_container = self.config.browser.find_elements(by=By.XPATH, value=x_reservations_hours)
    if len(slots_container) != 0:
        time_slots = self.config.browser.find_elements(by=By.XPATH, value=x_time_slots)
        if len(time_slots) > 0:
            msg = f'🎯 SLOT FOUND! {last_date_text} {month_year_text}: {location} - {queue} ({len(time_slots)} slots)'
            logging.info(msg)
            self.config.messenger.send_message(msg)
            slots_found = True
        else:
            logging.debug(f'Container found but no time slots for {last_date_text}')
    
    # Check if we need to look at next month
    # (if last date is close to end of month, check next month too)
    should_check_next_month = is_end_of_month(last_date_text, month_year_text)
    
    if should_check_next_month:
        logging.info(f'Last date {last_date_text} is near end of month, checking next month...')
        time.sleep(rand.uniform(0.15, 0.35))
        
        # Go to next month
        next_month_btn = self.config.browser.find_element(by=By.XPATH, value=x_next_month)
        self.human.human_click(next_month_btn)
        self.wait_spinner()
        
        # Get next month info
        try:
            next_month_year_text = self.config.browser.find_element(by=By.XPATH, value=x_month_year).text
            next_enabled_cells = self.config.browser.find_elements(by=By.XPATH, value=x_enabled_cells)
            logging.info(f'{len(next_enabled_cells)} enabled cells in {next_month_year_text}')
            
            if len(next_enabled_cells) > 0:
                # Filter weekends in next month
                next_valid_cells = []
                for cell in next_enabled_cells:
                    date_text = cell.text
                    if not is_weekend(date_text, next_month_year_text):
                        next_valid_cells.append(cell)
                
                if len(next_valid_cells) > 0:
                    # Check last date in next month
                    next_last_cell = next_valid_cells[-1]
                    next_last_date_text = next_last_cell.text
                    
                    logging.info(f'✅ Checking LAST date in next month: {next_last_date_text} {next_month_year_text}')
                    time.sleep(rand.uniform(0.15, 0.5))
                    
                    self.human.human_click(next_last_cell)
                    self.wait_spinner()
                    
                    # Check captcha
                    captcha_appeared = self.detect_captcha()
                    if captcha_appeared:
                        logging.info('Captcha was solved, continuing...')
                        time.sleep(rand.uniform(1, 2))
                    
                    # Check slots
                    slots_container = self.config.browser.find_elements(by=By.XPATH, value=x_reservations_hours)
                    if len(slots_container) != 0:
                        time_slots = self.config.browser.find_elements(by=By.XPATH, value=x_time_slots)
                        if len(time_slots) > 0:
                            msg = f'🎯 SLOT FOUND! {next_last_date_text} {next_month_year_text}: {location} - {queue} ({len(time_slots)} slots)'
                            logging.info(msg)
                            self.config.messenger.send_message(msg)
                            slots_found = True
                else:
                    logging.info(f'Next month has no non-weekend dates')
                
                # Go back to previous month
                logging.info('Returning to previous month...')
                time.sleep(rand.uniform(0.15, 0.35))
                prev_month_btn = self.config.browser.find_element(by=By.XPATH, value=x_prev_month)
                self.human.human_click(prev_month_btn)
                self.wait_spinner()
            else:
                logging.info(f'Next month ({next_month_year_text}) has no dates, staying in current month')
        except Exception as e:
            logging.error(f'Error checking next month: {e}')
    
    return slots_found
