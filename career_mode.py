# ============================================================================
# CAREER_MODE.PY - Motor principal del Modo Mi Consulta
# PSIC-O-TRONIC - Simulador de consulta psicologica
# ============================================================================

import time
import gc
from machine import Pin

from lcd_chars import convert_text
from audio import play as play_sound
from ntp_time import (
    sync_time, get_date_str, get_time_str, get_timestamp,
    get_today_str, is_quiet_hours, get_hour
)

# Importar sistema de errores
try:
    from error_handler import ErrorHandler, get_error_handler, check_memory
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False

from career_data import (
    load_career, save_career, reset_career,
    get_player_info, set_player_name, add_xp, set_rango,
    get_nivel, get_xp, get_xp_to_next, increment_stat, get_stats,
    get_pacientes, get_paciente_by_id, add_paciente, remove_paciente,
    update_paciente_progreso, add_historial_paciente, count_pacientes,
    get_mensajes_pendientes, count_mensajes_pendientes, add_mensaje,
    get_mensaje_by_id, remove_mensaje, has_mensaje_pendiente_de,
    is_setup_complete, set_setup_complete, get_backlight_timeout,
    set_ultimo_dia_jugado, get_ultimo_dia_jugado,
    increment_pacientes_nuevos_hoy,
    # Config opciones
    set_backlight_timeout, get_sound_enabled, set_sound_enabled,
    get_notifications_enabled, set_notifications_enabled,
    get_notification_sound, set_notification_sound,
    XP_SESION_CORRECTA, XP_SESION_INCORRECTA,
    XP_CURAR_PACIENTE_BASE, XP_PACIENTE_ABANDONA,
    # Economia
    get_dinero, add_dinero, get_economia_stats,
    DINERO_SESION_OK, DINERO_SESION_MAL, DINERO_CURAR_BASE, DINERO_HUYE,
    # Inventario
    get_inventario, count_inventario, has_item, get_item_cantidad,
    add_item, remove_item, get_farmaco_by_id, puede_comprar, comprar_farmaco,
    CATALOGO_FARMACOS, MAX_INVENTARIO,
    # Efectos
    get_efectos_activos, add_efecto_paciente, remove_efecto_paciente,
    clear_efectos_paciente,
    # Tutorials
    tutorial_visto, marcar_tutorial
)
from career_scheduler import (
    check_new_day, generate_daily_schedule,
    check_scheduled_messages, should_notify
)
from career_patients import (
    generate_doctor_name, generate_rank_name,
    generate_new_patient, generate_session_message,
    generate_intro_message, generate_emergency_message
)
from career_systems import (
    # Logros
    LOGROS, get_logros_desbloqueados, check_logros,
    aplicar_recompensa_logro,
    # Rachas
    RACHAS, get_racha_actual, incrementar_racha, romper_racha,
    # Mejoras
    MEJORAS, get_mejoras_compradas, tiene_mejora,
    puede_comprar_mejora, comprar_mejora, get_efecto_mejoras,
    # Eventos
    EVENTOS, generar_evento_diario, get_evento_hoy, aplicar_efecto_evento,
    # Pacientes especiales
    TIPOS_PACIENTE, seleccionar_tipo_paciente,
    get_modificadores_paciente, aplicar_modificadores_paciente,
    # Stats
    registrar_stat_logro,
    # Misiones
    MISIONES_DIARIAS, MISIONES_SEMANALES,
    generar_misiones_diarias, generar_misiones_semanales,
    actualizar_progreso_mision, reclamar_mision, get_misiones_activas,
    # Reputación
    RANGOS_REPUTACION, get_reputacion, get_rango_reputacion,
    modificar_reputacion, get_efectos_reputacion,
    # Crafting
    RECETAS, puede_craftear, craftear, get_recetas_disponibles,
    # Apuestas
    puede_apostar, hacer_apuesta, resolver_apuesta,
    get_apuesta_activa, get_stats_apuestas, get_max_apuesta,
    # Casos familiares
    CASOS_FAMILIARES, iniciar_caso_familiar, get_siguiente_familiar,
    completar_miembro_familiar, finalizar_caso_familiar, get_caso_activo,
    # Torneos
    TORNEOS, iniciar_torneo, registrar_accion_torneo, finalizar_torneo,
    # Regalos
    REGALOS, generar_regalo_paciente, aplicar_regalo,
    # Personalización
    BATAS, DECORACIONES_EXTRA, get_batas_disponibles,
    comprar_bata, equipar_bata,
    # Oráculo
    generar_visita_oraculo, get_prediccion_oraculo, aplicar_prediccion_oraculo,
    # Eventos temporada
    check_evento_temporada, get_item_temporada,
    # Combos
    COMBOS, check_combo, aplicar_combo,
    # Prestigio
    puede_prestigiar, hacer_prestigio, get_prestigio, get_bonus_prestigio,
    # Notificaciones
    get_notificacion_aleatoria
)


class CareerState:
    """Estados del modo carrera"""
    INIT = 0
    SETUP_TITULO = 1
    SETUP_GENERATING = 2
    SETUP_CONFIRM = 3
    SCREENSAVER = 10
    MENU_PRINCIPAL = 11
    LISTA_MENSAJES = 12
    LISTA_PACIENTES = 13
    VER_PACIENTE = 14
    LEYENDO_MENSAJE = 15
    ELIGIENDO_RESPUESTA = 16
    FEEDBACK = 17
    RESULTADO_PACIENTE = 18
    SUBIDA_NIVEL = 19
    ESTADISTICAS = 20
    CONFIG = 21
    # Tienda El Camello
    TIENDA = 22
    TIENDA_COMPRAR = 23
    INVENTARIO = 24
    USAR_ITEM = 25
    TUTORIAL_CAMELLO = 26
    # Sistemas principales
    LOGROS = 27
    LOGRO_DESBLOQUEADO = 28
    MEJORAS = 29
    MEJORA_COMPRAR = 31
    EVENTO_DIA = 32
    RACHA_BONUS = 33
    GENERANDO = 30
    # Misiones
    MISIONES = 34
    MISION_DETALLE = 35
    # Apuestas
    APUESTAS = 36
    APUESTA_CONFIRMAR = 37
    APUESTA_RESULTADO = 38
    # Crafting
    CRAFTING = 39
    CRAFTING_CONFIRMAR = 40
    # Personalización
    BATAS = 41
    BATA_COMPRAR = 42
    # Casos familiares
    CASO_FAMILIAR = 43
    CASO_COMPLETADO = 44
    # Torneos
    TORNEO = 45
    TORNEO_RESULTADO = 46
    # Prestigio
    PRESTIGIO = 47
    PRESTIGIO_CONFIRMAR = 48
    # Oráculo
    ORACULO = 49
    # Regalo paciente
    REGALO_PACIENTE = 50
    # Combo
    COMBO_ACTIVADO = 51
    # Tutorial inicial
    TUTORIAL_INICIO = 52
    # Ayuda
    AYUDA = 53
    # Opciones
    OPCIONES = 54
    # Portal WiFi
    PORTAL_WIFI = 55
    ERROR = 99


