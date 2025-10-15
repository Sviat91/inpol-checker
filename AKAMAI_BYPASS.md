# Akamai Bot Detection Bypass Techniques

This document describes the anti-detection techniques implemented to bypass Akamai bot protection on inpol.mazowieckie.pl.

## 🛡️ Implemented Protections

### 1. Browser Fingerprinting Protection

#### WebDriver Detection
```javascript
// Hide navigator.webdriver property
navigator.webdriver → undefined
```

#### Canvas Fingerprinting
- Adds noise to canvas data
- Makes fingerprint unique but consistent per session
- Prevents canvas-based bot detection

#### WebGL Fingerprinting
- Spoofs GPU vendor: "Intel Inc."
- Spoofs GPU renderer: "Intel Iris OpenGL Engine"
- Makes WebGL fingerprint look like real hardware

### 2. Geographic & Language Settings

#### Timezone
- Set to `Europe/Warsaw` (UTC+1)
- Consistent with Polish website location
- `Date.getTimezoneOffset()` returns -60

#### Language Headers
- Primary: `pl-PL` (Polish - Poland)
- Fallback: `pl`, `en-US`, `en`
- Matches typical Polish user profile

### 3. Browser Characteristics

#### User-Agent
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
AppleWebKit/537.36 (KHTML, like Gecko) 
Chrome/131.0.0.0 Safari/537.36
```
- Modern Chrome version
- Windows 10 platform
- Realistic browser signature

#### Chrome Properties
- `window.chrome.runtime` object present
- Plugins array populated
- Permissions API properly spoofed

### 4. Human Behavior Simulation

#### Typing Behavior
- Random delays between keystrokes: 50-150ms
- Simulates natural typing speed
- Varies by character

#### Mouse Movements
- Random movements before clicks
- Offset from element center (humans don't click perfectly)
- Occasional movements while "reading"

#### Delays & Pauses
- **Page load**: 1.5-3.0 seconds (reading time)
- **Between fields**: 0.5-1.2 seconds (thinking time)
- **Before submit**: 0.8-1.5 seconds (verification)
- **After click**: 0.2-0.5 seconds (reaction time)

#### Clicking Patterns
1. Random delay before click (thinking)
2. Move mouse to element with random offset
3. Small pause (0.1-0.3s)
4. Execute click
5. Small delay after click (0.2-0.5s)

#### Reading Simulation
- Random pauses: 1-3 seconds
- Occasional mouse movements (30% chance)
- Mimics human scanning behavior

## 🔧 Implementation Files

### Core Files
- **`lib/browser_factory.py`** - Chrome options & CDP commands
- **`lib/human_behavior.py`** - Human simulation utilities
- **`lib/checker.py`** - Updated to use human behavior

### Key Techniques by File

#### browser_factory.py
```python
# Anti-automation flags
--disable-blink-features=AutomationControlled
excludeSwitches: ['enable-automation']
useAutomationExtension: False

# CDP commands
- Page.addScriptToEvaluateOnNewDocument
- Emulation.setTimezoneOverride
- Emulation.setLocaleOverride
```

#### human_behavior.py
```python
# Main methods
slow_type()           # Realistic typing
human_click()         # Natural clicking
random_mouse_movement()  # Mouse activity
simulate_reading()    # Page scan behavior
```

## 📊 Detection Bypass Checklist

| Detection Method | Our Protection | Status |
|-----------------|----------------|--------|
| `navigator.webdriver` | CDP override → undefined | ✅ |
| User-Agent analysis | Real Chrome 131 signature | ✅ |
| Canvas fingerprinting | Noise injection | ✅ |
| WebGL fingerprinting | GPU spoofing | ✅ |
| Timezone checks | Europe/Warsaw | ✅ |
| Language headers | pl-PL primary | ✅ |
| Typing speed | 50-150ms delays | ✅ |
| Click patterns | Random offsets | ✅ |
| Mouse movements | Random activity | ✅ |
| Reading behavior | 1-3s pauses | ✅ |
| Page interaction | Natural flow | ✅ |

## 🎯 Behavioral Patterns

### Login Flow (Human-like)
```
1. Load page → Wait 1.5-3s (reading)
2. Close cookie banner (if present)
3. Click email field → Type slowly (50-150ms/char)
4. Wait 0.5-1.2s (thinking)
5. Click password field → Type slowly
6. Wait 0.8-1.5s (verification)
7. Move mouse randomly
8. Click submit button
9. Random mouse movement while waiting
```

### Timing Breakdown
- **Total login time**: ~8-15 seconds
- **Human average**: 10-20 seconds
- **Bot typical**: <2 seconds ❌
- **Our simulation**: 8-15 seconds ✅

## 🚀 Usage

The protections are automatically applied when creating a browser instance:

```python
from lib.browser_factory import BrowserFactory

# All anti-detection is built-in
factory = BrowserFactory()
browser = factory.create()

# Human behavior is automatically used in Checker
from lib.checker import Checker
checker = Checker(config)
checker.login()  # Uses human-like behavior
```

## 🔍 Debugging

To verify anti-detection is working:

```javascript
// Check in browser console
console.log(navigator.webdriver);        // → undefined
console.log(navigator.languages);        // → ['pl-PL', 'pl', ...]
console.log(new Date().getTimezoneOffset()); // → -60
```

## ⚠️ Notes

- All delays are randomized to avoid pattern detection
- Mouse movements use natural curves (ActionChains)
- Fingerprinting protection is session-consistent
- Geographic settings match target website location

## 📚 References

- [Akamai Bot Manager](https://www.akamai.com/products/bot-manager)
- [Canvas Fingerprinting](https://browserleaks.com/canvas)
- [WebGL Fingerprinting](https://browserleaks.com/webgl)
- [Selenium Stealth](https://github.com/diprajpatra/selenium-stealth)
