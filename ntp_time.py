# ============================================================================
# NTP_TIME.PY - Sincronizacion horaria para Espana
# PSIC-O-TRONIC - Modo Mi Consulta
# ============================================================================

import ntptime
import time
import machine

# Offset horario Espana (CET = +1, CEST = +2)
# Simplificado: +1 en invierno (nov-mar), +2 en verano (mar-oct)
TIMEZONE_WINTER = 1  # CET
TIMEZONE_SUMMER = 2  # CEST

# Dias de la semana en espanol (abreviados, 3 chars)
DIAS_SEMANA = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

# Meses en espanol (abreviados, 3 chars)
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def is_dst(month, day, weekday):
    """
    Determina si estamos en horario de verano (CEST).
    Espana: ultimo domingo de marzo a ultimo domingo de octubre.

    Args:
        month: Mes (1-12)
        day: Dia del mes (1-31)
        weekday: Dia de la semana (0=lunes, 6=domingo)

    Returns:
        True si es horario de verano
    """
    # Abril a septiembre: siempre verano
    if 4 <= month <= 9:
        return True

    # Noviembre a febrero: siempre invierno
    if month <= 2 or month >= 11:
        return False

    # Marzo: verano desde el ultimo domingo (a las 2:00 -> 3:00)
    if month == 3:
        # Calcular que dia de la semana fue el dia 31
        # weekday actual + (31 - day) dias = weekday del 31
        weekday_31 = (weekday + (31 - day)) % 7
        # Ultimo domingo: retroceder desde 31 hasta encontrar domingo (6)
        last_sunday = 31 - ((weekday_31 - 6) % 7)
        return day >= last_sunday

    # Octubre: invierno desde el ultimo domingo (a las 3:00 -> 2:00)
    if month == 10:
        weekday_31 = (weekday + (31 - day)) % 7
        last_sunday = 31 - ((weekday_31 - 6) % 7)
        return day < last_sunday

    return False


def get_timezone_offset():
    """Obtiene offset actual de Espana en segundos"""
    t = time.localtime()
    if is_dst(t[1], t[2], t[6]):
        return TIMEZONE_SUMMER * 3600
    return TIMEZONE_WINTER * 3600


def sync_time():
    """
    Sincroniza con servidor NTP.
    
    Returns:
        True si exito, False si fallo
    """
    try:
        ntptime.settime()
        print("[NTP] Sincronizado OK")
        return True
    except Exception as e:
        print(f"[NTP] Error: {e}")
        return False


def get_local_time():
    """
    Obtiene hora local de Espana.
    
    Returns:
        Tupla (year, month, day, hour, minute, second, weekday, yearday)
    """
    utc = time.time()
    offset = get_timezone_offset()
    local = time.localtime(utc + offset)
    return local


def get_timestamp():
    """
    Obtiene timestamp ISO para guardar en JSON.
    
    Returns:
        String "YYYY-MM-DDTHH:MM:SS"
    """
    t = get_local_time()
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}T{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"


def get_date_str():
    """
    Obtiene fecha formateada para LCD (max 10 chars).
    
    Returns:
        String "Mie 27-Nov"
    """
    t = get_local_time()
    dia = DIAS_SEMANA[t[6]]
    mes = MESES[t[1] - 1]
    return f"{dia} {t[2]:02d}-{mes}"


def get_time_str():
    """
    Obtiene hora formateada para LCD (5 chars).
    
    Returns:
        String "14:32"
    """
    t = get_local_time()
    return f"{t[3]:02d}:{t[4]:02d}"


def get_hour():
    """Obtiene hora actual (0-23)"""
    return get_local_time()[3]


def get_minute():
    """Obtiene minuto actual (0-59)"""
    return get_local_time()[4]


def get_weekday():
    """Obtiene dia de la semana (0=lunes, 6=domingo)"""
    return get_local_time()[6]


def get_today_str():
    """
    Obtiene fecha de hoy para comparaciones.
    
    Returns:
        String "YYYY-MM-DD"
    """
    t = get_local_time()
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"


def is_weekend():
    """True si es sabado o domingo"""
    return get_weekday() >= 5


def is_work_hours():
    """
    True si estamos en horario laboral.
    L-V: 9:00-14:00 y 17:00-20:00
    """
    if is_weekend():
        return False
    
    hour = get_hour()
    minute = get_minute()
    current = hour * 60 + minute
    
    # Manana: 9:00 (540) a 14:00 (840)
    # Tarde: 17:00 (1020) a 20:00 (1200)
    morning = 540 <= current < 840
    afternoon = 1020 <= current < 1200
    
    return morning or afternoon


def is_emergency_hours():
    """
    True si pueden llegar emergencias.
    Cualquier dia hasta las 22:30
    """
    hour = get_hour()
    minute = get_minute()
    current = hour * 60 + minute
    
    # Hasta las 22:30 (1350 minutos)
    return current <= 1350


def is_quiet_hours():
    """
    True si estamos en horas de silencio (no notificaciones).
    22:30 a 9:00
    """
    hour = get_hour()
    minute = get_minute()
    current = hour * 60 + minute
    
    # 22:30 (1350) a 23:59 (1439) o 00:00 (0) a 09:00 (540)
    return current >= 1350 or current < 540


def minutes_until(target_hour, target_minute):
    """
    Calcula minutos hasta una hora objetivo.
    
    Args:
        target_hour: Hora objetivo (0-23)
        target_minute: Minuto objetivo (0-59)
    
    Returns:
        Minutos hasta esa hora (puede ser negativo si ya paso)
    """
    t = get_local_time()
    current = t[3] * 60 + t[4]
    target = target_hour * 60 + target_minute
    return target - current


def parse_timestamp(ts_str):
    """
    Parsea timestamp ISO a tupla.
    
    Args:
        ts_str: "YYYY-MM-DDTHH:MM:SS"
    
    Returns:
        Tupla (year, month, day, hour, minute, second)
    """
    try:
        date_part, time_part = ts_str.split("T")
        year, month, day = [int(x) for x in date_part.split("-")]
        hour, minute, second = [int(x) for x in time_part.split(":")]
        return (year, month, day, hour, minute, second)
    except:
        return None


def timestamp_to_display(ts_str):
    """
    Convierte timestamp a formato corto para LCD.
    
    Args:
        ts_str: "YYYY-MM-DDTHH:MM:SS"
    
    Returns:
        String "14:32" o "27-Nov" si es otro dia
    """
    parsed = parse_timestamp(ts_str)
    if not parsed:
        return "??:??"
    
    today = get_today_str()
    msg_date = f"{parsed[0]:04d}-{parsed[1]:02d}-{parsed[2]:02d}"
    
    if msg_date == today:
        return f"{parsed[3]:02d}:{parsed[4]:02d}"
    else:
        mes = MESES[parsed[1] - 1]
        return f"{parsed[2]:02d}-{mes}"


# Test standalone
if __name__ == "__main__":
    print("=== Test NTP Time ===")
    print(f"Fecha: {get_date_str()}")
    print(f"Hora: {get_time_str()}")
    print(f"Timestamp: {get_timestamp()}")
    print(f"Fin de semana: {is_weekend()}")
    print(f"Horario laboral: {is_work_hours()}")
    print(f"Horas de silencio: {is_quiet_hours()}")
