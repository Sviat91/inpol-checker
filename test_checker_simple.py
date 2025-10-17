#!/usr/bin/env python3
"""
Simple test script for inpol-checker without working hours restrictions.
Run with: python test_checker_simple.py
"""

import logging
import os
import sys
import time

from lib.browser_factory import BrowserFactory
from lib.checker import Checker
from lib.checker_config import CheckerConfig
from lib.messenger import ConsoleMessenger, TelegramMessenger


def main():
    # Setup logging
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)
    
    # Check required environment variables
    required_vars = ['EMAIL', 'PASSWORD', 'CASE_ID']
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logging.error("Please set: EMAIL, PASSWORD, CASE_ID")
        sys.exit(1)
    
    # Create browser
    logging.info("Creating browser...")
    browser = BrowserFactory().create(window_size='1300,800')
    
    # Setup messenger
    if 'TELEGRAM_TOKEN' in os.environ and 'TELEGRAM_CHAT_ID' in os.environ:
        logging.info("Using Telegram messenger")
        messenger = TelegramMessenger()
    else:
        logging.info("Using console messenger (no Telegram configured)")
        messenger = ConsoleMessenger()
    
    try:
        # Create config
        config = CheckerConfig(
            email=os.environ['EMAIL'],
            password=os.environ['PASSWORD'],
            case_id=os.environ['CASE_ID'],
            messenger=messenger,
            browser=browser,
        )
        
        inpol = Checker(config)
        
        # Login
        logging.info("Logging in...")
        tries = 0
        while not inpol.login():
            if tries == 4:
                logging.error("Failed to login after 4 attempts")
                return
            tries += 1
            time.sleep(tries * 2)
        
        logging.info("✅ Login successful")
        
        # Open case page
        logging.info("Opening case page...")
        tries = 0
        while not inpol.open_case_page():
            if tries == 4:
                logging.error("Failed to open case page after 4 attempts")
                return
            tries += 1
            time.sleep(tries * 2)
        
        logging.info("✅ Case page opened")
        
        # Expand appointment panel
        logging.info("Expanding appointment panel...")
        inpol.expand_appointment_panel()
        
        # Get locations
        logging.info("Getting locations...")
        inpol.expand_locations()
        locations = inpol.get_locations()
        
        if len(locations) == 0:
            logging.error("No locations found!")
            return
        
        logging.info(f"✅ Found {len(locations)} location(s): {locations}")
        
        # НЕ перемешиваем - проходим адреса по порядку!
        
        # Get months to check
        months_to_check = int(os.environ.get('MONTHS_TO_CHECK', '3'))
        logging.info(f"Will check {months_to_check} months ahead")
        
        # Check each location with its queue
        for location in locations:
            logging.info(f"\n{'='*60}")
            logging.info(f"Checking location: {location}")
            logging.info(f"{'='*60}")
            
            inpol.select_location(location)
            
            try:
                # Атомарно: открыть dropdown очередей и выбрать первую
                logging.info("Getting and selecting queue (atomic operation)...")
                queue = inpol.select_first_queue_atomic()
                
                if queue is None:
                    msg = f'⚠️ No queues available for location "{location}" - skipping'
                    logging.warning(msg)
                    messenger.send_message(msg)
                    inpol.expand_locations()
                    continue
                
                logging.info(f"✅ Selected queue: {queue}")
                
                # Check calendar for this location/queue combo
                inpol.day_checker_full(
                    location=location, 
                    queue=queue, 
                    months_to_check=months_to_check
                )
                
                logging.info(f"✅ Finished checking {location} - {queue}")
                
            except Exception as e:
                logging.error(f"❌ Error checking location '{location}': {e}")
                logging.debug(f"Exception details:", exc_info=True)
            
            # Prepare for next location
            logging.info("Preparing for next location...")
            inpol.expand_locations()
        
        logging.info(f"\n{'='*60}")
        logging.info("✅ All locations and queues checked!")
        logging.info(f"{'='*60}")
        
    except KeyboardInterrupt:
        logging.info("\n⚠️ Interrupted by user")
    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        logging.debug("Exception details:", exc_info=True)
    finally:
        logging.info("Closing browser...")
        browser.quit()
        logging.info("Done!")


if __name__ == '__main__':
    main()
