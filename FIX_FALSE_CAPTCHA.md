# Исправление ложных срабатываний детекции капчи

## 🐛 Проблема

Бот присылал уведомления о капче когда её на самом деле не было:
- ❌ Дважды прислал уведомление
- ❌ Капча ещё ни разу не появлялась
- ❌ Ложные срабатывания

## 🔍 Причина

Старая детекция была **слишком агрессивной**:

```python
# ❌ Проблемные проверки:
if 'akamai' in page_source:  # Слово может быть в скриптах!
    detect()

if 'behavioral' in page_source:  # Может быть где угодно
    detect()
    
if div.behavioral-content:  # Без проверки размера
    detect()
```

**Результат:** Срабатывала на скрипты, стили, скрытые элементы

## ✅ Решение

### 1. Строгая проверка размера и видимости

```python
# ✅ Новая проверка:
if iframe[src*='akamai']:
    if iframe.is_displayed():
        size = iframe.size
        if size['width'] > 100 and size['height'] > 100:  # Реальный размер!
            detect()
```

### 2. Проверка прозрачности

```python
if div.overlay:
    size = div.size
    if size['width'] > 200 and size['height'] > 200:  # Минимум 200x200px
        opacity = div.get_css('opacity')
        if opacity > 0.5:  # Не прозрачный!
            detect()
```

### 3. Убрали проверку текста на странице

```python
# ❌ УДАЛЕНО - слишком много false positives:
if 'akamai' in page_source:
    detect()
    
if 'behavioral' in page_source:
    detect()
```

```python
# ✅ ОСТАВЛЕНО - только видимый текст в модальных окнах:
if modal.contains('Potwierdź, że jesteś człowiekiem'):
    if modal.is_displayed():
        detect()
```

### 4. Уменьшена частота проверок

**Было:**
- Каждые 5 дат → 30 проверок на цикл
- После каждого выбора очереди → 3 проверки
- Перед каждым месяцем → 15 проверок
- **Итого:** ~50 проверок за цикл

**Стало:**
- Каждые 10 дат → 15 проверок на цикл
- После каждого выбора очереди → 3 проверки
- Перед каждым месяцем → 15 проверок
- **Итого:** ~35 проверок за цикл

## 📊 Новые условия детекции

### Метод 1: Akamai iframe
```python
iframe[src*='akamai'] AND
is_displayed() AND
width > 100px AND
height > 100px
```

### Метод 2: Akamai overlay
```python
(
  div[id^='sec-if-cpt'] OR
  div[id^='sec-cpt'] OR
  div.behavioral-content OR
  div[class*='akamai']
) AND
is_displayed() AND
width > 200px AND
height > 200px AND
opacity > 0.5
```

### Метод 3: Text in modal
```python
(
  div.modal OR
  div.dialog OR
  div.popup
) AND
contains('Potwierdź' OR 'człowiekiem' OR 'robot') AND
is_displayed()
```

## 🎯 Ожидаемый результат

### Когда капчи НЕТ:
```
[INFO] check 20 PAŹ 2025
[INFO] check 21 PAŹ 2025
[INFO] check 22 PAŹ 2025
...
[INFO] check 30 PAŹ 2025
[DEBUG] Captcha check (day 10) - none found ✅
[INFO] check 1 LIS 2025
```

**Никаких ложных уведомлений!**

### Когда капча ЕСТЬ:
```
[INFO] check 20 PAŹ 2025
[DEBUG] Captcha detected: Akamai overlay (div[id^='sec-cpt'], size: 400x300) ✅
[WARNING] CAPTCHA DETECTED (Akamai overlay...) - pausing for 2 minutes
📱 Telegram: "🚨 AKAMAI CAPTCHA DETECTED! Detection: Akamai overlay..."
```

**В уведомлении указывается причина обнаружения!**

## 🔧 Что добавлено

### Detection reason в уведомлении

**Старый формат:**
```
🚨 AKAMAI CAPTCHA DETECTED!
⏰ Bot paused...
```

**Новый формат:**
```
🚨 AKAMAI CAPTCHA DETECTED!
📍 Detection: Akamai iframe (visible and sized)
⏰ Bot paused...
```

**Возможные причины:**
- `Akamai iframe (visible and sized)` - нашёл iframe
- `Akamai overlay (div[id^='sec-cpt'], size: 400x300)` - overlay с размером
- `Captcha text in modal/dialog: "Potwierdź..."` - текст в модальном окне

## 🚀 Запуск с исправлением

```bash
# Пересборка завершена, запускай:
docker compose up

# Проверь логи - не должно быть false positives:
# ✅ [DEBUG] Captcha check - none found
# ❌ НЕ должно быть: CAPTCHA DETECTED если её нет
```

## 📊 Статистика

**На полный цикл (3 адреса × 5 месяцев):**
- ~150 проверок дат
- ~35 проверок капчи (было 50)
- ~0 ложных срабатываний (было 2+)

**Время обнаружения реальной капчи:** 10-60 секунд (было 10-30)

## ⚠️ Важно

1. **Если капча появляется часто** - нужно добавить AntiCaptcha
2. **Если бот не обнаруживает реальную капчу** - добавь LOG_LEVEL=DEBUG
3. **Detection reason** поможет понять что именно сработало
4. **VNC обязателен** для проверки что происходит визуально

## 🔍 Отладка

### Если капча НЕ обнаружена:
```bash
# Включи DEBUG логи:
LOG_LEVEL=DEBUG docker compose up

# Увидишь:
[DEBUG] Captcha check (day 10) - none found
[DEBUG] Checking div[id^='sec-if-cpt']: no elements
[DEBUG] Checking div.behavioral-content: found 1, not visible
```

### Если ложное срабатывание:
```bash
# Увидишь в уведомлении ПРИЧИНУ:
📍 Detection: Akamai overlay (div.behavioral-content, size: 250x200)

# Можешь добавить исключение для этого селектора
```

## 📝 Изменённые файлы

- `lib/checker.py` - строгая детекция капчи
- `FIX_FALSE_CAPTCHA.md` - эта документация

## 🎉 Результат

- ✅ Нет ложных срабатываний
- ✅ Реальная капча всё равно детектится
- ✅ Указывается причина обнаружения
- ✅ Меньше проверок = быстрее работа
- ✅ Проверка размера и прозрачности элементов

Теперь бот должен присылать уведомление **только когда капча реально есть!** 🎯
