# ============================================================================
# CAREER_DATA.PY - Persistencia y estructuras de datos
# PSIC-O-TRONIC - Modo Mi Consulta
# ============================================================================

import ujson
import os

# Importar sistema de errores
try:
    from error_handler import report_error
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False

# Archivo de guardado
CAREER_FILE = "/career_save.json"

# Configuracion por defecto
DEFAULT_CAREER = {
    "jugador": {
        "titulo": "",           # Doctor/Doctora/Doctore
        "nombre": "",           # Nombre generado por IA
        "xp": 0,
        "nivel": 1,
        "rango": "Becario",
        "titulos_disponibles": [],  # Titulos desbloqueados por logros
        "titulo_activo": "",        # Titulo seleccionado para mostrar
        "stats": {
            "pacientes_curados": 0,
            "pacientes_abandonados": 0,
            "sesiones_correctas": 0,
            "sesiones_incorrectas": 0,
            "dias_jugados": 0,
            "fecha_inicio": "",
            # Rachas
            "racha_aciertos_actual": 0,
            "racha_aciertos_max": 0,
            "racha_curados_actual": 0,
            "racha_curados_max": 0,
            # Stats para logros
            "dinero_max": 0,
            "farmacos_usados": 0,
            "tipos_farmacos_usados": [],
            "suero_usado": 0,
            "camisa_usada": 0,
            "curas_perfectas": 0,
            "curas_rapidas": 0,
            "pacientes_dificiles": 0,
            # Pacientes especiales
            "vips_curados": 0,
            "influencers_curados": 0,
            "misteriosos_curados": 0,
            # Stats diarios (se resetean)
            "sesiones_hoy": 0,
            "dinero_hoy": 0,
            "farmacos_hoy": 0,
            "curados_hoy": 0,
            "huidos_hoy": 0,
            # Crafting
            "items_crafteados": 0
        }
    },
    "economia": {
        "dinero": 100,          # Empiezas con algo
        "total_ganado": 0,
        "total_gastado": 0
    },
    "inventario": [],           # Lista de items {id, cantidad}
    "mejoras": [],              # Mejoras de consulta compradas
    "logros": {
        "desbloqueados": [],    # IDs de logros conseguidos
        "notificados": [],      # Logros ya mostrados al jugador
        "pendientes": []        # Logros por notificar
    },
    "evento_hoy": {             # Evento diario actual
        "id": "",
        "nombre": "",
        "fecha": "",
        "efecto": {}
    },
    "evento_ayer": "",          # Para deja vu
    "descuento_logros": 0,      # Descuento acumulado por logros
    
    # === NUEVOS SISTEMAS ===
    "misiones": {
        "diarias": [],          # Misiones del día
        "semanales": [],        # Misiones de la semana
        "dia_generadas": "",    # Fecha de generación diarias
        "semana_generadas": ""  # Fecha de generación semanales
    },
    "reputacion": {
        "valor": 0,             # -100 a +100
        "historial": []         # Últimos cambios
    },
    "apuestas": {
        "totales": 0,
        "ganadas": 0,
        "perdidas": 0,
        "ganancias_total": 0,
        "perdidas_total": 0,
        "racha_actual": 0,
        "racha_max": 0
    },
    "apuesta_activa": None,     # Apuesta en curso
    "caso_activo": None,        # Caso familiar en curso
    "torneo_activo": None,      # Torneo en curso
    "batas_compradas": ["clasica"],
    "bata_equipada": "clasica",
    "decoraciones_compradas": [],
    "prestigio": {
        "nivel": 0,
        "bonus": 0,
        "estrellas": 0
    },
    "proximo_vip": False,       # Regalo recomendación
    "ultima_visita_oraculo": 0,
    "combos_activados": [],     # Combos del día
    
    "tutorials": {
        "tienda": False,
        "inventario": False,
        "mejoras": False,
        "logros": False,
        "evento": False,
        "misiones": False,
        "apuestas": False,
        "crafting": False
    },
    "pacientes": [],
    "mensajes_pendientes": [],
    "config": {
        "backlight_timeout": 30,
        "sound_enabled": True,
        "notifications_enabled": True,
        "notification_sound": True,
        "ultima_sync": "",
        "ultimo_dia_jugado": "",
        "ultima_actividad": "",          # Timestamp última vez activo
        "setup_completo": False
    },
    "programacion": {
        "proximos_mensajes": [],
        "ultimo_paciente_nuevo": "",
        "pacientes_nuevos_hoy": 0,
        "mensajes_recuperados": 0,       # Contador de mensajes catch-up
        "fecha_schedule": ""             # Fecha del schedule actual
    }
}

