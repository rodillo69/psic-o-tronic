# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PSIC-O-TRONIC** is a dark humor psychology game running on ESP32-S3 hardware with MicroPython. Players receive fictional clinical cases via AI (Google Gemini) and must choose the "most psychotic" response as an unethical psychologist. The game features an LCD display, physical buttons, LEDs, and audio feedback.

**Hardware Platform:**
- ESP32-S3 microcontroller
- 20x4 I2C LCD display
- 3 input buttons (Up, Down, Select) with 3 corresponding LEDs
- 1 notification LED
- Piezo speaker on GPIO 9
- I2C on GPIO 1 (SDA) and GPIO 2 (SCL)

**Key Technologies:**
- MicroPython (not standard Python - limited stdlib, ujson instead of json, urequests instead of requests)
- Google Gemini AI API for dynamic case generation
- WiFi connectivity for API access
- OTA updates from GitHub
- Persistent storage in ESP32 flash

## Architecture

### Main Game Loop
`main.py` contains the `PsicOTronic` class which implements a state machine architecture. All game states are defined in the `State` class (lines 56-86). The main loop runs at ~12.5 FPS (`FRAME_DELAY = 0.08`).

**State Flow:**
1. `BOOT` → `WIFI_CHECK` → `WIFI_PORTAL` (if needed) → `INTRO` → `MENU`
2. From `MENU`, players can enter: game modes, stats, settings, OTA updates, credits
3. Game flow: `MODE_SELECT` → `PLAYER_SELECT` → `QUOTA_SELECT` → `PASS_DEVICE` → `FETCHING` → `MESSAGE_ANIM` → `READING` → `CHOOSING` → `FEEDBACK`
4. Special states: `PAUSE` (triggered by UP+DOWN simultaneously), `ERROR`, `OTA_*` states

### LCD Buffer System
To prevent flickering, the game uses a double-buffer approach:
- `lcd_buffer`: Working buffer where content is written
- `lcd_shadow`: Shadow buffer tracking LCD physical state
- `_lcd_render()`: Only writes changed characters to physical LCD (lines 268-274)

**Important:** Always write to buffer first (`_lcd_put`, `_lcd_centered`, `_lcd_clear_buffer`), then call `_lcd_render()` to update display.

### Game Modes Architecture

Three game modes share common base (`GameSession` in `game_modes.py`):

1. **Classic Mode** (`MODE_CLASSIC`): Multiplayer (1-4 players), solve N cases with 3 lives per player
2. **Survival Mode** (`MODE_SURVIVAL`): Single player, survive as long as possible, leaderboard tracking
3. **Career Mode** ("Mi Consulta"): Complex simulation mode with its own state machine in `career_mode.py`

Career mode is significantly more complex with:
- Patient management system (`career_patients.py`)
- Daily scheduling and time simulation (`career_scheduler.py`)
- Achievement/upgrade/mission systems (`career_systems.py`)
- Persistent career state (`career_data.py`)
- Economy, inventory, reputation, crafting, tournaments, etc.

### AI Integration

`gemini_api.py` handles all Gemini API communication:
- `GeminiOracle.get_scenario()`: Generates clinical cases
- Uses `PROMPT_BASE` to define game's dark humor style
- History tracking prevents topic repetition (last 5 themes)
- Cleanses response text to remove leading punctuation
- Error scenarios returned when API fails

**API Configuration:**
- Default API key in `config.py`: `DEFAULT_API_KEY`
- Model: `gemini-2.0-flash` (configurable)
- Prompts are cleaned to remove accents/ñ before sending (MicroPython JSON limitation)

### Configuration & Persistence

`config.py` manages two JSON files in flash:
- `/config.json`: WiFi credentials, API key/model, settings
- `/stats.json`: Game statistics, records, career progress

**Memory Safety:** All file operations wrapped in try/except with error reporting to `error_handler.py`

### WiFi & Connectivity

WiFi managed by `wifi_portal.py`:
1. If no saved credentials, creates AP named "PSIC-O-TRONIC" (no password)
2. Serves captive portal web interface at 192.168.4.1
3. User configures WiFi + optional API key via mobile
4. Credentials saved to `/config.json`

**Portal Features:**
- Responsive CSS design for mobile
- WiFi scanning and selection
- API key configuration
- Career mode progress viewing
- Cancel by holding UP+SELECT buttons

### OTA Updates

`ota_update.py` implements GitHub-based OTA:
- Repository: `rodillo69/psic-o-tronic` (main branch)
- Version tracked in `/version.json`
- Downloads files listed in remote `version.json`
- Accessible from main menu if updates detected
- Can force update or skip

### Error Handling

`error_handler.py` provides centralized error management:
- HTTP error mapping (400, 401, 429, etc.)
- Memory monitoring and warnings
- Error reporting with context
- Persistent error log (optional)

## Development Commands

### Deploying to ESP32

**Prerequisites:**
- Install `ampy` or `mpremote` for file transfer
- Connect ESP32 via USB

**Using ampy:**
```bash
# Upload single file
ampy --port /dev/ttyUSB0 put main.py

# Upload all Python files
for f in *.py; do ampy --port /dev/ttyUSB0 put "$f"; done

# Run without saving
ampy --port /dev/ttyUSB0 run main.py
```

**Using mpremote:**
```bash
# Copy all files
mpremote connect /dev/ttyUSB0 cp *.py :

# Run
mpremote connect /dev/ttyUSB0 run main.py
```

### Testing & Debugging

**REPL Access:**
```bash
# Screen (macOS/Linux)
screen /dev/ttyUSB0 115200

# Minicom
minicom -D /dev/ttyUSB0 -b 115200
```

**Standalone Module Tests:**
Many modules have `if __name__ == "__main__"` blocks for testing:
```python
# Test config system
python config.py  # Won't work - must run on ESP32

# On ESP32 REPL:
import config
config.load_stats()
```

