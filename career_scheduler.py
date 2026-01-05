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
    get_fecha_schedule, set_fecha_schedule,
    get_mensajes_recuperados, increment_mensajes_recuperados, reset_mensajes_recuperados,
    get_ultima_actividad, set_ultima_actividad,
    get_paciente_by_id,
    MIN_PACIENTES, MAX_PACIENTES
)

# Probabilidades (aumentadas para más actividad)
PROB_MENSAJE_PACIENTE = 50       # % de que un paciente mande mensaje hoy
PROB_SEGUNDO_MENSAJE = 25       # % de que mande un segundo mensaje
PROB_PACIENTE_NUEVO = 35        # % de que llegue paciente nuevo (si hay espacio)
PROB_EMERGENCIA_FINDE = 15      # % de emergencia en fin de semana
PROB_EMERGENCIA_NOCHE = 10      # % de emergencia nocturna entre semana
MIN_MENSAJES_DIA = 2            # Mínimo de mensajes a generar por día

# Sistema de recuperación ante desconexiones
MAX_MENSAJES_RECUPERAR = 3      # Máximo de mensajes a recuperar por reconexión
HORAS_OFFLINE_URGENTE = 6       # Horas offline para considerar situación urgente
DIAS_OFFLINE_CRITICO = 2        # Días offline para situación crítica

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


def _parse_timestamp_to_epoch(ts_str):
    """
    Convierte timestamp ISO a valor comparable (minutos desde 2024-01-01).
    Solo para comparaciones relativas, no necesita precisión absoluta.
    """
    if not ts_str:
        return 0
    try:
        parsed = parse_timestamp(ts_str)
        if not parsed:
            return 0
        # Simplificado: días desde 2024 * 1440 + minutos del día
        year, month, day, hour, minute = parsed[0], parsed[1], parsed[2], parsed[3], parsed[4]
        days = (year - 2024) * 365 + (month - 1) * 30 + day
        return days * 1440 + hour * 60 + minute
    except:
        return 0


def get_offline_hours(data):
    """
    Calcula cuántas horas ha estado offline el dispositivo.

    Returns:
        Horas offline (float), 0 si no hay registro previo
    """
    ultima = get_ultima_actividad(data)
    if not ultima:
        return 0

    ultima_epoch = _parse_timestamp_to_epoch(ultima)
    ahora_epoch = _parse_timestamp_to_epoch(get_timestamp())

    if ahora_epoch <= ultima_epoch:
        return 0

    diff_mins = ahora_epoch - ultima_epoch
    return diff_mins / 60.0


def get_offline_days(data):
    """
    Calcula cuántos días completos ha estado offline.

    Returns:
        Días offline (int)
    """
    return int(get_offline_hours(data) / 24)


def recover_missed_messages(data):
    """
    Recupera mensajes que debieron llegar mientras el dispositivo estaba offline.
    Convierte mensajes programados cuya hora ya pasó en mensajes "urgentes"
    que se procesarán pronto.

    Esta función NO genera los mensajes, solo los marca para procesamiento
    inmediato manteniéndolos en la lista de programados.

    Returns:
        Cantidad de mensajes marcados para recuperación
    """
    now = get_timestamp()
    now_epoch = _parse_timestamp_to_epoch(now)
    programados = get_mensajes_programados(data)

    if not programados:
        return 0

    recovered = 0
    mensajes_urgentes = []
    mensajes_futuros = []

    for prog in programados:
        ts = prog["hora_programada"]
        ts_epoch = _parse_timestamp_to_epoch(ts)

        if ts_epoch < now_epoch:
            # Este mensaje debió llegar - marcarlo como urgente
            if recovered < MAX_MENSAJES_RECUPERAR:
                # Reprogramar para "ahora" (se procesará en el próximo ciclo)
                prog["hora_programada"] = now
                prog["es_recuperado"] = True  # Marcar como recuperado
                mensajes_urgentes.append(prog)
                recovered += 1
                increment_mensajes_recuperados(data)
                print(f"[SCHEDULER] Mensaje recuperado de paciente {prog['paciente_id']}")
            # Los demás mensajes atrasados se descartan (no sobrecargar)
        else:
            mensajes_futuros.append(prog)

    # Reconstruir lista: urgentes primero, luego futuros
    data["programacion"]["proximos_mensajes"] = mensajes_urgentes + mensajes_futuros

    if recovered > 0:
        print(f"[SCHEDULER] Total mensajes recuperados: {recovered}")

    return recovered


def check_new_day(data):
    """
    Comprueba si es un nuevo día.
    IMPORTANTE: No borra los mensajes programados - eso lo hace generate_daily_schedule
    después de intentar recuperar los perdidos.

    Args:
        data: Datos de carrera

    Returns:
        True si es nuevo día
    """
    today = get_today_str()
    ultimo = get_ultimo_dia_jugado(data)

    if today != ultimo:
        # Calcular tiempo offline para logging
        horas_offline = get_offline_hours(data)
        dias_offline = get_offline_days(data)

        print(f"[SCHEDULER] Nuevo dia: {today}")
        if horas_offline > 0:
            print(f"[SCHEDULER] Tiempo offline: {horas_offline:.1f}h ({dias_offline}d)")

        # Actualizar día ANTES de procesar (evita loops)
        set_ultimo_dia_jugado(data, today)
        reset_pacientes_nuevos_hoy(data)
        reset_mensajes_recuperados(data)

        # IMPORTANTE: NO limpiar mensajes aquí
        # Los mensajes del día anterior se recuperarán en generate_daily_schedule

        return True

    return False