# === CATALOGO DE FARMACOS ===
# id, nombre (max 14), precio, descripcion, efecto, raro (necesita licencia B)
CATALOGO_FARMACOS = [
    # === BASICOS ===
    {
        "id": "placebo",
        "nombre": "Placebo Premium",
        "precio": 80,
        "desc": "50% de que funcione",
        "efecto": "placebo",
        "raro": False
    },
    {
        "id": "cafe",
        "nombre": "Cafe del Jefe",
        "precio": 100,
        "desc": "Doble XP en acierto",
        "efecto": "doble_xp",
        "raro": False
    },
    {
        "id": "aspirina",
        "nombre": "Aspirina Plus",
        "precio": 60,
        "desc": "+1 tolerancia temporal",
        "efecto": "tolerancia_temp",
        "raro": False
    },
    {
        "id": "vitaminas",
        "nombre": "Vitaminas C",
        "precio": 120,
        "desc": "+20% dinero sesion",
        "efecto": "bonus_dinero",
        "raro": False
    },
    
    # === INTERMEDIOS ===
    {
        "id": "ansio",
        "nombre": "Ansioliticos",
        "precio": 250,
        "desc": "-1 sesion restante",
        "efecto": "reduce_sesion",
        "raro": False
    },
    {
        "id": "electro",
        "nombre": "Electroshock",
        "precio": 350,
        "desc": "Quita 1 opcion mala",
        "efecto": "elimina_opcion",
        "raro": False
    },
    {
        "id": "hipno",
        "nombre": "Hipnosis",
        "precio": 400,
        "desc": "Fallo no resta prog",
        "efecto": "protege_fallo",
        "raro": False
    },
    {
        "id": "olvido",
        "nombre": "Pastilla Olvido",
        "precio": 500,
        "desc": "Resetea progreso a 0",
        "efecto": "reset_progreso",
        "raro": False
    },
    {
        "id": "energia",
        "nombre": "Bebida Energy",
        "precio": 300,
        "desc": "Doble dinero 2 sesiones",
        "efecto": "doble_dinero",
        "raro": False
    },
    
    # === AVANZADOS ===
    {
        "id": "lobo",
        "nombre": "Lobotomia Light",
        "precio": 800,
        "desc": "No puede huir",
        "efecto": "no_huir",
        "raro": False
    },
    {
        "id": "suero",
        "nombre": "Suero Verdad",
        "precio": 1000,
        "desc": "Revela respuesta OK",
        "efecto": "revela_respuesta",
        "raro": False
    },
    {
        "id": "esteroides",
        "nombre": "Esteroides",
        "precio": 700,
        "desc": "+50% XP 3 sesiones",
        "efecto": "xp_boost",
        "raro": False
    },
    {
        "id": "sedante",
        "nombre": "Sedante Fuerte",
        "precio": 600,
        "desc": "-2 sesiones restantes",
        "efecto": "reduce_sesion_2",
        "raro": False
    },
    {
        "id": "camisa",
        "nombre": "Camisa Fuerza",
        "precio": 2000,
        "desc": "Cura instantanea!",
        "efecto": "cura_instantanea",
        "raro": False
    },
    
    # === RAROS (Licencia Clase B) ===
    {
        "id": "lsd",
        "nombre": "LSD Terapeutico",
        "precio": 1500,
        "desc": "Paciente revela todo",
        "efecto": "revela_todo",
        "raro": True
    },
    {
        "id": "ketamina",
        "nombre": "Ketamina",
        "precio": 1200,
        "desc": "Ignora 2 fallos",
        "efecto": "protege_doble",
        "raro": True
    },
    {
        "id": "mdma",
        "nombre": "MDMA Puro",
        "precio": 900,
        "desc": "Paciente +3 tolerancia",
        "efecto": "mega_tolerancia",
        "raro": True
    },
    {
        "id": "morfina",
        "nombre": "Morfina",
        "precio": 1100,
        "desc": "Progreso no baja",
        "efecto": "protege_progreso",
        "raro": True
    },
    {
        "id": "experimental",
        "nombre": "Droga X",
        "precio": 2500,
        "desc": "Efecto aleatorio!",
        "efecto": "aleatorio",
        "raro": True
    },
    {
        "id": "zombi",
        "nombre": "Suero Zombi",
        "precio": 3000,
        "desc": "Revive paciente huido",
        "efecto": "revive",
        "raro": True
    },
    {
        "id": "clon",
        "nombre": "Clonazepam X",
        "precio": 1800,
        "desc": "Duplica recompensa",
        "efecto": "duplica_recompensa",
        "raro": True
    },
    {
        "id": "adrenalina",
        "nombre": "Adrenalina",
        "precio": 800,
        "desc": "Sin limite tiempo",
        "efecto": "sin_tiempo",
        "raro": True
    },
]

