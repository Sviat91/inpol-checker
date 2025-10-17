# Улучшенная детекция Akamai капчи

## 🚨 Проблема

Akamai капча появлялась но бот ее не замечал, продолжал работать как ни в чем не бывало.

**Старая детекция:**
- Искала только `iframe[src*='akamai']`
- Капча часто появляется как **overlay div**, а не iframe
- Проверялась редко - только перед каждым месяцем

## ✅ Решение

### 1. Множественные методы детекции

```python
def detect_captcha():
    # Method 1: Akamai iframe
    if iframe[src*='akamai']:
        captcha_detected = True
    
    # Method 2: Akamai div overlay
    if div[id*='sec-if-cpt'] or div[id*='sec-cpt']:
        if div.is_displayed():
            captcha_detected = True
    
    # Method 3: Text на странице
    if 'potwierdź, że jesteś człowiekiem' in page_text:
        if captcha_button.exists():
            captcha_detected = True
    
    # Method 4: Captcha checkbox
    if input[type='checkbox'][id*='robot']:
        captcha_detected = True
```

### 2. Частая проверка

**Точки проверки:**
- ✅ После входа в систему
- ✅ После выбора адреса
- ✅ **После выбора очереди** (новое!)
- ✅ Перед каждым новым месяцем
- ✅ **Каждые 5 дат** (новое!)

**Результат:** Капча обнаруживается в течение 10-30 секунд

### 3. Telegram уведомление

**Формат сообщения:**
```
🚨 AKAMAI CAPTCHA DETECTED!

⏰ Bot paused for 2 minutes
🔗 VNC: http://localhost:6080 (password: password)
✅ Please solve the captcha manually

⚠️ If not solved in 2 min, bot will try to continue
```

**Что происходит:**
1. Бот обнаруживает капчу
2. Отправляет уведомление в Telegram
3. Логирует в консоль: `CAPTCHA DETECTED - pausing for 2 minutes`
4. Ждет 120 секунд
5. Продолжает работу

## 📋 Селекторы Akamai капчи

### Overlay DIV
```css
div[id*='sec-if-cpt']
div[id*='sec-cpt']
div.behavioral-content
```

### Iframe
```css
iframe[src*='akamai']
```

### Текст (мультиязычный)
- 🇵🇱 "Potwierdź, że jesteś człowiekiem"
- 🇵🇱 "Nie jestem robotem"
- 🇬🇧 "Confirm you are human"
- 🇬🇧 "I'm not a robot"
- 🇬🇧 "Verify you are human"

### Checkbox
```css
input[type='checkbox'][id*='robot']
input[type='checkbox'][class*='captcha']
```

## 🎯 Пример работы

### Когда капча НЕ обнаружена:
```
[INFO] check 20 PAŹ 2025
[INFO] check 21 PAŹ 2025
[INFO] check 22 PAŹ 2025
[INFO] check 23 PAŹ 2025
[INFO] check 24 PAŹ 2025
[DEBUG] Captcha check (day_counter=5) - none found
```

### Когда капча ОБНАРУЖЕНА:
```
[INFO] check 20 PAŹ 2025
[INFO] check 21 PAŹ 2025
[DEBUG] Captcha detected: Akamai div overlay found
[WARNING] CAPTCHA DETECTED - pausing for 2 minutes
[INFO] Waiting 120 seconds for captcha to be solved manually...

📱 Telegram: "🚨 AKAMAI CAPTCHA DETECTED! ..."

[через 2 минуты]
[INFO] Resuming after captcha wait period
[INFO] check 22 PAŹ 2025
```

## 🔧 Как решить капчу вручную

### Через VNC:
1. Открой браузер: http://localhost:6080
2. Пароль: `password`
3. Увидишь popup с капчей
4. Поставь галочку "Nie jestem robotem"
5. Подожди 2-5 секунд
6. Капча исчезнет
7. Бот продолжит работу

### Через Telegram:
1. Получишь уведомление: 🚨 AKAMAI CAPTCHA DETECTED!
2. Открой VNC (ссылка в сообщении)
3. Реши капчу (галочка)
4. Бот автоматически продолжит через 2 мин

## ⚙️ Конфигурация

### Настройка Telegram (ОБЯЗАТЕЛЬНО):
```bash
# В .env файле:
TELEGRAM_TOKEN=your_bot_token_from_@BotFather
TELEGRAM_CHAT_ID=your_chat_id_from_@userinfobot
```

**Без Telegram:**
- Уведомления только в консоли
- Придется постоянно смотреть логи
- **Не рекомендуется для продакшена**

### Время паузы:
По умолчанию: **120 секунд (2 минуты)**

Можно изменить в `lib/checker.py`:
```python
time.sleep(120)  # Change this number (seconds)
```

## 📊 Статистика проверок

**На полный цикл (3 адреса × 5 месяцев):**
- ~150 проверок дат
- ~30 проверок капчи (каждая 5-я дата)
- ~6 проверок перед месяцами
- ~3 проверки после выбора очереди

**Итого:** ~40 проверок капчи за цикл

**Время обнаружения:** 10-30 секунд после появления

## 🚀 Активация

### Пересборка Docker:
```bash
docker compose down
docker compose build
docker compose up
```

### Локальный запуск:
```bash
EMAIL=... PASSWORD=... CASE_ID=... \
TELEGRAM_TOKEN=... TELEGRAM_CHAT_ID=... \
python test_checker_simple.py
```

## 📝 Логи

### DEBUG уровень:
```bash
LOG_LEVEL=DEBUG python test_checker_simple.py
```

Увидишь:
```
[DEBUG] Captcha detected: Akamai iframe found
[DEBUG] Captcha detected: Akamai div overlay found
[DEBUG] Captcha detected: keyword "nie jestem robotem" found
[DEBUG] Captcha check (day_counter=5) - none found
```

## ⚠️ Важно

1. **Telegram обязателен** для продакшна
2. **VNC обязателен** для решения капчи
3. **2 минуты** достаточно для решения простой капчи
4. Если капча сложная (картинки) - может потребоваться больше времени
5. Бот продолжит работу даже если капча не решена (может упасть позже)

## 🎯 Следующий шаг

После тестирования можно добавить:
- **AntiCaptcha API** - автоматическое решение
- **2Captcha API** - альтернатива
- **Более длинная пауза** - для сложных капч
- **Retry логика** - повторная проверка после решения

Но сначала протестируем с ручным решением! 🚀
