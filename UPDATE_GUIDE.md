# Quick Update Guide

## ✅ Что обновлено

### 1. Селекторы
- Кнопка записи: `Cases.MakeAppointmentAtOffice`
- Все dropdown и календарь работают с актуальными селекторами

### 2. Akamai капча
- Автоматическое обнаружение `iframe[src*='akamai']`
- Telegram уведомление + пауза 2 минуты для ручного решения

### 3. Задержки
- Увеличены с 1 секунды до **2-5 секунд** (случайно)
- Применено ко всем действиям

### 4. Human-like клики
- Все клики через `human_click()` с random offset
- Имитация естественного поведения

### 5. Таймзона
- `TZ=Europe/Warsaw` в docker-compose.yml

## 🚀 Быстрый старт

```bash
# Остановить старый контейнер
docker compose down

# Пересобрать с новым кодом
docker compose build

# Запустить
docker compose up -d

# Смотреть логи
docker compose logs -f inpol-checker
```

## 📊 Ожидаемое поведение

### Скорость работы
- **Было**: ~2-4 секунды на дату
- **Стало**: ~8-20 секунд на дату (медленнее, но безопаснее)

### Капча
Если появится Akamai капча:
1. Получите Telegram уведомление
2. Подключитесь через VNC: `localhost:5900` (пароль: `password`)
3. Решите капчу вручную за 2 минуты
4. Бот продолжит работу

## 🔍 Проверка работы

### Успешные логи
```
INFO - expand appointment panel
INFO - expand list of locations
INFO - location selection (ul. Marszałkowska 3/5...)
INFO - open list of queues
INFO - queue selection (X - applications for TEMPORARY STAY)
INFO - 15 enabled cells in GRUDZIEŃ 2024
INFO - check 17 GRUDZIEŃ 2024
```

### Ошибка селектора
```
ERROR - Appointment button not found
```
→ Сайт изменился, нужно обновить селекторы в `selectors.md`

### Капча обнаружена
```
WARNING - ⚠️ AKAMAI CAPTCHA DETECTED! Please solve manually...
```
→ Подключитесь через VNC и решите капчу

## ⚙️ Настройка

### Уменьшить задержки (рискованно)
В `lib/checker.py` замените:
```python
time.sleep(rand.uniform(2, 5))  # Текущее: 2-5 секунд
```
На:
```python
time.sleep(rand.uniform(1, 3))  # Быстрее: 1-3 секунды
```

### Увеличить время ожидания капчи
В `lib/checker.py` метод `detect_captcha()`:
```python
time.sleep(120)  # Текущее: 2 минуты
```
На:
```python
time.sleep(300)  # 5 минут
```

## 🐛 Troubleshooting

### Бот не находит кнопку записи
**Причина**: Селектор устарел  
**Решение**: 
1. Откройте сайт через VNC
2. Найдите актуальный HTML элемент
3. Обновите селектор в `lib/checker.py` строка 100

### Слишком медленно работает
**Причина**: Задержки 2-5 секунд  
**Решение**: Уменьшите до 1-3 секунд (см. выше)  
**Риск**: Может быть обнаружен как бот

### Капча появляется постоянно
**Причина**: Akamai детектирует автоматизацию  
**Решение**: 
1. Увеличьте задержки до 3-7 секунд
2. Проверьте что HEADLESS=false (GUI режим)
3. Используйте VNC для первого входа вручную

## 📁 Измененные файлы

```
lib/checker.py          ← Основные изменения
docker-compose.yml      ← Добавлена TZ=Europe/Warsaw
CHANGELOG_SELECTORS.md  ← Детальное описание
UPDATE_GUIDE.md         ← Этот файл
```

## 🎯 Что НЕ изменилось

- ✅ Логика проверки дат
- ✅ Алгоритм поиска слотов
- ✅ Telegram уведомления
- ✅ Структура проекта
- ✅ Docker конфигурация (кроме TZ)

## 📞 Поддержка

Если бот не работает:
1. Проверьте логи: `docker compose logs -f`
2. Подключитесь через VNC: `localhost:5900`
3. Проверьте актуальность селекторов в `selectors.md`
4. Обновите селекторы в `lib/checker.py` при необходимости