# XP por acciones
XP_SESION_CORRECTA = 3
XP_SESION_INCORRECTA = -2
XP_CURAR_PACIENTE_BASE = 15      # + sesiones_totales
XP_PACIENTE_ABANDONA = -20

# DINERO por acciones
DINERO_SESION_OK = 50
DINERO_SESION_MAL = 20
DINERO_CURAR_BASE = 100          # + sesiones * 20
DINERO_HUYE = -50

# Umbrales de progreso de paciente
PROGRESO_ABANDONO = -3           # Si llega a esto, abandona
PROGRESO_CURADO = 0              # Debe completar sesiones con progreso >= 0

# Pacientes
MIN_PACIENTES = 5
MAX_PACIENTES = 10
MIN_SESIONES = 5
MAX_SESIONES = 10

# Inventario
MAX_INVENTARIO = 5


def file_exists(filename):
    """Comprueba si un archivo existe"""
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def load_career():
    """
    Carga datos de carrera desde flash.
    
    Returns:
        Dict con datos de carrera
    """
    if file_exists(CAREER_FILE):
        try:
            with open(CAREER_FILE, "r") as f:
                data = ujson.load(f)
                # Merge con defaults por si hay campos nuevos
                merged = _deep_merge(DEFAULT_CAREER.copy(), data)
                return merged
        except ValueError as e:
            print(f"[CAREER] JSON corrupt: {e}")
            if ERROR_HANDLER_AVAILABLE:
                report_error("storage_corrupt", "career_save.json", e)
        except OSError as e:
            print(f"[CAREER] Read error: {e}")
            if ERROR_HANDLER_AVAILABLE:
                report_error("storage_read_error", str(e), e)
        except Exception as e:
            print(f"[CAREER] Error loading: {e}")
            if ERROR_HANDLER_AVAILABLE:
                report_error("unknown_error", f"load_career: {e}", e)
    return _deep_copy(DEFAULT_CAREER)


def save_career(data):
    """
    Guarda datos de carrera en flash.
    
    Args:
        data: Dict con datos de carrera
    
    Returns:
        True si exito
    """
    try:
        with open(CAREER_FILE, "w") as f:
            ujson.dump(data, f)
        return True
    except OSError as e:
        print(f"[CAREER] Write error: {e}")
        if ERROR_HANDLER_AVAILABLE:
            # Detectar tipo de error
            err_str = str(e)
            if "ENOSPC" in err_str or "28" in err_str:
                report_error("storage_full", "career_save.json", e)
            else:
                report_error("storage_write_error", str(e), e)
        return False
    except Exception as e:
        print(f"[CAREER] Error saving: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("unknown_error", f"save_career: {e}", e)
        return False


def reset_career():
    """Resetea la carrera a valores por defecto"""
    save_career(_deep_copy(DEFAULT_CAREER))


def _deep_copy(obj):
    """Copia profunda de dict/list"""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(i) for i in obj]
    return obj


