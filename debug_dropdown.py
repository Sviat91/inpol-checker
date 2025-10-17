#!/usr/bin/env python3
"""
Debug script to test dropdown selection
"""

import logging
import os
import sys
import time

from lib.browser_factory import BrowserFactory
from lib.checker import Checker
from lib.checker_config import CheckerConfig
from lib.messenger import ConsoleMessenger

# Setup DEBUG logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)

# Check env vars
required = ['EMAIL', 'PASSWORD', 'CASE_ID']
missing = [v for v in required if v not in os.environ]
if missing:
    print(f"Missing: {', '.join(missing)}")
    sys.exit(1)

browser = BrowserFactory().create(window_size='1300,800')

try:
    config = CheckerConfig(
        email=os.environ['EMAIL'],
        password=os.environ['PASSWORD'],
        case_id=os.environ['CASE_ID'],
        messenger=ConsoleMessenger(),
        browser=browser,
    )
    
    inpol = Checker(config)
    
    # Login
    print("\n" + "="*60)
    print("LOGGING IN...")
    print("="*60)
    if not inpol.login():
        print("Login failed!")
        sys.exit(1)
    print("✅ Login OK")
    
    # Open case
    print("\n" + "="*60)
    print("OPENING CASE...")
    print("="*60)
    if not inpol.open_case_page():
        print("Failed to open case!")
        sys.exit(1)
    print("✅ Case page OK")
    
    # Expand panel
    print("\n" + "="*60)
    print("EXPANDING APPOINTMENT PANEL...")
    print("="*60)
    inpol.expand_appointment_panel()
    print("✅ Panel expanded")
    
    # Get locations
    print("\n" + "="*60)
    print("GETTING LOCATIONS...")
    print("="*60)
    inpol.expand_locations()
    locations = inpol.get_locations()
    print(f"✅ Found {len(locations)} locations:")
    for i, loc in enumerate(locations, 1):
        print(f"  {i}. {loc}")
    
    # Test FIRST location
    location = locations[0]
    print("\n" + "="*60)
    print(f"TESTING FIRST LOCATION: {location}")
    print("="*60)
    
    print(f"\n→ Selecting location: {location}")
    inpol.select_location(location)
    print("✅ Location selected")
    
    print("\n→ Selecting queue (atomic operation)...")
    
    try:
        queue = inpol.select_first_queue_atomic()
        
        if queue is None:
            print("\n❌ NO QUEUES FOUND!")
            sys.exit(1)
        
        print(f"✅ Queue selected successfully: {queue}")
        
        # Wait a bit
        time.sleep(3)
        
        print("\n→ Checking if calendar loaded...")
        from selenium.webdriver.common.by import By
        calendar = browser.find_elements(By.XPATH, '//mat-calendar[contains(@class,"reservation-calander")]')
        
        if calendar:
            print(f"✅ CALENDAR FOUND! ({len(calendar)} element(s))")
        else:
            print("⚠️ Calendar not found - this location/queue may not have slots")
        
    except Exception as e:
        print(f"\n❌ FAILED TO SELECT QUEUE!")
        print(f"Error: {e}")
        
        # Debug info
        print("\n--- DEBUG INFO ---")
        from selenium.webdriver.common.by import By
        all_options = browser.find_elements(By.XPATH, '//mat-option/span[@class="mat-option-text"]')
        print(f"Currently visible options: {len(all_options)}")
        for opt in all_options:
            try:
                print(f"  - '{opt.text}' (visible: {opt.is_displayed()})")
            except:
                print(f"  - (stale element)")
        
        raise
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\nPress Enter to close browser...")
    input()

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nPress Enter to close browser...")
    input()

finally:
    browser.quit()
