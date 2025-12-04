# ============================================================================
# MAIN.PY - PSIC-O-TRONIC v1.0
# Motor principal del juego
# ============================================================================

import time
import gc
import network
from machine import Pin, I2C

# Módulos propios
from lcd_chars import load_custom_chars, convert_text, get_lives_display
from config import (
    is_wifi_configured, get_wifi_config, load_stats, get_stats_summary,
    clear_wifi_config
)
from wifi_portal import run_wifi_portal, connect_saved_wifi
from gemini_api import get_oracle
from game_modes import GameSession, InitialsInput, MODE_CLASSIC, MODE_SURVIVAL
from audio import init_audio, play as play_sound

# Sistema OTA
try:
    from ota_update import ota_manager, reboot as ota_reboot
    OTA_AVAILABLE = True
except ImportError:
    OTA_AVAILABLE = False
    print("[MAIN] OTA no disponible")

# Hardware
from i2c_lcd import I2cLcd

# ============================================================================
# CONFIGURACIÓN HARDWARE
# ============================================================================

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

# Timing
FRAME_DELAY = 0.08
DEBOUNCE_MS = 280

# ============================================================================
# ESTADOS DEL JUEGO
# ============================================================================

class State:
    BOOT = 0
    WIFI_CHECK = 1
    WIFI_PORTAL = 2
    INTRO = 3
    MENU = 4
    MODE_SELECT = 5
    PLAYER_SELECT = 6
    QUOTA_SELECT = 7
    STORY_INTRO = 8
    PASS_DEVICE = 9
    FETCHING = 10
    MESSAGE_ANIM = 11
    READING = 12
    CHOOSING = 13
    FEEDBACK = 14
    CHAPTER_COMPLETE = 15
    INITIALS_INPUT = 16
    GAME_OVER = 17
    STATS = 18
    HOW_TO_PLAY = 19
    WIFI_SETTINGS = 20
    CREDITS = 21
    PAUSE = 22
    ERROR = 23
    # OTA Updates
    OTA_CHECK = 24
    OTA_INFO = 25
    OTA_UPDATING = 26
    OTA_RESULT = 27

# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class PsicOTronic:
    """Motor principal del juego PSIC-O-TRONIC"""
    
    def __init__(self):
        print("\n" + "="*40)
        print("  PSIC-O-TRONIC v1.0")
        print("="*40)
        
        # Inicializar hardware
        self._init_gpio()
        self._init_lcd()
        self._init_audio()
        
        # Estado
        self.state = State.BOOT
        self.prev_state = -1
        self.frame = 0
        
        # Menús
        self.menu_idx = 0
        self.mode_idx = 0
        self.player_count = 1
        self.quota_idx = 2  # Default: 5 casos
        self.quota_options = [3, 5, 7, 10, 15, 999]
        self.help_page = 0
        
        # Sesión de juego
        self.session = None
        self.oracle = get_oracle()
        
        # Para scroll de texto
        self.opt_scroll = 0
        
        # Input de iniciales
        self.initials_input = None
        
        # LED blinking
        self.blink_counter = 0
        self.blink_state = False
        
        # Estado antes de pausa
        self.pre_pause_state = None
        
        # Manejo de errores
        self.error_msg = ""
        self.error_detail = ""
        self.error_scroll = 0
        self.error_menu_idx = 0
        
        # Buffer LCD para evitar flickering
        self.lcd_buffer = [[' ' for _ in range(20)] for _ in range(4)]
        self.lcd_shadow = [[' ' for _ in range(20)] for _ in range(4)]
        
    def _init_gpio(self):
        """Inicializa pines GPIO"""
        print("[INIT] GPIO...")
        
        self.btn_up = Pin(PIN_BTN_UP, Pin.IN, Pin.PULL_UP)
        self.btn_select = Pin(PIN_BTN_SELECT, Pin.IN, Pin.PULL_UP)
        self.btn_down = Pin(PIN_BTN_DOWN, Pin.IN, Pin.PULL_UP)
        
        self.led_up = Pin(PIN_LED_UP, Pin.OUT)
        self.led_select = Pin(PIN_LED_SELECT, Pin.OUT)
        self.led_down = Pin(PIN_LED_DOWN, Pin.OUT)
        self.led_notify = Pin(PIN_LED_NOTIFY, Pin.OUT)
        
        self._leds_off()
        print("[INIT] GPIO OK")
    
    def _init_audio(self):
        """Inicializa sistema de audio"""
        print("[INIT] Audio...")
        self.audio = init_audio(PIN_SPEAKER)
        print("[INIT] Audio OK")
    
    def _init_lcd(self):
        """Inicializa LCD"""
        print("[INIT] LCD...")
        
        i2c = I2C(1, sda=Pin(PIN_I2C_SDA), scl=Pin(PIN_I2C_SCL), freq=400000)
        devs = i2c.scan()
        
        if not devs:
            print("[ERROR] No LCD found!")
            while True:
                self.led_notify.value(1)
                time.sleep(0.1)
                self.led_notify.value(0)
                time.sleep(0.1)
        
        self.lcd = I2cLcd(i2c, devs[0], 4, 20)
        load_custom_chars(self.lcd)
        self.lcd.clear()
        print(f"[INIT] LCD OK @ {hex(devs[0])}")
    
    def _leds_off(self):
        """Apaga todos los LEDs"""
        self.led_up.value(0)
        self.led_select.value(0)
        self.led_down.value(0)
        self.led_notify.value(0)
    
    def _leds_menu(self):
        """LEDs para navegación de menú"""
        self.led_up.value(1)
        self.led_down.value(1)
        self.led_select.value(self.blink_state)
    
    def _leds_select_only(self):
        """Solo LED select parpadeando"""
        self.led_up.value(0)
        self.led_down.value(0)
        self.led_select.value(self.blink_state)
    
    def _leds_scroll(self, can_up, can_down):
        """LEDs para scroll"""
        self.led_up.value(1 if can_up else 0)
        self.led_down.value(1 if can_down else 0)
        self.led_select.value(self.blink_state)
    
    def _update_blink(self):
        """Actualiza estado de parpadeo"""
        self.blink_counter += 1
        if self.blink_counter >= 6:
            self.blink_counter = 0
            self.blink_state = not self.blink_state
    
    # === INPUT ===
    
    _last_btn_time = 0
    
    def _get_input(self):
        """Lee input de botones con debounce"""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_btn_time) < DEBOUNCE_MS:
            return None
        
        cmd = None
        if self.btn_up.value() == 0:
            cmd = 'UP'
        elif self.btn_down.value() == 0:
            cmd = 'DOWN'
        elif self.btn_select.value() == 0:
            cmd = 'SELECT'
        
        if cmd:
            self._last_btn_time = now
        return cmd
    
    # === LCD HELPERS (CON BUFFER PARA EVITAR FLICKERING) ===
    
    def _lcd_clear_buffer(self):
        """Limpia el buffer (no la pantalla física)"""
        for y in range(4):
            for x in range(20):
                self.lcd_buffer[y][x] = ' '
    
    def _lcd_clear(self):
        """Limpia el buffer - alias para compatibilidad"""
        self._lcd_clear_buffer()
    
    def _lcd_put(self, x, y, text):
        """Escribe texto en el buffer"""
        if y < 0 or y >= 4:
            return
        safe = convert_text(text)
        for i, char in enumerate(safe):
            if 0 <= x + i < 20:
                self.lcd_buffer[y][x + i] = char
    
    def _lcd_centered(self, y, text):
        """Escribe texto centrado en el buffer"""
        safe = convert_text(text)
        x = max(0, (20 - len(safe)) // 2)
        self._lcd_put(x, y, safe)
    
    def _lcd_render(self):
        """Vuelca buffer a LCD físico, solo escribe lo que cambió"""
        for y in range(4):
            for x in range(20):
                if self.lcd_buffer[y][x] != self.lcd_shadow[y][x]:
                    self.lcd.move_to(x, y)
                    self.lcd.putchar(self.lcd_buffer[y][x])
                    self.lcd_shadow[y][x] = self.lcd_buffer[y][x]

    def _lcd_force_clear(self):
        """Limpia LCD físico completamente y sincroniza buffers"""
        self.lcd.clear()
        for y in range(4):
            for x in range(20):
                self.lcd_shadow[y][x] = ' '
                self.lcd_buffer[y][x] = ' '

    def _lcd_lines(self, lines):
        """Escribe múltiples líneas centradas"""
        self._lcd_clear_buffer()
        for i, line in enumerate(lines[:4]):
            self._lcd_centered(i, line)
        self._lcd_render()
    
    def _wrap_text(self, text, width=20):
        """Divide texto en líneas"""
        words = convert_text(text).split()
        lines = []
        current = ""
        for word in words:
            if not current:
                # Primera palabra
                current = word
            elif len(current) + 1 + len(word) <= width:
                # Cabe en la línea actual
                current += " " + word
            else:
                # Nueva línea
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines if lines else [""]
    
    # === EFECTOS ===
    
    def _effect_crt_intro(self):
        """Intro simple sin parpadeos"""
        self._lcd_clear()
        self._lcd_centered(0, "====================")
        self._lcd_centered(1, "  PSIC-O-TRONIC")
        self._lcd_centered(2, "     ver 1.0")
        self._lcd_centered(3, "====================")
    
    def _effect_message_alert(self):
        """Alerta de mensaje sin parpadeo"""
        self._lcd_clear()
        self._lcd_centered(0, "+------------------+")
        self._lcd_centered(1, "* MENSAJE ENTRANTE *")
        self._lcd_centered(2, "")
        self._lcd_centered(3, "+------------------+")
        self._lcd_render()
        self.led_notify.value(1)
        time.sleep(0.8)
        self.led_notify.value(0)
    
    # === ESTADOS DEL JUEGO ===
    
    def _update_boot(self, key):
        """Estado: Boot"""
        self._effect_crt_intro()
        time.sleep(1)
        self.state = State.WIFI_CHECK
    
    def _update_wifi_check(self, key):
        """Estado: Verificar WiFi"""
        self._lcd_lines([
            "Verificando",
            "conexión WiFi...",
            "",
            ""
        ])
        
        if is_wifi_configured():
            self._lcd_lines([
                "Conectando a",
                "red guardada...",
                "",
                ""
            ])
            
            success, result = connect_saved_wifi(timeout=10)
            
            if success:
                self._lcd_lines([
                    "WiFi conectado!",
                    f"IP: {result}",
                    "",
                    ""
                ])
                time.sleep(1)
                self.state = State.INTRO
            else:
                self._lcd_lines([
                    "Error conexión",
                    "Abriendo portal",
                    "de configuracion",
                    ""
                ])
                time.sleep(2)
                self.state = State.WIFI_PORTAL
        else:
            self.state = State.WIFI_PORTAL
    
    def _update_wifi_portal(self, key):
        """Estado: Portal cautivo WiFi"""
        def lcd_callback(lines):
            self._lcd_lines(lines)
        
        def check_cancel():
            return self.btn_select.value() == 0 and self.btn_up.value() == 0
        
        result = run_wifi_portal(lcd_callback=lcd_callback, check_button=check_cancel)
        
        if result and result.get("connected"):
            self._lcd_lines([
                "Configuración",
                "guardada!",
                "",
                "Reiniciando..."
            ])
            time.sleep(2)
            import machine
            machine.reset()
        else:
            self.state = State.INTRO
    
    def _update_intro(self, key):
        """Estado: Intro animada"""
        step = self.frame // 5
        
        if step < 8:
            self._lcd_clear()
            self._lcd_centered(0, "====================")
            self._lcd_centered(1, "  PSIC-O-TRONIC")
            self._lcd_centered(2, "     ver 1.0")
            
            # Barra de carga
            progress = min(20, step * 3)
            bar = chr(0) * progress + "." * (20 - progress)
            self._lcd_put(0, 3, bar)
            
            # LEDs secuenciales
            step_led = self.frame % 16
            self.led_up.value(1 if step_led < 4 else 0)
            self.led_select.value(1 if 4 <= step_led < 8 else 0)
            self.led_down.value(1 if 8 <= step_led < 12 else 0)
            self.led_notify.value(1 if step_led >= 12 else 0)
        else:
            self._leds_off()
            play_sound('boot')
            self.state = State.MENU
            self.menu_idx = 0
    
    def _update_menu(self, key):
        """Estado: Menú principal"""
        options = ["Jugar", "Estadisticas", "Como Jugar", "WiFi"]
        
        # Añadir opción OTA si está disponible
        if OTA_AVAILABLE:
            if ota_manager.has_update():
                options.append("Actualizar [!]")
            else:
                options.append("Actualizar")
        
        options.append("Creditos")
        
        self._lcd_clear()
        self._lcd_centered(0, "== MENU ==")
        
        # Mostrar 3 opciones visibles
        start = max(0, min(self.menu_idx - 1, len(options) - 3))
        for i in range(3):
            idx = start + i
            if idx < len(options):
                prefix = ">" if idx == self.menu_idx else " "
                self._lcd_put(1, i + 1, prefix + options[idx][:18])
        
        self._leds_menu()
        
        if key == 'UP':
            self.menu_idx = (self.menu_idx - 1) % len(options)
            play_sound('click')
        elif key == 'DOWN':
            self.menu_idx = (self.menu_idx + 1) % len(options)
            play_sound('click')
        elif key == 'SELECT':
            play_sound('beep')
            selected = options[self.menu_idx]
            if selected == "Jugar":
                self.state = State.MODE_SELECT
                self.mode_idx = 0
            elif selected == "Estadisticas":
                self.state = State.STATS
            elif selected == "Como Jugar":
                self.state = State.HOW_TO_PLAY
                self.help_page = 0
            elif selected == "WiFi":
                self.state = State.WIFI_SETTINGS
            elif selected.startswith("Actualizar"):
                self.state = State.OTA_CHECK
                self.frame = 0
            elif selected == "Creditos":
                self.state = State.CREDITS
    
    def _update_mode_select(self, key):
        """Estado: Selección de modo"""
        modes = ["Clásico", "Survival", "Mi Consulta"]
        
        self._lcd_clear()
        self._lcd_centered(0, "MODO DE JUEGO")
        
        for i, mode in enumerate(modes):
            prefix = ">" if i == self.mode_idx else " "
            self._lcd_put(1, i + 1, f"{prefix}{mode}")
        
        self._leds_menu()
        
        if key == 'UP':
            self.mode_idx = (self.mode_idx - 1) % 3
        elif key == 'DOWN':
            self.mode_idx = (self.mode_idx + 1) % 3
        elif key == 'SELECT':
            if self.mode_idx == 2:  # Mi Consulta
                self._launch_career_mode()
            else:
                self.state = State.PLAYER_SELECT
    
    def _launch_career_mode(self):
        """Lanza el modo Mi Consulta"""
        from career_mode import run_career_mode
        run_career_mode(
            self.lcd,
            self.btn_up,
            self.btn_select, 
            self.btn_down,
            self.led_up,
            self.led_select,
            self.led_down,
            self.led_notify
        )
        # Volver al menu principal
        self.state = State.MENU
        self.menu_idx = 0
        self.frame = 0
        self._lcd_force_clear()
    
    def _update_player_select(self, key):
        """Estado: Selección de jugadores"""
        self._lcd_clear()
        self._lcd_centered(0, "JUGADORES")
        self._lcd_centered(1, f"<< {self.player_count} >>")
        self._lcd_put(0, 3, " [^v]Cambiar [OK]>")
        
        self._leds_menu()
        
        if key == 'UP' and self.player_count < 4:
            self.player_count += 1
        elif key == 'DOWN' and self.player_count > 1:
            self.player_count -= 1
        elif key == 'SELECT':
            mode = MODE_SURVIVAL if self.mode_idx == 1 else MODE_CLASSIC
            if mode == MODE_SURVIVAL:
                self._start_game(mode)
            else:
                self.state = State.QUOTA_SELECT
    
    def _update_quota_select(self, key):
        """Estado: Selección de cuota"""
        val = self.quota_options[self.quota_idx]
        val_str = "INFINITO" if val == 999 else str(val)
        
        self._lcd_clear()
        self._lcd_centered(0, "CASOS A RESOLVER")
        self._lcd_centered(1, f"<< {val_str} >>")
        self._lcd_put(0, 3, " [^v]Cambiar [OK]>")
        
        self._leds_menu()
        
        if key == 'UP':
            self.quota_idx = min(len(self.quota_options) - 1, self.quota_idx + 1)
        elif key == 'DOWN':
            self.quota_idx = max(0, self.quota_idx - 1)
        elif key == 'SELECT':
            self._start_game(MODE_CLASSIC)
    
    def _start_game(self, mode):
        """Inicia una nueva partida"""
        quota = self.quota_options[self.quota_idx] if mode == MODE_CLASSIC else 999
        self.session = GameSession(mode, self.player_count, quota)
        self.session.start()
        self.state = State.PASS_DEVICE
    
    def _update_story_intro(self, key):
        """Estado: Intro de capítulo (historia)

        NOTA: Este estado es parte del modo historia que está en desarrollo.
        Los métodos necesarios aún no están implementados en GameSession.
        """
        # TODO: Implementar get_chapter_intro() en GameSession
        # intro = self.session.get_chapter_intro()

        # Fallback temporal: mostrar mensaje genérico
        self._lcd_clear()
        self._lcd_centered(0, "MODO HISTORIA")
        self._lcd_centered(1, "En desarrollo")
        self._lcd_centered(2, "")
        self._lcd_centered(3, "[OK] Continuar")

        self._leds_select_only()

        if key == 'SELECT':
            self.state = State.PASS_DEVICE
    
    def _update_pass_device(self, key):
        """Estado: Pasar dispositivo"""
        player = self.session.get_current_player()
        
        self._lcd_clear()
        self._lcd_put(0, 0, self.session.get_status_line())
        self._lcd_centered(1, "TURNO DE")
        self._lcd_centered(2, f"JUGADOR {player['id']}")
        self._lcd_centered(3, "[OK] Conectar")
        
        self._leds_select_only()
        
        if key == 'SELECT':
            self.state = State.FETCHING
            self.frame = 0
    
    def _update_fetching(self, key):
        """Estado: Obteniendo caso"""
        # Mostrar animación
        antenna = ["^", "|", "/", "-", "\\", "|"][(self.frame // 4) % 6]
        dots = "." * ((self.frame // 6) % 4)
        
        self._lcd_clear()
        self._lcd_centered(0, "+------------------+")
        self._lcd_centered(1, f"  CONECTANDO  {antenna}")
        self._lcd_put(0, 2, f" Línea psiquiátrica{dots}"[:20])
        self._lcd_centered(3, "+------------------+")
        
        self.led_notify.value(self.blink_state)
        
        # Primera frame: hacer la petición
        if self.frame == 1:
            gc.collect()
            modifier = self.session.get_prompt_modifier()
            self.session.scenario = self.oracle.get_scenario(
                mode=self.session.mode,
                story_modifier=modifier
            )
            
            # Comprobar error
            if self.session.scenario is None:
                self.state = State.ERROR
                self.error_msg = self.oracle.last_error or "Error desconocido"
                self.error_detail = ""
                self.led_notify.value(0)
                return
            
            # Preparar texto con nuevo formato
            sender = self.session.scenario.get('remitente', 'Anónimo')
            msg = self.session.scenario.get('mensaje', 'Error')
            msg = msg.lstrip('!?¡¿ ')  # Quitar signos al inicio
            
            # Formato: DE: nombre + salto + MSG: texto
            header = f"DE: {sender}"
            body = f"MSG: {msg}"
            
            # Wrap del cuerpo del mensaje
            body_lines = self._wrap_text(body)
            self.session.scroll_lines = [header] + body_lines
            self.session.scroll_idx = 0
            
            self.state = State.MESSAGE_ANIM
            self.frame = 0
    
    def _update_message_anim(self, key):
        """Estado: Animación de mensaje simple"""
        step = self.frame // 4
        
        # Sonido al inicio
        if self.frame == 1:
            play_sound('mensaje')
        
        if step < 4:
            # Mostrar mensaje entrante
            self._lcd_clear()
            self._lcd_centered(0, "+------------------+")
            self._lcd_centered(1, "* MENSAJE ENTRANTE *")
            self._lcd_centered(3, "+------------------+")
            self.led_notify.value((self.frame // 3) % 2)
        else:
            self.led_notify.value(0)
            self.state = State.READING
            self.session.scroll_idx = 0
    
    def _update_reading(self, key):
        """Estado: Leyendo mensaje (4 líneas completas)"""
        # Detectar pausa (UP + DOWN a la vez)
        if self.btn_up.value() == 0 and self.btn_down.value() == 0:
            self.pre_pause_state = State.READING
            self.state = State.PAUSE
            return
        
        self._lcd_clear()
        
        # Mostrar 4 líneas visibles (aprovechando toda la pantalla)
        lines = self.session.scroll_lines
        idx = self.session.scroll_idx
        
        for i in range(4):
            if idx + i < len(lines):
                self._lcd_put(0, i, lines[idx + i])
        
        # Solo LEDs para indicar scroll (sin iconos en pantalla)
        can_up = idx > 0
        can_down = (idx + 4) < len(lines)
        
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.session.scroll_idx -= 1
        elif key == 'DOWN' and can_down:
            self.session.scroll_idx += 1
        elif key == 'SELECT':
            self.state = State.CHOOSING
            self.session.selected_option = 0
            self.opt_scroll = 0
    
    def _update_choosing(self, key):
        """Estado: Eligiendo respuesta (4 opciones)"""
        # Detectar pausa (UP + DOWN a la vez)
        if self.btn_up.value() == 0 and self.btn_down.value() == 0:
            self.pre_pause_state = State.CHOOSING
            self.state = State.PAUSE
            return
        
        self._lcd_clear()
        
        opts = self.session.scenario.get('opciones', [])
        
        # Mostrar 4 opciones (una por línea)
        for i in range(min(4, len(opts))):
            text = convert_text(opts[i])
            prefix = ">" if i == self.session.selected_option else " "
            
            # Scroll horizontal para opción seleccionada larga
            if i == self.session.selected_option and len(text) > 18:
                offset = max(0, (self.opt_scroll // 3) - 2) % (len(text) - 17 + 3)
                if offset > len(text) - 18:
                    offset = len(text) - 18
                text = text[offset:offset + 18]
            
            self._lcd_put(0, i, f"{prefix}{text[:19]}")
        
        can_up = self.session.selected_option > 0
        can_down = self.session.selected_option < len(opts) - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.session.selected_option -= 1
            self.opt_scroll = 0
        elif key == 'DOWN' and can_down:
            self.session.selected_option += 1
            self.opt_scroll = 0
        elif key == 'SELECT':
            self.session.process_answer(self.session.selected_option)
            self.state = State.FEEDBACK
            self.frame = 0
    
    def _update_feedback(self, key):
        """Estado: Mostrando feedback"""
        blink = (self.frame // 4) % 2 == 0
        
        # Sonido al inicio
        if self.frame == 1:
            if self.session.last_result_ok:
                play_sound('correcto')
            else:
                play_sound('incorrecto')
        
        self._lcd_clear()
        
        if self.session.last_result_ok:
            self._lcd_centered(0, "== CORRECTO ==")
        else:
            self._lcd_centered(0, "== ERROR ==")
            self.led_notify.value(blink)
        
        # Mostrar feedback
        fb_lines = self._wrap_text(self.session.last_feedback)
        start_y = 2 if len(fb_lines) == 1 else 1
        for i, line in enumerate(fb_lines[:2]):
            self._lcd_centered(start_y + i, line)
        
        self._lcd_centered(3, "[OK] Continuar")
        self._leds_select_only()
        
        if key == 'SELECT':
            self.led_notify.value(0)
            
            game_state = self.session.check_game_state()
            
            if game_state == "win":
                self.state = State.GAME_OVER
            # NOTA: chapter_complete está comentado porque el modo historia no está implementado
            # elif game_state == "chapter_complete":
            #     self.state = State.CHAPTER_COMPLETE
            elif game_state == "game_over":
                # Comprobar si es récord
                if self.session.mode == MODE_SURVIVAL:
                    stats = load_stats()
                    if self.session.total_score > stats.get("survival_record", 0):
                        self.initials_input = InitialsInput()
                        self.state = State.INITIALS_INPUT
                        return
                self.state = State.GAME_OVER
            else:
                if self.session.next_turn():
                    self.state = State.PASS_DEVICE
                else:
                    self.state = State.GAME_OVER
    
    def _update_chapter_complete(self, key):
        """Estado: Capítulo completado (historia)

        NOTA: Este estado es parte del modo historia que está en desarrollo.
        Los métodos necesarios aún no están implementados en GameSession.
        """
        # TODO: Implementar get_chapter_outro() y advance_chapter() en GameSession
        # outro = self.session.get_chapter_outro(won=True)

        # Fallback temporal: mostrar mensaje genérico
        self._lcd_clear()
        self._lcd_centered(0, "CAPITULO COMPLETO")
        self._lcd_centered(1, "Modo historia")
        self._lcd_centered(2, "en desarrollo")
        self._lcd_centered(3, "[OK] Continuar")

        self._leds_select_only()

        if key == 'SELECT':
            # TODO: Implementar advance_chapter()
            # self.session.advance_chapter()
            # self.state = State.STORY_INTRO
            # Por ahora volver al menú
            self.state = State.MENU
    
    def _update_initials_input(self, key):
        """Estado: Input de iniciales para récord"""
        self._lcd_clear()
        self._lcd_centered(0, "NUEVO RÉCORD!")
        self._lcd_centered(1, "Tus iniciales:")
        self._lcd_centered(2, self.initials_input.get_display())
        self._lcd_centered(3, "[^v]Letra [OK]Sig")
        
        self._leds_menu()
        
        if key == 'UP':
            self.initials_input.up()
        elif key == 'DOWN':
            self.initials_input.down()
        elif key == 'SELECT':
            if self.initials_input.next():
                # Guardar récord
                initials = self.initials_input.get_initials()
                self.session.initials = initials
                
                from config import check_survival_record, check_streak_record
                if self.session.mode == MODE_SURVIVAL:
                    check_survival_record(self.session.total_score, initials)
                check_streak_record(self.session.current_streak, initials)
                
                self.state = State.GAME_OVER
    
    def _update_game_over(self, key):
        """Estado: Game Over"""
        # Sonido al inicio
        if self.frame == 1:
            if self.session.game_won:
                play_sound('victoria')
            else:
                play_sound('game_over')
        
        self._lcd_clear()
        
        if self.session.game_won:
            self._lcd_centered(0, "** VICTORIA **")
            self._lcd_centered(1, "OBJETIVO CUMPLIDO!")
        else:
            self._lcd_centered(0, "** GAME OVER **")
            self._lcd_centered(1, "TODOS DESPEDIDOS")
        
        mvp = self.session.get_mvp()
        if mvp:
            self._lcd_centered(2, f"MVP: P{mvp['id']} ({mvp['score']}pts)")
        
        self._lcd_centered(3, "[OK] Menú")
        self._leds_select_only()
        
        if key == 'SELECT':
            self.state = State.MENU
            self.menu_idx = 0
    
    def _update_stats(self, key):
        """Estado: Estadísticas"""
        summary = get_stats_summary()
        
        self._lcd_clear()
        self._lcd_centered(0, "= ESTADISTICAS =")
        self._lcd_put(0, 1, f"Partidas: {summary['games']}")
        self._lcd_put(0, 2, f"Casos: {summary['cases']}")
        self._lcd_put(0, 3, f"Racha: {summary['streak']}")
        
        self._leds_select_only()
        
        if key == 'SELECT':
            self.state = State.MENU
    
    def _update_how_to_play(self, key):
        """Estado: Cómo jugar"""
        pages = [
            # Página 1: Intro
            ["CÓMO JUGAR",
             "Eres un psicólogo",
             "poco ético. Pacientes",
             "te escriben."],
            # Página 2: Objetivo
            ["OBJETIVO",
             "Elige la respuesta",
             "MÁS PSICÓTICA para",
             "resolver el caso."],
            # Página 3: Vidas
            ["VIDAS",
             "Tienes 3 vidas:" + chr(0) + chr(0) + chr(0),
             "Si fallas, pierdes 1",
             "0 vidas = GAME OVER"],
            # Página 4: Controles
            ["CONTROLES",
             "[^] Arriba/Scroll",
             "[v] Abajo/Scroll",
             "[OK] Seleccionar"],
            # Página 5: Pausa
            ["PAUSA",
             "Pulsa [^]+[v] a la",
             "vez para pausar",
             "en la partida."],
            # Página 6: Modos
            ["MODOS",
             "Clásico: Cuota",
             "Survival: Infinito",
             "Historia: Campaña"],
            # Página 7: Modo Clásico
            ["CLÁSICO",
             "Elige cuántos casos",
             "resolver: 3,5,7...",
             "Cumple el objetivo!"],
            # Página 8: Modo Survival
            ["SURVIVAL",
             "Aguanta lo máximo",
             "posible sin fallar.",
             "Guarda tu récord!"],
            # Página 9: Modo Historia
            ["HISTORIA",
             "Campaña: El Interno",
             "Sube de rango en",
             "clínica corrupta."],
            # Página 10: WiFi 1
            ["CONEXIÓN",
             "El juego necesita",
             "internet para los",
             "casos con IA."],
            # Página 11: WiFi 2
            ["CONFIG WIFI",
             "Sin WiFi guardada",
             "se abre el portal",
             "de configuración."],
            # Página 12: WiFi 3
            ["PORTAL 1/4",
             "Busca en tu móvil",
             "la red WiFi:",
             "PSIC-O-TRONIC"],
            # Página 13: WiFi 4
            ["PORTAL 2/4",
             "Conéctate a esa",
             "red sin clave",
             "desde tu móvil."],
            # Página 14: WiFi 5
            ["PORTAL 3/4",
             "Se abre una web",
             "automáticamente",
             "(o 192.168.4.1)"],
            # Página 15: WiFi 6
            ["PORTAL 4/4",
             "Elige tu WiFi,",
             "pon la clave",
             "y pulsa CONECTAR"],
            # Página 16: WiFi 7
            ["LISTO",
             "El aparato guarda",
             "la config y luego",
             "conecta solo."],
            # Página 17: Info
            ["INFO",
             "PSIC-O-TRONIC v1.0",
             "Casos generados",
             "con Gemini AI"],
        ]
        
        self._lcd_clear()
        
        # Primera línea: título + paginación
        title = pages[self.help_page][0]
        page_num = f"{self.help_page + 1}/{len(pages)}"
        spaces = 20 - len(title) - len(page_num)
        self._lcd_put(0, 0, title + " " * spaces + page_num)
        
        # Resto de líneas
        for i in range(1, 4):
            self._lcd_put(0, i, pages[self.help_page][i])
        
        can_up = self.help_page > 0
        can_down = self.help_page < len(pages) - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.help_page -= 1
        elif key == 'DOWN' and can_down:
            self.help_page += 1
        elif key == 'SELECT':
            self.help_page = 0
            self.state = State.MENU
    
    def _update_wifi_settings(self, key):
        """Estado: Configuración WiFi"""
        ssid, _ = get_wifi_config()
        
        self._lcd_clear()
        self._lcd_centered(0, "CONFIG WiFi/API")
        if ssid:
            self._lcd_put(0, 1, f"Red: {ssid[:14]}")
        else:
            self._lcd_put(0, 1, "Red: Sin config")
        self._lcd_put(0, 2, "[OK] Abrir portal")
        self._lcd_centered(3, "[^] Volver")
        
        self._leds_menu()
        
        if key == 'UP':
            self.state = State.MENU
        elif key == 'SELECT':
            # No borrar config, solo abrir portal
            self.state = State.WIFI_PORTAL
    
    def _update_credits(self, key):
        """Estado: Créditos con scroll"""
        pages = [
            ["PSIC-O-TRONIC",
             "Versión 1.0",
             "Noviembre 2025",
             ""],
            ["Desarrollado por:",
             "Miguel Cañadas",
             "",
             ""],
            ["IA generativa:",
             "Google Gemini",
             "",
             ""],
            ["Hardware:",
             "ESP32-S3",
             "LCD 20x4 I2C",
             ""],
            ["Version 2.0",
             "Noviembre 2025",
             "",
             ""],
            ["[OK] Volver",
             "",
             "",
             ""],
        ]
        
        self._lcd_clear()
        for i, line in enumerate(pages[self.help_page]):
            self._lcd_centered(i, line)
        
        can_up = self.help_page > 0
        can_down = self.help_page < len(pages) - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.help_page -= 1
        elif key == 'DOWN' and can_down:
            self.help_page += 1
        elif key == 'SELECT':
            self.help_page = 0
            self.state = State.MENU
    
    def _update_pause(self, key):
        """Estado: Menú de pausa"""
        self._lcd_clear()
        self._lcd_centered(0, "== PAUSA ==")
        
        pause_options = ["Continuar", "Reiniciar", "Salir al menú"]
        
        for i, opt in enumerate(pause_options):
            prefix = ">" if i == self.menu_idx else " "
            self._lcd_put(1, i + 1, f"{prefix}{opt}")
        
        self._leds_menu()
        
        if key == 'UP':
            self.menu_idx = (self.menu_idx - 1) % 3
        elif key == 'DOWN':
            self.menu_idx = (self.menu_idx + 1) % 3
        elif key == 'SELECT':
            if self.menu_idx == 0:  # Continuar
                # Volver al estado anterior
                self.state = self.pre_pause_state if self.pre_pause_state else State.CHOOSING
            elif self.menu_idx == 1:  # Reiniciar
                self._start_game(self.session.mode)
            elif self.menu_idx == 2:  # Salir
                self.state = State.MENU
            self.menu_idx = 0
    
    def _update_error(self, key):
        """Estado: Pantalla de error con opciones"""
        # Preparar líneas de error
        error_lines = ["ERROR"]
        
        # Añadir detalles del error (wrapeado)
        if self.error_msg:
            error_lines.extend(self._wrap_text(self.error_msg))
        
        # Añadir soluciones
        error_lines.extend([
            "",
            "Soluciones:",
            "- Verifica WiFi",
            "- Cambia API Key",
            "- Espera 1 minuto",
        ])
        
        self._lcd_clear()
        
        # Mostrar contenido con scroll (3 líneas)
        idx = self.error_scroll
        for i in range(3):
            if idx + i < len(error_lines):
                line = error_lines[idx + i][:20]
                self._lcd_put(0, i, line)
        
        # Línea 4: opciones fijas
        if self.error_menu_idx == 0:
            self._lcd_put(0, 3, ">Reintentar   Menú")
        else:
            self._lcd_put(0, 3, " Reintentar  >Menú")
        
        # LEDs para scroll
        can_up = idx > 0
        can_down = (idx + 3) < len(error_lines)
        self._leds_scroll(can_up, can_down)
        
        # Controles - UP/DOWN hacen scroll primero, luego cambian opción
        if key == 'UP':
            if can_up:
                self.error_scroll -= 1
            else:
                self.error_menu_idx = 0
        elif key == 'DOWN':
            if can_down:
                self.error_scroll += 1
            else:
                self.error_menu_idx = 1
        elif key == 'SELECT':
            if self.error_menu_idx == 0:  # Reintentar
                self.error_scroll = 0
                self.error_menu_idx = 0
                self.state = State.FETCHING
            else:  # Menú
                self.error_scroll = 0
                self.error_menu_idx = 0
                self.state = State.MENU
    
    # === OTA UPDATES ===
    
    def _update_ota_check(self, key):
        """Verificar actualizaciones"""
        self._lcd_clear()
        
        if not OTA_AVAILABLE:
            self._lcd_centered(0, "OTA")
            self._lcd_centered(1, "No disponible")
            self._lcd_centered(3, "[OK] Volver")
            self._leds_select_only()
            if key == 'SELECT':
                self.state = State.MENU
            return
        
        # Animación
        dots = "." * ((self.frame // 5) % 4)
        self._lcd_centered(0, "ACTUALIZACIONES")
        self._lcd_centered(1, "Verificando" + dots)
        self._lcd_centered(2, "Conectando...")
        
        self._leds_off()
        
        # Verificar en frame 1
        if self.frame == 1:
            def status_cb(msg):
                pass
            ota_manager.check_async(status_cb)
        
        # Mostrar resultado después
        if self.frame > 20:
            self.state = State.OTA_INFO
    
    def _update_ota_info(self, key):
        """Info de actualización"""
        self._lcd_clear()
        
        if not OTA_AVAILABLE:
            self.state = State.MENU
            return
        
        current_ver = ota_manager.get_current_version()
        
        if ota_manager.has_update():
            info = ota_manager.get_update_info()
            new_ver = info.get("new_version", "?")
            num_files = len(info.get("files", []))
            
            self._lcd_centered(0, "UPDATE DISPONIBLE!")
            self._lcd_put(0, 1, "v" + current_ver + " -> v" + new_ver)
            self._lcd_put(0, 2, str(num_files) + " archivos")
            self._lcd_put(0, 3, "[OK]Instalar [^]No")
            
            self._leds_scroll(True, False)
            
            if key == 'SELECT':
                self.state = State.OTA_UPDATING
                self.frame = 0
            elif key == 'UP':
                self.state = State.MENU
        else:
            self._lcd_centered(0, "SIN ACTUALIZACIONES")
            self._lcd_centered(1, "Version actual:")
            self._lcd_centered(2, "v" + current_ver)
            self._lcd_centered(3, "[OK] Volver")
            
            self._leds_select_only()
            
            if key == 'SELECT':
                self.state = State.MENU
    
    def _update_ota_updating(self, key):
        """Proceso de actualización"""
        self._lcd_clear()
        
        # Animación
        spinner = ["|", "/", "-", "\\"][self.frame % 4]
        
        self._lcd_centered(0, "ACTUALIZANDO " + spinner)
        self._lcd_centered(1, ota_manager.status_msg[:20])
        self._lcd_centered(3, "No desconectar!")
        
        self._leds_off()
        
        # Ejecutar en frame 1
        if self.frame == 1:
            def progress_cb(msg):
                pass
            
            success, msg = ota_manager.perform_update(progress_cb)
            self._ota_success = success
            self._ota_result_msg = msg
            self.state = State.OTA_RESULT
            self.frame = 0
    
    def _update_ota_result(self, key):
        """Resultado de actualización"""
        self._lcd_clear()
        
        success = getattr(self, '_ota_success', False)
        msg = getattr(self, '_ota_result_msg', "")
        
        if success:
            self._lcd_centered(0, "ACTUALIZADO!")
            self._lcd_centered(1, msg[:20])
            self._lcd_centered(2, "Reiniciar ahora?")
            self._lcd_put(0, 3, "[OK]Si  [^]Despues")
            
            self._leds_scroll(True, False)
            
            if key == 'SELECT':
                self._lcd_clear()
                self._lcd_centered(1, "Reiniciando...")
                self._lcd_render()
                time.sleep(1)
                ota_reboot()
            elif key == 'UP':
                self.state = State.MENU
        else:
            self._lcd_centered(0, "ERROR UPDATE")
            self._lcd_centered(1, msg[:20])
            self._lcd_centered(3, "[OK] Volver")
            
            self._leds_select_only()
            
            if key == 'SELECT':
                self.state = State.MENU
    
    # === LOOP PRINCIPAL ===
    
    def run(self):
        """Bucle principal del juego"""
        print("[GAME] Starting main loop...")
        
        state_handlers = {
            State.BOOT: self._update_boot,
            State.WIFI_CHECK: self._update_wifi_check,
            State.WIFI_PORTAL: self._update_wifi_portal,
            State.INTRO: self._update_intro,
            State.MENU: self._update_menu,
            State.MODE_SELECT: self._update_mode_select,
            State.PLAYER_SELECT: self._update_player_select,
            State.QUOTA_SELECT: self._update_quota_select,
            State.STORY_INTRO: self._update_story_intro,
            State.PASS_DEVICE: self._update_pass_device,
            State.FETCHING: self._update_fetching,
            State.MESSAGE_ANIM: self._update_message_anim,
            State.READING: self._update_reading,
            State.CHOOSING: self._update_choosing,
            State.FEEDBACK: self._update_feedback,
            State.CHAPTER_COMPLETE: self._update_chapter_complete,
            State.INITIALS_INPUT: self._update_initials_input,
            State.GAME_OVER: self._update_game_over,
            State.STATS: self._update_stats,
            State.HOW_TO_PLAY: self._update_how_to_play,
            State.WIFI_SETTINGS: self._update_wifi_settings,
            State.CREDITS: self._update_credits,
            State.PAUSE: self._update_pause,
            State.ERROR: self._update_error,
            State.OTA_CHECK: self._update_ota_check,
            State.OTA_INFO: self._update_ota_info,
            State.OTA_UPDATING: self._update_ota_updating,
            State.OTA_RESULT: self._update_ota_result,
        }
        
        while True:
            time.sleep(FRAME_DELAY)
            self.frame += 1
            self.opt_scroll += 1
            self._update_blink()
            
            # Log cambio de estado
            if self.state != self.prev_state:
                print(f"[STATE] {self.prev_state} -> {self.state}")
                self.prev_state = self.state
                self.frame = 0
                # Limpiar shadow para forzar redibujado completo
                self.lcd.clear()
                for y in range(4):
                    for x in range(20):
                        self.lcd_shadow[y][x] = ' '
            
            # Input
            key = self._get_input()
            
            # Handler del estado actual
            handler = state_handlers.get(self.state)
            if handler:
                try:
                    handler(key)
                    # Renderizar buffer al LCD
                    self._lcd_render()
                except Exception as e:
                    print(f"[ERROR] State {self.state}: {e}")
                    import sys
                    sys.print_exception(e)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    try:
        game = PsicOTronic()
        game.run()
    except KeyboardInterrupt:
        print("\n[EXIT] Interrupted by user")
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import sys
        sys.print_exception(e)

if __name__ == "__main__":
    main()