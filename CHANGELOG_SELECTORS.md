# Changelog - Selector Updates & Akamai Protection

## 🎯 Обновления от 17.10.2025 (LATEST)

### ✅ 1. Мультиязычный селектор кнопки раскрытия

#### Проблема
Старый селектор зависел от английского текста кнопки, не работал с другими языками интерфейса.

#### Решение
```python
# Новый мультиязычный XPath с translate() для case-insensitive поиска:
x_appointment_button = '''//h3[
    contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "appointment") or 
    contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "wizyt") or 
    contains(translate(text(), "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"), "зустріч") or 
    contains(translate(text(), "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"), "встречу")
]/following::button[contains(@class, "btn--accordion")][1]'''
```

#### Поддерживаемые языки
- 🇬🇧 **English**: "Make an appointment at the office"
- 🇵🇱 **Polski**: "Umów się na wizytę w urzędzie"
- 🇺🇦 **Українська**: "Домовтеся про зустріч в офісі"
- 🇷🇺 **Русский**: "Назначить встречу в офисе"

#### Где применено
- ✅ `expand_appointment_panel()` - основной метод раскрытия
- ✅ `check_one_location()` - проверка одной локации

### ✅ 2. Обновлены селекторы календаря Material Design

#### Кликабельные даты
```python
# Было (работало, но не оптимально):
'//mat-calendar[...]/td[@role="gridcell" and not(contains(@class,"disabled"))]'

# Стало (точнее, кликаем именно контент ячейки):
'//mat-calendar[...]/td[@role="gridcell" and not(contains(@class,"disabled"))]//div[contains(@class,"mat-calendar-body-cell-content")]'
```

#### Месяц/год
```python
# Было (лишний /span):
'//button[contains(@class,"mat-calendar-period-button")]/span/span'

# Стало (проще и надежнее):
'//button[contains(@class,"mat-calendar-period-button")]/span'
```

#### Кнопки навигации
```python
# Добавлена кнопка предыдущего месяца:
x_prev_month = '//button[contains(@class,"mat-calendar-previous-button")]'
x_next_month = '//button[contains(@class,"mat-calendar-next-button")]'  # было и раньше
```

### ✅ 3. Улучшенная детекция временных слотов

#### Двухэтапная проверка
```python
# Шаг 1: Проверяем наличие контейнера
x_reservations_hours = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]'

# Шаг 2: Проверяем наличие самих слотов
x_time_slots = '//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]//*[contains(@class,"tile")]'
```

#### Логика проверки
```python
slots_container = browser.find_elements(By.XPATH, x_reservations_hours)
if len(slots_container) != 0:
    time_slots = browser.find_elements(By.XPATH, x_time_slots)
    if len(time_slots) > 0:
        # 🎯 SLOT FOUND! Отправляем уведомление
        msg = f'🎯 SLOT FOUND! {date} ({len(time_slots)} slots available)'
    else:
        # Контейнер есть, но слотов нет (распространенная ситуация)
        logging.debug(f'Container found but no time slots for {date}')
```

#### Преимущества
- ✅ Меньше ложных срабатываний
- ✅ Точное количество доступных слотов
- ✅ Лучшие DEBUG логи

### ✅ 4. Проверка капчи перед каждым месяцем

```python
while True:
    # ← ДОБАВЛЕНО: проверка перед каждым месяцем
    self.detect_captcha()
    
    month_year_text = ...
    enabled_cells = ...
    # ...
```

#### Зачем
- Akamai может показать капчу в любой момент
- Ранняя детекция = меньше потерянного времени
- Уведомление сразу после появления

### ✅ 5. Консистентные человекоподобные задержки

#### Обновлено везде на `rand.uniform(2, 5)`
- ✅ Загрузка страниц
- ✅ Раскрытие панели
- ✅ Открытие dropdown
- ✅ Выбор опций
- ✅ Клики по датам
- ✅ Навигация по месяцам