class CareerMode:
    """Motor del modo Mi Consulta"""
    
    def __init__(self, lcd, btn_up, btn_select, btn_down, led_up, led_select, led_down, led_notify):
        """
        Inicializa el modo carrera.
        
        Args:
            lcd: Objeto LCD
            btn_up, btn_select, btn_down: Pines de botones
            led_up, led_select, led_down: LEDs de botones
            led_notify: Pin LED notificacion
        """
        self.lcd = lcd
        self.btn_up = btn_up
        self.btn_select = btn_select
        self.btn_down = btn_down
        self.led_up = led_up
        self.led_select = led_select
        self.led_down = led_down
        self.led_notify = led_notify
        
        # Estado
        self.state = CareerState.INIT
        self.prev_state = -1
        self.frame = 0
        self.exit_requested = False
        
        # Datos
        self.data = None
        
        # UI
        self.menu_idx = 0
        self.scroll_idx = 0
        self.mensaje_actual = None
        self.paciente_actual = None
        self.selected_option = 0
        self.opt_scroll = 0
        self._ver_pagina = 0  # Para ver detalles de paciente
        self._stats_pagina = 0  # Para estadísticas
        
        # Titulo seleccionado en setup
        self.titulo_idx = 0
        self.titulos = ["Doctor", "Doctora", "Doctore"]
        self.nombre_generado = ""
        
        # Backlight
        self.backlight_on = True
        self.last_activity = time.time()
        
        # Notificacion
        self.blink_state = False
        self.blink_counter = 0
        self.last_beep_time = 0
        
        # Buffer LCD
        self.lcd_buffer = [[' ' for _ in range(20)] for _ in range(4)]
        self.lcd_shadow = [[' ' for _ in range(20)] for _ in range(4)]
        
        # Resultado ultimo feedback
        self.last_correct = False
        self.last_feedback = ""
        self.level_up_info = None
        self._feedback_lines = []  # Líneas de feedback con wrap
        self._feedback_scroll = 0  # Índice de scroll en feedback
        
        # Tienda El Camello
        self._tienda_idx = 0
        self._tienda_scroll = 0
        self._inv_idx = 0
        self._compra_msg = ""
        self._tutorial_page = 0
        self._item_seleccionado = None
        self._dinero_ganado = 0  # Para mostrar en feedback
        
        # Efectos activos en sesion actual
        self._efecto_doble_xp = False
        self._efecto_protege_fallo = False
        self._efecto_no_huir = False
        self._efecto_elimina_opcion = -1  # -1 = no activo, 0-3 = opcion eliminada
        self._efecto_revela = False
        
        # Logros
        self._logros_idx = 0
        self._logros_scroll = 0
        self._logro_nuevo = None  # Logro recién desbloqueado para mostrar
        self._logros_pendientes = []  # Cola de logros por notificar
        
        # Mejoras de consulta
        self._mejoras_idx = 0
        self._mejoras_scroll = 0
        self._mejora_seleccionada = None
        
        # Evento del día
        self._evento_mostrado = False
        self._evento_actual = None
        
        # Rachas
        self._racha_info = None  # Info de racha para mostrar
        self._racha_texto = None
        
        # Resultado paciente
        self._resultado_tipo = ""
        self._resultado_page = 0
        self._cierre_scroll = 0  # Scroll para cierre narrativo
        
        # Opciones
        self._opciones_idx = 0
        
        # Error handling
        self.error_msg = ""
        self._error_info = None  # Info del error actual
        self._error_handler = None
        
        # Inicializar error handler si disponible
        if ERROR_HANDLER_AVAILABLE:
            self._error_handler = get_error_handler()
            self._error_handler.set_callbacks(
                on_error=self._on_error_callback,
                on_recover=self._on_recover_callback
            )
    
    def _on_error_callback(self, error_info):
        """Callback cuando ocurre un error"""
        self._error_info = error_info
        # Si el error es crítico, cambiar a pantalla de error
        if error_info.get("severidad", 0) >= 2:  # ERROR o CRITICAL
            self._pre_error_state = self.state
            self.state = CareerState.ERROR
    
    def _on_recover_callback(self):
        """Callback cuando se recupera de un error"""
        self._error_info = None
    
    # === LCD HELPERS ===
    
    def _lcd_clear(self):
        """Limpia buffer LCD"""
        for y in range(4):
            for x in range(20):
                self.lcd_buffer[y][x] = ' '
    
    def _lcd_put(self, x, y, text):
        """Escribe texto en buffer"""
        text = convert_text(str(text))
        for i, char in enumerate(text):
            if x + i < 20:
                self.lcd_buffer[y][x + i] = char
    
    def _lcd_centered(self, y, text):
        """Escribe texto centrado"""
        text = convert_text(str(text))[:20]
        x = (20 - len(text)) // 2
        self._lcd_put(x, y, text)
    
    def _lcd_render(self):
        """Renderiza buffer a LCD fisico"""
        for y in range(4):
            for x in range(20):
                if self.lcd_buffer[y][x] != self.lcd_shadow[y][x]:
                    self.lcd.move_to(x, y)
                    self.lcd.putchar(self.lcd_buffer[y][x])
                    self.lcd_shadow[y][x] = self.lcd_buffer[y][x]
    
    def _lcd_force_clear(self):
        """Fuerza limpieza completa"""
        self.lcd.clear()
        for y in range(4):
            for x in range(20):
                self.lcd_shadow[y][x] = ' '
    
    def _wrap_text(self, text, width=20):
        """Divide texto en lineas"""
        text = convert_text(str(text))
        words = text.split()
        lines = []
        current = ""
        
        for word in words:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= width:
                current += " " + word
            else:
                lines.append(current)
                current = word
        
        if current:
            lines.append(current)
        
        return lines if lines else [""]
    
    # === INPUT ===
    
    def _get_input(self):
        """Lee input de botones, incluyendo combo UP+DOWN para volver"""
        # Leer estado inicial de botones
        up_pressed = self.btn_up.value() == 0
        down_pressed = self.btn_down.value() == 0
        select_pressed = self.btn_select.value() == 0
        
        # Si ningún botón presionado, salir rápido
        if not up_pressed and not down_pressed and not select_pressed:
            return None
        
        # Si UP o DOWN está presionado, esperar un poco para ver si el otro también
        if up_pressed or down_pressed:
            time.sleep(0.05)  # 50ms para detectar combo
            up_pressed = self.btn_up.value() == 0
            down_pressed = self.btn_down.value() == 0
            
            # Detectar combo UP+DOWN = BACK
            if up_pressed and down_pressed:
                time.sleep(0.15)  # Debounce adicional
                return 'BACK'
        
        # Botón individual
        if select_pressed:
            time.sleep(0.15)
            return 'SELECT'
        if up_pressed:
            time.sleep(0.15)
            return 'UP'
        if down_pressed:
            time.sleep(0.15)
            return 'DOWN'
        
        return None
    
    def _scroll_text(self, text, max_width, offset):
        """
        Genera texto con scroll lateral para textos largos.
        """
        text = convert_text(str(text))
        
        # Protección contra max_width inválido
        if max_width <= 0:
            return ""
        
        if len(text) <= max_width:
            # Padding manual en vez de ljust
            result = text
            while len(result) < max_width:
                result = result + " "
            return result
        
        # Scroll simple: desplazar 1 char cada 6 frames
        scroll_speed = 6
        pause_frames = 18  # 1.5 segundos de pausa al inicio
        
        # Ciclo total: pausa + scroll completo + pausa
        scroll_range = len(text) - max_width + 1
        cycle_len = pause_frames + (scroll_range * scroll_speed) + pause_frames
        
        pos = offset % cycle_len
        
        if pos < pause_frames:
            start = 0
        elif pos >= cycle_len - pause_frames:
            start = 0
        else:
            scroll_pos = pos - pause_frames
            start = scroll_pos // scroll_speed
            if start > scroll_range - 1:
                start = scroll_range - 1
        
        result = text[start:start + max_width]
        # Padding manual
        while len(result) < max_width:
            result = result + " "
        return result
    
    def _register_activity(self):
        """Registra actividad para backlight. NO enciende automaticamente."""
        self.last_activity = time.time()
    
    def _wake_up(self):
        """Enciende backlight y LEDs de botones"""
        if not self.backlight_on:
            self.backlight_on = True
            self.lcd.backlight_on()
            self._leds_on()
    
    def _leds_on(self):
        """Enciende LEDs de botones"""
        self.led_up.value(1)
        self.led_select.value(1)
        self.led_down.value(1)
    
    def _leds_off(self):
        """Apaga LEDs de botones"""
        self.led_up.value(0)
        self.led_select.value(0)
        self.led_down.value(0)
    
    def _leds_scroll(self, can_up, can_down):
        """Actualiza LEDs segun scroll disponible"""
        self.led_up.value(1 if can_up else 0)
        self.led_select.value(1)
        self.led_down.value(1 if can_down else 0)
    
    def _leds_select_only(self):
        """Solo LED select encendido"""
        self.led_up.value(0)
        self.led_select.value(1)
        self.led_down.value(0)
    
    # === BACKLIGHT ===
    
    def _check_backlight(self):
        """Verifica timeout de backlight"""
        if not self.backlight_on:
            return
        
        if not self.data:
            return
        
        timeout = get_backlight_timeout(self.data)
        elapsed = time.time() - self.last_activity
        
        if elapsed > timeout and self.state == CareerState.SCREENSAVER:
            self.backlight_on = False
            self.lcd.backlight_off()
            self._leds_off()
    
    # === NOTIFICACION ===
    
    def _update_notification(self):
        """Actualiza LED de notificacion"""
        if not self.data:
            self.led_notify.value(0)
            return
        
        if is_quiet_hours():
            self.led_notify.value(0)
            return
        
        if count_mensajes_pendientes(self.data) > 0:
            self.blink_counter += 1
            if self.blink_counter >= 10:
                self.blink_counter = 0
                self.blink_state = not self.blink_state
            self.led_notify.value(self.blink_state)
        else:
            self.led_notify.value(0)
    
    # === ESTADOS ===
    
    def _update_init(self, key):
        """Estado: Inicializacion"""
        self._lcd_clear()
        self._lcd_centered(0, "MI CONSULTA")
        self._lcd_centered(2, "Cargando...")
        
        # LEDs apagados durante carga
        self._leds_off()
        
        if self.frame == 1:
            # Cargar datos
            self.data = load_career()
            
            # Sincronizar hora
            sync_time()
            
            # Verificar setup
            if not is_setup_complete(self.data):
                self.state = CareerState.SETUP_TITULO
            else:
                # Verificar nuevo dia
                check_new_day(self.data)
                generate_daily_schedule(self.data)
                save_career(self.data)
                self.state = CareerState.SCREENSAVER
    
    def _update_setup_titulo(self, key):
        """Estado: Seleccion de titulo"""
        self._lcd_clear()
        self._lcd_centered(0, "ELIGE TU TITULO")
        
        for i, titulo in enumerate(self.titulos):
            prefix = ">" if i == self.titulo_idx else " "
            self._lcd_put(4, i + 1, f"{prefix}{titulo}")
        
        # LEDs dinamicos
        can_up = self.titulo_idx > 0
        can_down = self.titulo_idx < 2
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.titulo_idx -= 1
        elif key == 'DOWN' and can_down:
            self.titulo_idx += 1
        elif key == 'SELECT':
            self.state = CareerState.SETUP_GENERATING
            self.frame = 0
    
    def _update_setup_generating(self, key):
        """Estado: Generando nombre"""
        self._lcd_clear()
        self._lcd_centered(0, "GENERANDO")
        self._lcd_centered(1, "TU IDENTIDAD...")
        
        dots = "." * ((self.frame // 5) % 4)
        self._lcd_centered(2, dots)
        
        # LEDs apagados durante generacion
        self._leds_off()
        
        if self.frame == 1:
            titulo = self.titulos[self.titulo_idx]
            self.nombre_generado = generate_doctor_name(titulo)
            
            if not self.nombre_generado:
                self.nombre_generado = "Frasquito"
            
            self.state = CareerState.SETUP_CONFIRM
    
    def _update_setup_confirm(self, key):
        """Estado: Confirmar nombre"""
        titulo = self.titulos[self.titulo_idx]
        
        self._lcd_clear()
        self._lcd_centered(0, "TU NOMBRE ES:")
        self._lcd_centered(1, f"{titulo}")
        self._lcd_centered(2, self.nombre_generado)
        self._lcd_centered(3, "[OK] Aceptar")
        
        # Solo LED select
        self._leds_select_only()
        
        if key == 'SELECT':
            # Guardar nombre
            set_player_name(self.data, titulo, self.nombre_generado)
            
            # Inicializar stats
            self.data["jugador"]["stats"]["fecha_inicio"] = get_today_str()
            set_ultimo_dia_jugado(self.data, get_today_str())
            
            # Generar pacientes iniciales
            self.state = CareerState.GENERANDO
            self._generating_task = "pacientes_iniciales"
            self._generating_count = 0
            self.frame = 0
    
    def _update_generando(self, key):
        """Estado: Generando contenido"""
        self._lcd_clear()
        
        # LEDs apagados durante generacion
        self._leds_off()
        
        # Frases de espera rotativas
        frases_paciente = [
            "Revisando historial",
            "Leyendo expediente",
            "Analizando caso",
            "Consultando archivo",
            "Buscando paciente"
        ]
        frases_mensaje = [
            "Paciente escribiendo",
            "Recibiendo mensaje",
            "Conectando linea",
            "Esperando respuesta",
            "Linea ocupada"
        ]
        frases_inicio = [
            "Abriendo consulta",
            "Preparando agenda",
            "Fichando entrada",
            "Encendiendo luces",
            "Calentando cafe"
        ]
        
        dots = "." * ((self.frame // 5) % 4)
        frase_idx = (self.frame // 15) % 5
        
        if self._generating_task == "pacientes_iniciales":
            self._lcd_centered(0, "SALA DE ESPERA")
            self._lcd_centered(1, frases_inicio[frase_idx])
            self._lcd_centered(2, f"Paciente {self._generating_count+1}/3{dots}")
            
            if self.frame == 1 or (self.frame > 10 and self._generating_count < 3):
                pacientes_actuales = get_pacientes(self.data)
                paciente = generate_new_patient(
                    nivel_dificultad=1,
                    pacientes_existentes=pacientes_actuales,
                    tipo_paciente="normal"
                )
                if paciente:
                    add_paciente(self.data, paciente)
                    
                    # Generar primer mensaje
                    msg = generate_intro_message(paciente)
                    if msg:
                        msg["timestamp"] = get_timestamp()
                        add_mensaje(self.data, msg)
                    
                    self._generating_count += 1
                
                if self._generating_count >= 3:
                    set_setup_complete(self.data, True)
                    # Generar evento inicial
                    self._evento_actual = generar_evento_diario(self.data)
                    self._evento_mostrado = False
                    save_career(self.data)
                    generate_daily_schedule(self.data)
                    # Ir al tutorial inicial
                    self._tutorial_page = 0
                    self.state = CareerState.TUTORIAL_INICIO
        
        elif self._generating_task == "nuevo_paciente":
            self._lcd_centered(0, "SALA DE ESPERA")
            self._lcd_centered(1, frases_paciente[frase_idx])
            self._lcd_centered(2, f"Nuevo paciente{dots}")
            
            if self.frame == 1:
                pacientes_actuales = get_pacientes(self.data)
                
                # Seleccionar tipo de paciente
                tipo = seleccionar_tipo_paciente(self.data)
                
                paciente = generate_new_patient(
                    nivel_dificultad=get_nivel(self.data),
                    pacientes_existentes=pacientes_actuales,
                    tipo_paciente=tipo
                )
                if paciente:
                    # Aplicar modificadores del tipo
                    aplicar_modificadores_paciente(paciente, tipo, self.data)
                    
                    pid = add_paciente(self.data, paciente)
                    increment_pacientes_nuevos_hoy(self.data)
                    
                    msg = generate_intro_message(paciente)
                    if msg:
                        msg["timestamp"] = get_timestamp()
                        add_mensaje(self.data, msg)
                    
                    save_career(self.data)
                    play_sound('nuevo_paciente')
                
                self.state = CareerState.SCREENSAVER
        
        elif self._generating_task == "mensaje_sesion":
            self._lcd_centered(0, "BUSCA SONANDO")
            self._lcd_centered(1, frases_mensaje[frase_idx])
            self._lcd_centered(2, dots)
            
            if self.frame == 1:
                paciente = self.paciente_actual
                if paciente:
                    msg = generate_session_message(
                        paciente, 
                        paciente.get("historial", []),
                        get_nivel(self.data)
                    )
                    if msg:
                        msg["timestamp"] = get_timestamp()
                        add_mensaje(self.data, msg)
                        save_career(self.data)
                        play_sound('mensaje')
                
                self.state = CareerState.SCREENSAVER
    
    def _update_screensaver(self, key):
        """Estado: Screensaver / Reloj"""
        # Verificar mensajes programados
        if self.frame % 30 == 0:
            triggered = check_scheduled_messages(self.data)
            for prog in triggered:
                if prog["paciente_id"] == -1:
                    # Nuevo paciente
                    self._generating_task = "nuevo_paciente"
                    self.state = CareerState.GENERANDO
                    self.frame = 0
                    return
                else:
                    # Mensaje de paciente existente
                    self.paciente_actual = get_paciente_by_id(self.data, prog["paciente_id"])
                    if self.paciente_actual and not has_mensaje_pendiente_de(self.data, prog["paciente_id"]):
                        self._generating_task = "mensaje_sesion"
                        self.state = CareerState.GENERANDO
                        self.frame = 0
                        return
        
        # Verificar nuevo dia y generar evento
        if self.frame % 600 == 0:
            if check_new_day(self.data):
                generate_daily_schedule(self.data)
                # Generar evento del día
                self._evento_actual = generar_evento_diario(self.data)
                self._evento_mostrado = False
                save_career(self.data)
        
        # Mostrar evento del día si no se ha visto
        if not self._evento_mostrado and self._evento_actual:
            evento_id = self._evento_actual.get("id", "")
            if evento_id and evento_id != "dia_normal":
                self.state = CareerState.EVENTO_DIA
                return
            else:
                self._evento_mostrado = True
        
        # Dibujar screensaver
        self._lcd_clear()
        
        jugador = get_player_info(self.data)
        titulo_corto = jugador["titulo"][:3]
        nombre_corto = jugador["nombre"][:12]
        
        # Linea 0: Titulo + nombre
        self._lcd_put(0, 0, f"{titulo_corto}. {nombre_corto}")
        
        # Linea 1: Fecha y hora
        fecha = get_date_str()
        hora = get_time_str()
        self._lcd_put(0, 1, f"{fecha}   {hora}")
        
        # Linea 2: Mensajes con indicador visual
        num_msgs = count_mensajes_pendientes(self.data)
        if num_msgs > 0:
            # Parpadeo para llamar atencion
            if (self.frame // 8) % 2 == 0:
                self._lcd_put(0, 2, f">> {num_msgs} MENSAJES <<")
            else:
                self._lcd_put(0, 2, f"   {num_msgs} mensajes   ")
        else:
            # Info alternativa cuando no hay mensajes
            stats = get_stats(self.data)
            pacientes = count_pacientes(self.data)
            racha = get_racha_actual(self.data)
            tips = [
                f"{pacientes} pacientes",
                f"{stats['pacientes_curados']} curados",
                f"Racha: {racha}" if racha > 0 else "Sin racha",
                "Consulta vacia" if pacientes == 0 else f"{get_dinero(self.data)}E"
            ]
            tip_idx = (self.frame // 30) % len(tips)
            self._lcd_centered(2, tips[tip_idx])
        
        # Linea 3: Nivel y rango
        nivel = get_nivel(self.data)
        rango = jugador.get("rango", "Becario")[:13]
        self._lcd_put(0, 3, f"Nv{nivel} {rango}")
        
        # LEDs: encendidos solo si backlight activo
        if self.backlight_on:
            self._leds_select_only()
        
        # Input
        if key:
            self._register_activity()
            if not self.backlight_on:
                # Primer toque: solo encender pantalla y LEDs
                self._wake_up()
            else:
                # Segundo toque: ir al menu
                self.state = CareerState.MENU_PRINCIPAL
                self.menu_idx = 0
    
    def _update_menu_principal(self, key):
        """Estado: Menu principal"""
        self._lcd_clear()
        
        num_msgs = count_mensajes_pendientes(self.data)
        dinero = get_dinero(self.data)
        num_items = count_inventario(self.data)
        num_logros = len(get_logros_desbloqueados(self.data))
        misiones = get_misiones_activas(self.data)
        num_misiones = len([m for m in misiones.get("diarias", []) + misiones.get("semanales", []) 
                          if not m.get("reclamada")])
        prestigio = get_prestigio(self.data)
        
        # Mostrar barra de estado en línea 0
        # Formato adaptativo: dinero | racha | prestigio | inv
        status_parts = []
        status_parts.append(f"{dinero}E")
        
        racha = get_racha_actual(self.data)
        if racha >= 3:
            status_parts.append(f"x{racha}")
        
        if prestigio["nivel"] > 0:
            status_parts.append(f"P{prestigio['nivel']}")
        
        status_parts.append(f"[{num_items}]")
        
        # Unir con espacios y truncar a 20
        status_line = " ".join(status_parts)[:20]
        self._lcd_put(0, 0, status_line)
        
        # Construir opciones dinámicamente
        opciones = [
            ("mensajes", f"Mensajes ({num_msgs})"),
            ("pacientes", "Pacientes"),
            ("camello", "El Camello"),
            ("mejoras", "Mejoras"),
            ("logros", f"Logros ({num_logros})"),
            ("misiones", f"Misiones ({num_misiones})"),
            ("inventario", "Inventario"),
        ]
        
        # Opciones condicionales
        if tiene_mejora(self.data, "mesa_crafting"):
            opciones.append(("crafting", "Crafting"))
        if tiene_mejora(self.data, "ruleta"):
            opciones.append(("apuestas", "Apuestas"))
        if tiene_mejora(self.data, "album_familia"):
            caso_activo = get_caso_activo(self.data)
            if caso_activo:
                opciones.append(("casos", f"Caso: {caso_activo['nombre'][:8]}"))
            else:
                opciones.append(("casos", "Casos Familiares"))

        # Torneos siempre disponibles
        torneo_activo = self.data.get("torneo_activo")
        if torneo_activo:
            opciones.append(("torneos", f"Torneo: {torneo_activo['nombre'][:7]}"))
        else:
            opciones.append(("torneos", "Torneos"))

        opciones.append(("batas", "Vestuario"))
        opciones.append(("prestigio", f"Prestigio [{prestigio['nivel']}]"))
        opciones.append(("stats", "Estadisticas"))
        opciones.append(("opciones", "Opciones"))
        opciones.append(("ayuda", "Ayuda"))
        opciones.append(("volver", "Volver"))
        opciones.append(("salir", "Salir"))
        
        # Mostrar 3 opciones (dejamos línea 0 para dinero)
        for i in range(3):
            idx = self.scroll_idx + i
            if idx < len(opciones):
                prefix = ">" if idx == self.menu_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}{opciones[idx][1][:19]}")
        
        # LEDs dinamicos
        can_up = self.menu_idx > 0
        can_down = self.menu_idx < len(opciones) - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.menu_idx -= 1
            if self.menu_idx < self.scroll_idx:
                self.scroll_idx = self.menu_idx
        elif key == 'DOWN' and can_down:
            self.menu_idx += 1
            if self.menu_idx >= self.scroll_idx + 3:
                self.scroll_idx = self.menu_idx - 2
        elif key == 'SELECT':
            accion = opciones[self.menu_idx][0]
            
            if accion == "mensajes":
                self.state = CareerState.LISTA_MENSAJES
                self.scroll_idx = 0
            elif accion == "pacientes":
                self.state = CareerState.LISTA_PACIENTES
                self.scroll_idx = 0
            elif accion == "camello":
                if not tutorial_visto(self.data, "tienda"):
                    self._tutorial_page = 0
                    self.state = CareerState.TUTORIAL_CAMELLO
                else:
                    self._tienda_idx = 0
                    self._tienda_scroll = 0
                    self.state = CareerState.TIENDA
            elif accion == "mejoras":
                self._mejoras_idx = 0
                self._mejoras_scroll = 0
                self.state = CareerState.MEJORAS
            elif accion == "logros":
                self._logros_idx = 0
                self._logros_scroll = 0
                self.state = CareerState.LOGROS
            elif accion == "misiones":
                self._misiones_tab = 0
                self._misiones_idx = 0
                self.state = CareerState.MISIONES
            elif accion == "inventario":
                self._inv_idx = 0
                self.state = CareerState.INVENTARIO
            elif accion == "crafting":
                self._craft_idx = 0
                self.state = CareerState.CRAFTING
            elif accion == "apuestas":
                self._apuesta_cantidad = 50
                self.state = CareerState.APUESTAS
            elif accion == "casos":
                self._caso_idx = 0
                self.state = CareerState.CASO_FAMILIAR
            elif accion == "torneos":
                self._torneo_idx = 0
                self.state = CareerState.TORNEO
            elif accion == "batas":
                self._bata_idx = 0
                self._bata_scroll = 0
                self.state = CareerState.BATAS
            elif accion == "prestigio":
                self.state = CareerState.PRESTIGIO
            elif accion == "stats":
                self._stats_pagina = 0
                self.state = CareerState.ESTADISTICAS
            elif accion == "opciones":
                self._opciones_idx = 0
                self.state = CareerState.OPCIONES
            elif accion == "ayuda":
                self._tutorial_page = 0
                self.state = CareerState.AYUDA
            elif accion == "volver":
                # Registrar actividad antes de volver a SCREENSAVER
                self._register_activity()
                self._wake_up()
                self.state = CareerState.SCREENSAVER
                self.scroll_idx = 0
                self.menu_idx = 0
            elif accion == "salir":
                save_career(self.data)
                self.exit_requested = True
        elif key == 'BACK':
            # Registrar actividad antes de volver a SCREENSAVER
            self._register_activity()
            self._wake_up()
            self.state = CareerState.SCREENSAVER
            self.scroll_idx = 0
            self.menu_idx = 0
    
    def _update_lista_mensajes(self, key):
        """Estado: Lista de mensajes pendientes"""
        mensajes = get_mensajes_pendientes(self.data)
        
        self._lcd_clear()
        
        if not mensajes:
            self._lcd_centered(0, "BANDEJA VACIA")
            self._lcd_centered(1, "----------------")
            self._lcd_centered(2, "Sin mensajes")
            self._lcd_centered(3, "[OK] Volver")
            self._leds_select_only()
            
            if key == 'SELECT':
                self.state = CareerState.MENU_PRINCIPAL
            return
        
        # Titulo
        self._lcd_put(0, 0, f"MENSAJES ({len(mensajes)})")
        
        # Lista con opcion Volver al final
        total_items = len(mensajes) + 1
        
        # Mostrar 2 items (dejamos linea para titulo y controles)
        for i in range(min(2, total_items - self.scroll_idx)):
            item_idx = self.scroll_idx + i
            prefix = ">" if i == 0 else " "
            
            if item_idx < len(mensajes):
                msg = mensajes[item_idx]
                paciente = get_paciente_by_id(self.data, msg["paciente_id"])
                nombre = paciente["nombre"][:12] if paciente else "???"
                # Indicador de tipo (nuevo vs sesion)
                sesion = paciente["sesiones_completadas"] if paciente else 0
                icono = "*" if sesion == 0 else " "
                self._lcd_put(0, 1 + i, f"{prefix}{icono}{nombre}")
            else:
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")
        
        # Linea 3: instrucciones
        self._lcd_put(0, 3, "[OK]Leer [^v]Nav")
        
        # LEDs dinamicos
        can_up = self.scroll_idx > 0
        can_down = self.scroll_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.scroll_idx -= 1
        elif key == 'DOWN' and can_down:
            self.scroll_idx += 1
        elif key == 'SELECT':
            if self.scroll_idx < len(mensajes):
                self.mensaje_actual = mensajes[self.scroll_idx]
                self.paciente_actual = get_paciente_by_id(self.data, self.mensaje_actual["paciente_id"])
                self.state = CareerState.LEYENDO_MENSAJE
                self.scroll_idx = 0
            else:
                self.state = CareerState.MENU_PRINCIPAL
                self.scroll_idx = 0
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
            self.scroll_idx = 0
    
    def _update_leyendo_mensaje(self, key):
        """Estado: Leyendo mensaje de paciente"""
        if not self.mensaje_actual or not self.paciente_actual:
            self.state = CareerState.LISTA_MENSAJES
            return
        
        self._lcd_clear()
        
        # Preparar texto con indicador de sesión
        p = self.paciente_actual
        nombre = p["nombre"][:6]
        sesion = f"{p['sesiones_completadas']+1}/{p['sesiones_totales']}"
        
        # Mini barra de progreso (4 chars)
        progreso = p.get("progreso", 0)
        filled = max(0, min(4, int((progreso + 3) * 4 / 6)))
        mini_bar = "=" * filled + "-" * (4 - filled)
        
        # Línea 0: Nombre [ses] ====
        # Max: 6 + 1 + 5 + 1 + 1 + 4 + 1 = 19 chars
        header = f"{nombre} [{sesion}] {mini_bar}"
        
        contenido = self.mensaje_actual["contenido"]
        
        lines = [header]
        lines.extend(self._wrap_text(contenido))
        
        # Mostrar 4 lineas con scroll
        for i in range(4):
            if self.scroll_idx + i < len(lines):
                self._lcd_put(0, i, lines[self.scroll_idx + i][:20])
        
        can_down = (self.scroll_idx + 4) < len(lines)
        can_up = self.scroll_idx > 0
        
        # LEDs dinamicos
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.scroll_idx -= 1
        elif key == 'DOWN' and can_down:
            self.scroll_idx += 1
        elif key == 'SELECT':
            self.state = CareerState.ELIGIENDO_RESPUESTA
            self.selected_option = 0
            self.opt_scroll = 0
    
    def _update_eligiendo_respuesta(self, key):
        """Estado: Eligiendo respuesta"""
        if not self.mensaje_actual:
            self.state = CareerState.LISTA_MENSAJES
            return
        
        self._lcd_clear()
        
        opciones = self.mensaje_actual.get("opciones", [])
        correcta = self.mensaje_actual.get("correcta", 0)
        pid = self.paciente_actual["id"] if self.paciente_actual else 0
        efectos = get_efectos_activos(self.data, pid)
        
        # Efecto: revelar respuesta
        revela = "revela" in efectos
        
        # Efecto: eliminar opción incorrecta
        opcion_eliminada = -1
        if "elimina_opcion" in efectos:
            # Encontrar una opción incorrecta al azar para tachar
            import random
            incorrectas = [i for i in range(len(opciones)) if i != correcta]
            if incorrectas:
                opcion_eliminada = random.choice(incorrectas)
                # Eliminar el efecto después de usarlo (solo una vez)
                remove_efecto_paciente(self.data, pid, "elimina_opcion")
        
        for i in range(min(4, len(opciones))):
            text = convert_text(opciones[i])
            
            # Indicadores especiales
            if revela and i == correcta:
                prefix = "*"  # Marca la correcta
            elif i == opcion_eliminada:
                prefix = "X"  # Tachada
                text = "---TACHADA---"
            elif i == self.selected_option:
                prefix = ">"
            else:
                prefix = " "
            
            # Scroll horizontal para opcion larga
            if i == self.selected_option and len(text) > 18:
                offset = max(0, (self.opt_scroll // 3) - 2) % (len(text) - 17 + 3)
                if offset > len(text) - 18:
                    offset = len(text) - 18
                text = text[offset:offset + 18]
            
            self._lcd_put(0, i, f"{prefix}{text[:19]}")
        
        # LEDs dinamicos
        can_up = self.selected_option > 0
        can_down = self.selected_option < len(opciones) - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.selected_option -= 1
            self.opt_scroll = 0
        elif key == 'DOWN' and can_down:
            self.selected_option += 1
            self.opt_scroll = 0
        elif key == 'SELECT':
            # No permitir seleccionar opción eliminada
            if self.selected_option == opcion_eliminada:
                pass  # Ignorar
            else:
                self._process_answer()
    
    def _process_answer(self):
        """Procesa la respuesta seleccionada"""
        correcta = self.mensaje_actual.get("correcta", 0)
        es_correcto = (self.selected_option == correcta)
        pid = self.paciente_actual["id"] if self.paciente_actual else 0
        efectos = get_efectos_activos(self.data, pid)
        
        self.last_correct = es_correcto
        self._racha_texto = None
        
        # === RACHAS ===
        if es_correcto:
            racha_info = incrementar_racha(self.data, "aciertos")
            self._racha_info = racha_info
            if racha_info.get("texto"):
                self._racha_texto = racha_info["texto"]
        else:
            romper_racha(self.data, "aciertos")
            self._racha_info = None
        
        # === MULTIPLICADORES DE MEJORAS ===
        xp_mult_mejora = get_efecto_mejoras(self.data, "xp_mult")
        if not xp_mult_mejora:
            xp_mult_mejora = 1.0
        dinero_mult_mejora = get_efecto_mejoras(self.data, "dinero_mult")
        if not dinero_mult_mejora:
            dinero_mult_mejora = 1.0
        bonus_sesion = get_efecto_mejoras(self.data, "bonus_sesion")
        if not bonus_sesion:
            bonus_sesion = 0
        
        # Multiplicador de racha
        racha_mult = self._racha_info.get("multiplicador", 1.0) if self._racha_info else 1.0
        
        # Calcular XP (con posible doble por fármaco)
        xp_mult = 2 if "doble_xp" in efectos else 1
        if "doble_xp" in efectos:
            remove_efecto_paciente(self.data, pid, "doble_xp")
        
        # Efecto protege_fallo
        protegido = "protege_fallo" in efectos and not es_correcto
        if protegido:
            remove_efecto_paciente(self.data, pid, "protege_fallo")
        
        # Mejora: primer fallo gratis
        primer_fallo_gratis = tiene_mejora(self.data, "seguridad") and not es_correcto
        historial = self.paciente_actual.get("historial", [])
        if primer_fallo_gratis and len([h for h in historial if not h.get("correcto", True)]) == 0:
            protegido = True
        
        if es_correcto:
            self.last_feedback = self.mensaje_actual.get("feedback_correcto", "Bien")
            xp_ganada = int(XP_SESION_CORRECTA * xp_mult * xp_mult_mejora)
            add_xp(self.data, xp_ganada)
            increment_stat(self.data, "sesiones_correctas")

            # Dinero con multiplicadores
            dinero_base = int((DINERO_SESION_OK + bonus_sesion) * dinero_mult_mejora * racha_mult)
            self._dinero_ganado = dinero_base
            add_dinero(self.data, dinero_base)

            # Verificar combos al acertar
            combos_acierto = check_combo(self.data, self.paciente_actual, "acierto")
            if combos_acierto:
                for combo_id in combos_acierto:
                    combo_resultado = aplicar_combo(self.data, combo_id)
                    if combo_resultado:
                        self._combo_actual = combo_resultado

            # Registrar racha en torneo si activo
            if self.data.get("torneo_activo"):
                racha = get_racha_actual(self.data)
                registrar_accion_torneo(self.data, "racha", racha)

            # Mostrar racha en feedback
            if self._racha_texto:
                self.last_feedback = self._racha_texto
        else:
            self.last_feedback = self.mensaje_actual.get("feedback_incorrecto", "Mal")
            if not protegido:
                add_xp(self.data, XP_SESION_INCORRECTA)
            else:
                self.last_feedback += " (Protegido)"
            increment_stat(self.data, "sesiones_incorrectas")
            
            # Dinero (menos pero algo)
            dinero_base = int((DINERO_SESION_MAL + bonus_sesion) * dinero_mult_mejora)
            self._dinero_ganado = dinero_base
            add_dinero(self.data, dinero_base)
        
        # Limpiar efecto revela si se usó
        if "revela" in efectos:
            remove_efecto_paciente(self.data, pid, "revela")
        
        # Actualizar paciente (con protección si aplica)
        if protegido:
            # No actualizar progreso negativo
            resultado = {"estado": "continua"}
            self.paciente_actual["sesiones_completadas"] += 1
        else:
            # Verificar efecto no_huir
            no_huir = "no_huir" in efectos
            
            # Mejora caja_fuerte: no pierdes dinero si huyen
            protege_huida_dinero = tiene_mejora(self.data, "caja_fuerte")
            
            resultado = update_paciente_progreso(
                self.data, 
                self.paciente_actual["id"],
                es_correcto
            )
            # Si iba a huir pero tiene efecto no_huir
            if resultado["estado"] == "abandona" and no_huir:
                resultado["estado"] = "continua"
                self.paciente_actual["progreso"] = -2  # Lo dejamos al borde
                remove_efecto_paciente(self.data, pid, "no_huir")
                self.last_feedback += " (No huye!)"
        
        # Registrar en historial
        sesion_num = self.paciente_actual.get("sesiones_completadas", 0) + 1
        opciones = self.mensaje_actual.get("opciones", [])
        opcion_texto = opciones[self.selected_option] if self.selected_option < len(opciones) else "?"
        
        add_historial_paciente(
            self.data,
            self.paciente_actual["id"],
            get_today_str(),
            get_time_str(),
            self.selected_option,
            es_correcto,
            sesion_num,
            opcion_texto
        )
        
        # Eliminar mensaje
        remove_mensaje(self.data, self.mensaje_actual["id_mensaje"])
        
        # Verificar estado del paciente
        if resultado["estado"] == "curado":
            xp_bonus = int((XP_CURAR_PACIENTE_BASE + self.paciente_actual["sesiones_totales"]) * xp_mult * xp_mult_mejora)
            level_result = add_xp(self.data, xp_bonus)
            increment_stat(self.data, "pacientes_curados")
            
            # Racha de curados
            incrementar_racha(self.data, "curados")
            
            # Comprobar cura perfecta (sin fallos)
            fallos = len([h for h in self.paciente_actual.get("historial", []) if not h.get("correcto", True)])
            if fallos == 0:
                registrar_stat_logro(self.data, "curas_perfectas")
            
            # Dinero bonus por curar
            dinero_bonus = int((DINERO_CURAR_BASE + (self.paciente_actual["sesiones_totales"] * 20)) * dinero_mult_mejora)
            
            # Multiplicador por tipo de paciente
            tipo_mult = self.paciente_actual.get("dinero_mult", 1.0)
            dinero_bonus = int(dinero_bonus * tipo_mult)
            
            add_dinero(self.data, dinero_bonus)
            self._dinero_ganado += dinero_bonus
            
            # Stats para logros por tipo
            tipo = self.paciente_actual.get("tipo", "normal")
            if tipo == "vip":
                registrar_stat_logro(self.data, "vips_curados")
            elif tipo == "influencer":
                registrar_stat_logro(self.data, "influencers_curados")
            elif tipo == "misterioso":
                registrar_stat_logro(self.data, "misteriosos_curados")

            # === VERIFICAR COMBOS AL CURAR ===
            combos_activados = check_combo(self.data, self.paciente_actual, "curar")
            if combos_activados:
                for combo_id in combos_activados:
                    combo_resultado = aplicar_combo(self.data, combo_id)
                    if combo_resultado:
                        self._combo_actual = combo_resultado
                        # El combo se mostrará después del resultado

            # === GENERAR REGALO DE PACIENTE ===
            regalo = generar_regalo_paciente(self.data, self.paciente_actual)
            if regalo:
                self._regalo_actual = regalo

            # === REGISTRAR EN TORNEO SI ACTIVO ===
            if self.data.get("torneo_activo"):
                registrar_accion_torneo(self.data, "curar")
                registrar_accion_torneo(self.data, "dinero", dinero_bonus)

            # === VERIFICAR VISITA DEL ORÁCULO ===
            if generar_visita_oraculo(self.data):
                self._visita_oraculo = True

            remove_paciente(self.data, self.paciente_actual["id"])
            clear_efectos_paciente(self.data, pid)

            if level_result["nivel_cambio"] == 1:
                nuevo_rango = generate_rank_name(level_result["nuevo_nivel"])
                set_rango(self.data, nuevo_rango)
                self.level_up_info = {
                    "nivel": level_result["nuevo_nivel"],
                    "rango": nuevo_rango
                }

            self.state = CareerState.RESULTADO_PACIENTE
            self._resultado_tipo = "curado"
            
        elif resultado["estado"] == "abandona":
            add_xp(self.data, XP_PACIENTE_ABANDONA)
            increment_stat(self.data, "pacientes_abandonados")
            
            # Romper racha de curados
            romper_racha(self.data, "curados")
            
            remove_paciente(self.data, self.paciente_actual["id"])
            clear_efectos_paciente(self.data, pid)
            
            # Penalización de dinero (si no tiene caja fuerte)
            if not tiene_mejora(self.data, "caja_fuerte"):
                add_dinero(self.data, DINERO_HUYE)
                self._dinero_ganado = DINERO_HUYE
            else:
                self._dinero_ganado = 0
            
            self.state = CareerState.RESULTADO_PACIENTE
            self._resultado_tipo = "abandona"
        else:
            self.state = CareerState.FEEDBACK
        
        # === VERIFICAR LOGROS ===
        nuevos_logros = check_logros(self.data)
        if nuevos_logros:
            self._logros_pendientes.extend(nuevos_logros)
        
        save_career(self.data)
        self.frame = 0
    
    def _update_feedback(self, key):
        """Estado: Mostrando feedback con scroll para textos largos"""
        # Sonido al inicio
        if self.frame == 1:
            if self.last_correct:
                play_sound('correcto')
            else:
                play_sound('incorrecto')

        # Preparar líneas de feedback en primera frame
        if self.frame <= 1:
            self._feedback_lines = []
            self._feedback_scroll = 0

            # Título
            if self.last_correct:
                racha = get_racha_actual(self.data)
                if racha >= 3:
                    self._feedback_lines.append(f"x{racha} RACHA!")
                else:
                    self._feedback_lines.append("CORRECTO!")
            else:
                self._feedback_lines.append("INCORRECTO")

            # Feedback con wrap por palabras
            if self.last_feedback:
                fb_wrapped = self._wrap_text(self.last_feedback)
                self._feedback_lines.extend(fb_wrapped)

            # Línea de dinero
            racha_mult = self._racha_info.get("multiplicador", 1.0) if self._racha_info else 1.0
            if self._dinero_ganado > 0:
                dinero_txt = f"+{self._dinero_ganado}E"
            else:
                dinero_txt = f"{self._dinero_ganado}E"
            if racha_mult > 1.0 and self.last_correct:
                dinero_txt += f" (x{racha_mult:.1f})"
            self._feedback_lines.append("")
            self._feedback_lines.append(dinero_txt)

        self._lcd_clear()

        # Mostrar con scroll (3 líneas de contenido + 1 de controles)
        idx = self._feedback_scroll
        for i in range(3):
            if idx + i < len(self._feedback_lines):
                self._lcd_centered(i, self._feedback_lines[idx + i])

        # Indicadores de scroll y continuar
        can_up = idx > 0
        can_down = (idx + 3) < len(self._feedback_lines)

        if can_up or can_down:
            arrows = ""
            if can_up:
                arrows += "[^]"
            if can_down:
                arrows += "[v]"
            self._lcd_put(0, 3, arrows)
            self._lcd_put(14, 3, "[OK]>")
            self._leds_scroll(can_up, can_down)
        else:
            self._lcd_centered(3, "[OK] Continuar")
            self._leds_select_only()

        # Manejar scroll
        if key == 'UP' and can_up:
            self._feedback_scroll -= 1
            return
        elif key == 'DOWN' and can_down:
            self._feedback_scroll += 1
            return

        if key == 'SELECT':
            self._dinero_ganado = 0
            self._racha_info = None
            self._feedback_lines = []
            self._feedback_scroll = 0

            # Verificar si hay logros pendientes
            if self._logros_pendientes:
                self._logro_nuevo = self._logros_pendientes.pop(0)
                self.state = CareerState.LOGRO_DESBLOQUEADO
            elif self.level_up_info:
                self.state = CareerState.SUBIDA_NIVEL
            else:
                self.state = CareerState.LISTA_MENSAJES
                self.scroll_idx = 0
            self.mensaje_actual = None
    
    def _update_resultado_paciente(self, key):
        """Estado: Paciente curado o abandona - Con cierre narrativo"""
        # Debug
        if self.frame == 1:
            print(f"[CAREER] RESULTADO_PACIENTE: tipo={self._resultado_tipo}, paciente={self.paciente_actual is not None}")

        # Sonido al inicio
        if self.frame == 1:
            if self._resultado_tipo == "curado":
                play_sound('curado')
            else:
                play_sound('huye')
            # Inicializar página
            self._resultado_page = 0

        self._lcd_clear()

        # Seguridad: verificar que paciente_actual existe
        if not self.paciente_actual:
            print("[CAREER] ERROR: paciente_actual es None en RESULTADO_PACIENTE")
            self._register_activity()
            self._wake_up()
            self.state = CareerState.SCREENSAVER
            return

        p = self.paciente_actual
        nombre = p.get("nombre", "???")[:14]

        # Obtener cierre narrativo
        if self._resultado_tipo == "curado":
            cierre = p.get("cierre_curado", "")
        else:
            cierre = p.get("cierre_huye", "")
        
        # Página 0: Título + nombre + dinero
        # Página 1: Cierre narrativo (si existe)
        page = getattr(self, '_resultado_page', 0)
        
        if page == 0:
            if self._resultado_tipo == "curado":
                frases = ["PACIENTE CURADO!", "ALTA MEDICA!", "CASO CERRADO!", "TRATAMIENTO OK!"]
                self._lcd_centered(0, frases[(self.frame // 8) % len(frases)])
                self._lcd_centered(1, nombre)
                if self._dinero_ganado > 0:
                    self._lcd_centered(2, f"+{self._dinero_ganado}E")
                else:
                    self._lcd_centered(2, "Caso cerrado!")
            else:
                frases = ["PACIENTE HUYE!", "SE FUE!", "TE DEJA!", "ABANDONA!"]
                self._lcd_centered(0, frases[(self.frame // 8) % len(frases)])
                self._lcd_centered(1, nombre)
                self._lcd_centered(2, f"{DINERO_HUYE}E")
            
            # Indicador de página si hay cierre
            if cierre:
                self._lcd_put(0, 3, "[OK]")
                self._lcd_put(12, 3, "Mas >>")
            else:
                self._lcd_centered(3, "[OK] Continuar")
        else:
            # Página 1: Cierre narrativo con scroll
            self._lcd_centered(0, "== DESENLACE ==")

            # Wrap del cierre y scroll si es largo
            cierre_lines = self._wrap_text(cierre) if cierre else [""]
            cierre_scroll = getattr(self, '_cierre_scroll', 0)

            # Mostrar 2 líneas con scroll
            for i in range(2):
                if cierre_scroll + i < len(cierre_lines):
                    self._lcd_centered(i + 1, cierre_lines[cierre_scroll + i])

            # Indicadores de scroll
            can_up = cierre_scroll > 0
            can_down = (cierre_scroll + 2) < len(cierre_lines)

            if can_up or can_down:
                arrows = ""
                if can_up:
                    arrows += "[^]"
                if can_down:
                    arrows += "[v]"
                self._lcd_put(0, 3, arrows)
                self._lcd_put(14, 3, "[OK]>")
                self._leds_scroll(can_up, can_down)

                # Manejar scroll
                if key == 'UP' and can_up:
                    self._cierre_scroll = cierre_scroll - 1
                    return
                elif key == 'DOWN' and can_down:
                    self._cierre_scroll = cierre_scroll + 1
                    return
            else:
                self._lcd_centered(3, "[OK] Continuar")
        
        # Solo LED select
        self._leds_select_only()

        # Debug: mostrar si se detecta tecla
        if key:
            print(f"[CAREER] RESULTADO_PACIENTE: key={key}, page={page}, cierre={len(cierre) if cierre else 0}")

        if key == 'SELECT':
            print(f"[CAREER] SELECT presionado, page={page}, cierre={'SI' if cierre else 'NO'}")
            if page == 0 and cierre:
                # Ir a página de cierre
                self._resultado_page = 1
                self._cierre_scroll = 0  # Reset scroll
                self.frame = 0
            else:
                # Terminar
                print("[CAREER] Saliendo de RESULTADO_PACIENTE a SCREENSAVER")
                self._dinero_ganado = 0
                self._resultado_page = 0
                self._cierre_scroll = 0

                # Guardar antes de salir
                save_career(self.data)

                # Registrar actividad antes de volver a SCREENSAVER
                self._register_activity()
                self._wake_up()  # Asegurar backlight encendido

                # Verificar transiciones encadenadas
                next_state = self._get_next_state_after_result()
                self.state = next_state
                self.paciente_actual = None

        elif key == 'BACK' or key == 'UP' or key == 'DOWN':
            # Ruta de escape: cualquier otra tecla también permite salir
            print(f"[CAREER] Tecla escape {key} - forzando salida")
            self._dinero_ganado = 0
            self._resultado_page = 0

            # Guardar antes de salir
            save_career(self.data)

            # Registrar actividad antes de volver a SCREENSAVER
            self._register_activity()
            self._wake_up()

            # Verificar transiciones encadenadas
            next_state = self._get_next_state_after_result()
            self.state = next_state
            self.paciente_actual = None

    def _get_next_state_after_result(self):
        """Determina el siguiente estado después del resultado de paciente"""
        # Verificar regalo pendiente
        if hasattr(self, '_regalo_actual') and self._regalo_actual:
            print("[CAREER] -> REGALO_PACIENTE")
            return CareerState.REGALO_PACIENTE
        # Verificar combo pendiente
        if hasattr(self, '_combo_actual') and self._combo_actual:
            print("[CAREER] -> COMBO_ACTIVADO")
            return CareerState.COMBO_ACTIVADO
        # Verificar visita del oráculo
        if hasattr(self, '_visita_oraculo') and self._visita_oraculo:
            print("[CAREER] -> ORACULO")
            self._visita_oraculo = False
            return CareerState.ORACULO
        # Verificar subida de nivel
        if self.level_up_info:
            print("[CAREER] -> SUBIDA_NIVEL")
            return CareerState.SUBIDA_NIVEL
        # Por defecto, volver al screensaver
        print("[CAREER] -> SCREENSAVER")
        return CareerState.SCREENSAVER
    
    def _update_subida_nivel(self, key):
        """Estado: Subida de nivel con animación"""
        # Sonido al inicio
        if self.frame == 1:
            play_sound('level_up')
        
        self._lcd_clear()
        
        # Animación de celebración
        celebraciones = [
            "!! LEVEL UP !!",
            "** LEVEL UP **",
            "## LEVEL UP ##",
            "<< LEVEL UP >>",
        ]
        cel_idx = (self.frame // 4) % len(celebraciones)
        self._lcd_centered(0, celebraciones[cel_idx])
        
        nivel = self.level_up_info['nivel']
        rango = self.level_up_info['rango']
        
        self._lcd_centered(1, f"Nivel {nivel}")
        
        # Mostrar nuevo rango con efecto
        if self.frame < 20:
            # Revelación gradual
            visible = min(len(rango), self.frame // 2)
            rango_display = rango[:visible] + "_" * (len(rango) - visible)
            self._lcd_centered(2, rango_display)
        else:
            self._lcd_centered(2, rango)
        
        self._lcd_centered(3, "[OK] Continuar")
        
        # LEDs todos encendidos para celebrar
        self._leds_on()
        
        if key == 'SELECT':
            self.level_up_info = None

            # Registrar actividad antes de volver a SCREENSAVER
            self._register_activity()
            self._wake_up()  # Asegurar backlight encendido

            self.state = CareerState.SCREENSAVER
    
    def _update_lista_pacientes(self, key):
        """Estado: Lista de pacientes con mini-barras de progreso"""
        pacientes = get_pacientes(self.data)
        
        self._lcd_clear()
        
        if not pacientes:
            self._lcd_centered(1, "Sin pacientes")
            self._lcd_centered(3, "[OK] Volver")
            self._leds_select_only()
            
            if key == 'SELECT':
                self.state = CareerState.MENU_PRINCIPAL
            return
        
        # Lista con opcion Volver al final
        total_items = len(pacientes) + 1  # +1 para "Volver"
        
        # Función para mini-barra de 4 chars
        def mini_bar(progreso):
            # -3 a +3 → 0 a 4 bloques
            filled = max(0, min(4, (progreso + 3) * 4 // 6))
            return "=" * filled + "-" * (4 - filled)
        
        # Mostrar 3 items
        for i in range(min(3, total_items - self.scroll_idx)):
            item_idx = self.scroll_idx + i
            prefix = ">" if i == 0 else " "
            
            if item_idx < len(pacientes):
                p = pacientes[item_idx]
                nombre = p['nombre'][:8]
                bar = mini_bar(p.get('progreso', 0))
                sesiones = f"{p['sesiones_completadas']}/{p['sesiones_totales']}"
                # Formato: >NombreXX [====] 2/5
                self._lcd_put(0, i, f"{prefix}{nombre:<8}[{bar}]{sesiones}")
            else:
                # Opcion Volver
                self._lcd_put(0, i, f"{prefix}< Volver")
        
        self._lcd_put(0, 3, "[OK]Sel [^v]Nav")
        
        # LEDs dinamicos
        can_up = self.scroll_idx > 0
        can_down = self.scroll_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self.scroll_idx -= 1
        elif key == 'DOWN' and can_down:
            self.scroll_idx += 1
        elif key == 'SELECT':
            if self.scroll_idx < len(pacientes):
                self.paciente_actual = pacientes[self.scroll_idx]
                self.state = CareerState.VER_PACIENTE
                self.scroll_idx = 0
            else:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
                self.scroll_idx = 0
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
            self.scroll_idx = 0
    
    def _update_ver_paciente(self, key):
        """Estado: Ver detalles de paciente con páginas"""
        if not self.paciente_actual:
            self.state = CareerState.LISTA_PACIENTES
            return
        
        p = self.paciente_actual
        inv = get_inventario(self.data)
        historial = p.get("historial", [])
        
        # Calcular número de páginas
        # 0: Info personal, 1: Ocupación, 2: Progreso, 3: Historial, 4: Recetar (si inv)
        num_paginas = 4 if historial else 3  # Añadir historial si existe
        if inv:
            num_paginas += 1  # Página de recetar
        
        # Navegación entre páginas
        if key == 'UP':
            self._ver_pagina = max(0, self._ver_pagina - 1)
            self.opt_scroll = 0
            self._inv_idx = 0
        elif key == 'DOWN':
            self._ver_pagina = min(num_paginas - 1, self._ver_pagina + 1)
            self.opt_scroll = 0
        elif key == 'SELECT':
            # Página de recetar es la última si hay inventario
            pag_recetar = num_paginas - 1 if inv else -1
            if self._ver_pagina == pag_recetar and inv:
                # Usar fármaco
                item = inv[self._inv_idx]
                f = get_farmaco_by_id(item["id"])
                if f:
                    self._item_seleccionado = f
                    self.state = CareerState.USAR_ITEM
                    return
            else:
                self.state = CareerState.LISTA_PACIENTES
                self.paciente_actual = None
                self._ver_pagina = 0
                return
        elif key == 'BACK':
            self.state = CareerState.LISTA_PACIENTES
            self.paciente_actual = None
            self._ver_pagina = 0
            return
        
        self._lcd_clear()
        
        # Auto-scroll helper
        def scroll_text(text, max_len):
            text = convert_text(text)
            if len(text) > max_len:
                offset = (self.opt_scroll // 4) % (len(text) - max_len + 3)
                return text[offset:offset + max_len]
            return text[:max_len]
        
        # Barra de progreso ASCII [====----] 10 chars
        def progress_bar(progreso, width=10):
            # -3 a +3 → 0 a width bloques
            filled = max(0, min(width, int((progreso + 3) * width / 6)))
            return "[" + "=" * filled + "-" * (width - filled) + "]"
        
        if self._ver_pagina == 0:
            # Página 1: Info personal
            self._lcd_put(0, 0, scroll_text(p["nombre"], 20))
            self._lcd_put(0, 1, f"Edad: {scroll_text(p.get('edad', '?'), 14)}")
            self._lcd_put(0, 2, f"Sexo: {scroll_text(p.get('sexo', '?'), 14)}")
            self._lcd_put(0, 3, "[v]Mas       [OK]")
            
        elif self._ver_pagina == 1:
            # Página 2: Ocupación y caso
            self._lcd_put(0, 0, scroll_text(p.get("ocupacion", "?"), 20))
            self._lcd_put(0, 1, "--------------------")
            caso = p.get("problema_corto", "")
            self._lcd_put(0, 2, scroll_text(caso, 20))
            self._lcd_put(0, 3, "[^][v]       [OK]")
            
        elif self._ver_pagina == 2:
            # Página 3: Progreso con barra ASCII y tolerancia
            sesion_txt = f"{p['sesiones_completadas']}/{p['sesiones_totales']}"
            self._lcd_put(0, 0, f"{p['nombre'][:8]} {sesion_txt}")
            
            # Barra de progreso ASCII de 10 chars
            progreso = p.get("progreso", 0)
            bar = progress_bar(progreso, 10)
            estado = "Bien" if progreso > 1 else "Mal" if progreso < -1 else "Ok"
            self._lcd_put(0, 1, f"{bar} {estado}")
            
            # Tolerancia (errores restantes)
            tolerancia = p.get("tolerancia", 3)
            self._lcd_put(0, 2, f"Aguante: {tolerancia} errores")
            
            # Mostrar efectos activos
            efectos = get_efectos_activos(self.data, p["id"])
            if efectos:
                ef_str = ",".join(e[:3] for e in efectos[:3])
                self._lcd_put(0, 3, f"[{ef_str}]  [^v][OK]")
            else:
                self._lcd_put(0, 3, "[^][v]       [OK]")
        
        elif self._ver_pagina == 3 and historial:
            # Página 4: Historial de decisiones
            self._lcd_centered(0, "== HISTORIAL ==")
            
            # Mostrar últimas 3 decisiones
            ultimas = historial[-3:] if len(historial) >= 3 else historial
            for i, h in enumerate(ultimas):
                opcion = h.get("opcion_texto", "?")[:11]
                resultado = "OK" if h.get("correcto") else "X"
                sesion = h.get("sesion", i + 1)
                # Formato: 1.OpcionTexto OK (max 20)
                self._lcd_put(0, 1 + i, f"{sesion}.{opcion} [{resultado}]")
            
            if len(historial) < 3:
                # Rellenar líneas vacías
                for i in range(len(historial), 3):
                    if i < 2:  # Solo líneas 1-2
                        self._lcd_put(0, 1 + i, "")
            
            self._lcd_put(0, 3, "[^][v]       [OK]")
        
        # Página de recetar (última si hay inventario)
        pag_recetar = (4 if historial else 3) if inv else -1
        if self._ver_pagina == pag_recetar and inv:
            # Página N: Recetar fármaco
            self._lcd_centered(0, "RECETAR FARMACO")
            
            # Mostrar items disponibles
            for i in range(min(2, len(inv))):
                idx = self._inv_idx if i == 0 else min(self._inv_idx + 1, len(inv) - 1)
                if idx < len(inv):
                    item = inv[idx]
                    f = get_farmaco_by_id(item["id"])
                    if f:
                        prefix = ">" if idx == self._inv_idx else " "
                        self._lcd_put(0, 1 + i, f"{prefix}{f['nombre'][:14]} x{item['cantidad']}")
            
            self._lcd_put(0, 3, "[OK]Usar [^v]Nav")
            
            # Navegación dentro de inventario
            if key == 'UP' and self._inv_idx > 0:
                self._inv_idx -= 1
            elif key == 'DOWN' and self._inv_idx < len(inv) - 1:
                self._inv_idx += 1
        
        # LEDs dinámicos según página
        can_up = self._ver_pagina > 0
        can_down = self._ver_pagina < num_paginas - 1
        self._leds_scroll(can_up, can_down)
    
    def _update_estadisticas(self, key):
        """Estado: Ver estadisticas con páginas"""
        stats = get_stats(self.data)
        jugador = get_player_info(self.data)
        
        # Navegación entre páginas
        if key == 'UP':
            self._stats_pagina = max(0, self._stats_pagina - 1)
        elif key == 'DOWN':
            self._stats_pagina = min(3, self._stats_pagina + 1)
        elif key == 'SELECT' or key == 'BACK':
            self._stats_pagina = 0
            self.state = CareerState.MENU_PRINCIPAL
            return
        
        self._lcd_clear()
        
        if self._stats_pagina == 0:
            # Página 1: Pacientes
            self._lcd_centered(0, "-- PACIENTES --")
            self._lcd_put(0, 1, f"Curados: {stats['pacientes_curados']}")
            self._lcd_put(0, 2, f"Huidos: {stats['pacientes_abandonados']}")
            activos = count_pacientes(self.data)
            self._lcd_put(0, 3, f"Activos: {activos} [v]Mas")
            
        elif self._stats_pagina == 1:
            # Página 2: Sesiones
            self._lcd_centered(0, "-- SESIONES --")
            self._lcd_put(0, 1, f"OK: {stats['sesiones_correctas']}")
            self._lcd_put(0, 2, f"Mal: {stats['sesiones_incorrectas']}")
            total_ses = stats['sesiones_correctas'] + stats['sesiones_incorrectas']
            if total_ses > 0:
                tasa = (stats['sesiones_correctas'] * 100) // total_ses
                self._lcd_put(0, 3, f"Tasa: {tasa}%  [^][v]")
            else:
                self._lcd_put(0, 3, "Tasa: --   [^][v]")
        
        elif self._stats_pagina == 2:
            # Página 3: Nivel y XP
            self._lcd_centered(0, "-- PROGRESO --")
            self._lcd_put(0, 1, f"Nivel: {get_nivel(self.data)}")
            xp = get_xp(self.data)
            xp_next = get_xp_to_next(self.data)
            self._lcd_put(0, 2, f"XP: {xp}/{xp_next}")
            # Barra de progreso XP
            pct = (xp * 16) // xp_next if xp_next > 0 else 0
            barra = "=" * pct + "-" * (16 - pct)
            self._lcd_put(0, 3, barra[:16] + "[v]")
        
        else:
            # Página 4: Volver
            self._lcd_centered(0, "-- STATS --")
            self._lcd_centered(1, "")
            self._lcd_centered(2, "[OK] Volver")
            self._lcd_centered(3, "[^] Mas stats")
        
        # LEDs dinámicos
        can_up = self._stats_pagina > 0
        can_down = self._stats_pagina < 3
        self._leds_scroll(can_up, can_down)
    
    # === TIENDA EL CAMELLO ===
    
    def _update_tutorial_camello(self, key):
        """Tutorial del Camello - primera vez"""
        self._lcd_clear()
        
        paginas = [
            ["  EL CAMELLO  ", "----------------", "Bienvenido a la", "farmacia secreta"],
            ["Aqui vendemos", "medicinas para", "tus pacientes...", "sin receta!"],
            ["Ganas dinero por", "cada consulta y", "mas si curas al", "paciente"],
            ["Compra farmacos", "y usalos para", "facilitar las", "consultas"],
            ["Algunas drogas", "revelan respuesta", "otras reducen", "sesiones..."],
            ["Recuerda:", "Todo es ilegal", "pero efectivo!", "[OK] Empezar"]
        ]
        
        if self._tutorial_page >= len(paginas):
            marcar_tutorial(self.data, "tienda")
            save_career(self.data)
            self._tienda_idx = 0
            self._tienda_scroll = 0
            self.state = CareerState.TIENDA
            return
        
        pag = paginas[self._tutorial_page]
        for i, linea in enumerate(pag):
            self._lcd_centered(i, linea)
        
        self._leds_select_only()
        
        if key == 'SELECT':
            self._tutorial_page += 1
    
    def _update_tutorial_inicio(self, key):
        """Tutorial inicial - primera vez que juegas"""
        self._lcd_clear()
        
        paginas = [
            # Página 1: Bienvenida
            ["  MI CONSULTA  ", "================", "Bienvenido a tu", "consulta, Doctor!"],
            # Página 2: Objetivo
            ["   OBJETIVO    ", "Atiende pacientes", "Elige respuestas", "y gana dinero"],
            # Página 3: Pacientes
            ["   PACIENTES   ", "Te escriben con", "problemas raros", "Tu los 'ayudas'"],
            # Página 4: Respuestas
            ["  RESPUESTAS   ", "Elige la opcion", "mas PSICOTICA", "(pero sutil)"],
            # Página 5: Aciertos/Fallos
            ["  RESULTADOS   ", "Acierto: progreso", "Fallo: retroceso", "3 fallos = huye"],
            # Página 6: Curar
            ["    CURAR      ", "Completa todas", "las sesiones con", "progreso positivo"],
            # Página 7: Dinero
            ["    DINERO     ", "Ganas por sesion", "y bonus al curar", "Usalo en tienda!"],
            # Página 8: El Camello
            ["  EL CAMELLO   ", "Tienda secreta", "Compra farmacos", "para tus pacientes"],
            # Página 9: Fármacos
            ["   FARMACOS    ", "Revelan respuesta", "Reducen sesiones", "Protegen fallos"],
            # Página 10: Mejoras
            ["   MEJORAS     ", "Mejora tu consulta", "Sofa, diploma,", "decoracion..."],
            # Página 11: Logros
            ["    LOGROS     ", "Desbloquea logros", "por tus hazanas", "Gana recompensas!"],
            # Página 12: Misiones
            ["   MISIONES    ", "Diarias y semanales", "Cumplelas para", "bonus extra"],
            # Página 13: Subir nivel
            ["  SUBIR NIVEL  ", "Gana XP por sesion", "Sube de nivel y", "rango de doctor"],
            # Página 14: Controles
            ["   CONTROLES   ", "[^] Arriba/Navegar", "[v] Abajo/Navegar", "[OK] Seleccionar"],
            # Página 15: Final
            ["   LISTO!      ", "Ya puedes empezar", "Buena suerte,", "[OK] Jugar!"]
        ]
        
        if self._tutorial_page >= len(paginas):
            marcar_tutorial(self.data, "inicio")
            save_career(self.data)

            # Registrar actividad antes de volver a SCREENSAVER
            self._register_activity()
            self._wake_up()

            self.state = CareerState.SCREENSAVER
            return
        
        pag = paginas[self._tutorial_page]
        for i, linea in enumerate(pag):
            self._lcd_centered(i, linea)
        
        self._leds_select_only()
        
        if key == 'SELECT':
            self._tutorial_page += 1
    
    def _update_ayuda(self, key):
        """Pantalla de ayuda - accesible desde menú"""
        self._lcd_clear()
        
        paginas = [
            # Página 1: Resumen
            ["     AYUDA     ", "================", "Guia de Mi", "Consulta [OK]>>"],
            # Página 2: Objetivo
            ["   OBJETIVO    ", "Atiende pacientes", "Elige respuestas", "psicoticas"],
            # Página 3: Pacientes
            ["   PACIENTES   ", "Barra: -3 a +3", "+3 = curado", "3 fallos = huye"],
            # Página 4: Dinero
            ["    DINERO     ", "Por sesion: 5-15E", "Bonus curar: 20E", "Gasta en tienda"],
            # Página 5: El Camello
            ["  EL CAMELLO   ", "Farmacos:", "Aspirina=ver rpta", "Prozac=proteger"],
            # Página 6: Más fármacos
            ["  MAS FARMACOS ", "Valium=-1 sesion", "Rivotril=cura ya", "Y mas en tienda!"],
            # Página 7: Mejoras
            ["   MEJORAS     ", "Compra mejoras:", "Sofa=+tolerancia", "Diploma=+dinero"],
            # Página 8: Logros
            ["    LOGROS     ", "35 logros total", "Curar, rachas,", "niveles, gastar"],
            # Página 9: Misiones
            ["   MISIONES    ", "3 diarias/dia", "Semanales=bonus", "extra grande"],
            # Página 10: Sistemas
            ["  AVANZADO     ", "Crafting=combinar", "Apuestas=arriesga", "Prestigio=reset+"],
            # Página 11: Controles
            ["   CONTROLES   ", "[^] Subir/Scroll", "[v] Bajar/Scroll", "[OK] Seleccionar"],
            # Página 12: Volver
            ["     FIN       ", "", "[OK] Volver al", "menu principal"]
        ]
        
        total_pags = len(paginas)
        
        if key == 'UP' and self._tutorial_page > 0:
            self._tutorial_page -= 1
        elif key == 'DOWN' and self._tutorial_page < total_pags - 1:
            self._tutorial_page += 1
        elif key == 'SELECT':
            if self._tutorial_page >= total_pags - 1:
                # Última página: volver al menú
                self.state = CareerState.MENU_PRINCIPAL
                return
            else:
                # Avanzar página
                self._tutorial_page += 1
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
            return
        
        # Asegurar que está en rango
        self._tutorial_page = max(0, min(total_pags - 1, self._tutorial_page))
        
        pag = paginas[self._tutorial_page]
        for i, linea in enumerate(pag):
            self._lcd_centered(i, linea)
        
        # LEDs para navegación
        can_up = self._tutorial_page > 0
        can_down = self._tutorial_page < total_pags - 1
        self._leds_scroll(can_up, can_down)
    
    def _update_tienda(self, key):
        """Tienda El Camello - catálogo"""
        self._lcd_clear()
        
        dinero = get_dinero(self.data)
        
        # Título con dinero
        self._lcd_put(0, 0, f"EL CAMELLO  {dinero}E")
        
        # Lista de items + opción Volver
        total_items = len(CATALOGO_FARMACOS) + 1  # +1 para Volver
        
        # Mostrar 3 items
        for i in range(3):
            idx = self._tienda_scroll + i
            if idx < len(CATALOGO_FARMACOS):
                f = CATALOGO_FARMACOS[idx]
                prefix = ">" if idx == self._tienda_idx else " "
                
                # Obtener datos de forma segura
                if isinstance(f, dict):
                    precio = f.get("precio", 0)
                    nombre = f.get("nombre", "?")
                else:
                    precio = 0
                    nombre = "?"
                
                nombre = str(nombre)
                puede = dinero >= precio
                ind = " " if puede else "x"
                
                # Calcular espacio disponible para nombre
                precio_str = str(precio) + "E"
                nombre_max = 20 - 2 - len(precio_str) - 1
                if nombre_max < 1:
                    nombre_max = 1
                
                # Scroll solo en item seleccionado
                if idx == self._tienda_idx and len(nombre) > nombre_max:
                    nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                else:
                    nombre_disp = nombre[:nombre_max]
                    # Padding manual
                    while len(nombre_disp) < nombre_max:
                        nombre_disp = nombre_disp + " "
                
                self._lcd_put(0, 1 + i, prefix + ind + nombre_disp + " " + precio_str)
            elif idx == len(CATALOGO_FARMACOS):
                # Opción Volver
                prefix = ">" if idx == self._tienda_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")
        
        # LEDs
        can_up = self._tienda_idx > 0
        can_down = self._tienda_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self._tienda_idx -= 1
            if self._tienda_idx < self._tienda_scroll:
                self._tienda_scroll = self._tienda_idx
        elif key == 'DOWN' and can_down:
            self._tienda_idx += 1
            if self._tienda_idx >= self._tienda_scroll + 3:
                self._tienda_scroll = self._tienda_idx - 2
        elif key == 'SELECT':
            if self._tienda_idx < len(CATALOGO_FARMACOS):
                # Ver detalle del fármaco
                self._item_seleccionado = CATALOGO_FARMACOS[self._tienda_idx]
                self.state = CareerState.TIENDA_COMPRAR
            else:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
                self.menu_idx = 2
                self.scroll_idx = 0
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
            self.menu_idx = 2
            self.scroll_idx = 0
    
    def _update_tienda_comprar(self, key):
        """Confirmación de compra"""
        self._lcd_clear()
        
        f = self._item_seleccionado
        if not f or not isinstance(f, dict):
            self.state = CareerState.TIENDA
            return
        
        # Obtener datos de forma segura
        item_id = f.get("id", "")
        nombre = str(f.get("nombre", "?"))
        desc = str(f.get("desc", ""))
        precio = f.get("precio", 0)
        
        dinero = get_dinero(self.data)
        puede, msg = puede_comprar(self.data, item_id)
        
        # Línea 0: nombre con scroll si es largo
        if len(nombre) > 20:
            nombre_disp = self._scroll_text(nombre, 20, self.frame)
        else:
            nombre_disp = nombre[:20]
        self._lcd_centered(0, nombre_disp)
        
        # Línea 1: descripción con scroll si es larga
        if len(desc) > 20:
            desc_disp = self._scroll_text(desc, 20, self.frame + 30)  # offset para no sincronizar
        else:
            desc_disp = desc[:20]
        self._lcd_put(0, 1, desc_disp)
        
        self._lcd_put(0, 2, f"Precio: {precio}E")
        
        if self._compra_msg:
            # Mostrar resultado de compra
            self._lcd_centered(3, self._compra_msg)
            self._leds_select_only()
            if key == 'SELECT':
                self._compra_msg = ""
                self.state = CareerState.TIENDA
        else:
            if puede:
                self._lcd_put(0, 3, "[OK]Comprar [^]No")
            else:
                self._lcd_put(0, 3, f"{msg[:8]} [OK]")
            
            self._leds_scroll(True, False)
            
            if key == 'SELECT':
                if puede:
                    ok, _ = comprar_farmaco(self.data, item_id)
                    if ok:
                        self._compra_msg = f"Comprado!"
                        save_career(self.data)
                        play_sound('compra')
                    else:
                        self._compra_msg = "Error!"
                else:
                    self.state = CareerState.TIENDA
            elif key == 'UP' or key == 'BACK':
                self.state = CareerState.TIENDA
    
    def _update_inventario(self, key):
        """Ver inventario"""
        self._lcd_clear()
        
        inv = get_inventario(self.data)
        
        self._lcd_centered(0, "INVENTARIO")
        
        if not inv:
            self._lcd_centered(1, "Vacio!")
            self._lcd_centered(2, "Compra en")
            self._lcd_centered(3, "El Camello [OK]")
            self._leds_select_only()
            if key == 'SELECT' or key == 'BACK':
                self.state = CareerState.MENU_PRINCIPAL
            return
        
        total_items = len(inv) + 1  # +1 para Volver
        
        # Mostrar items
        for i in range(3):
            idx = self._inv_idx + i
            if idx < len(inv):
                item = inv[idx]
                f = get_farmaco_by_id(item["id"])
                if f:
                    prefix = ">" if idx == self._inv_idx else " "
                    cantidad_str = "x" + str(item['cantidad'])
                    nombre = str(f['nombre'])
                    # Espacio: 20 - 1(prefix) - len(cantidad) - 1(espacio)
                    nombre_max = 20 - 1 - len(cantidad_str) - 1
                    if nombre_max < 1:
                        nombre_max = 1
                    
                    if idx == self._inv_idx and len(nombre) > nombre_max:
                        nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                    else:
                        nombre_disp = nombre[:nombre_max]
                        while len(nombre_disp) < nombre_max:
                            nombre_disp = nombre_disp + " "
                    
                    self._lcd_put(0, 1 + i, prefix + nombre_disp + " " + cantidad_str)
            elif idx == len(inv):
                prefix = ">" if idx == self._inv_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")
        
        can_up = self._inv_idx > 0
        can_down = self._inv_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self._inv_idx -= 1
        elif key == 'DOWN' and can_down:
            self._inv_idx += 1
        elif key == 'SELECT':
            if self._inv_idx < len(inv):
                # Seleccionar item (sin acción directa en este contexto)
                pass
            else:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_usar_item(self, key):
        """Usar item en paciente"""
        self._lcd_clear()
        
        if not self.paciente_actual or not self._item_seleccionado:
            self.state = CareerState.VER_PACIENTE
            return
        
        f = self._item_seleccionado
        p = self.paciente_actual
        
        self._lcd_centered(0, f"Usar {f['nombre'][:14]}")
        self._lcd_centered(1, f"en {p['nombre'][:14]}?")
        
        # Descripción con scroll
        desc = str(f.get("desc", ""))
        if len(desc) > 20:
            desc_disp = self._scroll_text(desc, 20, self.frame)
        else:
            desc_disp = desc[:20]
        self._lcd_put(0, 2, desc_disp)
        
        self._lcd_put(0, 3, "[OK]Si  [^]No")
        
        self._leds_scroll(True, False)
        
        if key == 'SELECT':
            # Aplicar efecto
            exito = self._aplicar_farmaco(f["id"], p)
            if exito:
                remove_item(self.data, f["id"])
                save_career(self.data)
            self._item_seleccionado = None
            self._ver_pagina = 0
            self.state = CareerState.VER_PACIENTE
        elif key == 'UP':
            self._item_seleccionado = None
            self.state = CareerState.VER_PACIENTE
    
    def _aplicar_farmaco(self, item_id, paciente):
        """Aplica efecto de fármaco. Returns True si se usó."""
        import random
        
        efecto = get_farmaco_by_id(item_id)["efecto"]
        pid = paciente["id"]
        
        if efecto == "placebo":
            # 50% de funcionar como ansiolítico
            if random.random() < 0.5:
                if paciente["sesiones_totales"] > paciente["sesiones_completadas"] + 1:
                    paciente["sesiones_totales"] -= 1
                    self._compra_msg = "Funciono!"
                else:
                    self._compra_msg = "Sin efecto"
            else:
                self._compra_msg = "Era placebo!"
            play_sound('pastilla')
            
        elif efecto == "doble_xp":
            add_efecto_paciente(self.data, pid, "doble_xp")
            self._compra_msg = "Doble XP activo"
            play_sound('cafe')
            
        elif efecto == "reduce_sesion":
            if paciente["sesiones_totales"] > paciente["sesiones_completadas"] + 1:
                paciente["sesiones_totales"] -= 1
                self._compra_msg = "-1 sesion!"
            else:
                self._compra_msg = "Ya casi acaba"
            play_sound('pastilla')
            
        elif efecto == "elimina_opcion":
            add_efecto_paciente(self.data, pid, "elimina_opcion")
            self._compra_msg = "Electroshock OK"
            play_sound('electroshock')
            
        elif efecto == "protege_fallo":
            add_efecto_paciente(self.data, pid, "protege_fallo")
            self._compra_msg = "Hipnosis activa"
            play_sound('hipnosis')
            
        elif efecto == "reset_progreso":
            if paciente["progreso"] < 0:
                paciente["progreso"] = 0
                self._compra_msg = "Progreso a 0!"
            else:
                self._compra_msg = "No hacia falta"
            play_sound('pastilla')
            
        elif efecto == "no_huir":
            add_efecto_paciente(self.data, pid, "no_huir")
            self._compra_msg = "No puede huir"
            play_sound('lobotomia')
            
        elif efecto == "revela_respuesta":
            add_efecto_paciente(self.data, pid, "revela")
            self._compra_msg = "Verdad activa"
            play_sound('suero')
            
        elif efecto == "cura_instantanea":
            # Curar inmediatamente
            paciente["sesiones_completadas"] = paciente["sesiones_totales"]
            paciente["progreso"] = 10
            self._compra_msg = "CURADO!"
            play_sound('curado')
            # Procesar curación
            self._procesar_curacion(paciente)
        
        return True
    
    def _procesar_curacion(self, paciente):
        """Procesa curación de paciente (por camisa de fuerza)"""
        # XP y dinero
        xp_base = XP_CURAR_PACIENTE_BASE + paciente["sesiones_totales"]
        add_xp(self.data, xp_base)
        
        dinero_base = DINERO_CURAR_BASE + (paciente["sesiones_totales"] * 20)
        add_dinero(self.data, dinero_base)
        
        increment_stat(self.data, "pacientes_curados")
        
        # Eliminar paciente y mensajes
        pid = paciente["id"]
        remove_paciente(self.data, pid)
        for m in get_mensajes_pendientes(self.data):
            if m["paciente_id"] == pid:
                remove_mensaje(self.data, m["id_mensaje"])
        
        clear_efectos_paciente(self.data, pid)
        save_career(self.data)
    
    # === LOGROS ===
    
    def _update_logros(self, key):
        """Ver lista de logros"""
        self._lcd_clear()
        
        desbloqueados = get_logros_desbloqueados(self.data)
        logros_lista = list(LOGROS.items())
        total = len(logros_lista)
        total_items = total + 1  # +1 para Volver
        
        self._lcd_put(0, 0, f"LOGROS ({len(desbloqueados)}/{total})")
        
        # Mostrar 3 items
        for i in range(3):
            idx = self._logros_scroll + i
            if idx < total:
                logro_id, logro = logros_lista[idx]
                desbloqueado = logro_id in desbloqueados
                secreto = logro.get("secreto", False)
                
                prefix = ">" if idx == self._logros_idx else " "
                nombre = logro["nombre"]
                nombre_max = 16  # 20 - 4 ([X] o [ ])
                
                if desbloqueado:
                    if idx == self._logros_idx and len(nombre) > nombre_max:
                        nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                    else:
                        nombre_disp = nombre[:nombre_max]
                    self._lcd_put(0, 1 + i, f"{prefix}[X]{nombre_disp}")
                elif secreto:
                    self._lcd_put(0, 1 + i, f"{prefix}[ ]???")
                else:
                    if idx == self._logros_idx and len(nombre) > nombre_max:
                        nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                    else:
                        nombre_disp = nombre[:nombre_max]
                    self._lcd_put(0, 1 + i, f"{prefix}[ ]{nombre_disp}")
            elif idx == total:
                prefix = ">" if idx == self._logros_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")
        
        can_up = self._logros_idx > 0
        can_down = self._logros_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self._logros_idx -= 1
            if self._logros_idx < self._logros_scroll:
                self._logros_scroll = self._logros_idx
        elif key == 'DOWN' and can_down:
            self._logros_idx += 1
            if self._logros_idx >= self._logros_scroll + 3:
                self._logros_scroll = self._logros_idx - 2
        elif key == 'SELECT':
            if self._logros_idx < total:
                # Mostrar detalle del logro seleccionado
                logro_id, logro = logros_lista[self._logros_idx]
                if logro_id in desbloqueados or not logro.get("secreto", False):
                    self._logro_nuevo = logro_id
                    self.state = CareerState.LOGRO_DESBLOQUEADO
                else:
                    # Volver al menú si es secreto no desbloqueado
                    self.state = CareerState.MENU_PRINCIPAL
            else:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
                self.scroll_idx = 2
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_logro_desbloqueado(self, key):
        """Mostrar logro desbloqueado o detalle"""
        self._lcd_clear()
        
        if not self._logro_nuevo:
            self.state = CareerState.MENU_PRINCIPAL
            return
        
        logro = LOGROS.get(self._logro_nuevo, {})
        desbloqueados = get_logros_desbloqueados(self.data)
        es_nuevo = self._logro_nuevo not in desbloqueados
        
        # Sonido si es nuevo
        if self.frame == 1 and es_nuevo:
            play_sound('level_up')
            # Aplicar recompensa
            aplicar_recompensa_logro(self.data, self._logro_nuevo)
            save_career(self.data)
        
        # Animación si es nuevo
        if es_nuevo and self.frame < 10:
            celebraciones = ["!! LOGRO !!", "** LOGRO **", "## LOGRO ##"]
            self._lcd_centered(0, celebraciones[self.frame % 3])
        else:
            self._lcd_centered(0, "LOGRO")
        
        # Nombre con scroll
        nombre = str(logro.get("nombre", "?"))
        if len(nombre) > 20:
            nombre_disp = self._scroll_text(nombre, 20, self.frame)
        else:
            nombre_disp = nombre[:20]
        self._lcd_centered(1, nombre_disp)
        
        # Descripción con scroll
        desc = str(logro.get("desc", ""))
        if len(desc) > 20:
            desc_disp = self._scroll_text(desc, 20, self.frame + 30)
        else:
            desc_disp = desc[:20]
        self._lcd_centered(2, desc_disp)
        
        # Mostrar recompensa
        recompensa = logro.get("recompensa", {})
        rew_txt = ""
        if "dinero" in recompensa:
            rew_txt += f"+{recompensa['dinero']}E "
        if "item" in recompensa:
            rew_txt += "+Item "
        if "titulo" in recompensa:
            rew_txt += f"[{recompensa['titulo']}]"
        if "descuento" in recompensa:
            rew_txt += f"-{recompensa['descuento']}%"
        
        self._lcd_centered(3, rew_txt[:20] if rew_txt else "[OK]")
        
        self._leds_select_only()
        
        if key == 'SELECT':
            self._logro_nuevo = None
            # Si hay más logros pendientes
            if self._logros_pendientes:
                self._logro_nuevo = self._logros_pendientes.pop(0)
            elif self.level_up_info:
                self.state = CareerState.SUBIDA_NIVEL
            else:
                self.state = CareerState.MENU_PRINCIPAL
                self.menu_idx = 0
                self.scroll_idx = 0
    
    # === MEJORAS DE CONSULTA ===
    
    def _update_mejoras(self, key):
        """Ver lista de mejoras"""
        self._lcd_clear()
        
        dinero = get_dinero(self.data)
        compradas = get_mejoras_compradas(self.data)
        
        # Validar que compradas es lista
        if not isinstance(compradas, list):
            compradas = []
        
        mejoras_lista = list(MEJORAS.items())
        total_items = len(mejoras_lista) + 1  # +1 para Volver
        
        self._lcd_put(0, 0, f"MEJORAS  {dinero}E")
        
        # Mostrar 3 items
        for i in range(3):
            idx = self._mejoras_scroll + i
            if idx < len(mejoras_lista):
                mejora_id, mejora = mejoras_lista[idx]
                comprada = mejora_id in compradas
                
                prefix = ">" if idx == self._mejoras_idx else " "
                nombre = str(mejora.get("nombre", "?"))
                precio = mejora.get("precio", 0)
                
                if comprada:
                    # Formato: ">* Nombre" - 17 chars para nombre
                    nombre_max = 17
                    if idx == self._mejoras_idx and len(nombre) > nombre_max:
                        nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                    else:
                        nombre_disp = nombre[:nombre_max]
                        while len(nombre_disp) < nombre_max:
                            nombre_disp = nombre_disp + " "
                    self._lcd_put(0, 1 + i, prefix + "* " + nombre_disp)
                else:
                    # Formato: ">  Nombre precioE"
                    precio_str = str(precio) + "E"
                    nombre_max = 20 - 2 - len(precio_str) - 1
                    if nombre_max < 1:
                        nombre_max = 1
                    
                    if idx == self._mejoras_idx and len(nombre) > nombre_max:
                        nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                    else:
                        nombre_disp = nombre[:nombre_max]
                        while len(nombre_disp) < nombre_max:
                            nombre_disp = nombre_disp + " "
                    
                    self._lcd_put(0, 1 + i, prefix + "  " + nombre_disp + " " + precio_str)
            elif idx == len(mejoras_lista):
                prefix = ">" if idx == self._mejoras_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")
        
        can_up = self._mejoras_idx > 0
        can_down = self._mejoras_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self._mejoras_idx -= 1
            if self._mejoras_idx < self._mejoras_scroll:
                self._mejoras_scroll = self._mejoras_idx
        elif key == 'DOWN' and can_down:
            self._mejoras_idx += 1
            if self._mejoras_idx >= self._mejoras_scroll + 3:
                self._mejoras_scroll = self._mejoras_idx - 2
        elif key == 'SELECT':
            if self._mejoras_idx < len(mejoras_lista):
                mejora_id, _ = mejoras_lista[self._mejoras_idx]
                self._mejora_seleccionada = mejora_id
                self.state = CareerState.MEJORA_COMPRAR
            else:
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_mejora_comprar(self, key):
        """Confirmar compra de mejora"""
        self._lcd_clear()
        
        mejora_id = self._mejora_seleccionada
        if not mejora_id:
            self.state = CareerState.MEJORAS
            return
        
        mejora = MEJORAS.get(mejora_id, {})
        compradas = get_mejoras_compradas(self.data)
        
        # Nombre con scroll
        nombre = str(mejora.get("nombre", "?"))
        if len(nombre) > 20:
            nombre_disp = self._scroll_text(nombre, 20, self.frame)
        else:
            nombre_disp = nombre[:20]
        self._lcd_centered(0, nombre_disp)
        
        # Descripción con scroll
        desc = str(mejora.get("desc", ""))
        if len(desc) > 20:
            desc_disp = self._scroll_text(desc, 20, self.frame + 30)
        else:
            desc_disp = desc[:20]
        self._lcd_put(0, 1, desc_disp)
        
        if mejora_id in compradas:
            self._lcd_centered(2, "YA COMPRADA")
            self._lcd_put(0, 3, "[OK] Volver")
            self._leds_select_only()
            if key == 'SELECT':
                self.state = CareerState.MEJORAS
        else:
            puede, resultado = puede_comprar_mejora(self.data, mejora_id)
            
            if self._compra_msg:
                self._lcd_centered(2, self._compra_msg)
                self._lcd_put(0, 3, "[OK] Continuar")
                self._leds_select_only()
                if key == 'SELECT':
                    self._compra_msg = ""
                    self.state = CareerState.MEJORAS
            elif puede:
                self._lcd_put(0, 2, f"Precio: {resultado}E")
                self._lcd_put(0, 3, "[OK]Comprar [^]No")
                self._leds_scroll(True, False)
                
                if key == 'SELECT':
                    ok, msg = comprar_mejora(self.data, mejora_id)
                    if ok:
                        self._compra_msg = "Comprada!"
                        play_sound('compra')
                        save_career(self.data)
                    else:
                        self._compra_msg = msg
                elif key == 'UP':
                    self.state = CareerState.MEJORAS
            else:
                self._lcd_centered(2, resultado)
                self._lcd_put(0, 3, "[OK] Volver")
                self._leds_select_only()
                if key == 'SELECT':
                    self.state = CareerState.MEJORAS
    
    # === EVENTO DEL DÍA ===
    
    def _update_evento_dia(self, key):
        """Mostrar evento del día"""
        self._lcd_clear()
        
        evento = self._evento_actual
        if not evento:
            evento = get_evento_hoy(self.data)
        
        # Sonido según tipo
        if self.frame == 1:
            tipo = evento.get("tipo", "neutro")
            if tipo == "bueno":
                play_sound('correcto')
            elif tipo == "malo":
                play_sound('incorrecto')
            else:
                play_sound('mensaje')
        
        # Título con animación
        tipo = evento.get("tipo", "neutro")
        if tipo == "bueno":
            iconos = ["+++", "***", "!!!"]
        elif tipo == "malo":
            iconos = ["---", "xxx", "..."]
        else:
            iconos = ["???", "***", "!!!"]
        
        icono = iconos[(self.frame // 5) % 3]
        self._lcd_centered(0, f"{icono} EVENTO {icono}")

        # Nombre con scroll horizontal si es largo
        nombre = evento.get("nombre", "?")
        if len(nombre) > 20:
            nombre = self._scroll_text(nombre, 20, self.frame)
        self._lcd_centered(1, nombre)

        # Descripción con scroll horizontal si es larga
        desc = evento.get("desc", "")
        if len(desc) > 20:
            desc = self._scroll_text(desc, 20, self.frame + 30)
        self._lcd_centered(2, desc)
        self._lcd_centered(3, "[OK] Continuar")
        
        self._leds_select_only()
        
        if key == 'SELECT':
            self._evento_actual = None
            self._evento_mostrado = True
            marcar_tutorial(self.data, "evento")
            save_career(self.data)

            # Registrar actividad antes de volver a SCREENSAVER
            self._register_activity()
            self._wake_up()

            self.state = CareerState.SCREENSAVER
    
    # === MISIONES ===
    
    def _update_misiones(self, key):
        """Ver misiones activas"""
        self._lcd_clear()
        
        misiones = get_misiones_activas(self.data)
        diarias = misiones.get("diarias", [])
        semanales = misiones.get("semanales", [])
        
        if not hasattr(self, '_misiones_tab'):
            self._misiones_tab = 0  # 0=diarias, 1=semanales
            self._misiones_idx = 0
        
        # Título
        tab_txt = "DIA" if self._misiones_tab == 0 else "SEM"
        self._lcd_put(0, 0, f"MISIONES [{tab_txt}]")
        
        lista = diarias if self._misiones_tab == 0 else semanales
        total_items = len(lista) + 1  # +1 para Volver
        
        if not lista:
            self._lcd_centered(1, "Sin misiones")
            self._lcd_put(0, 2, ">< Volver")
            self._lcd_put(0, 3, "[^v]Tab [OK]Sel")
        else:
            for i in range(2):
                idx = self._misiones_idx + i if self._misiones_idx < len(lista) else self._misiones_idx
                if idx < len(lista):
                    m = lista[idx]
                    prefix = ">" if idx == self._misiones_idx else " "
                    estado = "[X]" if m.get("completada") else "[ ]"
                    nombre = m.get('nombre', '?')
                    nombre_max = 15  # 20 - 1(prefix) - 4([X] )
                    
                    if idx == self._misiones_idx and len(nombre) > nombre_max:
                        nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                    else:
                        nombre_disp = nombre[:nombre_max]
                    
                    self._lcd_put(0, 1 + i, f"{prefix}{estado}{nombre_disp}")
                elif idx == len(lista):
                    prefix = ">" if idx == self._misiones_idx else " "
                    self._lcd_put(0, 1 + i, f"{prefix}< Volver")
            self._lcd_put(0, 3, "[^v]Nav [OK]Sel")
        
        self._leds_on()
        
        if key == 'UP':
            if self._misiones_idx > 0:
                self._misiones_idx -= 1
            else:
                # Cambiar tab
                self._misiones_tab = 1 - self._misiones_tab
                nueva_lista = diarias if self._misiones_tab == 0 else semanales
                self._misiones_idx = len(nueva_lista)  # Ir a Volver
        elif key == 'DOWN':
            if self._misiones_idx < total_items - 1:
                self._misiones_idx += 1
            else:
                # Cambiar tab
                self._misiones_tab = 1 - self._misiones_tab
                self._misiones_idx = 0
        elif key == 'SELECT':
            if self._misiones_idx < len(lista):
                self._mision_actual = lista[self._misiones_idx]
                self._mision_es_diaria = self._misiones_tab == 0
                self.state = CareerState.MISION_DETALLE
            else:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_mision_detalle(self, key):
        """Detalle de misión"""
        self._lcd_clear()
        
        m = self._mision_actual
        if not m:
            self.state = CareerState.MISIONES
            return
        
        # Nombre con scroll
        nombre = str(m.get("nombre", "?"))
        if len(nombre) > 20:
            nombre_disp = self._scroll_text(nombre, 20, self.frame)
        else:
            nombre_disp = nombre[:20]
        self._lcd_centered(0, nombre_disp)
        
        # Descripción con scroll
        desc = str(m.get("desc", ""))
        if len(desc) > 20:
            desc_disp = self._scroll_text(desc, 20, self.frame + 30)
        else:
            desc_disp = desc[:20]
        self._lcd_put(0, 1, desc_disp)
        
        # Progreso
        if m.get("completada"):
            if m.get("reclamada"):
                self._lcd_centered(2, "YA RECLAMADA")
                self._lcd_put(0, 3, "[OK] Volver")
            else:
                self._lcd_centered(2, "COMPLETADA!")
                self._lcd_put(0, 3, "[OK] Reclamar")
        else:
            prog = m.get("progreso", 0)
            self._lcd_centered(2, f"Progreso: {prog}")
            self._lcd_put(0, 3, "[OK] Volver")
        
        self._leds_select_only()
        
        if key == 'SELECT':
            if m.get("completada") and not m.get("reclamada"):
                # Reclamar recompensa
                recompensa = reclamar_mision(
                    self.data, 
                    m["id"], 
                    self._mision_es_diaria
                )
                if recompensa:
                    if "dinero" in recompensa:
                        add_dinero(self.data, recompensa["dinero"])
                    if "item" in recompensa:
                        add_item(self.data, recompensa["item"])
                    play_sound('compra')
                    save_career(self.data)
            self.state = CareerState.MISIONES
        elif key == 'BACK':
            self.state = CareerState.MISIONES
    
    # === APUESTAS ===
    
    def _update_apuestas(self, key):
        """Menú de apuestas"""
        self._lcd_clear()
        
        if not tiene_mejora(self.data, "ruleta"):
            self._lcd_centered(0, "BLOQUEADO")
            self._lcd_centered(1, "Necesitas comprar")
            self._lcd_centered(2, "Ruleta del Loco")
            self._lcd_put(0, 3, "[OK] Volver")
            self._leds_select_only()
            if key == 'SELECT' or key == 'BACK':
                self.state = CareerState.MENU_PRINCIPAL
            return
        
        if not hasattr(self, '_apuesta_cantidad'):
            self._apuesta_cantidad = 0  # 0 = opción Volver
        
        dinero = get_dinero(self.data)
        max_ap = get_max_apuesta(self.data)
        
        self._lcd_centered(0, "RULETA DEL LOCO")
        self._lcd_centered(1, f"Tienes: {dinero}E")
        
        if self._apuesta_cantidad == 0:
            self._lcd_centered(2, "< Volver")
            self._lcd_put(0, 3, "[v]Apostar [OK]Salir")
        else:
            self._lcd_centered(2, f"Apostar: {self._apuesta_cantidad}E")
            self._lcd_put(0, 3, "[^v]+-25 [OK]Apostar")
        
        self._leds_on()
        
        if key == 'UP':
            if self._apuesta_cantidad == 0:
                self._apuesta_cantidad = 0  # Ya está en 0
            else:
                self._apuesta_cantidad = min(max_ap, self._apuesta_cantidad + 25)
        elif key == 'DOWN':
            if self._apuesta_cantidad <= 25:
                self._apuesta_cantidad = 0  # Volver
            else:
                self._apuesta_cantidad = max(25, self._apuesta_cantidad - 25)
        elif key == 'SELECT':
            if self._apuesta_cantidad == 0:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
            else:
                puede, msg = puede_apostar(self.data, self._apuesta_cantidad)
                if puede:
                    self.state = CareerState.APUESTA_CONFIRMAR
                else:
                    self._compra_msg = msg
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_apuesta_confirmar(self, key):
        """Confirmar apuesta"""
        self._lcd_clear()
        
        self._lcd_centered(0, "CONFIRMAR APUESTA")
        self._lcd_centered(1, f"{self._apuesta_cantidad}E")
        self._lcd_centered(2, "Si aciertas: x2")
        self._lcd_put(0, 3, "[OK]Si [^]No")
        
        self._leds_scroll(True, False)
        
        if key == 'SELECT':
            ok, _ = hacer_apuesta(self.data, self._apuesta_cantidad)
            if ok:
                save_career(self.data)
                # Volver a eligiendo respuesta
                self.state = CareerState.ELIGIENDO_RESPUESTA
        elif key == 'UP':
            self.state = CareerState.APUESTAS
    
    def _update_apuesta_resultado(self, key):
        """Resultado de apuesta"""
        self._lcd_clear()
        
        resultado = self._apuesta_resultado
        if not resultado:
            self.state = CareerState.FEEDBACK
            return
        
        if resultado["resultado"] == "gano":
            if self.frame == 1:
                play_sound('level_up')
            self._lcd_centered(0, "GANASTE!")
            self._lcd_centered(1, f"+{resultado['ganancia']}E")
            mult = resultado.get("multiplicador", 2)
            self._lcd_centered(2, f"x{mult}")
        else:
            if self.frame == 1:
                play_sound('huye')
            self._lcd_centered(0, "PERDISTE...")
            self._lcd_centered(1, f"-{resultado['perdida']}E")
        
        self._lcd_put(0, 3, "[OK] Continuar")
        self._leds_select_only()
        
        if key == 'SELECT':
            self._apuesta_resultado = None
            self.state = CareerState.FEEDBACK
    
    # === CRAFTING ===
    
    def _update_crafting(self, key):
        """Menú de crafting"""
        self._lcd_clear()
        
        if not tiene_mejora(self.data, "mesa_crafting"):
            self._lcd_centered(0, "BLOQUEADO")
            self._lcd_centered(1, "Necesitas comprar")
            self._lcd_centered(2, "Mesa de Crafting")
            self._lcd_put(0, 3, "[OK] Volver")
            self._leds_select_only()
            if key == 'SELECT' or key == 'BACK':
                self.state = CareerState.MENU_PRINCIPAL
            return
        
        if not hasattr(self, '_craft_idx'):
            self._craft_idx = 0
        
        recetas = get_recetas_disponibles(self.data)
        total_items = len(recetas) + 1  # +1 para Volver
        
        self._lcd_put(0, 0, "CRAFTING")
        
        for i in range(3):
            idx = self._craft_idx + i
            if idx < len(recetas):
                r = recetas[idx]
                prefix = ">" if idx == self._craft_idx else " "
                puede = " " if r["puede"] else "x"
                nombre = r["receta"]["nombre"]
                nombre_max = 17  # 20 - 3 (prefix + puede + espacio)
                
                if idx == self._craft_idx and len(nombre) > nombre_max:
                    nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                else:
                    nombre_disp = nombre[:nombre_max]
                
                self._lcd_put(0, 1 + i, f"{prefix}{puede}{nombre_disp}")
            elif idx == len(recetas):
                prefix = ">" if idx == self._craft_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")
        
        can_up = self._craft_idx > 0
        can_down = self._craft_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self._craft_idx -= 1
        elif key == 'DOWN' and can_down:
            self._craft_idx += 1
        elif key == 'SELECT':
            if self._craft_idx < len(recetas):
                self._craft_seleccionado = recetas[self._craft_idx]
                self.state = CareerState.CRAFTING_CONFIRMAR
            else:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_crafting_confirmar(self, key):
        """Confirmar crafting"""
        self._lcd_clear()
        
        r = self._craft_seleccionado
        if not r:
            self.state = CareerState.CRAFTING
            return
        
        receta = r["receta"]
        
        # Nombre con scroll
        nombre = str(receta.get("nombre", "?"))
        if len(nombre) > 20:
            nombre_disp = self._scroll_text(nombre, 20, self.frame)
        else:
            nombre_disp = nombre[:20]
        self._lcd_centered(0, nombre_disp)
        
        # Descripción con scroll
        desc = str(receta.get("desc", ""))
        if len(desc) > 20:
            desc_disp = self._scroll_text(desc, 20, self.frame + 30)
        else:
            desc_disp = desc[:20]
        self._lcd_put(0, 1, desc_disp)
        
        # Ingredientes con scroll
        ings = ", ".join([f"{c}x{i}" for i, c in receta.get("ingredientes", [])])
        if len(ings) > 20:
            ings_disp = self._scroll_text(ings, 20, self.frame + 60)
        else:
            ings_disp = ings[:20]
        self._lcd_put(0, 2, ings_disp)
        
        if r["puede"]:
            self._lcd_put(0, 3, "[OK]Crear [^]No")
            self._leds_scroll(True, False)
            
            if key == 'SELECT':
                ok, msg = craftear(self.data, list(RECETAS.keys())[self._craft_idx])
                if ok:
                    play_sound('compra')
                    save_career(self.data)
                    self._compra_msg = f"Creado: {msg}"
                self.state = CareerState.CRAFTING
            elif key == 'UP':
                self.state = CareerState.CRAFTING
        else:
            self._lcd_put(0, 3, "Faltan items [OK]")
            self._leds_select_only()
            if key == 'SELECT':
                self.state = CareerState.CRAFTING
    
    # === BATAS ===
    
    def _update_batas(self, key):
        """Selección de batas"""
        self._lcd_clear()
        
        if not hasattr(self, '_bata_idx'):
            self._bata_idx = 0
        if not hasattr(self, '_bata_scroll'):
            self._bata_scroll = 0
        
        batas = get_batas_disponibles(self.data)
        equipada = self.data.get("bata_equipada", "clasica")
        total_items = len(batas) + 1  # +1 para Volver
        
        self._lcd_put(0, 0, "VESTUARIO")
        
        for i in range(3):
            idx = self._bata_scroll + i
            if idx < len(batas):
                b = batas[idx]
                prefix = ">" if idx == self._bata_idx else " "
                
                # Obtener datos de forma segura
                if isinstance(b, dict):
                    bata_id = b.get("id", "")
                    bata_info = b.get("bata", {})
                else:
                    bata_id = ""
                    bata_info = {}
                
                if isinstance(bata_info, dict):
                    nombre = str(bata_info.get("nombre", "?"))
                else:
                    nombre = "?"
                
                # Determinar estado
                if bata_id == equipada:
                    estado = "[E]"
                elif b.get("comprada", False):
                    estado = "*"
                elif not b.get("disponible", True):
                    estado = "X"
                else:
                    if isinstance(bata_info, dict):
                        precio = bata_info.get("precio", 0)
                    else:
                        precio = 0
                    estado = str(precio) + "E"
                
                # Calcular espacio para nombre
                nombre_max = 20 - 1 - len(estado) - 1
                if nombre_max < 1:
                    nombre_max = 1
                
                # Scroll solo en item seleccionado
                if idx == self._bata_idx and len(nombre) > nombre_max:
                    nombre_disp = self._scroll_text(nombre, nombre_max, self.frame)
                else:
                    nombre_disp = nombre[:nombre_max]
                    while len(nombre_disp) < nombre_max:
                        nombre_disp = nombre_disp + " "
                
                self._lcd_put(0, 1 + i, prefix + estado + " " + nombre_disp)
            elif idx == len(batas):
                prefix = ">" if idx == self._bata_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")
        
        can_up = self._bata_idx > 0
        can_down = self._bata_idx < total_items - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self._bata_idx -= 1
            if self._bata_idx < self._bata_scroll:
                self._bata_scroll = self._bata_idx
        elif key == 'DOWN' and can_down:
            self._bata_idx += 1
            if self._bata_idx >= self._bata_scroll + 3:
                self._bata_scroll = self._bata_idx - 2
        elif key == 'SELECT':
            if self._bata_idx < len(batas):
                self._bata_seleccionada = batas[self._bata_idx]
                self.state = CareerState.BATA_COMPRAR
            else:
                # Volver
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_bata_comprar(self, key):
        """Comprar/equipar bata"""
        self._lcd_clear()
        
        b = self._bata_seleccionada
        if not b or not isinstance(b, dict):
            self.state = CareerState.BATAS
            return
        
        bata = b.get("bata", {})
        bata_id = b.get("id", "")
        nombre = str(bata.get("nombre", "?"))
        desc = str(bata.get("desc", ""))
        precio = bata.get("precio", 0)
        comprada = b.get("comprada", False)
        disponible = b.get("disponible", True)
        
        # Nombre con scroll
        if len(nombre) > 20:
            nombre_disp = self._scroll_text(nombre, 20, self.frame)
        else:
            nombre_disp = nombre[:20]
        self._lcd_centered(0, nombre_disp)
        
        # Descripción con scroll
        if len(desc) > 20:
            desc_disp = self._scroll_text(desc, 20, self.frame + 30)
        else:
            desc_disp = desc[:20]
        self._lcd_put(0, 1, desc_disp)
        
        equipada = self.data.get("bata_equipada", "clasica")
        
        if bata_id == equipada:
            self._lcd_centered(2, "EQUIPADA")
            self._lcd_put(0, 3, "[OK] Volver")
        elif comprada:
            self._lcd_centered(2, "Ya la tienes")
            self._lcd_put(0, 3, "[OK]Equipar [^]No")
        elif not disponible:
            self._lcd_centered(2, "Requisito no OK")
            self._lcd_put(0, 3, "[OK] Volver")
        else:
            self._lcd_put(0, 2, f"Precio: {precio}E")
            self._lcd_put(0, 3, "[OK]Comprar [^]No")
        
        self._leds_scroll(True, False)
        
        if key == 'SELECT':
            if comprada and bata_id != equipada:
                equipar_bata(self.data, bata_id)
                save_career(self.data)
            elif not comprada and disponible:
                ok, msg = comprar_bata(self.data, bata_id)
                if ok:
                    play_sound('compra')
                    equipar_bata(self.data, bata_id)
                    save_career(self.data)
            self.state = CareerState.BATAS
        elif key == 'UP' or key == 'BACK':
            self.state = CareerState.BATAS
    
    # === PRESTIGIO ===
    
    def _update_prestigio(self, key):
        """Menú de prestigio"""
        self._lcd_clear()
        
        prestigio = get_prestigio(self.data)
        nivel = self.data["jugador"].get("nivel", 1)
        puede, msg = puede_prestigiar(self.data)
        
        self._lcd_centered(0, f"PRESTIGIO [{prestigio['nivel']}]")
        self._lcd_put(0, 1, f"Nivel actual: {nivel}")
        self._lcd_put(0, 2, f"Bonus: +{int(prestigio['bonus']*100)}%")
        
        if puede:
            self._lcd_put(0, 3, "[OK]Prestigiar [^]No")
            self._leds_scroll(True, False)
        else:
            self._lcd_put(0, 3, msg[:20])
            self._leds_select_only()
        
        if key == 'SELECT' and puede:
            self.state = CareerState.PRESTIGIO_CONFIRMAR
        elif key == 'UP' or key == 'BACK' or (key == 'SELECT' and not puede):
            self.state = CareerState.MENU_PRINCIPAL
    
    def _update_prestigio_confirmar(self, key):
        """Confirmar prestigio"""
        self._lcd_clear()
        
        self._lcd_centered(0, "ADVERTENCIA!")
        self._lcd_put(0, 1, "Perderas nivel")
        self._lcd_put(0, 2, "dinero y pacientes")
        self._lcd_put(0, 3, "[OK]Confirmar [^]No")
        
        self._leds_scroll(True, False)
        
        if key == 'SELECT':
            ok, resultado = hacer_prestigio(self.data)
            if ok:
                play_sound('level_up')
                save_career(self.data)
                self._compra_msg = f"Prestigio {resultado['nivel']}!"
            self.state = CareerState.MENU_PRINCIPAL
        elif key == 'UP':
            self.state = CareerState.PRESTIGIO
    
    # === ORÁCULO ===
    
    def _update_oraculo(self, key):
        """Visita del oráculo"""
        self._lcd_clear()
        
        if not hasattr(self, '_oraculo_pred'):
            self._oraculo_pred = get_prediccion_oraculo()
        
        pred = self._oraculo_pred
        
        if self.frame == 1:
            play_sound('mensaje')
        
        # Animación mística
        mistico = ["*", "~", ".", "*"]
        m = mistico[(self.frame // 10) % 4]
        
        self._lcd_centered(0, f"{m} EL ORACULO {m}")
        
        # Frase
        frase = pred["frase"]
        lines = self._wrap_text(frase)
        for i, line in enumerate(lines[:2]):
            self._lcd_centered(1 + i, line)
        
        self._lcd_put(0, 3, "[OK] Escuchar")
        self._leds_select_only()
        
        if key == 'SELECT':
            # Aplicar predicción
            resultado = aplicar_prediccion_oraculo(self.data, pred)
            save_career(self.data)
            self._oraculo_pred = None

            # Registrar actividad antes de volver a SCREENSAVER
            self._register_activity()
            self._wake_up()

            self.state = CareerState.SCREENSAVER
    
    # === REGALO PACIENTE ===
    
    def _update_regalo_paciente(self, key):
        """Mostrar regalo de paciente"""
        self._lcd_clear()
        
        regalo = self._regalo_actual
        if not regalo:
            self.state = CareerState.RESULTADO_PACIENTE
            return
        
        if self.frame == 1:
            play_sound('mensaje')
        
        self._lcd_centered(0, "REGALO RECIBIDO!")
        self._lcd_centered(1, regalo["regalo"]["nombre"][:20])
        
        # Efecto
        efecto = regalo["regalo"]["efecto"]
        if "dinero" in efecto:
            self._lcd_centered(2, f"+{efecto['dinero']}E")
        elif "reputacion" in efecto:
            rep = efecto["reputacion"]
            signo = "+" if rep > 0 else ""
            self._lcd_centered(2, f"{signo}{rep} Reputacion")
        
        self._lcd_put(0, 3, "[OK] Continuar")
        self._leds_select_only()
        
        if key == 'SELECT':
            aplicar_regalo(self.data, regalo)
            save_career(self.data)
            self._regalo_actual = None
            # Usar función helper para determinar siguiente estado
            self.state = self._get_next_state_after_result()
    
    # === COMBO ACTIVADO ===
    
    def _update_combo_activado(self, key):
        """Mostrar combo activado"""
        self._lcd_clear()
        
        combo = self._combo_actual
        if not combo:
            self.state = CareerState.FEEDBACK
            return
        
        if self.frame == 1:
            play_sound('level_up')
        
        # Animación
        celebraciones = ["!! COMBO !!", "** COMBO **", "## COMBO ##"]
        self._lcd_centered(0, celebraciones[self.frame % 3])
        
        self._lcd_centered(1, combo["combo"][:20])
        
        # Efectos
        efectos = combo.get("efectos", [])
        if efectos:
            self._lcd_centered(2, " ".join(efectos)[:20])
        
        self._lcd_put(0, 3, "[OK] Continuar")
        self._leds_select_only()
        
        if key == 'SELECT':
            self._combo_actual = None
            # Usar función helper para determinar siguiente estado
            self.state = self._get_next_state_after_result()
    
    # === OPCIONES ===
    
    def _update_opciones(self, key):
        """Menú de opciones/ajustes"""
        self._lcd_clear()
        
        # Obtener valores actuales
        backlight = get_backlight_timeout(self.data)
        sound = get_sound_enabled(self.data)
        notif = get_notifications_enabled(self.data)
        notif_sound = get_notification_sound(self.data)
        
        # Lista de opciones
        opciones = [
            ("backlight", f"Standby: {backlight}s"),
            ("sound", f"Sonido: {'Si' if sound else 'No'}"),
            ("notif", f"Notific: {'Si' if notif else 'No'}"),
            ("notif_sound", f"Beep: {'Si' if notif_sound else 'No'}"),
            ("volver", "< Volver")
        ]
        
        total = len(opciones)
        
        # Título
        self._lcd_put(0, 0, "== OPCIONES ==")
        
        # Mostrar 3 opciones
        scroll = max(0, self._opciones_idx - 2)
        for i in range(3):
            idx = scroll + i
            if idx < total:
                prefix = ">" if idx == self._opciones_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}{opciones[idx][1][:18]}")
        
        # LEDs
        can_up = self._opciones_idx > 0
        can_down = self._opciones_idx < total - 1
        self._leds_scroll(can_up, can_down)
        
        if key == 'UP' and can_up:
            self._opciones_idx -= 1
        elif key == 'DOWN' and can_down:
            self._opciones_idx += 1
        elif key == 'SELECT':
            accion = opciones[self._opciones_idx][0]
            
            if accion == "backlight":
                # Ciclar: 15, 30, 60, 120, 300 (5min)
                valores = [15, 30, 60, 120, 300]
                idx_actual = valores.index(backlight) if backlight in valores else 1
                nuevo = valores[(idx_actual + 1) % len(valores)]
                set_backlight_timeout(self.data, nuevo)
                save_career(self.data)
                play_sound('button')
            elif accion == "sound":
                set_sound_enabled(self.data, not sound)
                save_career(self.data)
                if not sound:  # Ahora está encendido
                    play_sound('button')
            elif accion == "notif":
                set_notifications_enabled(self.data, not notif)
                save_career(self.data)
                play_sound('button')
            elif accion == "notif_sound":
                set_notification_sound(self.data, not notif_sound)
                save_career(self.data)
                play_sound('button')
            elif accion == "volver":
                self.state = CareerState.MENU_PRINCIPAL
                self.menu_idx = 0
                self.scroll_idx = 0
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL
            self.menu_idx = 0
            self.scroll_idx = 0
    
    # === PORTAL WIFI ===
    
    def _update_portal_wifi(self, key):
        """Lanza el portal WiFi"""
        self._lcd_clear()
        
        self._lcd_centered(0, "PORTAL WiFi")
        self._lcd_centered(1, "Abriendo portal...")
        self._lcd_centered(2, "Conecta a la red")
        self._lcd_centered(3, "PSIC-O-TRONIC")
        
        self._lcd_render()
        self._leds_off()
        
        # Guardar antes de salir
        save_career(self.data)
        
        # Importar y ejecutar portal
        try:
            from wifi_portal import run_wifi_portal
            
            def lcd_callback(lines):
                self._lcd_force_clear()
                for i, line in enumerate(lines[:4]):
                    self._lcd_centered(i, line[:20])
                self._lcd_render()
            
            def check_cancel():
                return self.btn_select.value() == 0
            
            result = run_wifi_portal(lcd_callback=lcd_callback, check_button=check_cancel)
            
            # Resultado
            self._lcd_force_clear()
            if result.get("connected"):
                self._lcd_centered(1, "WiFi conectado!")
            else:
                self._lcd_centered(1, "Portal cerrado")
            self._lcd_centered(3, "[OK] Continuar")
            self._lcd_render()
            
            # Esperar OK
            while self.btn_select.value() == 1:
                time.sleep(0.1)
            time.sleep(0.2)
            
        except Exception as e:
            print(f"[PORTAL] Error: {e}")
        
        # Volver
        self._lcd_force_clear()
        self.state = CareerState.MENU_PRINCIPAL
        self.menu_idx = 0
        self.scroll_idx = 0

    # === CASOS FAMILIARES ===

    def _update_caso_familiar(self, key):
        """Menú de casos familiares"""
        self._lcd_clear()

        # Verificar si tiene la mejora necesaria
        if not tiene_mejora(self.data, "album_familia"):
            self._lcd_centered(0, "BLOQUEADO")
            self._lcd_centered(1, "Necesitas comprar")
            self._lcd_centered(2, "Album de Familia")
            self._lcd_put(0, 3, "[OK] Volver")
            self._leds_select_only()
            if key == 'SELECT' or key == 'BACK':
                self.state = CareerState.MENU_PRINCIPAL
            return

        if not hasattr(self, '_caso_idx'):
            self._caso_idx = 0

        # Verificar si hay caso activo
        caso_activo = get_caso_activo(self.data)
        if caso_activo:
            # Mostrar caso en progreso
            self._lcd_centered(0, "CASO EN CURSO")
            self._lcd_centered(1, caso_activo["nombre"][:20])
            prog = f"{caso_activo['miembros_curados']}/{caso_activo['miembros_total']}"
            self._lcd_centered(2, f"Progreso: {prog}")
            self._lcd_put(0, 3, "[OK]Continuar [^]No")

            self._leds_scroll(True, False)

            if key == 'SELECT':
                # Continuar con siguiente miembro
                siguiente = get_siguiente_familiar(self.data)
                if siguiente:
                    self._familiar_actual = siguiente
                    self.state = CareerState.GENERANDO
                else:
                    # Caso terminado
                    resultado = finalizar_caso_familiar(self.data)
                    self._caso_resultado = resultado
                    self.state = CareerState.CASO_COMPLETADO
            elif key == 'UP' or key == 'BACK':
                self.state = CareerState.MENU_PRINCIPAL
            return

        # Lista de casos disponibles
        casos = list(CASOS_FAMILIARES.items())
        total_items = len(casos) + 1  # +1 para Volver

        self._lcd_put(0, 0, "CASOS FAMILIARES")

        for i in range(3):
            idx = self._caso_idx + i if self._caso_idx < len(casos) else self._caso_idx
            if idx < len(casos):
                caso_id, caso = casos[idx]
                prefix = ">" if idx == self._caso_idx else " "
                nombre = caso["nombre"][:17]
                self._lcd_put(0, 1 + i, f"{prefix}{nombre}")
            elif idx == len(casos):
                prefix = ">" if idx == self._caso_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")

        can_up = self._caso_idx > 0
        can_down = self._caso_idx < total_items - 1
        self._leds_scroll(can_up, can_down)

        if key == 'UP' and can_up:
            self._caso_idx -= 1
        elif key == 'DOWN' and can_down:
            self._caso_idx += 1
        elif key == 'SELECT':
            if self._caso_idx < len(casos):
                caso_id, caso = casos[self._caso_idx]
                iniciar_caso_familiar(self.data, caso_id)
                save_career(self.data)
                play_sound('mensaje')
                # Iniciar con el primer miembro
                siguiente = get_siguiente_familiar(self.data)
                if siguiente:
                    self._familiar_actual = siguiente
                    self.state = CareerState.GENERANDO
            else:
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL

    def _update_caso_completado(self, key):
        """Resultado de caso familiar completado"""
        self._lcd_clear()

        resultado = getattr(self, '_caso_resultado', None)
        if not resultado:
            self.state = CareerState.MENU_PRINCIPAL
            return

        if self.frame == 1:
            if resultado["completado"]:
                play_sound('level_up')
            else:
                play_sound('huye')

        # Animación
        if resultado["completado"]:
            titulos = ["CASO COMPLETADO!", "FAMILIA CURADA!", "EXITO TOTAL!"]
            self._lcd_centered(0, titulos[(self.frame // 10) % 3])
        else:
            self._lcd_centered(0, "CASO PARCIAL")

        self._lcd_centered(1, f"Curados: {resultado['curados']}/{resultado['total']}")

        recompensa = resultado.get("recompensa", {})
        if recompensa.get("dinero"):
            self._lcd_centered(2, f"+{recompensa['dinero']}E")
            if self.frame == 1:
                from career_data import add_dinero
                add_dinero(self.data, recompensa["dinero"])
                save_career(self.data)

        self._lcd_put(0, 3, "[OK] Continuar")
        self._leds_select_only()

        if key == 'SELECT':
            self._caso_resultado = None
            self.state = CareerState.MENU_PRINCIPAL

    # === TORNEOS ===

    def _update_torneo(self, key):
        """Menú de torneos semanales"""
        self._lcd_clear()

        if not hasattr(self, '_torneo_idx'):
            self._torneo_idx = 0

        # Verificar si hay torneo activo
        torneo_activo = self.data.get("torneo_activo")
        if torneo_activo:
            self._lcd_centered(0, "TORNEO ACTIVO")
            self._lcd_centered(1, torneo_activo["nombre"][:20])
            stats = torneo_activo["stats"]
            self._lcd_put(0, 2, f"Curados:{stats['pacientes_curados']}")

            if stats["violaciones"] > 0:
                self._lcd_put(0, 3, f"Violaciones:{stats['violaciones']}")
            else:
                self._lcd_put(0, 3, "[OK]Info [^]Cancelar")

            self._leds_scroll(True, False)

            if key == 'UP':
                # Cancelar torneo
                self.data["torneo_activo"] = None
                save_career(self.data)
                play_sound('huye')
            elif key == 'SELECT' or key == 'BACK':
                self.state = CareerState.MENU_PRINCIPAL
            return

        # Lista de torneos
        torneos = list(TORNEOS.items())
        total_items = len(torneos) + 1

        self._lcd_put(0, 0, "TORNEOS SEMANALES")

        for i in range(3):
            idx = self._torneo_idx + i if self._torneo_idx < len(torneos) else self._torneo_idx
            if idx < len(torneos):
                torneo_id, torneo = torneos[idx]
                prefix = ">" if idx == self._torneo_idx else " "
                nombre = torneo["nombre"][:17]
                self._lcd_put(0, 1 + i, f"{prefix}{nombre}")
            elif idx == len(torneos):
                prefix = ">" if idx == self._torneo_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}< Volver")

        can_up = self._torneo_idx > 0
        can_down = self._torneo_idx < total_items - 1
        self._leds_scroll(can_up, can_down)

        if key == 'UP' and can_up:
            self._torneo_idx -= 1
        elif key == 'DOWN' and can_down:
            self._torneo_idx += 1
        elif key == 'SELECT':
            if self._torneo_idx < len(torneos):
                torneo_id, torneo = torneos[self._torneo_idx]
                # Mostrar detalles antes de iniciar
                self._torneo_seleccionado = (torneo_id, torneo)
                self._lcd_force_clear()
                self._lcd_centered(0, torneo["nombre"][:20])
                self._lcd_put(0, 1, torneo["desc"][:20])
                premio = torneo.get("premio", {})
                self._lcd_put(0, 2, f"Premio: {premio.get('dinero', 0)}E")
                self._lcd_put(0, 3, "[OK]Iniciar [^]No")
                self._lcd_render()

                # Esperar confirmación
                while True:
                    time.sleep(0.1)
                    if self.btn_select.value() == 0:
                        iniciar_torneo(self.data, torneo_id)
                        save_career(self.data)
                        play_sound('mensaje')
                        break
                    if self.btn_up.value() == 0:
                        break
                time.sleep(0.2)
            else:
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL

    def _update_torneo_resultado(self, key):
        """Resultado de torneo finalizado"""
        self._lcd_clear()

        resultado = getattr(self, '_torneo_resultado', None)
        if not resultado:
            self.state = CareerState.MENU_PRINCIPAL
            return

        if self.frame == 1:
            if resultado["gano"]:
                play_sound('level_up')
            else:
                play_sound('game_over')

        if resultado["gano"]:
            titulos = ["TORNEO GANADO!", "VICTORIA!", "CAMPEON!"]
            self._lcd_centered(0, titulos[(self.frame // 10) % 3])
        else:
            self._lcd_centered(0, "TORNEO PERDIDO")

        self._lcd_centered(1, resultado["torneo"][:20])

        premio = resultado.get("premio")
        if premio:
            if premio.get("dinero"):
                self._lcd_centered(2, f"+{premio['dinero']}E")
                if self.frame == 1:
                    from career_data import add_dinero
                    add_dinero(self.data, premio["dinero"])
            if premio.get("titulo"):
                self._lcd_put(0, 2, f"Titulo: {premio['titulo']}")
        else:
            self._lcd_centered(2, "Sin premio")

        self._lcd_put(0, 3, "[OK] Continuar")
        self._leds_select_only()

        if key == 'SELECT':
            save_career(self.data)
            self._torneo_resultado = None
            self.state = CareerState.MENU_PRINCIPAL

    # === RACHA BONUS ===

    def _update_racha_bonus(self, key):
        """Notificación de bonus por racha"""
        self._lcd_clear()

        bonus = getattr(self, '_racha_bonus_info', None)
        if not bonus:
            self.state = CareerState.FEEDBACK
            return

        if self.frame == 1:
            play_sound('level_up')

        # Animación de fuego
        fuego = ["~*~", "*~*", "~*~", "***"]
        f = fuego[(self.frame // 5) % 4]

        tipo = bonus.get("tipo", "aciertos")
        racha = bonus.get("racha", 0)

        self._lcd_centered(0, f"{f} RACHA {f}")
        self._lcd_centered(1, f"{racha} {tipo}!")

        # Mostrar bonus
        if racha >= 10:
            self._lcd_centered(2, "EN LLAMAS! x5")
        elif racha >= 7:
            self._lcd_centered(2, "IMPARABLE! x3")
        elif racha >= 5:
            self._lcd_centered(2, "RACHA! x2")
        elif racha >= 3:
            self._lcd_centered(2, "Bonus activo")

        self._lcd_put(0, 3, "[OK] Continuar")
        self._leds_select_only()

        if key == 'SELECT':
            self._racha_bonus_info = None
            self.state = CareerState.FEEDBACK

    # === CONFIG (Configuración avanzada) ===

    def _update_config(self, key):
        """Configuración avanzada de la carrera"""
        self._lcd_clear()

        if not hasattr(self, '_config_idx'):
            self._config_idx = 0

        opciones = [
            ("reset_tutorial", "Reset tutoriales"),
            ("export_data", "Exportar datos"),
            ("borrar_carrera", "Borrar carrera"),
            ("volver", "< Volver")
        ]

        self._lcd_put(0, 0, "== CONFIGURACION ==")

        for i in range(3):
            idx = self._config_idx + i if self._config_idx < len(opciones) - 1 else max(0, len(opciones) - 3)
            actual_idx = self._config_idx
            if idx < len(opciones):
                prefix = ">" if idx == actual_idx else " "
                self._lcd_put(0, 1 + i, f"{prefix}{opciones[idx][1][:18]}")

        can_up = self._config_idx > 0
        can_down = self._config_idx < len(opciones) - 1
        self._leds_scroll(can_up, can_down)

        if key == 'UP' and can_up:
            self._config_idx -= 1
        elif key == 'DOWN' and can_down:
            self._config_idx += 1
        elif key == 'SELECT':
            accion = opciones[self._config_idx][0]
            if accion == "reset_tutorial":
                self.data["tutoriales_vistos"] = []
                save_career(self.data)
                play_sound('button')
            elif accion == "borrar_carrera":
                # Confirmar antes de borrar
                self._lcd_force_clear()
                self._lcd_centered(0, "CONFIRMAR BORRADO")
                self._lcd_centered(1, "Se perdera TODO")
                self._lcd_centered(2, "el progreso")
                self._lcd_put(0, 3, "[OK]Borrar [^]No")
                self._lcd_render()

                while True:
                    time.sleep(0.1)
                    if self.btn_select.value() == 0:
                        # Borrar carrera
                        from career_data import reset_career
                        reset_career()
                        self.data = None
                        self.exit_requested = True
                        return
                    if self.btn_up.value() == 0:
                        break
                time.sleep(0.2)
            elif accion == "volver":
                self.state = CareerState.MENU_PRINCIPAL
        elif key == 'BACK':
            self.state = CareerState.MENU_PRINCIPAL

    # === PANTALLA DE ERROR ===

    def _update_error(self, key):
        """Pantalla de error con información amigable"""
        self._lcd_clear()
        
        # Obtener info del error
        if ERROR_HANDLER_AVAILABLE and self._error_handler:
            info = self._error_handler.get_display_info()
            if info:
                self._lcd_put(0, 0, info["line0"])
                self._lcd_put(0, 1, info["line1"])
                self._lcd_put(0, 2, info["line2"])
                self._lcd_put(0, 3, info["line3"])
            else:
                self._lcd_centered(0, "ERROR")
                self._lcd_centered(1, self.error_msg[:20] if self.error_msg else "Algo fallo")
                self._lcd_centered(3, "[OK] Volver")
        else:
            # Fallback si no hay error handler
            self._lcd_centered(0, "!! ERROR !!")
            self._lcd_centered(1, self.error_msg[:20] if self.error_msg else "Error desconocido")
            self._lcd_centered(3, "[OK] Volver")
        
        # Parpadear LED
        self.blink_counter = (self.blink_counter + 1) % 10
        self.led_notify.value(1 if self.blink_counter < 5 else 0)
        
        self._leds_select_only()
        
        if key == 'SELECT' or key == 'BACK':
            # Limpiar error
            if ERROR_HANDLER_AVAILABLE and self._error_handler:
                self._error_handler.clear()
            self._error_info = None
            self.error_msg = ""
            self.led_notify.value(0)
            
            # Registrar actividad antes de cambiar de estado
            self._register_activity()
            self._wake_up()

            # Volver al estado anterior o al screensaver
            if hasattr(self, '_pre_error_state') and self._pre_error_state:
                # Si estaba generando, volver al screensaver
                if self._pre_error_state == CareerState.GENERANDO:
                    self.state = CareerState.SCREENSAVER
                else:
                    self.state = self._pre_error_state
                self._pre_error_state = None
            else:
                self.state = CareerState.SCREENSAVER
    
    # === VERIFICACIÓN DE MEMORIA ===
    
    def _check_memory_periodically(self):
        """Verifica memoria periódicamente"""
        if ERROR_HANDLER_AVAILABLE and self.frame % 100 == 0:
            check_memory()
    
    # === LOOP PRINCIPAL ===
    
    def run(self):
        """Ejecuta el modo carrera"""
        print("[CAREER] Iniciando modo Mi Consulta")
        
        self._lcd_force_clear()
        self._leds_on()  # Encender LEDs de botones al iniciar
        
        state_handlers = {
            CareerState.INIT: self._update_init,
            CareerState.SETUP_TITULO: self._update_setup_titulo,
            CareerState.SETUP_GENERATING: self._update_setup_generating,
            CareerState.SETUP_CONFIRM: self._update_setup_confirm,
            CareerState.GENERANDO: self._update_generando,
            CareerState.SCREENSAVER: self._update_screensaver,
            CareerState.MENU_PRINCIPAL: self._update_menu_principal,
            CareerState.LISTA_MENSAJES: self._update_lista_mensajes,
            CareerState.LISTA_PACIENTES: self._update_lista_pacientes,
            CareerState.VER_PACIENTE: self._update_ver_paciente,
            CareerState.LEYENDO_MENSAJE: self._update_leyendo_mensaje,
            CareerState.ELIGIENDO_RESPUESTA: self._update_eligiendo_respuesta,
            CareerState.FEEDBACK: self._update_feedback,
            CareerState.RESULTADO_PACIENTE: self._update_resultado_paciente,
            CareerState.SUBIDA_NIVEL: self._update_subida_nivel,
            CareerState.ESTADISTICAS: self._update_estadisticas,
            # Tienda El Camello
            CareerState.TUTORIAL_CAMELLO: self._update_tutorial_camello,
            CareerState.TUTORIAL_INICIO: self._update_tutorial_inicio,
            CareerState.AYUDA: self._update_ayuda,
            CareerState.TIENDA: self._update_tienda,
            CareerState.TIENDA_COMPRAR: self._update_tienda_comprar,
            CareerState.INVENTARIO: self._update_inventario,
            CareerState.USAR_ITEM: self._update_usar_item,
            # Sistemas principales
            CareerState.LOGROS: self._update_logros,
            CareerState.LOGRO_DESBLOQUEADO: self._update_logro_desbloqueado,
            CareerState.MEJORAS: self._update_mejoras,
            CareerState.MEJORA_COMPRAR: self._update_mejora_comprar,
            CareerState.EVENTO_DIA: self._update_evento_dia,
            # Misiones
            CareerState.MISIONES: self._update_misiones,
            CareerState.MISION_DETALLE: self._update_mision_detalle,
            # Apuestas
            CareerState.APUESTAS: self._update_apuestas,
            CareerState.APUESTA_CONFIRMAR: self._update_apuesta_confirmar,
            CareerState.APUESTA_RESULTADO: self._update_apuesta_resultado,
            # Crafting
            CareerState.CRAFTING: self._update_crafting,
            CareerState.CRAFTING_CONFIRMAR: self._update_crafting_confirmar,
            # Personalización
            CareerState.BATAS: self._update_batas,
            CareerState.BATA_COMPRAR: self._update_bata_comprar,
            # Prestigio
            CareerState.PRESTIGIO: self._update_prestigio,
            CareerState.PRESTIGIO_CONFIRMAR: self._update_prestigio_confirmar,
            # Oráculo
            CareerState.ORACULO: self._update_oraculo,
            # Regalo
            CareerState.REGALO_PACIENTE: self._update_regalo_paciente,
            # Combo
            CareerState.COMBO_ACTIVADO: self._update_combo_activado,
            # Opciones
            CareerState.OPCIONES: self._update_opciones,
            # Portal WiFi
            CareerState.PORTAL_WIFI: self._update_portal_wifi,
            # Error
            CareerState.ERROR: self._update_error,
            # Casos familiares y torneos
            CareerState.CASO_FAMILIAR: self._update_caso_familiar,
            CareerState.CASO_COMPLETADO: self._update_caso_completado,
            CareerState.TORNEO: self._update_torneo,
            CareerState.TORNEO_RESULTADO: self._update_torneo_resultado,
            # Racha bonus
            CareerState.RACHA_BONUS: self._update_racha_bonus,
            # Configuración
            CareerState.CONFIG: self._update_config,
        }
        
        while not self.exit_requested:
            time.sleep(0.08)
            self.frame += 1
            self.opt_scroll += 1
            
            # Log cambio estado
            if self.state != self.prev_state:
                print(f"[CAREER] State: {self.prev_state} -> {self.state}")
                self.prev_state = self.state
                self.frame = 0
                self._lcd_force_clear()
            
            # Input
            key = self._get_input()
            if key:
                self._register_activity()
            
            # Handler
            handler = state_handlers.get(self.state)
            if handler:
                try:
                    handler(key)
                except Exception as e:
                    print(f"[CAREER] Error en handler {self.state}: {e}")
                    # Ir a estado de error
                    self.error_msg = str(e)[:20]
                    self.state = CareerState.ERROR
            
            # Render
            self._lcd_render()
            
            # Backlight
            self._check_backlight()
            
            # Notificacion
            self._update_notification()
            
            # Verificar memoria periódicamente
            self._check_memory_periodically()
            
            gc.collect()
        
        # Saliendo del modo carrera
        print("[CAREER] Saliendo al menu principal")
        self._leds_off()
        self.led_notify.value(0)
        self._lcd_force_clear()


def run_career_mode(lcd, btn_up, btn_select, btn_down, led_up, led_select, led_down, led_notify):
    """Helper para ejecutar el modo carrera"""
    mode = CareerMode(lcd, btn_up, btn_select, btn_down, led_up, led_select, led_down, led_notify)
    mode.run()
