# Fix: docker-entrypoint line endings

## Проблема
```
exec /usr/bin/docker-entrypoint: no such file or directory
```

## Причина
Windows Git конвертирует LF → CRLF, что ломает bash скрипты в Linux контейнерах.

## Решение

### 1. Создан .gitattributes
```
docker-entrypoint text eol=lf
*.sh text eol=lf
```

### 2. Пересборка образа
```bash
# Остановить контейнер
docker compose down

# Пересобрать с нуля
docker compose build --no-cache

# Запустить
docker compose up -d

# Проверить логи
docker compose logs -f
```

## Ожидаемый результат
```
Starting Xvfb...
Waiting for Xvfb to initialize...
Starting Fluxbox window manager...
Waiting for Fluxbox to initialize...
Starting x11vnc on port 5900...
Environment configured:
  DISPLAY=:99
  CHROMEDRIVER_PATH=/usr/bin/chromedriver
  CHROME_BINARY=/usr/bin/chromium
  HEADLESS=false
  Window Manager: Fluxbox
Starting application: python run_staged_multi_loop_wh.py
```

## Если проблема повторяется

### Вручную исправить окончания строк
```bash
# В PowerShell
(Get-Content docker-entrypoint -Raw).Replace("`r`n", "`n") | Set-Content docker-entrypoint -NoNewline

# Или в Git Bash
dos2unix docker-entrypoint
```

### Проверить окончания строк
```bash
# В Git Bash
file docker-entrypoint
# Должно быть: "ASCII text" (не "ASCII text, with CRLF line terminators")
```

## Коммит изменений
```bash
git add .gitattributes
git add --renormalize docker-entrypoint
git commit -m "fix: docker-entrypoint line endings (LF)"
git push
```
