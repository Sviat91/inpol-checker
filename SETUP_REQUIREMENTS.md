# Требования для полной работы inpol-checker бота

## ✅ Обновлено в последней версии

### Селекторы (обновлены согласно selectors.md)

1. **Кнопка раскрытия "Umów się na wizytę w urzędzie"**
   - ✅ Мультиязычный XPath работает для EN/PL/UA/RU
   - ✅ Использует translate() для регистронезависимого поиска
   - ✅ Находит кнопку через заголовок h3 на любом языке

2. **Dropdown локации (mat-select)**
   - ✅ Селектор `//mat-select[@name="location"]`
   - ✅ WebDriverWait для ожидания видимости
   - ✅ Human-like клики через HumanBehavior

3. **Dropdown очереди (mat-select)**
   - ✅ Селектор `//mat-select[@name="queueName"]`
   - ✅ WebDriverWait для ожидания видимости
   - ✅ Human-like клики

4. **Календарь (Material Design)**
   - ✅ Кликабельные даты: `//div[contains(@class,"mat-calendar-body-cell-content")]`
   - ✅ Навигация вперёд: `//button[contains(@class,"mat-calendar-next-button")]`
   - ✅ Навигация назад: `//button[contains(@class,"mat-calendar-previous-button")]`
   - ✅ Текущий месяц/год: `//button[contains(@class,"mat-calendar-period-button")]/span`

5. **Временные слоты**
   - ✅ Контейнер: `//div[@class="reservation__hours"]//div[@class="tiles tiles--hours"]//div[@class="row"]`
   - ✅ Отдельные слоты: `//*[contains(@class,"tile")]`
   - ✅ Двойная проверка: сначала контейнер, потом слоты

6. **Akamai Captcha**
   - ✅ Детект капчи через iframe `[src*='akamai']`
   - ✅ Пауза 2 минуты для ручного решения
   - ✅ Уведомление в Telegram
   - ✅ Проверка перед каждым месяцем календаря

7. **Человекоподобное поведение**
   - ✅ Задержки 2-5 секунд между действиями
   - ✅ Медленная печать через HumanBehavior.slow_type()
   - ✅ Случайные движения мыши
   - ✅ Плавный скролл элементов

## 🔧 Необходимые переменные окружения

### Обязательные
```bash
EMAIL=your-email@example.com          # Email для входа
PASSWORD=your-password                 # Пароль
CASE_ID=123456                        # ID вашего кейса
```

### Опциональные
```bash
# Telegram уведомления (настоятельно рекомендуется)
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz  # Bot token от @BotFather
TELEGRAM_CHAT_ID=123456789                           # Ваш chat ID

# Настройки работы
MONTHS_TO_CHECK=3                      # Сколько месяцев вперёд проверять (по умолчанию 3)
SLEEP_INTERVAL=300                     # Интервал между проверками в секундах (по умолчанию 300 = 5 мин)
HEADLESS=false                         # Headless режим (true/false, по умолчанию false)
LOG_LEVEL=INFO                         # Уровень логирования (DEBUG/INFO/WARNING/ERROR)

# Chrome profile (для сохранения сессий)
PROFILE_PATH=/path/to/chrome/profile   # Путь к профилю Chrome (опционально)
```

## 🐳 Docker setup (рекомендуется)

### 1. Создайте .env файл
```bash
cp .env.example .env
# Отредактируйте .env с вашими данными
```

### 2. Запустите контейнеры
```bash
docker compose up --remove-orphans -d
```

### 3. Доступ к VNC (для просмотра браузера)
- **URL**: http://localhost:6080
- **Password**: `secret` (можно изменить в docker-compose.yml)
- Полезно для:
  - Ручного решения капчи
  - Отладки селекторов
  - Визуального контроля работы

## 🔍 Проверка работы

### Тест proxy и браузера
```bash
python test-proxy.py
```

### Запуск с DEBUG логами
```bash
LOG_LEVEL=DEBUG EMAIL=... PASSWORD=... CASE_ID=... python run_staged_multi_loop_wh.py
```

### Запуск в рабочие часы (7:00-23:00)
```bash
EMAIL=... PASSWORD=... CASE_ID=... python run_staged_multi_loop_wh.py
```

## ⚙️ Systemd service (для автозапуска)

```bash
# 1. Скопируйте unit файл
sudo cp systemd.service /etc/systemd/system/inpol-checker.service

# 2. Отредактируйте пути и переменные
sudo nano /etc/systemd/system/inpol-checker.service

# 3. Активируйте сервис
sudo systemctl daemon-reload
sudo systemctl enable inpol-checker
sudo systemctl start inpol-checker

# 4. Проверьте статус
sudo systemctl status inpol-checker

# 5. Логи
sudo journalctl -u inpol-checker -f
```

