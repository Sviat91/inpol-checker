# Docker Deployment Guide

## Quick Start

```bash
# 1. Create .env file with your credentials
cat > .env << EOF
EMAIL=your.email@example.com
PASSWORD=your_password
CASE_ID=your_case_id
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
EOF

# 2. Build and run
docker compose build
docker compose up -d

# 3. View logs
docker compose logs -f

# 4. Connect via VNC
# Address: localhost:5900
# Password: password
```

## Environment Variables

### Required
- `EMAIL` - Login at inpol.mazowieckie.pl
- `PASSWORD` - Password at inpol
- `CASE_ID` - Case ID from URL

### Optional
- `TELEGRAM_TOKEN` - Telegram bot token (for notifications)
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID
- `HEADLESS` - Run in headless mode (default: `true`)
- `MONTHS_TO_CHECK` - Number of months to check (default: `5`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `SLEEP_INTERVAL` - Check interval (default: `15m`)
- `SLEEP_INTERVAL_JITTER` - Random jitter (default: `3m`)

## Technical Details

- **Base Image**: `python:3.12-slim-bookworm`
- **Browser**: Chromium + ChromeDriver
- **Display**: Xvfb (virtual framebuffer)
- **VNC**: Port 5900 for remote viewing
- **Window Manager**: Fluxbox

## Troubleshooting

### Build fails
```bash
# Clean rebuild
docker compose down -v
docker compose build --no-cache
```

### Container crashes
```bash
# Check logs
docker compose logs

# Interactive shell
docker compose run --rm inpol-checker bash
```

### VNC not working
Ensure port 5900 is not blocked by firewall.