def _deep_merge(base, update):
    """Merge profundo de dicts"""
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# === FUNCIONES DE JUGADOR ===

def get_player_info(data):
    """Obtiene info del jugador"""
    return data.get("jugador", DEFAULT_CAREER["jugador"])


def set_player_name(data, titulo, nombre):
    """
    Establece titulo y nombre del jugador.
    
    Args:
        data: Datos de carrera
        titulo: "Doctor", "Doctora" o "Doctore"
        nombre: Nombre generado por IA
    """
    data["jugador"]["titulo"] = titulo
    data["jugador"]["nombre"] = nombre


def add_xp(data, amount):
    """
    Anade o resta XP al jugador.
    Maneja subidas y bajadas de nivel.
    
    Args:
        data: Datos de carrera
        amount: XP a anadir (puede ser negativo)
    
    Returns:
        Dict con info del cambio: {"nivel_cambio": 0/1/-1, "nuevo_nivel": X}
    """
    jugador = data["jugador"]
    jugador["xp"] += amount
    
    result = {"nivel_cambio": 0, "nuevo_nivel": jugador["nivel"]}
    
    # Calcular XP necesario para siguiente nivel
    xp_siguiente = jugador["nivel"] * 50
    
    # Subir de nivel
    if jugador["xp"] >= xp_siguiente:
        jugador["nivel"] += 1
        jugador["xp"] -= xp_siguiente
        result["nivel_cambio"] = 1
        result["nuevo_nivel"] = jugador["nivel"]
    
    # Bajar de nivel
    elif jugador["xp"] < 0 and jugador["nivel"] > 1:
        jugador["nivel"] -= 1
        xp_nivel_anterior = jugador["nivel"] * 50
        jugador["xp"] = xp_nivel_anterior + jugador["xp"]  # xp es negativo
        if jugador["xp"] < 0:
            jugador["xp"] = 0
        result["nivel_cambio"] = -1
        result["nuevo_nivel"] = jugador["nivel"]
    
    elif jugador["xp"] < 0:
        jugador["xp"] = 0
    
    return result


def set_rango(data, rango):
    """Establece el rango del jugador"""
    data["jugador"]["rango"] = rango


def get_nivel(data):
    """Obtiene nivel actual"""
    return data["jugador"]["nivel"]


def get_xp(data):
    """Obtiene XP actual"""
    return data["jugador"]["xp"]


def get_xp_to_next(data):
    """Obtiene XP necesario para siguiente nivel"""
    return data["jugador"]["nivel"] * 50


def increment_stat(data, stat_name, amount=1):
    """Incrementa una estadistica"""
    if stat_name in data["jugador"]["stats"]:
        data["jugador"]["stats"][stat_name] += amount


def get_stats(data):
    """Obtiene estadisticas"""
    return data["jugador"]["stats"]


# === FUNCIONES DE PACIENTES ===

def get_pacientes(data):
    """Obtiene lista de pacientes activos"""
    return data.get("pacientes", [])


def get_paciente_by_id(data, paciente_id):
    """Obtiene un paciente por su ID"""
    for p in data["pacientes"]:
        if p["id"] == paciente_id:
            return p
    return None


def add_paciente(data, paciente):
    """
    Anade un nuevo paciente.
    
    Args:
        data: Datos de carrera
        paciente: Dict con datos del paciente
    """
    # Asignar ID unico
    max_id = 0
    for p in data["pacientes"]:
        if p["id"] > max_id:
            max_id = p["id"]
    paciente["id"] = max_id + 1
    
    data["pacientes"].append(paciente)
    return paciente["id"]


def remove_paciente(data, paciente_id):
    """Elimina un paciente"""
    data["pacientes"] = [p for p in data["pacientes"] if p["id"] != paciente_id]
    # Tambien eliminar sus mensajes pendientes
    data["mensajes_pendientes"] = [
        m for m in data["mensajes_pendientes"] 
        if m["paciente_id"] != paciente_id
    ]


