# Исправление проблемы с dropdown

## 🐛 Проблемы

1. **Адреса перемешивались** - `shuffle(locations)` выбирал случайный адрес
2. **Dropdown закрывался** - задержка перед кликом закрывала выпадающий список
3. **Лишний цикл по очередям** - для каждого адреса есть только 1 очередь

## ✅ Исправлено

### 1. Убран shuffle - адреса по порядку

**Было:**
```python
shuffle(locations)  # Случайный порядок
for location in locations:
    ...
```

**Стало:**
```python
# НЕ перемешиваем - проходим по порядку!
for location in locations:  # 1, 2, 3 по порядку
    ...
```

### 2. Убраны задержки перед кликом по dropdown элементам

**Было:**
```python
def select_location(location_name):
    time.sleep(rand.uniform(2, 5))  # ← Dropdown закрывается!
    element = find_element(...)
    click(element)  # ← Элемент уже не виден
```

**Стало:**
```python
def select_location(location_name):
    # Кликаем СРАЗУ, пока dropdown открыт
    element = WebDriverWait(..., 3).until(
        EC.element_to_be_clickable(...)
    )
    click(element)
```

### 3. Упрощена логика с очередями

**Было:**
```python
for queue in queues:  # Цикл по всем очередям
    for date in dates:
        ...
    # Переоткрывать dropdown...
```

**Стало:**
```python
# Берем единственную очередь для этого адреса
queue = queues[0]
select_queue(queue)

# Проверяем даты
for date in dates:
    ...
```

## 📊 Порядок работы

```
1. Логин ✓
2. Открытие кейса ✓
3. Раскрытие панели ✓
4. Получение списка адресов ✓

5. АДРЕС #1 (Al. Jerozolimskie 28)
   ├─ Выбор адреса ✓
   ├─ Открытие dropdown очереди ✓
   ├─ Получение очереди (1 штука) ✓
   ├─ Клик по очереди СРАЗУ (без задержки) ✓
   ├─ Ожидание календаря ✓
   └─ Проверка дат ✓

6. АДРЕС #2 (pl. Bankowy 3/5)
   ├─ Выбор адреса ✓
   ├─ Открытие dropdown очереди ✓
   └─ ... (повтор)

7. АДРЕС #3 (ul. Marszałkowska 3/5)
   └─ ... (повтор)
```

## 🔧 Изменённые файлы

1. **lib/checker.py**
   - `select_location()` - убрана задержка, добавлен WebDriverWait
   - `select_queue()` - убрана задержка, добавлен WebDriverWait

2. **run_staged_multi_loop_wh.py**
   - Убран `shuffle(locations)`
   - Убран цикл по очередям
   - Упрощена логика - берем единственную очередь

3. **test_checker_simple.py**
   - Убран `shuffle(locations)`
   - Убран цикл по очередям
   - Упрощена логика

## 🧪 Тестирование

```bash
# Запустить Docker
docker compose up

# Логи должны показать:
# [INFO] === Checking location: Al. Jerozolimskie 28, 00-024 Warszawa ===
# [INFO] location selection (Al. Jerozolimskie 28, 00-024 Warszawa)
# [INFO] Found queue: ...
# [INFO] queue selection (...)
# [INFO] waiting for calendar to load...
# [INFO] Calendar loaded successfully
# [INFO] 15 enabled cells in ...
#
# [INFO] === Checking location: pl. Bankowy 3/5 00-950 Warszawa ===
# ...
#
# [INFO] === Checking location: ul. Marszałkowska 3/5, 00-624 Warszawa ===
# ...
```

## ⚠️ Важно

### Dropdown открыт только секунду!
После вызова `expand_locations()` или `expand_queues()`:
- Dropdown **открыт**
- `get_locations()` / `get_queues()` - **читаем список**
- `select_location()` / `select_queue()` - **кликаем СРАЗУ**
- ❌ **НЕ добавляем** `time.sleep()` между чтением и кликом!

### Порядок адресов
- ✅ Адреса проходятся **по порядку** как в списке
- ❌ **НЕ** случайно (shuffle убран)

### Одна очередь = один адрес
- Для каждого адреса система показывает **только одну очередь**
- Берем `queues[0]` - первую и единственную
- Если очередей != 1, логируем warning но продолжаем

## 🎯 Результат

Теперь бот:
1. ✅ Проходит адреса по порядку (1→2→3)
2. ✅ Не падает на выборе адреса/очереди
3. ✅ Кликает пока dropdown открыт
4. ✅ Для каждого адреса берет единственную очередь
5. ✅ Проверяет все даты для каждой комбинации

## 🚀 Запуск

```bash
docker compose up

# Или локально
EMAIL=... PASSWORD=... CASE_ID=... python test_checker_simple.py
```