#### Специальные задержки
```python
# После раскрытия панели (ждем анимацию):
time.sleep(rand.uniform(2, 3))

# Перед кликом по кнопке (имитация "думания"):
time.sleep(rand.uniform(1, 2))

# Скролл + небольшая пауза:
element.location_once_scrolled_into_view
time.sleep(rand.uniform(0.5, 1.0))
```

### ✅ 6. JavaScript клики для accordion кнопок

```python
# Вместо обычного клика:
button_el.click()

# Используем JavaScript (надежнее для accordion):
self.config.browser.execute_script("arguments[0].click();", button_el)
```

#### Причина
- Accordion кнопки иногда перекрываются другими элементами
- JavaScript клик обходит эту проблему
- Более стабильная работа

### ✅ 7. Создана документация SETUP_REQUIREMENTS.md

Полное руководство включает:
- ✅ Список обязательных и опциональных переменных окружения
- ✅ Docker setup инструкции
- ✅ VNC доступ для ручного решения капчи
- ✅ Systemd service для автозапуска
- ✅ Troubleshooting распространенных проблем
- ✅ Описание режимов работы
- ✅ Уровни логирования
- ✅ Будущие улучшения

## 📊 Сравнение селекторов

### Кнопка раскрытия

| Версия | Селектор | Языки | Надежность |
|--------|----------|-------|------------|
| **16.10.2025** | `//button[.//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]]` | 1 (token) | ⚠️ Средняя |
| **17.10.2025** | Multi-language XPath через translate() | 4 (EN/PL/UA/RU) | ✅ Высокая |

### Календарь

| Элемент | Старый | Новый | Улучшение |
|---------|--------|-------|-----------|
| **Даты** | `td[@role="gridcell"]` | `td[@role="gridcell"]//div[...mat-calendar-body-cell-content]` | Кликаем в правильное место |
| **Месяц/год** | `button[...]/span/span` | `button[...]/span` | Проще, надежнее |
| **Слоты** | Одна проверка контейнера | Двойная проверка (контейнер + слоты) | Меньше ложных срабатываний |

## 🎯 Обновления от 16.10.2025

### ✅ 1. Обновлены селекторы (из selectors.md)

#### Кнопка записи
```python
# Старый (не работает):
'//div/h3[contains(text(),"Make an appointment at the office")]/following-sibling::button'

# Новый (актуальный):
'//button[.//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]]'
```

#### Dropdown локаций и очередей
- `//mat-select[@name="location"]` - ✅ работает
- `//mat-select[@name="queueName"]` - ✅ работает
- `//mat-option/span[@class="mat-option-text"]` - ✅ работает

#### Календарь
- Enabled cells: `//mat-calendar[contains(@class,"reservation-calander")]/div/mat-month-view/table/tbody/tr/td[@role="gridcell" and not(contains(@class,"disabled"))]` - ✅ работает
- Next month: `//button[contains(@class,"mat-calendar-next-button")]` - ✅ работает
- Month/Year: `//button[contains(@class,"mat-calendar-period-button")]/span/span` - ✅ работает

### ✅ 2. Добавлена обработка Akamai капчи

#### Новый метод `detect_captcha()`
```python
def detect_captcha(self):
    """Detect Akamai captcha and wait for manual solving."""
    try:
        captcha_iframes = self.config.browser.find_elements(
            By.CSS_SELECTOR, "iframe[src*='akamai']"
        )
        if captcha_iframes:
            msg = '⚠️ AKAMAI CAPTCHA DETECTED! Please solve manually in VNC within 2 minutes'
            logging.warning(msg)
            self.config.messenger.send_message(msg)
            time.sleep(120)  # Wait 2 minutes
            return True
    except Exception as e:
        logging.debug(f'Captcha detection error: {e}')
    return False
```

#### Где вызывается
- ✅ `open_case_page()` - после загрузки страницы кейса
- ✅ `check_one_location()` - перед началом проверки локации

### ✅ 3. Увеличены задержки (2-5 секунд)

#### Было
```python
time.sleep(1)
self.random_sleep()  # 0.3-0.9 секунд
```

#### Стало
```python
time.sleep(rand.uniform(2, 5))  # 2-5 секунд случайно
```

