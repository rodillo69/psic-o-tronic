# MEJORAS SUGERIDAS PARA PSIC-O-TRONIC

**Fecha:** 2024-12-04
**Versión actual:** 1.3
**Estado:** Proyecto 100% funcional

---

## 🎯 MEJORAS PRIORITARIAS (Rápidas y de Alto Impacto)

### 1. 🔄 **Watchdog Timer** (Anti-freeze)
**Impacto:** ALTO | **Esfuerzo:** BAJO (30 min)

**Problema:** Si el ESP32 se cuelga, queda bloqueado hasta reset manual.

**Solución:**
```python
from machine import WDT

# En __init__:
self.wdt = WDT(timeout=10000)  # 10 segundos

# En main loop (línea ~1313):
self.wdt.feed()  # Reset watchdog cada frame
```

**Beneficio:** Auto-reinicio automático si el juego se congela.

---

### 2. 💾 **Backup Automático de Saves**
**Impacto:** ALTO | **Esfuerzo:** BAJO (20 min)

**Problema:** Si se corrompe `/stats.json` o `/career_save.json`, se pierden todos los datos.

**Solución:**
```python
# En config.py, añadir:
def backup_file(filename):
    """Crea backup con timestamp"""
    try:
        import os
        backup_name = filename + '.bak'
        # Copiar archivo actual a backup
        with open(filename, 'r') as src:
            data = src.read()
        with open(backup_name, 'w') as dst:
            dst.write(data)
    except:
        pass

# Llamar antes de save_stats() y save_career()
```

**Beneficio:** Recuperación de datos en caso de corrupción.

---

### 3. 🐛 **Modo Debug con Log**
**Impacto:** MEDIO | **Esfuerzo:** BAJO (30 min)

**Problema:** Difícil diagnosticar problemas en producción sin logs.

**Solución:**
```python
# Crear debug_config.json:
{
    "debug_mode": false,
    "log_to_file": false,
    "verbose_api": false
}

# En main.py:
DEBUG_MODE = load_debug_config()

def debug_log(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")
        # Opcional: escribir a /debug.log

# Usar en lugares críticos:
debug_log(f"State transition: {self.prev_state} -> {self.state}")
debug_log(f"API call: {scenario}")
```

**Beneficio:** Diagnóstico rápido de problemas, desactivable en producción.

---

### 4. ⚡ **Indicador de Rate Limiting API**
**Impacto:** MEDIO | **Esfuerzo:** BAJO (20 min)

**Problema:** Usuario no sabe cuándo puede volver a jugar si alcanza límite API.

**Solución:**
```python
# En gemini_api.py:
class GeminiOracle:
    def __init__(self):
        self.last_call_time = 0
        self.cooldown_seconds = 0

    def get_scenario(self):
        # Si 429 (rate limit):
        if status == 429:
            self.cooldown_seconds = 60  # Esperar 1 minuto
            self.last_call_time = time.time()
            self.last_error = f"Límite API. Espera {self.cooldown_seconds}s"

# En main.py estado ERROR:
if oracle.cooldown_seconds > 0:
    elapsed = time.time() - oracle.last_call_time
    remaining = max(0, oracle.cooldown_seconds - int(elapsed))
    self._lcd_put(0, 2, f"Espera: {remaining}s")
```

**Beneficio:** Usuario sabe exactamente cuánto esperar.

---

### 5. 🎮 **Easter Egg: Código Konami**
**Impacto:** BAJO | **Esfuerzo:** BAJO (15 min)

**Diversión:** ALTA 😄

**Solución:**
```python
# En __init__:
self.konami_sequence = []
self.konami_code = ['UP', 'UP', 'DOWN', 'DOWN', 'UP', 'DOWN', 'UP', 'DOWN']

# En _get_input():
if cmd:
    self.konami_sequence.append(cmd)
    if len(self.konami_sequence) > 8:
        self.konami_sequence.pop(0)

    if self.konami_sequence == self.konami_code:
        self._activate_konami()

def _activate_konami(self):
    # Vidas infinitas, modo dios, etc
    play_sound('victoria')
    self._lcd_lines([
        "CODIGO KONAMI!",
        "Modo Dios ON",
        "Vidas: INFINITAS",
        ""
    ])
    self.god_mode = True
```

**Beneficio:** Diversión, testing más fácil.

---

## 🚀 MEJORAS DE NIVEL MEDIO (Más trabajo, más valor)

### 6. 📊 **Estadísticas Avanzadas**
**Impacto:** MEDIO | **Esfuerzo:** MEDIO (2 horas)

**Mejora:** Pantalla de estadísticas más completa:

```
=== ESTADISTICAS ===
Partidas: 42
Casos OK: 156 (87%)
Casos KO: 23 (13%)
-------------------
Racha máx: 15 (MGC)
Survival: 23 (MGC)
-------------------
Tiempo total: 4h 23m
Favoritos: Classic
```

**Implementación:**
- Añadir campos a `stats.json`: `casos_fallados`, `tiempo_jugado`, `modo_favorito`
- Pantalla multi-página con scroll
- Gráficos ASCII simples (barras)

