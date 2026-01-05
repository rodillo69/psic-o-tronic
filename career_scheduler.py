# ============================================================================
# CAREER_SCHEDULER.PY - Horarios y programacion de mensajes
# PSIC-O-TRONIC - Modo Mi Consulta
# ============================================================================

import random
import time

from ntp_time import (
    get_local_time, get_timestamp, get_today_str,
    get_hour, get_minute, get_weekday,
    is_weekend, is_work_hours, is_emergency_hours,
    parse_timestamp
)
from career_data import (
    get_pacientes, get_mensajes_pendientes, has_mensaje_pendiente_de,
    count_pacientes, can_add_paciente, needs_more_pacientes,
    get_pacientes_nuevos_hoy, increment_pacientes_nuevos_hoy,
    reset_pacientes_nuevos_hoy, get_ultimo_dia_jugado, set_ultimo_dia_jugado,
    get_programacion, add_mensaje_programado, get_mensajes_programados,
    remove_mensaje_programado, clear_mensajes_programados,
    MIN_PACIENTES, MAX_PACIENTES
)

# Probabilidades (aumentadas para más actividad)
PROB_MENSAJE_PACIENTE = 50       # % de que un paciente mande mensaje hoy
PROB_SEGUNDO_MENSAJE = 25       # % de que mande un segundo mensaje
PROB_PACIENTE_NUEVO = 35        # % de que llegue paciente nuevo (si hay espacio)
PROB_EMERGENCIA_FINDE = 15      # % de emergencia en fin de semana
PROB_EMERGENCIA_NOCHE = 10      # % de emergencia nocturna entre semana
MIN_MENSAJES_DIA = 2            # Mínimo de mensajes a generar por día

# Limites
MAX_PACIENTES_NUEVOS_DIA = 2
MAX_MENSAJES_PACIENTE_DIA = 2

# Horarios (minutos desde medianoche)
HORARIO_MANANA_INICIO = 9 * 60      # 9:00
HORARIO_MANANA_FIN = 14 * 60        # 14:00
HORARIO_TARDE_INICIO = 17 * 60      # 17:00
HORARIO_TARDE_FIN = 20 * 60         # 20:00
HORARIO_EMERGENCIA_FIN = 22 * 60 + 30  # 22:30


def _get_current_minutes():
    """Obtiene minutos desde medianoche"""
    t = get_local_time()
    return t[3] * 60 + t[4]


def _minutos_a_hora(minutos):
    """Convierte minutos a string HH:MM"""
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"


def _random_time_in_range(min_minutes, max_minutes):
    """Genera hora aleatoria en rango"""
    return random.randint(min_minutes, max_minutes - 1)


def _random_work_time():
    """
    Genera hora aleatoria en horario laboral.
    
    Returns:
        Minutos desde medianoche
    """
    # 60% manana, 40% tarde (manana es mas larga)
    if random.randint(1, 100) <= 60:
        return _random_time_in_range(HORARIO_MANANA_INICIO, HORARIO_MANANA_FIN)
    else:
        return _random_time_in_range(HORARIO_TARDE_INICIO, HORARIO_TARDE_FIN)


def _is_time_passed(target_minutes):
    """True si la hora objetivo ya paso hoy"""
    return _get_current_minutes() >= target_minutes


def check_new_day(data):
    """
    Comprueba si es un nuevo dia y resetea contadores.
    
    Args:
        data: Datos de carrera
    
    Returns:
        True si es nuevo dia
    """
    today = get_today_str()
    ultimo = get_ultimo_dia_jugado(data)
    
    if today != ultimo:
        print(f"[SCHEDULER] Nuevo dia: {today}")
        set_ultimo_dia_jugado(data, today)
        reset_pacientes_nuevos_hoy(data)
        clear_mensajes_programados(data)
        return True
    
    return False


def generate_daily_schedule(data):
    """
    Genera programacion de mensajes para hoy.
    Debe llamarse al inicio de cada dia.
    Garantiza un mínimo de actividad diaria.

    Args:
        data: Datos de carrera
    """
    today = get_today_str()
    is_finde = is_weekend()

    print(f"[SCHEDULER] Generando horario para {today}")

    # Limpiar programacion anterior
    clear_mensajes_programados(data)

    pacientes = get_pacientes(data)

    if is_finde:
        # Fin de semana: solo emergencias ocasionales
        _schedule_weekend_emergencies(data, pacientes)
    else:
        # Dia laboral normal
        _schedule_workday_messages(data, pacientes)
        _schedule_new_patients(data)
        _schedule_night_emergencies(data, pacientes)

    # Verificar mínimo de mensajes programados
    programados = get_mensajes_programados(data)
    if len(programados) < MIN_MENSAJES_DIA and pacientes:
        _ensure_minimum_messages(data, pacientes, MIN_MENSAJES_DIA - len(programados))

    print(f"[SCHEDULER] Total mensajes programados: {len(get_mensajes_programados(data))}")