def update_paciente_progreso(data, paciente_id, correcto):
    """
    Actualiza progreso de un paciente tras una sesion.
    
    Args:
        data: Datos de carrera
        paciente_id: ID del paciente
        correcto: True si respondio bien
    
    Returns:
        Dict con resultado: {"estado": "continua/curado/abandona", "paciente": {...}}
    """
    paciente = get_paciente_by_id(data, paciente_id)
    if not paciente:
        return {"estado": "error", "paciente": None}
    
    # Actualizar progreso
    if correcto:
        paciente["progreso"] += 1
        paciente["sesiones_completadas"] += 1
    else:
        paciente["progreso"] -= 1
        # Decrementar tolerancia (errores restantes)
        tolerancia_actual = paciente.get("tolerancia", 3)
        paciente["tolerancia"] = max(0, tolerancia_actual - 1)
    
    # Verificar estado por progreso negativo
    if paciente["progreso"] <= PROGRESO_ABANDONO:
        return {"estado": "abandona", "paciente": paciente}
    
    # Verificar estado por tolerancia agotada
    if paciente.get("tolerancia", 3) <= 0:
        return {"estado": "abandona", "paciente": paciente}
    
    if paciente["sesiones_completadas"] >= paciente["sesiones_totales"]:
        if paciente["progreso"] >= PROGRESO_CURADO:
            return {"estado": "curado", "paciente": paciente}
        else:
            return {"estado": "abandona", "paciente": paciente}
    
    return {"estado": "continua", "paciente": paciente}


def add_historial_paciente(data, paciente_id, fecha, hora, respuesta, correcto, sesion=0, opcion_texto=""):
    """Anade entrada al historial de un paciente"""
    paciente = get_paciente_by_id(data, paciente_id)
    if paciente:
        if "historial" not in paciente:
            paciente["historial"] = []
        paciente["historial"].append({
            "fecha": fecha,
            "hora": hora,
            "respuesta": respuesta,
            "correcto": correcto,
            "sesion": sesion,
            "opcion_texto": opcion_texto
        })


def count_pacientes(data):
    """Cuenta pacientes activos"""
    return len(data["pacientes"])


def can_add_paciente(data):
    """True si se puede anadir otro paciente"""
    return count_pacientes(data) < MAX_PACIENTES


def needs_more_pacientes(data):
    """True si hay menos del minimo de pacientes"""
    return count_pacientes(data) < MIN_PACIENTES


# === FUNCIONES DE MENSAJES ===

def get_mensajes_pendientes(data):
    """Obtiene lista de mensajes pendientes"""
    return data.get("mensajes_pendientes", [])


def count_mensajes_pendientes(data):
    """Cuenta mensajes pendientes"""
    return len(data["mensajes_pendientes"])


def add_mensaje(data, mensaje):
    """
    Anade un mensaje pendiente.
    
    Args:
        data: Datos de carrera
        mensaje: Dict con datos del mensaje
    """
    # Asignar ID unico
    max_id = 0
    for m in data["mensajes_pendientes"]:
        if m.get("id_mensaje", 0) > max_id:
            max_id = m["id_mensaje"]
    mensaje["id_mensaje"] = max_id + 1
    
    data["mensajes_pendientes"].append(mensaje)
    return mensaje["id_mensaje"]


def get_mensaje_by_id(data, mensaje_id):
    """Obtiene un mensaje por su ID"""
    for m in data["mensajes_pendientes"]:
        if m["id_mensaje"] == mensaje_id:
            return m
    return None


def remove_mensaje(data, mensaje_id):
    """Elimina un mensaje pendiente"""
    data["mensajes_pendientes"] = [
        m for m in data["mensajes_pendientes"] 
        if m["id_mensaje"] != mensaje_id
    ]


def has_mensaje_pendiente_de(data, paciente_id):
    """True si hay mensaje pendiente de este paciente"""
    for m in data["mensajes_pendientes"]:
        if m["paciente_id"] == paciente_id:
            return True
    return False


# === FUNCIONES DE PROGRAMACION ===

