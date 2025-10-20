# План улучшения обработки Akamai Bot Manager

## 🎯 Цель
Минимизировать появление Akamai Behavioral Challenge и надежно обрабатывать его когда он появляется.

## 📋 Текущая ситуация

### Что есть сейчас:
- ✅ Базовая детекция капчи в `detect_captcha()`
- ✅ Проверка `#proceed-button`
- ✅ Telegram уведомления
- ✅ Пауза 120 секунд
- ✅ HumanBehavior с базовыми задержками

### Проблемы:
- ❌ Обычный Selenium (палится Bot Manager)
- ❌ Недостаточно человекоподобное поведение
- ❌ Нет сохранения cookies между запусками
- ❌ Детекция только по `#proceed-button`
- ❌ Нет проверки после каждого критичного действия
- ❌ Нет multi-language поддержки для текстов

## 🔧 План реализации

### Фаза 1: Undetected ChromeDriver (ПРИОРИТЕТ!)
**Цель:** Перейти с обычного Selenium на undetected-chromedriver

#### 1.1 Обновить requirements.txt
```python
# Добавить:
undetected-chromedriver>=3.5.4
```

#### 1.2 Обновить BrowserFactory (`lib/browser_factory.py`)
```python
import undetected_chromedriver as uc

class BrowserFactory:
    def create(self, window_size='1300,800', headless=False):
        options = uc.ChromeOptions()
        
        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--window-size={window_size}')
        
        # Random User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36...',
            # ... список UA
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        if headless:
            options.add_argument('--headless=new')
        
        # Create undetected driver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Additional anti-detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
        return driver
```

**Время:** 30 минут  
**Приоритет:** 🔴 HIGH

---

### Фаза 2: Cookie Persistence
**Цель:** Сохранять cookies между запусками для реюза сессии

#### 2.1 Создать Cookie Manager (`lib/cookie_manager.py`)
```python
import json
import os
import logging
from pathlib import Path

class CookieManager:
    def __init__(self, cookie_file='/opt/data/cookies.json'):
        self.cookie_file = Path(cookie_file)
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_cookies(self, driver):
        """Save all cookies from current session"""
        cookies = driver.get_cookies()
        
        # Filter important Akamai cookies
        important = ['ak_bmsc', 'bm_sz', '_abck', 'PHPSESSID']
        
        with open(self.cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        logging.info(f'Saved {len(cookies)} cookies to {self.cookie_file}')
        
        # Log Akamai cookies specifically
        for cookie in cookies:
            if cookie['name'] in important:
                logging.debug(f'Akamai cookie: {cookie["name"]}={cookie["value"][:20]}...')
    
    def load_cookies(self, driver):
        """Load cookies into driver"""
        if not self.cookie_file.exists():
            logging.info('No saved cookies found')
            return False
        
        try:
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
            
            # Driver must be on same domain
            driver.get('https://inpol.mazowieckie.pl')
            
            for cookie in cookies:
                try:
                    # Remove 'sameSite' if not compatible
                    if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        del cookie['sameSite']
                    
                    driver.add_cookie(cookie)
                except Exception as e:
                    logging.debug(f'Could not add cookie {cookie.get("name")}: {e}')
            
            logging.info(f'Loaded {len(cookies)} cookies')
            return True
            
        except Exception as e:
            logging.error(f'Error loading cookies: {e}')
            return False
    
    def clear_cookies(self):
        """Clear saved cookies"""
        if self.cookie_file.exists():
            self.cookie_file.unlink()
            logging.info('Cleared saved cookies')
```

#### 2.2 Интегрировать в Checker
```python
# В __init__
self.cookie_manager = CookieManager()

# После login
self.cookie_manager.save_cookies(self.config.browser)

# В начале session (перед login)
if self.cookie_manager.load_cookies(self.config.browser):
    # Try to use existing session
    self.config.browser.get(case_page_url)
    if self.is_logged_in():
        logging.info('Reusing existing session!')
        return True
```

#### 2.3 Обновить docker-compose.yml
```yaml
services:
  inpol-checker:
    volumes:
      - ./data:/opt/data  # Persistent cookies
```

**Время:** 45 минут  
**Приоритет:** 🟡 MEDIUM