def _schedule_workday_messages(data, pacientes):
    """Programa mensajes de pacientes para dia laboral"""
    for paciente in pacientes:
        # Saltar si ya tiene mensaje pendiente
        if has_mensaje_pendiente_de(data, paciente["id"]):
            continue
        
        # Primer mensaje del dia
        if random.randint(1, 100) <= PROB_MENSAJE_PACIENTE:
            hora = _random_work_time()
            ts = _make_timestamp_today(hora)
            add_mensaje_programado(data, paciente["id"], ts)
            print(f"[SCHEDULER] Programado msg de {paciente['nombre'][:10]} a las {_minutos_a_hora(hora)}")
            
            # Posible segundo mensaje
            if random.randint(1, 100) <= PROB_SEGUNDO_MENSAJE:
                # Al menos 2 horas despues
                hora2 = hora + random.randint(120, 180)
                if hora2 < HORARIO_TARDE_FIN:
                    ts2 = _make_timestamp_today(hora2)
                    add_mensaje_programado(data, paciente["id"], ts2)
                    print(f"[SCHEDULER] Programado 2do msg a las {_minutos_a_hora(hora2)}")


def _schedule_weekend_emergencies(data, pacientes):
    """Programa emergencias de fin de semana"""
    if not pacientes:
        return
    
    if random.randint(1, 100) <= PROB_EMERGENCIA_FINDE:
        # Elegir paciente aleatorio sin mensaje pendiente
        disponibles = [p for p in pacientes if not has_mensaje_pendiente_de(data, p["id"])]
        if disponibles:
            paciente = random.choice(disponibles)
            # Emergencia en cualquier momento hasta las 22:30
            hora = _random_time_in_range(10 * 60, HORARIO_EMERGENCIA_FIN)
            ts = _make_timestamp_today(hora)
            add_mensaje_programado(data, paciente["id"], ts)
            print(f"[SCHEDULER] EMERGENCIA finde: {paciente['nombre'][:10]} a las {_minutos_a_hora(hora)}")


def _schedule_night_emergencies(data, pacientes):
    """Programa emergencias nocturnas entre semana"""
    if not pacientes:
        return
    
    if random.randint(1, 100) <= PROB_EMERGENCIA_NOCHE:
        disponibles = [p for p in pacientes if not has_mensaje_pendiente_de(data, p["id"])]
        if disponibles:
            paciente = random.choice(disponibles)
            # Entre las 20:00 y 22:30
            hora = _random_time_in_range(HORARIO_TARDE_FIN, HORARIO_EMERGENCIA_FIN)
            ts = _make_timestamp_today(hora)
            add_mensaje_programado(data, paciente["id"], ts)
            print(f"[SCHEDULER] EMERGENCIA noche: {paciente['nombre'][:10]} a las {_minutos_a_hora(hora)}")


def _schedule_new_patients(data):
    """Programa llegada de nuevos pacientes"""
    if not can_add_paciente(data):
        return
    
    # Forzar si hay menos del minimo
    force = needs_more_pacientes(data)
    
    nuevos_hoy = get_pacientes_nuevos_hoy(data)
    if nuevos_hoy >= MAX_PACIENTES_NUEVOS_DIA:
        return
    
    # Probabilidad o forzado
    if force or random.randint(1, 100) <= PROB_PACIENTE_NUEVO:
        # Programar "llegada" - se procesara como paciente_id = -1
        hora = _random_work_time()
        ts = _make_timestamp_today(hora)
        add_mensaje_programado(data, -1, ts)  # -1 = nuevo paciente
        print(f"[SCHEDULER] Nuevo paciente programado a las {_minutos_a_hora(hora)}")
        
        # Posible segundo nuevo paciente
        if can_add_paciente(data) and (force or random.randint(1, 100) <= PROB_PACIENTE_NUEVO // 2):
            if nuevos_hoy + 1 < MAX_PACIENTES_NUEVOS_DIA:
                hora2 = _random_work_time()
                if abs(hora2 - hora) > 60:  # Al menos 1 hora de diferencia
                    ts2 = _make_timestamp_today(hora2)
                    add_mensaje_programado(data, -1, ts2)
                    print(f"[SCHEDULER] 2do nuevo paciente a las {_minutos_a_hora(hora2)}")


def _make_timestamp_today(minutos):
    """Crea timestamp para hoy a la hora indicada"""
    t = get_local_time()
    hora = minutos // 60
    mins = minutos % 60
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}T{hora:02d}:{mins:02d}:00"