#### Где применено
- ✅ Загрузка страниц
- ✅ Открытие dropdown меню
- ✅ Выбор локаций
- ✅ Выбор очередей
- ✅ Клики по датам календаря
- ✅ Переключение месяцев

### ✅ 4. Human-like поведение

#### Замена обычных кликов
```python
# Было:
element.click()

# Стало:
self.human.human_click(element)
```

#### Где применено
- ✅ Кнопка "Umów wizytę"
- ✅ Dropdown локаций
- ✅ Выбор локации
- ✅ Dropdown очередей
- ✅ Выбор очереди
- ✅ Клики по датам
- ✅ Кнопка следующего месяца

### ✅ 5. Таймзона Europe/Warsaw

#### docker-compose.yml
```yaml
environment:
  - "TZ=Europe/Warsaw"  # ← ДОБАВЛЕНО
  - "CHROMEDRIVER_PATH=/usr/bin/chromedriver"
  - "CHROME_BINARY=/usr/bin/chromium"
```

#### Эффект
- Системное время контейнера = Warsaw time
- Логи с правильным временем
- Совпадает с browser_factory.py (Emulation.setTimezoneOverride)

## 📊 Сравнение поведения

### До обновления
```
Action                  Delay       Click Type
─────────────────────────────────────────────
Load page              1s          -
Open dropdown          0.3-0.9s    element.click()
Select option          0.3-0.9s    element.click()
Click date             0.3-0.9s    element.click()
Next month             0.3-0.9s    element.click()

Total per date: ~2-4 seconds
Detection risk: HIGH ⚠️
```

### После обновления
```
Action                  Delay       Click Type
─────────────────────────────────────────────
Load page              2-5s        -
Captcha check          0-120s      -
Open dropdown          2-5s        human_click()
Select option          2-5s        human_click()
Click date             2-5s        human_click()
Next month             2-5s        human_click()

Total per date: ~8-20 seconds
Detection risk: LOW ✅
```

## 🔧 Обновленные файлы

1. **lib/checker.py**
   - ✅ Добавлен `detect_captcha()`
   - ✅ Обновлены все селекторы
   - ✅ Увеличены задержки до 2-5 секунд
   - ✅ Заменены клики на `human_click()`
   - ✅ Добавлены проверки капчи

2. **docker-compose.yml**
   - ✅ Добавлена `TZ=Europe/Warsaw`

3. **Без изменений** (как требовалось)
   - ✅ Основная логика работы бота
   - ✅ Алгоритм проверки дат
   - ✅ Telegram уведомления
   - ✅ Структура проекта

## 🚀 Как применить обновления

```bash
# 1. Пересобрать контейнер
docker compose down
docker compose build

# 2. Запустить
docker compose up -d

# 3. Проверить логи
docker compose logs -f

# 4. Подключиться через VNC (если капча)
# localhost:5900 (password: password)
```

## 📝 Логи

### Успешная работа
```
INFO - expand appointment panel
INFO - expand list of locations
INFO - location selection (ul. Marszałkowska 3/5, 00-624 Warszawa)
INFO - open list of queues
INFO - queue selection (X - applications for TEMPORARY STAY)
INFO - 15 enabled cells in GRUDZIEŃ 2024
INFO - check 17 GRUDZIEŃ 2024
```

### Обнаружена капча
```
WARNING - ⚠️ AKAMAI CAPTCHA DETECTED! Please solve manually in VNC within 2 minutes
[Telegram notification sent]
[Waiting 120 seconds...]
```

## ⚠️ Важные замечания

1. **Капча** - если появляется, у вас есть 2 минуты чтобы решить через VNC
2. **Задержки** - бот теперь работает медленнее (8-20 сек на дату), но безопаснее
3. **Селекторы** - если сайт снова изменится, обновите `selectors.md` и `checker.py`
4. **Логика** - алгоритм проверки НЕ изменен, только селекторы и задержки

## 🎯 Следующие шаги

1. ✅ Протестировать на реальном сайте
2. ⏳ Собрать статистику обнаружения капчи
3. ⏳ При необходимости скорректировать задержки
4. ⏳ Обновить селекторы слотов времени (когда появятся)