---

### 7. 🏆 **Sistema de Achievements Visuales**
**Impacto:** MEDIO | **Esfuerzo:** MEDIO (1.5 horas)

**Mejora:** Mostrar achievements desbloqueados con animación.

```python
ACHIEVEMENTS = {
    'first_win': {'icon': '★', 'name': 'Primera victoria'},
    'perfectionist': {'icon': '♦', 'name': 'Racha de 10'},
    'survivor': {'icon': '◆', 'name': 'Survival +20'},
    'workaholic': {'icon': '⚡', 'name': 'Career 100 casos'},
}

# Cuando se desbloquea:
def _show_achievement_popup(achievement_id):
    play_sound('victoria')
    # Animación de achievement desbloqueado
    for i in range(20):
        self._lcd_clear()
        if i % 2 == 0:
            icon = ACHIEVEMENTS[achievement_id]['icon']
            name = ACHIEVEMENTS[achievement_id]['name']
            self._lcd_centered(1, f"{icon} {name} {icon}")
        self._lcd_render()
        time.sleep(0.1)
```

---

### 8. ⚙️ **Configuración Avanzada**
**Impacto:** MEDIO | **Esfuerzo:** MEDIO (2 horas)

**Añadir menú de configuración:**

```
CONFIG > Pantalla
├── Brillo LCD (0-100%)
├── Contraste (0-10)
└── Screensaver (1-10 min)

CONFIG > Audio
├── Volumen (0-100%)
├── Efectos ON/OFF
└── Tono test

CONFIG > Juego
├── Velocidad texto (1-5)
├── Debounce (100-500ms)
└── Confirmar salida (ON/OFF)
```

**Implementación:**
- Estado `CONFIG_MENU` con sub-menús
- Persistir en `config.json`
- Aplicar ajustes en tiempo real

---

### 9. 🎓 **Tutorial Interactivo Primera Vez**
**Impacto:** ALTO | **Esfuerzo:** MEDIO (2 horas)

**Problema:** Usuario nuevo puede estar confundido.

**Solución:**
```python
# En config.json:
"first_time": true

# Si first_time en boot:
def _run_tutorial(self):
    steps = [
        ("Bienvenido!", "Pulsa botones para", "navegar menus", "[OK] Siguiente"),
        ("Este es el menu", "principal", "Usa [^][v] para", "navegar"),
        # ... más pasos ...
    ]
    for step in steps:
        # Mostrar paso
        # Esperar OK
        # Highlight de controles con LEDs
```

**Beneficio:** Onboarding suave para nuevos usuarios.

---

## 🔥 MEJORAS AVANZADAS (Más ambiciosas)

### 10. 📡 **Modo Multijugador Online**
**Impacto:** ALTO | **Esfuerzo:** ALTO (1 semana)

**Concepto:**
- Servidor simple (Flask/FastAPI)
- Matchmaking básico
- Compartir mismo caso
- Ver quién responde más rápido

**Arquitectura:**
```
ESP32 ─────► Servidor HTTP ◄───── ESP32
      GET /match             otro jugador
      POST /answer
      GET /result
```

---

### 11. 🌐 **Portal Web para Estadísticas**
**Impacto:** MEDIO | **Esfuerzo:** ALTO (4-5 horas)

**Mejora:** Extender `wifi_portal.py` con más páginas:

```
http://192.168.4.1/
├── /config     (ya existe)
├── /stats      (nuevo) - Ver estadísticas
├── /career     (nuevo) - Ver progreso carrera
├── /logs       (nuevo) - Ver logs debug
└── /update     (nuevo) - Forzar OTA check
```

**Beneficio:** Gestión completa desde móvil sin LCD.

---

### 12. 🎨 **Temas Visuales**
**Impacto:** BAJO | **Esfuerzo:** MEDIO (2 horas)

**Concepto:** Personalizar caracteres LCD y estilos:

```python
THEMES = {
    'classic': {'heart': chr(0), 'empty': chr(1), ...},
    'retro': {'heart': '♥', 'empty': '♡', ...},
    'cyber': {'heart': '◆', 'empty': '◇', ...},
}

# Cambiar en opciones
set_theme('cyber')
```

---

### 13. 🔊 **Melodías Custom**
**Impacto:** BAJO | **Esfuerzo:** MEDIO (1-2 horas)

**Mejora:** Melodías en vez de beeps simples:

```python
MELODIES = {
    'victory': [(440, 200), (554, 200), (659, 400)],  # A, C#, E
    'game_over': [(392, 300), (349, 300), (330, 600)],  # G, F, E
}

def play_melody(name):
    for freq, duration in MELODIES[name]:
        self.audio.freq(freq)
        self.audio.duty(512)
        time.sleep_ms(duration)
        self.audio.duty(0)
```

---

### 14. 💾 **Sistema de Saves Multiple**
**Impacto:** MEDIO | **Esfuerzo:** MEDIO (2 horas)

