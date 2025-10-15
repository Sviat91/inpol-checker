"""
Human-like behavior simulation to bypass Akamai bot detection.
Adds random delays, mouse movements, and natural interaction patterns.
"""

import random
import time
from typing import Optional

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class HumanBehavior:
    """Simulates human-like behavior in browser automation."""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.actions = ActionChains(driver)
    
    def random_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Add random delay to simulate human thinking time."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def slow_type(self, element: WebElement, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
        """Type text slowly with random delays between keystrokes."""
        element.click()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))
    
    def human_click(self, element: WebElement):
        """Click element with random delay before and after."""
        # Random delay before click (thinking time)
        self.random_delay(0.3, 0.8)
        
        # Move mouse to element with random offset
        self._move_to_element_with_offset(element)
        
        # Small delay before actual click
        time.sleep(random.uniform(0.1, 0.3))
        
        # Click
        element.click()
        
        # Small delay after click
        time.sleep(random.uniform(0.2, 0.5))
    
    def _move_to_element_with_offset(self, element: WebElement):
        """Move mouse to element with slight random offset (more human-like)."""
        # Get element size
        size = element.size
        width = size.get('width', 0)
        height = size.get('height', 0)
        
        # Calculate random offset within element bounds
        # Avoid exact center - humans don't click perfectly centered
        x_offset = random.randint(-int(width * 0.3), int(width * 0.3))
        y_offset = random.randint(-int(height * 0.3), int(height * 0.3))
        
        # Move to element with offset
        actions = ActionChains(self.driver)
        actions.move_to_element_with_offset(element, x_offset, y_offset)
        actions.perform()
    
    def random_mouse_movement(self):
        """Perform random mouse movements to simulate human behavior."""
        try:
            # Get window size
            window_size = self.driver.get_window_size()
            width = window_size['width']
            height = window_size['height']
            
            # Random number of movements (1-3)
            movements = random.randint(1, 3)
            
            for _ in range(movements):
                # Random coordinates within window
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                
                # Move in small steps to make it more natural
                actions = ActionChains(self.driver)
                actions.move_by_offset(x // 2, y // 2)
                actions.pause(random.uniform(0.1, 0.3))
                actions.move_by_offset(x // 2, y // 2)
                actions.perform()
                
                time.sleep(random.uniform(0.2, 0.5))
        except Exception:
            # If mouse movement fails, just continue
            pass
    
    def scroll_slowly(self, scroll_amount: int = 300):
        """Scroll page slowly like a human reading."""
        # Scroll in small increments
        increments = 5
        scroll_per_increment = scroll_amount // increments
        
        for _ in range(increments):
            self.driver.execute_script(f'window.scrollBy(0, {scroll_per_increment});')
            time.sleep(random.uniform(0.1, 0.3))
    
    def hover_element(self, element: WebElement, duration: Optional[float] = None):
        """Hover over element for random or specified duration."""
        if duration is None:
            duration = random.uniform(0.5, 1.5)
        
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
        time.sleep(duration)
    
    def simulate_reading(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Simulate human reading time with random mouse movements."""
        read_time = random.uniform(min_seconds, max_seconds)
        
        # Occasionally move mouse while "reading"
        if random.random() < 0.3:  # 30% chance
            self.random_mouse_movement()
        
        time.sleep(read_time)
