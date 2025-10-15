# Repository Guidelines

## Project Structure & Module Organization
The automation core lives in `lib/`, which holds Selenium-based helpers for browser control, scheduling, and messaging. `run_staged_multi_loop_wh.py` orchestrates the working-hours loop and slot checking, while `test-proxy.py` provides a quick manual probe for browser/VNC setups. Support assets such as `Dockerfile`, `docker-compose.yml`, and `systemd.service` enable containerized or service deployments.

## Build, Test, and Development Commands
Install dependencies with `pip install -r requirements.txt` and launch the checker via `EMAIL=… PASSWORD=… CASE_ID=… python run_staged_multi_loop_wh.py`. Use `docker compose up --remove-orphans` after creating a `.env` file to run the packaged Chromium/VNC stack. Run `python test-proxy.py` to confirm the browser setup and profile before long sessions.

## Coding Style & Naming Conventions
Follow idiomatic Python 3 practices: four-space indentation, black-style line wrapping (~88 chars), and descriptive snake_case for functions and variables. Prefer f-strings for logging, keep Selenium locators centralized in `Checker`, and store constants (environment variable names, timeouts) in uppercase. When touching shared utilities, add concise comments only where control flow is non-obvious.

## Testing Guidelines
There is no automated test suite yet; rely on targeted scripts and local dry runs. Use `LOG_LEVEL=DEBUG python run_staged_multi_loop_wh.py` to observe scheduling behaviour, and capture Telegram notifications via the console messenger when tokens are absent. New features should include a lightweight harness under `tests/` or extend `test-proxy.py` to exercise browser, login, or scheduling edges.

## Commit & Pull Request Guidelines
Recent commits favour short, action-oriented subjects (e.g., “fix orphans”, “Update README.md”); continue with concise imperative phrasing and group related changes. Each pull request should include: purpose summary, manual verification steps (commands run, environment variables used), and any screenshots of browser output when UI behaviour changes. Link issues when available and call out risks such as updated selectors or timing adjustments.

## Configuration & Secrets
Required runtime variables are `EMAIL`, `PASSWORD`, and `CASE_ID`; optional overrides such as `MONTHS_TO_CHECK`, `SLEEP_INTERVAL`, and `HEADLESS` tune behaviour without code changes. Persist secrets in local `.env` files or secure secret stores—never commit them. Set `PROFILE_PATH` when you need a reusable Chrome profile, and confirm Telegram credentials (`TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`) before enabling production alerts.