---

### Фаза 3: Улучшенное человекоподобное поведение
**Цель:** Сделать действия более естественными

#### 3.1 Обновить HumanBehavior (`lib/human_behavior.py`)
```python
from selenium.webdriver.common.action_chains import ActionChains
import random
import time

class HumanBehavior:
    def __init__(self, browser):
        self.browser = browser
    
    def random_delay(self, min_sec=3, max_sec=8):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        logging.debug(f'Human delay: {delay:.2f}s')
        time.sleep(delay)
    
    def move_to_element(self, element):
        """Move mouse to element with random path"""
        actions = ActionChains(self.browser)
        
        # Get element location
        location = element.location
        size = element.size
        
        # Random offset within element
        offset_x = random.randint(-size['width']//4, size['width']//4)
        offset_y = random.randint(-size['height']//4, size['height']//4)
        
        # Move with pause
        actions.move_to_element_with_offset(element, offset_x, offset_y)
        actions.pause(random.uniform(0.1, 0.3))
        actions.perform()
        
        logging.debug(f'Moved mouse to element at ({location["x"]}, {location["y"]})')
    
    def human_click(self, element):
        """Click with human-like behavior"""
        try:
            # Random pre-click delay
            time.sleep(random.uniform(0.2, 0.5))
            
            # Move to element first
            self.move_to_element(element)
            
            # Small pause before click
            time.sleep(random.uniform(0.1, 0.3))
            
            # Click
            actions = ActionChains(self.browser)
            actions.click(element)
            actions.perform()
            
            # Small post-click delay
            time.sleep(random.uniform(0.1, 0.2))
            
            logging.debug('Human click completed')
            
        except Exception as e:
            logging.warning(f'Human click failed, using fallback: {e}')
            # Fallback to JS click
            self.browser.execute_script("arguments[0].click();", element)
    
    def human_scroll(self, element):
        """Scroll element into view naturally"""
        # Scroll to element
        self.browser.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        time.sleep(random.uniform(0.3, 0.7))
    
    def type_like_human(self, element, text):
        """Type text with human-like delays"""
        element.clear()
        
        for char in text:
            element.send_keys(char)
            # Random typing speed
            time.sleep(random.uniform(0.05, 0.15))
        
        # Pause after typing
        time.sleep(random.uniform(0.2, 0.5))
```

#### 3.2 Обновить все клики в Checker
```python
# Вместо:
element.click()

# Использовать:
self.human.random_delay(3, 8)  # Before critical action
self.human.human_click(element)
```

**Время:** 1 час  
**Приоритет:** 🔴 HIGH

---

### Фаза 4: Улучшенная детекция Akamai Challenge
**Цель:** Надежно обнаруживать челлендж на всех языках

