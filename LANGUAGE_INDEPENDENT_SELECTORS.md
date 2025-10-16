# Language-Independent Selectors

## Проблема
Текст на сайте может меняться в зависимости от языка интерфейса:
- `Cases.MakeAppointmentAtOffice` (английский)
- `Umów wizytę w urzędzie` (польский)
- Другие варианты

Поиск по тексту ненадежен!

## Решение
Используем **структурные селекторы** - ищем по HTML атрибутам и классам, которые не зависят от языка.

---

## Обновленные селекторы

### 1. Проверка наличия секции записи
```python
# Было (зависит от языка):
'//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]'

# Стало (language-independent):
'//mat-select[@name="location"]'
```
**Логика**: Если есть dropdown с `name="location"`, значит секция записи существует.

### 2. Проверка раскрыта ли панель
```python
# Проверяем видимость location dropdown
x_location_dropdown = '//mat-select[@name="location"]'
dropdown_elements = browser.find_elements(By.XPATH, x_location_dropdown)

if len(dropdown_elements) > 0 and dropdown_elements[0].is_displayed():
    # Панель раскрыта
else:
    # Панель закрыта, нужно кликнуть
```

### 3. Поиск кнопки для раскрытия
```python
# Было (зависит от текста):
'//h3[contains(text(),"Cases.MakeAppointmentAtOffice")]/parent::button'

# Стало (по структуре DOM):
'//button[following-sibling::div[contains(@class,"accordion__more")]//mat-select[@name="location"]]'
```
**Логика**: Ищем `button`, у которого есть sibling `div.accordion__more`, содержащий `mat-select[name="location"]`.

---

## Преимущества

✅ **Работает на любом языке** - не зависит от текста  
✅ **Надежнее** - атрибуты `name="location"` стабильнее чем текст  
✅ **Проще поддержка** - не нужно добавлять переводы  

---

## Обновленные методы

### `open_case_page()`
```python
# Ищем mat-select вместо h3 с текстом
x_appointment_section = '//div[contains(@class,"accordion")]//mat-select[@name="location"]'
self.waiter.until(EC.presence_of_element_located((By.XPATH, x_appointment_section)))
```

### `expand_appointment_panel()`
```python
# 1. Проверяем видимость dropdown
x_location_dropdown = '//mat-select[@name="location"]'
dropdown_elements = self.config.browser.find_elements(by=By.XPATH, value=x_location_dropdown)

if dropdown_elements[0].is_displayed():
    # Уже раскрыто
    return

# 2. Ищем кнопку по структуре
x_accordion_button = '//button[following-sibling::div[contains(@class,"accordion__more")]//mat-select[@name="location"]]'
button_el = self.config.browser.find_element(by=By.XPATH, value=x_accordion_button)
button_el.click()
```

### `check_one_location()`
Аналогично `expand_appointment_panel()`.

---

## Другие language-independent селекторы

| Элемент | Селектор | Почему надежен |
|---------|----------|----------------|
| Location dropdown | `//mat-select[@name="location"]` | Атрибут `name` |
| Queue dropdown | `//mat-select[@name="queueName"]` | Атрибут `name` |
| Location options | `//mat-option/span[@class="mat-option-text"]` | Класс Material |
| Queue options | `//mat-option/span[@class="mat-option-text"]` | Класс Material |
| Calendar dates | `//td[@role="gridcell"]` | ARIA атрибут |
| Next month button | `//button[contains(@class,"mat-calendar-next-button")]` | Класс Material |
| Spinner | `//mat-spinner[@role="progressbar"]` | ARIA атрибут |

---

## Тестирование

Бот теперь должен работать независимо от языка интерфейса:
- 🇵🇱 Польский
- 🇬🇧 Английский  
- 🇺🇦 Украинский (если добавят)
- Любой другой

---

## Дата обновления
16.10.2025 - Переход на language-independent селекторы
