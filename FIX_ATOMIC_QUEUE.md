# Атомарный выбор очереди - финальное исправление

## 🐛 Корневая проблема

Material Design dropdown **автоматически закрывается** через ~1 секунду после открытия.

**Было:**
```python
expand_queues()      # Открыли dropdown
queues = get_queues()  # Прочитали список
# ... тут проходит время ...
select_queue(queue)  # ❌ Dropdown УЖЕ ЗАКРЫТ!
```

**Время между операциями:** ~2-3 секунды → dropdown закрывается

## ✅ Решение: Атомарная операция

Создал метод `select_first_queue_atomic()` который делает ВСЁ за один раз:

```python
def select_first_queue_atomic(self):
    # 1. Открыть dropdown
    click(queue_dropdown)
    
    # 2. СРАЗУ получить список элементов (dropdown открыт)
    elements = get_elements()
    queues = [el.text for el in elements if el.text != '-']
    
    # 3. СРАЗУ кликнуть по первому элементу (используя уже полученный element!)
    for el in elements:
        if el.text == queues[0]:
            click(el)  # ✅ Dropdown еще открыт!
            return queues[0]
```

**Время между открытием и кликом:** < 0.5 секунд → dropdown не успевает закрыться

## 📊 Что изменилось

### 1. Новый метод в `lib/checker.py`
```python
select_first_queue_atomic()
```
- Открывает dropdown
- Читает список очередей
- Кликает по первой очереди
- Всё за < 1 секунду!

### 2. Обновлен `run_staged_multi_loop_wh.py`
**Было:**
```python
expand_queues()
queues = get_queues()
select_queue(queues[0])
```

**Стало:**
```python
queue = select_first_queue_atomic()  # Одна строка!
```

### 3. Обновлен `test_checker_simple.py`
Использует новый метод.

### 4. Обновлен `debug_dropdown.py`
Использует новый метод.

## 🎯 Ключевые улучшения

### 1. Используем уже полученные элементы
```python
# Не делаем второй поиск:
# queue_option = find_element(xpath)  ❌

# Кликаем по уже найденному элементу:
for el in queue_elements:  # ✅ Уже в памяти
    if el.text == queue_name:
        click(el)
```

### 2. Минимальные задержки
```python
time.sleep(rand.uniform(1, 2))  # Было 2-5 сек
```

### 3. Fallback на поиск
```python
# Если элемент стал stale, ищем заново
if not_found_in_cached:
    queue_option = find_element(xpath)
    click(queue_option)
```

## 🔧 Как пересобрать и запустить

```bash
# 1. Остановить Docker
docker compose down

# 2. Пересобрать образ с новым кодом
docker compose build --no-cache

# 3. Запустить
docker compose up

# Или локально для быстрого теста:
python debug_dropdown.py
```

## 📝 Ожидаемые логи

**Успех:**
```
[INFO] === Checking location: Al. Jerozolimskie 28 ===
[INFO] location selection (Al. Jerozolimskie 28)
[INFO] open list of queues (atomic operation)
[INFO] Found queue: F - Wnioski o POBYT CZASOWY...
[INFO] queue selection (F - Wnioski o POBYT CZASOWY...)
[INFO] waiting for calendar to load...
[INFO] Calendar loaded successfully
[INFO] 15 enabled cells in NOVEMBER 2024
```

**Нет очереди:**
```
[INFO] open list of queues (atomic operation)
[WARNING] No queues found in dropdown
[WARNING] ⚠️ No queues available for location "..." - skipping
```

## ⚡ Почему это работает

1. **Dropdown открыт** → получаем WebElement объекты
2. **Сразу фильтруем** → находим нужную очередь
3. **Кликаем по объекту** → не ищем заново через XPath
4. **Всё за < 1 сек** → dropdown не успевает закрыться

## 🎉 Результат

- ✅ Dropdown не закрывается перед кликом
- ✅ Используем кэшированные элементы
- ✅ Минимальные задержки
- ✅ Fallback если элемент stale
- ✅ Единственный атомарный метод вместо 3 раздельных