def get_programacion(data):
    """Obtiene datos de programacion"""
    return data.get("programacion", DEFAULT_CAREER["programacion"])


def add_mensaje_programado(data, paciente_id, timestamp):
    """Programa un mensaje futuro"""
    prog = data["programacion"]
    prog["proximos_mensajes"].append({
        "paciente_id": paciente_id,
        "hora_programada": timestamp
    })


def get_mensajes_programados(data):
    """Obtiene mensajes programados"""
    return data["programacion"]["proximos_mensajes"]


def remove_mensaje_programado(data, paciente_id, timestamp):
    """Elimina un mensaje programado"""
    prog = data["programacion"]
    prog["proximos_mensajes"] = [
        m for m in prog["proximos_mensajes"]
        if not (m["paciente_id"] == paciente_id and m["hora_programada"] == timestamp)
    ]


def clear_mensajes_programados(data):
    """Limpia todos los mensajes programados"""
    data["programacion"]["proximos_mensajes"] = []


def set_ultimo_paciente_nuevo(data, fecha):
    """Registra cuando se anadio el ultimo paciente nuevo"""
    data["programacion"]["ultimo_paciente_nuevo"] = fecha


def get_pacientes_nuevos_hoy(data):
    """Obtiene cuantos pacientes nuevos llegaron hoy"""
    return data["programacion"].get("pacientes_nuevos_hoy", 0)


def increment_pacientes_nuevos_hoy(data):
    """Incrementa contador de pacientes nuevos hoy"""
    data["programacion"]["pacientes_nuevos_hoy"] = \
        data["programacion"].get("pacientes_nuevos_hoy", 0) + 1


def reset_pacientes_nuevos_hoy(data):
    """Resetea contador de pacientes nuevos (nuevo dia)"""
    data["programacion"]["pacientes_nuevos_hoy"] = 0


def get_fecha_schedule(data):
    """Obtiene fecha del schedule actual"""
    return data["programacion"].get("fecha_schedule", "")


def set_fecha_schedule(data, fecha):
    """Establece fecha del schedule actual"""
    data["programacion"]["fecha_schedule"] = fecha


def get_mensajes_recuperados(data):
    """Obtiene contador de mensajes recuperados hoy"""
    return data["programacion"].get("mensajes_recuperados", 0)


def increment_mensajes_recuperados(data):
    """Incrementa contador de mensajes recuperados"""
    data["programacion"]["mensajes_recuperados"] = \
        data["programacion"].get("mensajes_recuperados", 0) + 1


def reset_mensajes_recuperados(data):
    """Resetea contador de mensajes recuperados"""
    data["programacion"]["mensajes_recuperados"] = 0


def get_ultima_actividad(data):
    """Obtiene timestamp de última actividad"""
    return data["config"].get("ultima_actividad", "")


def set_ultima_actividad(data, timestamp):
    """Establece timestamp de última actividad"""
    data["config"]["ultima_actividad"] = timestamp


# === FUNCIONES DE CONFIG ===

def get_config(data):
    """Obtiene configuracion"""
    return data.get("config", DEFAULT_CAREER["config"])


def set_config(data, key, value):
    """Establece un valor de configuracion"""
    data["config"][key] = value


def is_setup_complete(data):
    """True si el setup inicial esta completo"""
    return data["config"].get("setup_completo", False)


def set_setup_complete(data, complete=True):
    """Marca el setup como completo"""
    data["config"]["setup_completo"] = complete


def get_backlight_timeout(data):
    """Obtiene timeout de backlight en segundos"""
    return data["config"].get("backlight_timeout", 30)


def set_backlight_timeout(data, seconds):
    """Establece timeout de backlight"""
    data["config"]["backlight_timeout"] = seconds


def get_sound_enabled(data):
    """Obtiene si el sonido está habilitado"""
    return data["config"].get("sound_enabled", True)


def set_sound_enabled(data, enabled):
    """Establece si el sonido está habilitado"""
    data["config"]["sound_enabled"] = enabled


def get_notifications_enabled(data):
    """Obtiene si las notificaciones están habilitadas"""
    return data["config"].get("notifications_enabled", True)