**Concepto:** 3 slots de guardado para Career Mode:

```
CARRERA
├── Slot 1: Dr. Pérez - Nivel 5
├── Slot 2: Dr. Smith - Nivel 12
└── Slot 3: [VACIO]

[OK] Jugar [^v] Cambiar
```

---

### 15. 🎲 **Modo Desafío Diario**
**Impacto:** MEDIO | **Esfuerzo:** ALTO (4 horas)

**Concepto:**
- Caso del día (seed basado en fecha)
- Todos los jugadores tienen el mismo caso
- Ranking global (requiere servidor)
- Recompensas especiales

---

## 🛠️ MEJORAS TÉCNICAS (Para devs)

### 16. 🧪 **Tests Unitarios**
**Impacto:** ALTO | **Esfuerzo:** ALTO (1 semana)

```python
# tests/test_game_modes.py
def test_game_session_init():
    session = GameSession(MODE_CLASSIC, 2, 5)
    assert session.num_players == 2
    assert session.quota == 5

def test_process_answer_correct():
    session.scenario = {'correcta': 0}
    result = session.process_answer(0)
    assert result == True
    assert session.total_score == 1
```

**Beneficio:** Prevenir regresiones en futuras actualizaciones.

---

### 17. 📝 **Sistema de Logging Robusto**
**Impacto:** MEDIO | **Esfuerzo:** MEDIO (3 horas)

```python
class Logger:
    LEVELS = {'DEBUG': 0, 'INFO': 1, 'WARN': 2, 'ERROR': 3}

    def __init__(self, level='INFO'):
        self.level = self.LEVELS[level]
        self.log_file = '/system.log'
        self.max_size = 10240  # 10KB

    def log(self, level, msg):
        if self.LEVELS[level] >= self.level:
            timestamp = time.localtime()
            entry = f"[{timestamp}] {level}: {msg}\n"
            print(entry, end='')
            self._write_to_file(entry)

    def _write_to_file(self, entry):
        # Rotar log si es muy grande
        # Escribir al archivo
```

---

### 18. ⚡ **Optimización de Memoria Agresiva**
**Impacto:** MEDIO | **Esfuerzo:** ALTO (1 semana)

**Técnicas:**
- Lazy loading de módulos pesados (career_mode solo cuando se usa)
- Pooling de buffers LCD
- Limpieza agresiva de variables temporales
- Strings frozen (MicroPython feature)
- Bytecode precompilado (.mpy files)

```python
# En vez de:
from career_mode import run_career_mode

# Hacer:
def _launch_career_mode(self):
    import career_mode  # Import lazy
    career_mode.run_career_mode(...)
    del career_mode  # Liberar memoria
    gc.collect()
```

---

## 📊 MATRIZ DE PRIORIZACIÓN

```
                    │ Bajo Esfuerzo │ Medio Esfuerzo │ Alto Esfuerzo
────────────────────┼────────────────┼────────────────┼───────────────
Alto Impacto        │  1, 2, 9       │   6, 7, 8      │   10, 16
                    │  (HACER YA)    │  (PLANIFICAR)  │  (ROADMAP)
────────────────────┼────────────────┼────────────────┼───────────────
Medio Impacto       │  3, 4          │  11, 13, 14    │   15, 18
                    │  (NICE TO HAVE)│  (OPCIONAL)    │  (SI HAY TIEMPO)
────────────────────┼────────────────┼────────────────┼───────────────
Bajo Impacto        │  5             │  12            │   17
                    │  (DIVERSION)   │  (PULIR)       │  (LARGO PLAZO)
```

---

## 🎯 RECOMENDACIÓN: TOP 3 PARA IMPLEMENTAR AHORA

### 🥇 **1. Watchdog Timer** (30 min)
Protección contra cuelgues - Crítico para estabilidad.

### 🥈 **2. Backup Automático** (20 min)
Proteger datos de usuario - Una línea de código, mucho valor.

### 🥉 **3. Tutorial Primera Vez** (2 horas)
Mejor experiencia de usuario - Inversión que vale la pena.

**Total: ~3 horas para mejoras significativas** 🚀

---

## 🔮 VISIÓN A LARGO PLAZO

**v1.4** - Watchdog + Backups + Debug mode
**v1.5** - Tutorial + Estadísticas avanzadas
**v1.6** - Achievements + Configuración avanzada
**v2.0** - Modo historia completo + Multiplayer online
**v3.0** - Portal web completo + Sistema de mods

---

## 💡 IDEAS LOCAS (Para pensar)

- 🎤 **Voice commands** via módulo de voz
- 📸 **Cámara ESP32-CAM** para foto de jugador
- 🔊 **Text-to-speech** para leer casos en voz alta
- 🌡️ **Sensores** que afecten gameplay (temperatura, luz)
- 🎮 **Joystick analógico** para navegación más fluida
- 💡 **LED RGB strip** para efectos visuales
- 📡 **Bluetooth** para mandos externos
- ⌚ **Smartwatch companion app**

---

**Elaborado por Claude Code - Diciembre 2024**