#### 4.1 Создать AkamaiDetector (`lib/akamai_detector.py`)
```python
import logging
from selenium.webdriver.common.by import By

class AkamaiDetector:
    """Detect Akamai Bot Manager Behavioral Challenge"""
    
    # Multi-language challenge texts
    CHALLENGE_TEXTS = {
        'pl': ['Nie jestem robotem', 'Potwierdź', 'jestem człowiekiem'],
        'en': ['I am not a robot', 'Verify', 'I am human'],
        'ru': ['Я не робот', 'Подтвердить', 'Я человек'],
        'ua': ['Я не робот', 'Підтвердити', 'Я людина']
    }
    
    # Akamai-specific cookies
    AKAMAI_COOKIES = ['ak_bmsc', 'bm_sz', '_abck']
    
    # Challenge button IDs/classes
    CHALLENGE_SELECTORS = [
        '#proceed-button',
        'button[onclick*="behavioral_verify"]',
        'div[onclick*="AKCPT"]',
        '.behavioral-content button',
        'button.challenge-button'
    ]
    
    def __init__(self, browser):
        self.browser = browser
    
    def detect_challenge(self):
        """
        Comprehensive Akamai challenge detection
        Returns: (detected: bool, method: str, details: dict)
        """
        
        # Method 1: Check for challenge button (most reliable)
        button_result = self._check_challenge_button()
        if button_result['detected']:
            return True, 'challenge_button', button_result
        
        # Method 2: Check for challenge text in page
        text_result = self._check_challenge_text()
        if text_result['detected']:
            return True, 'challenge_text', text_result
        
        # Method 3: Check for Akamai overlay
        overlay_result = self._check_akamai_overlay()
        if overlay_result['detected']:
            return True, 'akamai_overlay', overlay_result
        
        # Method 4: Check cookies for challenge state
        cookie_result = self._check_akamai_cookies()
        if cookie_result['detected']:
            return True, 'cookie_state', cookie_result
        
        # Method 5: Check page source for AKCPT
        source_result = self._check_page_source()
        if source_result['detected']:
            return True, 'page_source', source_result
        
        return False, None, {}
    
    def _check_challenge_button(self):
        """Check for challenge button elements"""
        for selector in self.CHALLENGE_SELECTORS:
            try:
                elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        # Check if it's actually the challenge button
                        text = element.text.lower()
                        
                        for lang, phrases in self.CHALLENGE_TEXTS.items():
                            for phrase in phrases:
                                if phrase.lower() in text:
                                    return {
                                        'detected': True,
                                        'selector': selector,
                                        'text': element.text,
                                        'language': lang,
                                        'size': element.size,
                                        'location': element.location
                                    }
            except Exception as e:
                logging.debug(f'Error checking selector {selector}: {e}')
        
        return {'detected': False}
    
    def _check_challenge_text(self):
        """Check for challenge text in visible elements"""
        try:
            body_text = self.browser.find_element(By.TAG_NAME, 'body').text.lower()
            
            for lang, phrases in self.CHALLENGE_TEXTS.items():
                for phrase in phrases:
                    if phrase.lower() in body_text:
                        return {
                            'detected': True,
                            'phrase': phrase,
                            'language': lang,
                            'context': body_text[max(0, body_text.find(phrase.lower())-50):
                                               body_text.find(phrase.lower())+50]
                        }
        except Exception as e:
            logging.debug(f'Error checking challenge text: {e}')
        
        return {'detected': False}
    
    def _check_akamai_overlay(self):
        """Check for Akamai overlay elements"""
        overlay_selectors = [
            "div[id^='sec-if-cpt']",
            "div[id^='sec-cpt']",
            "div.behavioral-content",
            "div[class*='akamai']",
            "iframe[src*='akamai']"
        ]
        
        for selector in overlay_selectors:
            try:
                elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        size = element.size
                        if size['width'] > 200 and size['height'] > 200:
                            opacity = element.value_of_css_property('opacity')
                            if opacity and float(opacity) > 0.5:
                                return {
                                    'detected': True,
                                    'selector': selector,
                                    'size': size,
                                    'opacity': opacity
                                }
            except Exception as e:
                logging.debug(f'Error checking overlay {selector}: {e}')
        
        return {'detected': False}
    
    def _check_akamai_cookies(self):
        """Check Akamai cookies for challenge indicators"""
        try:
            cookies = {c['name']: c['value'] for c in self.browser.get_cookies()}
            
            found_cookies = {}
            for cookie_name in self.AKAMAI_COOKIES:
                if cookie_name in cookies:
                    found_cookies[cookie_name] = cookies[cookie_name][:50]  # Truncate
            
            if found_cookies:
                # Check if _abck indicates challenge state
                if '_abck' in found_cookies:
                    abck_value = found_cookies['_abck']
                    # Akamai challenge state indicators (simplified)
                    if '~0~' in abck_value or '~-1~' in abck_value:
                        return {
                            'detected': True,
                            'cookies': found_cookies,
                            'reason': 'Challenge state in _abck cookie'
                        }
        except Exception as e:
            logging.debug(f'Error checking cookies: {e}')
        
        return {'detected': False}
    
    def _check_page_source(self):
        """Check page source for Akamai challenge indicators"""
        try:
            source = self.browser.page_source
            
            indicators = [
                'AKCPT.behavioral_verify',
                'akamai.bot.manager',
                'behavioral-content',
                'proceed-button'
            ]
            
            found = []
            for indicator in indicators:
                if indicator in source:
                    found.append(indicator)
            
            if len(found) >= 2:  # Multiple indicators = likely challenge
                return {
                    'detected': True,
                    'indicators': found,
                    'count': len(found)
                }
        except Exception as e:
            logging.debug(f'Error checking page source: {e}')
        
        return {'detected': False}
```