def set_notifications_enabled(data, enabled):
    """Establece si las notificaciones están habilitadas"""
    data["config"]["notifications_enabled"] = enabled


def get_notification_sound(data):
    """Obtiene si el sonido de notificaciones está habilitado"""
    return data["config"].get("notification_sound", True)


def set_notification_sound(data, enabled):
    """Establece si el sonido de notificaciones está habilitado"""
    data["config"]["notification_sound"] = enabled


def set_ultimo_dia_jugado(data, fecha):
    """Registra ultimo dia jugado"""
    data["config"]["ultimo_dia_jugado"] = fecha


def get_ultimo_dia_jugado(data):
    """Obtiene ultimo dia jugado"""
    return data["config"].get("ultimo_dia_jugado", "")


# === FUNCIONES DE UTILIDAD ===

def create_paciente_template():
    """Crea template vacio de paciente"""
    return {
        "id": 0,
        "nombre": "",
        "edad": "",
        "sexo": "",
        "ocupacion": "",
        "problema_corto": "",
        "problema_detalle": "",
        "personalidad": "",
        "sesiones_totales": 0,
        "sesiones_completadas": 0,
        "progreso": 0,
        "tolerancia": 3,        # Errores permitidos antes de huir
        "historial": [],
        "contexto_ia": "",
        # Cierres narrativos
        "cierre_curado": "",    # Texto al curar (40 chars)
        "cierre_huye": ""       # Texto al huir (40 chars)
    }


def create_mensaje_template():
    """Crea template vacio de mensaje"""
    return {
        "id_mensaje": 0,
        "paciente_id": 0,
        "timestamp": "",
        "contenido": "",
        "opciones": [],
        "correcta": 0,
        "feedback_correcto": "",
        "feedback_incorrecto": ""
    }


# === FUNCIONES DE ECONOMIA ===

def get_dinero(data):
    """Obtiene dinero actual"""
    if "economia" not in data:
        data["economia"] = DEFAULT_CAREER["economia"].copy()
    return data["economia"].get("dinero", 0)


def add_dinero(data, cantidad):
    """Añade (o resta) dinero"""
    if "economia" not in data:
        data["economia"] = DEFAULT_CAREER["economia"].copy()
    
    data["economia"]["dinero"] = max(0, data["economia"]["dinero"] + cantidad)
    
    if cantidad > 0:
        data["economia"]["total_ganado"] = \
            data["economia"].get("total_ganado", 0) + cantidad
    else:
        data["economia"]["total_gastado"] = \
            data["economia"].get("total_gastado", 0) + abs(cantidad)
    
    return data["economia"]["dinero"]


def get_economia_stats(data):
    """Obtiene stats de economía"""
    if "economia" not in data:
        data["economia"] = DEFAULT_CAREER["economia"].copy()
    return data["economia"]


# === FUNCIONES DE INVENTARIO ===

def get_inventario(data):
    """Obtiene lista de inventario"""
    if "inventario" not in data:
        data["inventario"] = []
    return data["inventario"]


def count_inventario(data):
    """Cuenta items totales en inventario"""
    inv = get_inventario(data)
    return sum(item.get("cantidad", 0) for item in inv)


def has_item(data, item_id):
    """Comprueba si tiene un item"""
    inv = get_inventario(data)
    for item in inv:
        if item["id"] == item_id and item.get("cantidad", 0) > 0:
            return True
    return False


def get_item_cantidad(data, item_id):
    """Obtiene cantidad de un item"""
    inv = get_inventario(data)
    for item in inv:
        if item["id"] == item_id:
            return item.get("cantidad", 0)
    return 0


def add_item(data, item_id, cantidad=1):
    """Añade item al inventario"""
    if "inventario" not in data:
        data["inventario"] = []
    
    # Buscar si ya existe
    for item in data["inventario"]:
        if item["id"] == item_id:
            item["cantidad"] = item.get("cantidad", 0) + cantidad
            return True
    
    # Comprobar espacio
    if count_inventario(data) >= MAX_INVENTARIO:
        return False
    
    # Añadir nuevo
    data["inventario"].append({
        "id": item_id,
        "cantidad": cantidad
    })
    return True