def generate_daily_schedule(data, force=False):
    """
    Genera programacion de mensajes para hoy.
    Debe llamarse al inicio de cada dia.
    Garantiza un mínimo de actividad diaria.

    ROBUSTO ante desconexiones:
    1. Primero intenta recuperar mensajes perdidos del día anterior
    2. Solo genera nuevo schedule si no hay uno para hoy
    3. Registra la fecha del schedule para evitar duplicados

    Args:
        data: Datos de carrera
        force: Si True, regenera aunque ya exista schedule para hoy
    """
    today = get_today_str()
    fecha_schedule = get_fecha_schedule(data)
    is_finde = is_weekend()

    # Verificar si ya existe schedule para hoy
    if fecha_schedule == today and not force:
        print(f"[SCHEDULER] Schedule de {today} ya existe, saltando generación")
        # Aún así, intentar recuperar mensajes perdidos por reconexión
        recovered = recover_missed_messages(data)
        if recovered > 0:
            print(f"[SCHEDULER] Recuperados {recovered} mensajes tras reconexión")
        return

    print(f"[SCHEDULER] Generando horario para {today}")

    # PASO 1: Intentar recuperar mensajes del día anterior antes de limpiar
    recovered = recover_missed_messages(data)
    if recovered > 0:
        print(f"[SCHEDULER] Recuperados {recovered} mensajes antes de generar nuevo schedule")

    # PASO 2: Preservar mensajes recuperados, limpiar el resto
    mensajes_recuperados = [
        m for m in get_mensajes_programados(data)
        if m.get("es_recuperado", False)
    ]

    # Limpiar programación anterior (excepto recuperados)
    clear_mensajes_programados(data)

    # Restaurar mensajes recuperados
    for m in mensajes_recuperados:
        data["programacion"]["proximos_mensajes"].append(m)

    # PASO 3: Generar nuevos mensajes para hoy
    pacientes = get_pacientes(data)

    if is_finde:
        # Fin de semana: solo emergencias ocasionales
        _schedule_weekend_emergencies(data, pacientes)
    else:
        # Dia laboral normal
        _schedule_workday_messages(data, pacientes)
        _schedule_new_patients(data)
        _schedule_night_emergencies(data, pacientes)

    # PASO 4: Verificar mínimo de mensajes programados
    programados = get_mensajes_programados(data)
    mensajes_nuevos = [m for m in programados if not m.get("es_recuperado", False)]
    if len(mensajes_nuevos) < MIN_MENSAJES_DIA and pacientes:
        _ensure_minimum_messages(data, pacientes, MIN_MENSAJES_DIA - len(mensajes_nuevos))

    # PASO 5: Registrar fecha del schedule
    set_fecha_schedule(data, today)

    total = len(get_mensajes_programados(data))
    print(f"[SCHEDULER] Total mensajes programados: {total} ({recovered} recuperados)")


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


# === FUNCIONES DE ACTIVIDAD Y RECONEXIÓN ===

def update_activity(data):
    """
    Actualiza el timestamp de última actividad.
    Llamar periódicamente (cada minuto o en cambios importantes).
    """
    set_ultima_actividad(data, get_timestamp())


def check_reconnection(data):
    """
    Verifica si hubo una reconexión tras desconexión prolongada.
    Útil para mostrar mensajes al usuario o ajustar comportamiento.

    Returns:
        Dict con info de reconexión:
        {
            "reconectado": bool,
            "horas_offline": float,
            "dias_offline": int,
            "es_urgente": bool (más de HORAS_OFFLINE_URGENTE),
            "es_critico": bool (más de DIAS_OFFLINE_CRITICO)
        }
    """
    horas = get_offline_hours(data)
    dias = get_offline_days(data)

    return {
        "reconectado": horas > 0.5,  # Más de 30 minutos = reconexión significativa
        "horas_offline": horas,
        "dias_offline": dias,
        "es_urgente": horas >= HORAS_OFFLINE_URGENTE,
        "es_critico": dias >= DIAS_OFFLINE_CRITICO
    }


def is_message_recovered(prog):
    """
    Verifica si un mensaje programado es recuperado (llegó tarde).

    Args:
        prog: Dict del mensaje programado

    Returns:
        True si es un mensaje recuperado
    """
    return prog.get("es_recuperado", False)


def get_recovery_stats(data):
    """
    Obtiene estadísticas de recuperación de mensajes.

    Returns:
        Dict con stats:
        {
            "mensajes_recuperados_hoy": int,
            "mensajes_pendientes_recuperados": int
        }
    """
    programados = get_mensajes_programados(data)
    pendientes_recuperados = sum(
        1 for p in programados if p.get("es_recuperado", False)
    )

    return {
        "mensajes_recuperados_hoy": get_mensajes_recuperados(data),
        "mensajes_pendientes_recuperados": pendientes_recuperados
    }


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