#### 4.2 Интегрировать в Checker
```python
from lib.akamai_detector import AkamaiDetector

class Checker:
    def __init__(self, config):
        self.config = config
        self.human = HumanBehavior(config.browser)
        self.akamai = AkamaiDetector(config.browser)
        self._cached_check_date = None
    
    def detect_captcha(self):
        """Wrapper around AkamaiDetector for backwards compatibility"""
        detected, method, details = self.akamai.detect_challenge()
        
        if detected:
            self._handle_akamai_challenge(method, details)
            return True
        
        return False
    
    def _handle_akamai_challenge(self, method, details):
        """Handle detected Akamai challenge"""
        current_url = self.config.browser.current_url
        
        # Build detailed message
        msg = f'🚨 AKAMAI CHALLENGE DETECTED!\n\n'
        msg += f'🔍 Detection Method: {method}\n'
        msg += f'🌐 URL: {current_url}\n'
        msg += f'⏰ Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
        
        # Add method-specific details
        if method == 'challenge_button':
            msg += f'📍 Button text: "{details.get("text", "N/A")}"\n'
            msg += f'🌍 Language: {details.get("language", "N/A")}\n'
        elif method == 'challenge_text':
            msg += f'📝 Found phrase: "{details.get("phrase", "N/A")}"\n'
            msg += f'🌍 Language: {details.get("language", "N/A")}\n'
        elif method == 'akamai_overlay':
            msg += f'📐 Overlay size: {details.get("size", {})}\n'
        elif method == 'cookie_state':
            msg += f'🍪 Cookies: {details.get("cookies", {})}\n'
        
        msg += f'\n⏸️ Bot paused for 120 seconds\n'
        msg += f'🔗 VNC: http://localhost:6080 (password: password)\n'
        msg += f'✋ Please solve the challenge manually\n'
        
        logging.warning(f'AKAMAI CHALLENGE DETECTED via {method}')
        logging.debug(f'Challenge details: {details}')
        
        self.config.messenger.send_message(msg)
        
        # Wait for manual solving
        logging.info('Waiting 120 seconds for challenge resolution...')
        time.sleep(120)
        
        # Refresh page to check if challenge is gone
        logging.info('Refreshing page after challenge wait...')
        self.config.browser.refresh()
        time.sleep(random.uniform(3, 5))
        
        # Recheck
        still_detected, _, _ = self.akamai.detect_challenge()
        if still_detected:
            logging.warning('Challenge still present after wait!')
            self.config.messenger.send_message('⚠️ Challenge still active after 120s wait')
        else:
            logging.info('Challenge appears to be resolved!')
            self.config.messenger.send_message('✅ Challenge resolved, continuing...')
```

**Время:** 2 часа  
**Приоритет:** 🔴 HIGH

---

### Фаза 5: Проверка после критичных действий
**Цель:** Автоматически проверять челлендж после каждого важного действия

#### 5.1 Декоратор для критичных действий
```python
def check_challenge_after(func):
    """Decorator to check for Akamai challenge after critical actions"""
    def wrapper(self, *args, **kwargs):
        # Execute original function
        result = func(self, *args, **kwargs)
        
        # Check for challenge
        time.sleep(random.uniform(0.5, 1.0))  # Small delay for overlay to appear
        detected = self.detect_captcha()
        
        if detected:
            logging.info(f'Challenge detected after {func.__name__}')
        
        return result
    
    return wrapper
```

#### 5.2 Применить к критичным методам
```python
@check_challenge_after
def select_location(self, location_name):
    # ... existing code ...

@check_challenge_after  
def select_first_queue_atomic(self):
    # ... existing code ...

# В check_last_date_only после клика по дате:
self.human.human_click(date_info['cell'])
self.wait_spinner()

# СРАЗУ проверяем челлендж
self.detect_captcha()
```

**Время:** 30 минут  
**Приоритет:** 🟡 MEDIUM

---

### Фаза 6: Увеличенные задержки
**Цель:** Добавить random delays между всеми действиями