def remove_item(data, item_id, cantidad=1):
    """Quita item del inventario"""
    if "inventario" not in data:
        return False
    
    for item in data["inventario"]:
        if item["id"] == item_id:
            if item.get("cantidad", 0) >= cantidad:
                item["cantidad"] -= cantidad
                # Limpiar si está vacío
                if item["cantidad"] <= 0:
                    data["inventario"].remove(item)
                return True
    return False


def get_farmaco_by_id(item_id):
    """Obtiene datos de fármaco del catálogo"""
    for f in CATALOGO_FARMACOS:
        if f["id"] == item_id:
            return f
    return None


def puede_comprar(data, item_id):
    """Comprueba si puede comprar un fármaco"""
    farmaco = get_farmaco_by_id(item_id)
    if not farmaco:
        return False, "No existe"
    
    dinero = get_dinero(data)
    if dinero < farmaco["precio"]:
        return False, "Sin pasta"
    
    if count_inventario(data) >= MAX_INVENTARIO:
        return False, "Inventario lleno"
    
    return True, "OK"


def comprar_farmaco(data, item_id):
    """Compra un fármaco. Returns (exito, mensaje)"""
    puede, msg = puede_comprar(data, item_id)
    if not puede:
        return False, msg
    
    farmaco = get_farmaco_by_id(item_id)
    add_dinero(data, -farmaco["precio"])
    add_item(data, item_id)
    return True, farmaco["nombre"]


# === FUNCIONES DE TUTORIAL ===

def tutorial_visto(data, tutorial_id):
    """Comprueba si se ha visto un tutorial"""
    if "tutorials" not in data:
        data["tutorials"] = {"tienda": False, "inventario": False}
    return data["tutorials"].get(tutorial_id, False)


def marcar_tutorial(data, tutorial_id):
    """Marca un tutorial como visto"""
    if "tutorials" not in data:
        data["tutorials"] = {"tienda": False, "inventario": False}
    data["tutorials"][tutorial_id] = True


# === EFECTOS ACTIVOS ===

def get_efectos_activos(data, paciente_id):
    """Obtiene efectos activos para un paciente"""
    # Los efectos se almacenan en el paciente
    p = get_paciente_by_id(data, paciente_id)
    if p:
        return p.get("efectos", [])
    return []


def add_efecto_paciente(data, paciente_id, efecto):
    """Añade un efecto activo a un paciente"""
    p = get_paciente_by_id(data, paciente_id)
    if p:
        if "efectos" not in p:
            p["efectos"] = []
        p["efectos"].append(efecto)
        return True
    return False


def remove_efecto_paciente(data, paciente_id, efecto):
    """Elimina un efecto de un paciente"""
    p = get_paciente_by_id(data, paciente_id)
    if p and "efectos" in p:
        if efecto in p["efectos"]:
            p["efectos"].remove(efecto)
            return True
    return False


def clear_efectos_paciente(data, paciente_id):
    """Limpia todos los efectos de un paciente"""
    p = get_paciente_by_id(data, paciente_id)
    if p:
        p["efectos"] = []


# Test standalone
if __name__ == "__main__":
    print("=== Test Career Data ===")
    
    # Cargar o crear
    data = load_career()
    print(f"Setup completo: {is_setup_complete(data)}")
    print(f"Pacientes: {count_pacientes(data)}")
    print(f"Mensajes: {count_mensajes_pendientes(data)}")
    
    # Test XP
    print("\n[Test XP]")
    result = add_xp(data, 100)
    print(f"Nivel: {get_nivel(data)}, XP: {get_xp(data)}")
    print(f"Cambio: {result}")
    
    # Test Economia
    print("\n[Test Economia]")
    print(f"Dinero: {get_dinero(data)}")
    add_dinero(data, 500)
    print(f"Dinero tras +500: {get_dinero(data)}")
    
    # Test Inventario
    print("\n[Test Inventario]")
    comprar_farmaco(data, "placebo")
    print(f"Inventario: {get_inventario(data)}")