def _ensure_minimum_messages(data, pacientes, cantidad_faltante):
    """
    Asegura un mínimo de mensajes programados.
    Se llama cuando el algoritmo normal no generó suficientes.
    """
    if not pacientes or cantidad_faltante <= 0:
        return

    # Filtrar pacientes sin mensaje pendiente
    disponibles = [p for p in pacientes if not has_mensaje_pendiente_de(data, p["id"])]

    if not disponibles:
        return

    for i in range(min(cantidad_faltante, len(disponibles))):
        paciente = disponibles[i % len(disponibles)]
        hora = _random_work_time()
        ts = _make_timestamp_today(hora)
        add_mensaje_programado(data, paciente["id"], ts)
        print(f"[SCHEDULER] Mensaje extra (mínimo): {paciente['nombre'][:10]} a las {_minutos_a_hora(hora)}")


def check_scheduled_messages(data, remove_processed=False):
    """
    Comprueba si hay mensajes programados que deben activarse.
    NO elimina los mensajes de la programación por defecto.

    Args:
        data: Datos de carrera
        remove_processed: Si True, elimina los mensajes de la lista

    Returns:
        Lista de dicts {"paciente_id": X, "hora_programada": "..."} a activar
    """
    now = get_timestamp()
    programados = get_mensajes_programados(data)

    to_activate = []

    for prog in programados:
        ts = prog["hora_programada"]

        # Comparar timestamps (string comparison works for ISO format)
        if ts <= now:
            to_activate.append(prog.copy())

    # Solo eliminar si se solicita explícitamente
    if remove_processed:
        for prog in to_activate:
            remove_mensaje_programado(data, prog["paciente_id"], prog["hora_programada"])

    return to_activate


def mark_message_processed(data, paciente_id, timestamp):
    """
    Marca un mensaje específico como procesado (lo elimina de programación).
    Llamar después de generar el mensaje exitosamente.
    """
    remove_mensaje_programado(data, paciente_id, timestamp)


def get_pending_scheduled_count(data):
    """Obtiene cantidad de mensajes programados pendientes de procesar"""
    now = get_timestamp()
    programados = get_mensajes_programados(data)
    return sum(1 for p in programados if p["hora_programada"] <= now)


def get_next_scheduled_time(data):
    """
    Obtiene la hora del proximo mensaje programado.
    
    Returns:
        String "HH:MM" o None si no hay
    """
    programados = get_mensajes_programados(data)
    if not programados:
        return None
    
    # Ordenar por hora
    programados.sort(key=lambda x: x["hora_programada"])
    
    ts = programados[0]["hora_programada"]
    parsed = parse_timestamp(ts)
    if parsed:
        return f"{parsed[3]:02d}:{parsed[4]:02d}"
    return None


def should_notify(data):
    """
    Determina si se debe notificar (LED/sonido).
    No notificar en horas de silencio.
    
    Returns:
        True si hay mensajes y no es hora de silencio
    """
    from ntp_time import is_quiet_hours
    
    if is_quiet_hours():
        return False
    
    from career_data import count_mensajes_pendientes
    return count_mensajes_pendientes(data) > 0


def get_random_delay():
    """
    Genera delay aleatorio para variabilidad.
    
    Returns:
        Segundos de delay (0-300)
    """
    return random.randint(0, 300)


# Test standalone
if __name__ == "__main__":
    print("=== Test Career Scheduler ===")
    print(f"Es fin de semana: {is_weekend()}")
    print(f"Horario laboral: {is_work_hours()}")
    print(f"Hora actual: {_minutos_a_hora(_get_current_minutes())}")
    
    # Test hora aleatoria
    for i in range(5):
        h = _random_work_time()
        print(f"Hora aleatoria {i+1}: {_minutos_a_hora(h)}")