#### 6.1 Обновить задержки в Checker
```python
# Перед каждым критичным действием:
self.human.random_delay(3, 8)

# Например:
def expand_locations(self):
    self.human.random_delay(3, 8)  # Вместо time.sleep(0.15-0.35)
    logging.info('expand list of locations')
    # ...

def select_location(self, location_name):
    self.human.random_delay(3, 8)  # Вместо быстрых задержек
    # ...
```

#### 6.2 Добавить переменную окружения для контроля
```python
# В .env:
HUMAN_DELAY_MIN=3
HUMAN_DELAY_MAX=8

# В HumanBehavior:
def random_delay(self):
    min_sec = int(os.environ.get('HUMAN_DELAY_MIN', '3'))
    max_sec = int(os.environ.get('HUMAN_DELAY_MAX', '8'))
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
```

**Время:** 30 минут  
**Приоритет:** 🟡 MEDIUM

---

## 📊 Приоритизация

### Критичные (делать первыми):
1. **Фаза 1: Undetected ChromeDriver** - основа anti-detection
2. **Фаза 4: Улучшенная детекция** - надежное обнаружение
3. **Фаза 3: Человекоподобное поведение** - минимизация появления

### Важные (делать потом):
4. **Фаза 2: Cookie Persistence** - реюз сессий
5. **Фаза 5: Проверка после действий** - автоматика
6. **Фаза 6: Увеличенные задержки** - дополнительная маскировка

---

## 🧪 Тестирование

### Для каждой фазы:
1. Docker rebuild
2. Запуск с LOG_LEVEL=DEBUG
3. Наблюдение за логами
4. Проверка что челлендж обнаруживается
5. Проверка Telegram уведомлений

### Метрики успеха:
- ✅ Челлендж появляется реже (< 1 раз в 10 запусков)
- ✅ Когда появляется - обнаруживается в 100% случаев
- ✅ Telegram уведомление приходит немедленно
- ✅ После паузы бот корректно продолжает работу

---

## 📁 Файловая структура

```
lib/
  ├── akamai_detector.py       # NEW - Comprehensive detection
  ├── cookie_manager.py        # NEW - Cookie persistence
  ├── browser_factory.py       # MODIFY - Use undetected-chromedriver
  ├── human_behavior.py        # MODIFY - Enhanced human-like actions
  ├── checker.py              # MODIFY - Integrate all improvements
  └── checker_config.py       # MODIFY - Add AkamaiDetector

requirements.txt             # MODIFY - Add undetected-chromedriver
docker-compose.yml          # MODIFY - Add persistent volume
.env                        # MODIFY - Add HUMAN_DELAY_* vars
```

---

## ⏱️ Оценка времени

| Фаза | Время | Приоритет |
|------|-------|-----------|
| 1. Undetected ChromeDriver | 30 мин | 🔴 HIGH |
| 2. Cookie Persistence | 45 мин | 🟡 MEDIUM |
| 3. Human Behavior | 1 час | 🔴 HIGH |
| 4. Akamai Detector | 2 часа | 🔴 HIGH |
| 5. Check After Actions | 30 мин | 🟡 MEDIUM |
| 6. Increased Delays | 30 мин | 🟡 MEDIUM |
| **ВСЕГО** | **~5-6 часов** | |

---

## 🚀 Порядок выполнения

1. **Фаза 4** - Создать AkamaiDetector (детекция важнее всего!)
2. **Фаза 1** - Переход на undetected-chromedriver
3. **Фаза 3** - Улучшить HumanBehavior
4. **Фаза 2** - Cookie persistence
5. **Фаза 5** - Декораторы для проверок
6. **Фаза 6** - Увеличенные задержки

После каждой фазы - тестирование!

---

## 💡 Дополнительные улучшения (опционально)

### Для будущего:
- API-солвер интеграция (2Captcha, Anti-Captcha)
- Machine Learning для предсказания появления челленджа
- Автоматическое решение через headless browser simulation
- Ротация прокси для распределения запросов
- Fingerprint randomization (canvas, WebGL, audio)

---

**Готов приступить! Начинаем с Фазы 4 (детекция) как самой критичной?**