## 📋 Что проверяет бот

1. **Логин** → Вход в систему с вашими учетными данными
2. **Открытие кейса** → Переход на страницу вашего дела
3. **Раскрытие панели** → Клик по "Umów się na wizytę w urzędzie" (любой язык)
4. **Выбор локации** → Перебор всех доступных адресов
5. **Выбор очереди** → Выбор нужной очереди для визы
6. **Проверка календаря** → Поиск доступных дат (3+ месяцев вперед)
7. **Поиск слотов** → Проверка наличия временных окон
8. **Уведомление** → Telegram сообщение при находке слота

## 🚨 Важные моменты

### Антибот защита
- ✅ Бот использует человекоподобное поведение
- ✅ Случайные задержки 2-6 секунд
- ✅ Медленная печать с вариациями
- ✅ Случайные движения мыши
- ⚠️ **Не запускайте слишком часто** (рекомендуется 5+ минут между проверками)
- ⚠️ **Используйте Chrome profile** для сохранения cookies

### Akamai Captcha
- 🔍 Автоматически детектируется
- ⏸️ Бот ставит на паузу 2 минуты
- 📱 Вы получите Telegram уведомление
- 🖥️ Решите капчу в VNC (http://localhost:6080)
- ✅ Бот продолжит работу автоматически

### Telegram уведомления
Настоятельно рекомендуется настроить Telegram бота:

1. Создайте бота через @BotFather
2. Получите token (формат: `123456789:ABCdefGHI...`)
3. Получите свой chat_id (можно через @userinfobot)
4. Добавьте в .env:
   ```
   TELEGRAM_TOKEN=your-token
   TELEGRAM_CHAT_ID=your-chat-id
   ```

## 🔄 Режим работы

### Основной цикл (run_staged_multi_loop_wh.py)
- Работает только в рабочие часы: **7:00 - 23:00**
- Вне рабочих часов спит до 7:00
- Проверяет слоты каждые 5 минут (настраивается через SLEEP_INTERVAL)
- Автоматически перезапускается при ошибках

### Проверка одной локации
```python
from lib.checker import Checker
from lib.checker_config import CheckerConfig

config = CheckerConfig(...)
checker = Checker(config)

# Проверить локацию #0
checker.check_one_location(0)
```

## 📝 Логи и отладка

### Уровни логирования
- **DEBUG**: Подробная информация о каждом действии, полезно для отладки селекторов
- **INFO**: Основные действия и прогресс
- **WARNING**: Предупреждения (неправильные списки, капча)
- **ERROR**: Ошибки входа, недоступность страниц

### Полезные DEBUG сообщения
```
DEBUG:root:Looking for appointment accordion button with multi-language selector
DEBUG:root:Clicking accordion button via JavaScript
DEBUG:root:Found 15 enabled cells in November 2024
DEBUG:root:Container found but no time slots for 17
```

## 🎯 Следующие шаги

1. ✅ Обновлены все селекторы
2. ✅ Добавлена мультиязычность
3. ✅ Улучшена детекция слотов
4. ✅ Добавлена капча детекция
5. ✅ Человекоподобное поведение

### Возможные улучшения

- [ ] Автоматическое бронирование слота (сейчас только уведомление)
- [ ] Поддержка нескольких кейсов одновременно
- [ ] Web dashboard для мониторинга
- [ ] Статистика по найденным слотам
- [ ] Email уведомления (сейчас только Telegram)
- [ ] Proxy rotation для обхода rate limits

## 🆘 Troubleshooting

### Бот не находит кнопку раскрытия
- Проверьте, что используется последняя версия с мультиязычным XPath
- Включите DEBUG логи: `LOG_LEVEL=DEBUG`
- Проверьте в VNC, что кнопка действительно присутствует

### Бот не видит слоты
- Селекторы обновлены для Material Design компонентов
- Проверяется сначала контейнер, потом сами слоты
- DEBUG логи покажут "Container found but no time slots for..."

### Капча блокирует работу
- Настройте VNC доступ
- Бот автоматически уведомит вас
- Решите капчу вручную в течение 2 минут
- Используйте больший SLEEP_INTERVAL (10+ минут)

### Chrome падает/зависает
- Используйте Docker контейнер (стабильнее)
- Проверьте оперативную память
- Попробуйте HEADLESS=true режим

## 📞 Поддержка

При проблемах:
1. Включите DEBUG логирование
2. Проверьте VNC визуально
3. Проверьте актуальность селекторов в selectors.md
4. Создайте issue с логами и скриншотами
