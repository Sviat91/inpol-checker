# План решения проблем бота

## 🎯 Две основные проблемы

### 1. ❌ Бот не видит капчу
**Статус:** Требует отладки и тестирования

### 2. ❌ Неправильное определение последней даты для проверки
**Статус:** Логика понятна, готов к реализации

---

## 📋 Задача 1: Исправление логики определения даты (ПРИОРИТЕТ!)

### Проблема:
Текущая логика слишком простая:
```python
# ❌ Сейчас:
last_date = valid_cells[-1]  # Просто берем последнюю дату
if is_end_of_month(last_date):  # Если в последних 5 днях
    check_next_month()
```

**Что не так:**
- Даты появляются на **~6 недель** вперед
- Бот должен **идти до самой дальней даты**, пропуская месяцы где последняя дата = последний рабочий день
- Сейчас останавливается слишком рано

### Правильная логика:

#### Шаг 1: Определить последний рабочий день месяца
```python
def get_last_working_day_of_month(year, month):
    """
    Получить последний рабочий день месяца (пропуская выходные).
    
    Например:
    - Октябрь 2025: последний день 31 (пятница) → 31
    - Ноябрь 2025: последний день 30 (воскресенье), 29 (суббота) → 28 (пятница)
    - Декабрь 2025: последний день 31 (среда) → 31
    """
    last_day = calendar.monthrange(year, month)[1]
    
    # Идем назад от последнего дня до первого рабочего дня
    for day in range(last_day, 0, -1):
        weekday = datetime(year, month, day).weekday()
        if weekday < 5:  # Mon-Fri
            return day
    
    return last_day  # Fallback
```

#### Шаг 2: Алгоритм поиска даты для проверки
```
1. Загрузить текущий месяц календаря
2. Получить все доступные даты (игнорируя выходные)
3. Найти последнюю доступную дату (last_available_date)
4. Определить последний рабочий день месяца (last_working_day)

5. ЕСЛИ last_available_date == last_working_day:
   → Это значит даты идут дальше в следующий месяц
   → Переход в следующий месяц
   → GOTO шаг 2
   
6. ИНАЧЕ last_available_date < last_working_day:
   → Мы нашли самую дальнюю доступную дату!
   → Это наша дата для проверки
   → STOP и проверяем эту дату
```

#### Пример работы:

**Сценарий 1: Октябрь 2025**
```
Текущий месяц: PAŹ 2025 (Октябрь)
Доступные даты (без выходных): [1, 2, 3, ..., 29, 30, 31]
Последняя доступная дата: 31 (пятница)
Последний рабочий день месяца: 31 (пятница)

31 == 31 → Идем в следующий месяц!
```

**Сценарий 2: Ноябрь 2025**
```
Текущий месяц: LIS 2025 (Ноябрь)
Доступные даты (без выходных): [3, 4, 5, ..., 26, 27, 28]
Последняя доступная дата: 28 (пятница)
Последний рабочий день месяца: 28 (пятница, т.к. 29 сб, 30 вс)

28 == 28 → Идем в следующий месяц!
```

**Сценарий 3: Декабрь 2025**
```
Текущий месяц: GRU 2025 (Декабрь)
Доступные даты: []
Нет дат!

→ Возвращаемся в предыдущий месяц (Ноябрь)
→ Проверяем последнюю дату: 28 LIS 2025
```

**Сценарий 4: Ноябрь (альтернатива)**
```
Текущий месяц: LIS 2025 (Ноябрь)
Доступные даты (без выходных): [3, 4, 5, ..., 26, 27]
Последняя доступная дата: 27 (четверг)
Последний рабочий день месяца: 28 (пятница)

27 < 28 → Это наша дата для проверки!
→ Проверяем 27 LIS 2025 СРАЗУ, не идем в декабрь
```

### Реализация:

#### Новый метод `find_furthest_available_date()`:
```python
def find_furthest_available_date(self):
    """
    Найти самую дальнюю доступную дату (до 6 недель вперед).
    
    Алгоритм:
    1. Начинаем с текущего месяца
    2. Пока последняя доступная дата == последний рабочий день месяца:
       - Переходим в следующий месяц
    3. Возвращаем месяц + дату для проверки
    """
    max_months_to_check = 3  # Макс 3 месяца вперед (безопасность)
    
    for month_offset in range(max_months_to_check):
        # Получаем инфо о текущем месяце
        month_year_text = get_current_month()
        enabled_cells = get_enabled_dates()
        
        if len(enabled_cells) == 0:
            # Нет дат в этом месяце
            if month_offset > 0:
                # Возвращаемся назад
                click_prev_month()
                return get_last_available_date()
            else:
                # Нет дат вообще
                return None
        
        # Фильтруем выходные
        valid_cells = [cell for cell in enabled_cells 
                       if not is_weekend(cell.text, month_year_text)]
        
        if len(valid_cells) == 0:
            continue
        
        # Последняя доступная дата
        last_available_date = int(valid_cells[-1].text)
        
        # Последний рабочий день месяца
        year, month = parse_month_year(month_year_text)
        last_working_day = get_last_working_day_of_month(year, month)
        
        logging.info(f'Month: {month_year_text}, Last available: {last_available_date}, '
                     f'Last working day: {last_working_day}')
        
        if last_available_date == last_working_day:
            # Даты идут дальше, переходим в следующий месяц
            logging.info(f'Last date {last_available_date} matches last working day '
                         f'{last_working_day}, checking next month...')
            click_next_month()
            continue
        else:
            # Нашли дату для проверки!
            logging.info(f'Found date to check: {last_available_date} {month_year_text} '
                         f'(not end of month)')
            return {
                'cell': valid_cells[-1],
                'date': last_available_date,
                'month_year': month_year_text,
                'months_forward': month_offset
            }
    
    # Достигли лимита месяцев
    logging.warning(f'Reached max months ({max_months_to_check}), using last available')
    return {
        'cell': valid_cells[-1],
        'date': int(valid_cells[-1].text),
        'month_year': month_year_text,
        'months_forward': max_months_to_check
    }
```

#### Обновить `check_last_date_only()`:
```python
def check_last_date_only(self, location, queue):
    # Загружаем календарь
    load_calendar()
    
    # Ищем самую дальнюю дату (проходя по месяцам)
    date_info = self.find_furthest_available_date()
    
    if date_info is None:
        logging.warning('No dates available at all')
        return None
    
    # Кликаем по найденной дате
    logging.info(f'✅ Checking FURTHEST date: {date_info["date"]} {date_info["month_year"]}')
    human_click(date_info['cell'])
    wait_spinner()
    
    # Проверяем капчу
    detect_captcha()
    
    # Проверяем слоты
    check_slots()
    
    # Возвращаемся в начальный месяц (если уходили вперед)
    if date_info['months_forward'] > 0:
        for _ in range(date_info['months_forward']):
            click_prev_month()
    
    return slots_found
```

### Кеширование даты:

```python
class Checker:
    def __init__(self, config):
        self.config = config
        self.human = HumanBehavior(config.browser)
        self._cached_check_date = None  # Кеш для текущей сессии
    
    def find_furthest_available_date(self):
        # Если уже нашли дату в этой сессии - используем кеш
        if self._cached_check_date is not None:
            logging.info(f'Using cached date: {self._cached_check_date["date"]} '
                         f'{self._cached_check_date["month_year"]}')
            
            # Переходим к нужному месяцу
            target_month = self._cached_check_date['months_forward']
            for _ in range(target_month):
                click_next_month()
            
            # Находим ту же дату
            enabled_cells = get_enabled_dates()
            valid_cells = filter_weekends(enabled_cells)
            target_date = self._cached_check_date['date']
            
            for cell in valid_cells:
                if int(cell.text) == target_date:
                    return {
                        'cell': cell,
                        'date': target_date,
                        'month_year': get_current_month(),
                        'months_forward': target_month
                    }
        
        # Иначе ищем дату заново
        date_info = self._find_furthest_date_uncached()
        
        # Сохраняем в кеш (без WebElement, только данные)
        self._cached_check_date = {
            'date': date_info['date'],
            'month_year': date_info['month_year'],
            'months_forward': date_info['months_forward']
        }
        
        return date_info
```

### План реализации:

1. ✅ Создать `get_last_working_day_of_month(year, month)`
2. ✅ Создать `parse_month_year(month_year_text)` → (year, month)
3. ✅ Переписать `find_furthest_available_date()` с правильной логикой
4. ✅ Добавить кеширование `_cached_check_date`
5. ✅ Обновить `check_last_date_only()` для использования нового метода
6. ✅ Добавить логирование для отладки
7. ✅ Тестирование на реальных данных

### Тесты:

**Тест 1: Даты до конца месяца**
```
Октябрь: 1-31 (31 = пятница)
→ Идем в ноябрь
Ноябрь: 1-28 (28 = пятница, последний рабочий)
→ Идем в декабрь
Декабрь: нет дат
→ Возвращаемся, проверяем 28 ноября
```

**Тест 2: Даты НЕ до конца месяца**
```
Октябрь: 1-30 (30 = четверг, 31 = пятница)
→ 30 < 31, проверяем 30 октября СРАЗУ
```

**Тест 3: Кеширование**
```
Адрес 1: Ищем дату → 28 ноября → сохраняем в кеш
Адрес 2: Используем кеш → 28 ноября (без поиска!)
Адрес 3: Используем кеш → 28 ноября (без поиска!)
```

---

## 📋 Задача 2: Исправление детекции капчи (ВТОРАЯ ПРИОРИТЕТ)

### Проблема:
Бот не видит капчу, хотя она появляется (видно на скриншоте).

### Возможные причины:

#### Причина 1: Кнопка в iframe
```python
# Возможно кнопка #proceed-button находится ВНУТРИ iframe
# Нужно переключиться в iframe перед поиском

# Попробовать:
iframe = browser.find_element(By.CSS_SELECTOR, "iframe[src*='akamai']")
browser.switch_to.frame(iframe)
proceed_button = browser.find_element(By.ID, "proceed-button")
browser.switch_to.default_content()
```

#### Причина 2: Элемент загружается с задержкой
```python
# Кнопка может появиться с задержкой после клика
# Нужно подождать немного перед проверкой

click_date()
time.sleep(0.5-1.0)  # Даем время капче появиться
detect_captcha()
```

#### Причина 3: Элемент есть, но невидим в контексте Selenium
```python
# Может быть element.is_displayed() возвращает False
# но визуально элемент видим

# Нужно проверять:
proceed_button = find_element("#proceed-button")
if proceed_button:
    # Проверяем не только is_displayed, но и размеры
    size = proceed_button.size
    location = proceed_button.location
    opacity = proceed_button.value_of_css_property('opacity')
    z_index = proceed_button.value_of_css_property('z-index')
    
    logging.debug(f'Proceed button: size={size}, loc={location}, '
                  f'opacity={opacity}, z-index={z_index}')
```

#### Причина 4: Селектор неправильный
```python
# Может быть ID динамический или атрибуты другие
# Нужно искать по другим признакам

# Попробовать:
# 1. По тексту кнопки
buttons = browser.find_elements(By.XPATH, "//button[contains(., 'Kontynuuj')]")

# 2. По классу
buttons = browser.find_elements(By.CSS_SELECTOR, "button.btn, div.btn")

# 3. По onclick
buttons = browser.find_elements(By.XPATH, 
    "//button[@onclick='AKCPT.behavioral_verify()'] | "
    "//div[@onclick='AKCPT.behavioral_verify()']")
```

### План отладки капчи:

#### Этап 1: Диагностика (БЕЗ изменения кода)
```python
# Добавить детальное логирование в detect_captcha():

def detect_captcha(self):
    logging.debug('=== CAPTCHA DETECTION START ===')
    
    # Проверяем наличие iframe
    iframes = browser.find_elements(By.TAG_NAME, 'iframe')
    logging.debug(f'Total iframes on page: {len(iframes)}')
    for i, iframe in enumerate(iframes):
        src = iframe.get_attribute('src') or ''
        logging.debug(f'  Iframe {i}: src="{src}", displayed={iframe.is_displayed()}')
    
    # Проверяем proceed-button в main context
    proceed_buttons = browser.find_elements(By.ID, 'proceed-button')
    logging.debug(f'Proceed buttons in main context: {len(proceed_buttons)}')
    for btn in proceed_buttons:
        logging.debug(f'  Button: displayed={btn.is_displayed()}, '
                      f'size={btn.size}, text="{btn.text}"')
    
    # Проверяем proceed-button в каждом iframe
    for i, iframe in enumerate(iframes):
        try:
            browser.switch_to.frame(iframe)
            proceed_buttons = browser.find_elements(By.ID, 'proceed-button')
            logging.debug(f'Proceed buttons in iframe {i}: {len(proceed_buttons)}')
            for btn in proceed_buttons:
                logging.debug(f'  Button: displayed={btn.is_displayed()}, '
                              f'size={btn.size}, text="{btn.text}"')
            browser.switch_to.default_content()
        except Exception as e:
            logging.debug(f'Error checking iframe {i}: {e}')
            browser.switch_to.default_content()
    
    # Проверяем любые кнопки с "Kontynuuj"
    kontynuuj_buttons = browser.find_elements(By.XPATH, "//*[contains(., 'Kontynuuj')]")
    logging.debug(f'Elements with "Kontynuuj": {len(kontynuuj_buttons)}')
    for btn in kontynuuj_buttons:
        logging.debug(f'  Element: tag={btn.tag_name}, displayed={btn.is_displayed()}, '
                      f'text="{btn.text}"')
    
    # Проверяем AKCPT в page source
    page_source = browser.page_source
    if 'AKCPT' in page_source:
        logging.debug('AKCPT found in page source!')
        if 'behavioral_verify' in page_source:
            logging.debug('behavioral_verify() found in page source!')
    
    logging.debug('=== CAPTCHA DETECTION END ===')
```

#### Этап 2: На основе логов определить где кнопка
- Запустить бот с LOG_LEVEL=DEBUG
- Дождаться капчи
- Проанализировать логи
- Понять где находится #proceed-button

#### Этап 3: Исправить детекцию
На основе результатов Этапа 2:
- Если в iframe → добавить switch_to.frame
- Если другой селектор → обновить селектор
- Если задержка → добавить ожидание

### План реализации (после диагностики):

1. ⏳ Добавить детальное логирование в `detect_captcha()`
2. ⏳ Запустить бот, дождаться капчи
3. ⏳ Проанализировать DEBUG логи
4. ⏳ Определить где находится кнопка
5. ⏳ Обновить метод `detect_captcha()` на основе результатов
6. ⏳ Тестирование

---

## 🎯 Порядок выполнения:

### Фаза 1: Исправление логики дат (НАЧАТЬ С ЭТОГО!)
1. Реализовать `get_last_working_day_of_month()`
2. Реализовать `parse_month_year()`
3. Переписать `find_furthest_available_date()`
4. Добавить кеширование
5. Обновить `check_last_date_only()`
6. Тестирование

### Фаза 2: Диагностика капчи
1. Добавить детальное логирование
2. Запустить и дождаться капчи
3. Проанализировать логи
4. Определить решение

### Фаза 3: Исправление капчи (после диагностики)
1. Обновить `detect_captcha()` на основе результатов
2. Тестирование

---

## 📊 Приоритеты:

| Задача | Приоритет | Сложность | Время |
|--------|-----------|-----------|-------|
| Логика дат | 🔴 HIGH | Средняя | 30-60 мин |
| Кеширование | 🟡 MEDIUM | Низкая | 15 мин |
| Диагностика капчи | 🔴 HIGH | Низкая | 10 мин + ожидание |
| Исправление капчи | 🔴 HIGH | Низкая-Средняя | 15-30 мин |

---

## ✅ Критерии успеха:

### Задача 1 (Даты):
- ✅ Бот проходит все месяцы пока не найдет самую дальнюю дату
- ✅ Бот правильно определяет последний рабочий день месяца
- ✅ Бот проверяет только 1 дату за цикл
- ✅ Кеш работает - дата определяется 1 раз за сессию
- ✅ Логи показывают процесс поиска даты

### Задача 2 (Капча):
- ✅ Бот обнаруживает капчу когда она появляется
- ✅ Telegram уведомление отправляется
- ✅ Бот делает паузу 2 минуты
- ✅ После решения бот продолжает работу

---

## 🚀 Начинаем с Задачи 1!

Готов приступить к реализации правильной логики определения даты.