**Memory Monitoring:**
```python
import gc
gc.collect()
gc.mem_free()  # Check available RAM
```

### OTA Update Workflow

1. Update `version.json` with new version number and file list
2. Push changes to `rodillo69/psic-o-tronic` main branch
3. Device checks GitHub for `version.json`
4. Downloads changed files from raw.githubusercontent.com
5. Prompts user to reboot

## Code Style & Conventions

### MicroPython Constraints

**DO:**
- Use `ujson` instead of `json`
- Use `urequests` instead of `requests`
- Use `os.stat()` to check file existence (no `os.path.exists()`)
- Call `gc.collect()` before large operations
- Use simple loops instead of comprehensions when memory-critical

**DON'T:**
- Use f-strings extensively (prefer format() or %)
- Import large modules at global scope
- Create large lists/dicts in memory
- Use standard library modules unavailable in MicroPython

### Text Handling

Custom character mapping in `lcd_chars.py`:
- Custom LCD chars 0-7 defined (heart, empty heart, etc.)
- `convert_text()`: Maps Spanish characters to LCD-safe equivalents
- Special characters: `chr(0)` = filled heart, `chr(1)` = empty heart

### Input Debouncing

Button reads use time-based debouncing (`DEBOUNCE_MS = 280`):
```python
def _get_input(self):
    now = time.ticks_ms()
    if time.ticks_diff(now, self._last_btn_time) < DEBOUNCE_MS:
        return None
    # ... check buttons
```

### Audio System

`audio.py` provides sound effects via PWM:
- `init_audio(pin)`: Initialize speaker
- `play(sound_name)`: Play predefined sound ('boot', 'click', 'beep', 'mensaje', 'correcto', 'incorrecto', 'victoria', 'game_over')
- Non-blocking playback

## Important Patterns

### Adding New Game States

1. Add state constant to `State` class in `main.py`
2. Create handler method: `def _update_<state_name>(self, key):`
3. Register in `state_handlers` dict in `run()` method
4. Implement LCD rendering with buffer system
5. Handle input (UP/DOWN/SELECT) in handler
6. Set `self.state` to transition

### Career Mode Extensions

Career mode is modular - systems are defined in `career_systems.py`:
- Achievements: `LOGROS` dict
- Upgrades: `MEJORAS` dict
- Missions: `MISIONES_DIARIAS`, `MISIONES_SEMANALES`
- Events: `EVENTOS` dict
- Recipes: `RECETAS` dict

Add new content by extending these dicts and implementing corresponding logic.

### AI Prompt Modification

Modify `PROMPT_BASE` in `gemini_api.py` to change case generation behavior:
- Style defined in "ESTILO DE HUMOR" section
- Categories in "CATEGORIAS TEMATICAS"
- Difficulty rules in "REGLAS DE DIFICULTAD"

**Critical:** Response must be valid JSON matching `JSON_TEMPLATE`. The AI generates: theme, sender name, message, 4 options, correct index (0-3), win/lose feedback.

## Hardware Pin Configuration

Defined in `main.py` lines 37-46:
```python
PIN_BTN_UP = 4
PIN_BTN_SELECT = 5
PIN_BTN_DOWN = 6
PIN_LED_UP = 7
PIN_LED_SELECT = 15
PIN_LED_DOWN = 16
PIN_LED_NOTIFY = 17
PIN_SPEAKER = 9
PIN_I2C_SDA = 1
PIN_I2C_SCL = 2
```

### LCD Communication

I2C LCD library: `i2c_lcd.py` (standard MicroPython LCD driver)
- Default address: Auto-detected via `i2c.scan()`
- 400kHz I2C frequency
- 4x20 character display

## Common Issues

**Memory Errors:**
- Call `gc.collect()` before API requests
- Limit string operations in loops
- Close `urequests` responses: `res.close()`

**WiFi Issues:**
- Portal may timeout if no interaction
- Check saved credentials with `config.get_wifi_config()`
- Clear config: `config.clear_wifi_config()`

**API Errors:**
- Default API key may hit rate limits
- Users should configure their own Gemini key via portal
- Check `gemini_api.py` error handling for HTTP status codes

**OTA Failures:**
- Requires stable WiFi during download
- Large files may cause memory issues
- Version format must be semver: "X.Y.Z"

## Repository Structure

```
/
├── main.py              # Main game engine & state machine
├── config.py            # Configuration & stats persistence
├── game_modes.py        # Classic & Survival mode logic
├── career_mode.py       # Career mode main loop (3600+ lines)
├── career_data.py       # Career persistent data management
├── career_patients.py   # Patient generation & AI prompts
├── career_scheduler.py  # Time simulation & scheduling
├── career_systems.py    # Achievements/upgrades/missions/etc
├── gemini_api.py        # Gemini AI integration
├── wifi_portal.py       # Captive portal for setup
├── ota_update.py        # Over-the-air update system
├── error_handler.py     # Centralized error management
├── audio.py             # Sound effects via PWM
├── ui_renderer.py       # UI helper functions
├── lcd_chars.py         # LCD character mapping
├── lcd_api.py           # LCD low-level API
├── i2c_lcd.py           # I2C LCD driver
├── ntp_time.py          # NTP time synchronization
└── version.json         # Version info for OTA
```

## Testing Notes

**Standalone Testing:**
Most modules cannot run on desktop Python due to MicroPython-specific imports. Test on actual ESP32 hardware or use MicroPython Unix port.

**WiFi Testing:**
Portal can be tested by monitoring serial output while connecting phone to "PSIC-O-TRONIC" AP.

**API Testing:**
Run `gemini_api.py` standalone on ESP32 REPL after WiFi configured.
