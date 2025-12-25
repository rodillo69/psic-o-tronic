# ============================================================================
# CONFIG.PY - Configuración y Estadísticas Persistentes
# PSIC-O-TRONIC - Guardado en Flash del ESP32
# ============================================================================

import ujson
import os

# Importar sistema de errores
try:
    from error_handler import report_error
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False

# Archivos de configuración
CONFIG_FILE = "/config.json"
STATS_FILE = "/stats.json"

# Configuración por defecto
DEFAULT_CONFIG = {
    "wifi_ssid": "",
    "wifi_pass": "",
    "wifi_configured": False,
    "brightness": 100,
    "sound_enabled": True,
    "version": "1.0",
    "api_key": "",
    "api_model": "gemini-2.5-flash-lite",
    "data_version": "2.3",  # Versión de estructura de datos
}

# Estadísticas por defecto
DEFAULT_STATS = {
    "total_games": 0,           # Partidas jugadas totales
    "total_cases_solved": 0,    # Casos resueltos totales
    "best_streak": 0,           # Mejor racha sin fallar
    "best_streak_initials": "---",  # Iniciales del récord racha
    "survival_record": 0,       # Récord modo survival
    "survival_initials": "---", # Iniciales del récord survival
    "history_progress": 0,      # Progreso modo historia (capítulo)
    "history_rank": "Interno",  # Rango actual en modo historia
}


def file_exists(filename):
    """Comprueba si un archivo existe"""
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def load_config():
    """Carga la configuración desde flash"""
    if file_exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = ujson.load(f)
                # Merge con defaults por si hay campos nuevos
                merged = DEFAULT_CONFIG.copy()
                merged.update(config)
                return merged
        except ValueError as e:
            print(f"[CONFIG] JSON corrupt: {e}")
            if ERROR_HANDLER_AVAILABLE:
                report_error("storage_corrupt", "config.json", e)
        except Exception as e:
            print(f"[CONFIG] Error loading: {e}")
            if ERROR_HANDLER_AVAILABLE:
                report_error("storage_read_error", str(e), e)
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Guarda la configuración en flash"""
    try:
        with open(CONFIG_FILE, "w") as f:
            ujson.dump(config, f)
        return True
    except OSError as e:
        print(f"[CONFIG] Write error: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("storage_write_error", "config.json", e)
        return False
    except Exception as e:
        print(f"[CONFIG] Error saving: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("unknown_error", f"save_config: {e}", e)
        return False


def load_stats():
    """Carga las estadísticas desde flash"""
    if file_exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                stats = ujson.load(f)
                # Merge con defaults
                merged = DEFAULT_STATS.copy()
                merged.update(stats)
                return merged
        except ValueError as e:
            print(f"[STATS] JSON corrupt: {e}")
            if ERROR_HANDLER_AVAILABLE:
                report_error("storage_corrupt", "stats.json", e)
        except Exception as e:
            print(f"[STATS] Error loading: {e}")
            if ERROR_HANDLER_AVAILABLE:
                report_error("storage_read_error", str(e), e)
    return DEFAULT_STATS.copy()


def save_stats(stats):
    """Guarda las estadísticas en flash"""
    try:
        with open(STATS_FILE, "w") as f:
            ujson.dump(stats, f)
        return True
    except OSError as e:
        print(f"[STATS] Write error: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("storage_write_error", "stats.json", e)
        return False
    except Exception as e:
        print(f"[STATS] Error saving: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("unknown_error", f"save_stats: {e}", e)
        return False


def reset_stats():
    """Resetea todas las estadísticas"""
    save_stats(DEFAULT_STATS.copy())


def update_stat(key, value):
    """Actualiza una estadística específica"""
    stats = load_stats()
    stats[key] = value
    save_stats(stats)


def increment_stat(key, amount=1):
    """Incrementa una estadística numérica"""
    stats = load_stats()
    if key in stats and isinstance(stats[key], int):
        stats[key] += amount
        save_stats(stats)
        return stats[key]
    return None


# --- Funciones específicas de estadísticas ---

def record_game_start():
    """Registra inicio de partida"""
    return increment_stat("total_games")


def record_case_solved():
    """Registra caso resuelto"""
    return increment_stat("total_cases_solved")


def check_streak_record(streak, initials="???"):
    """
    Comprueba y actualiza récord de racha.
    
    Args:
        streak: Racha actual
        initials: Iniciales del jugador (3 chars)
        
    Returns:
        True si es nuevo récord
    """
    stats = load_stats()
    if streak > stats["best_streak"]:
        stats["best_streak"] = streak
        stats["best_streak_initials"] = initials[:3].upper()
        save_stats(stats)
        return True
    return False


def check_survival_record(score, initials="???"):
    """
    Comprueba y actualiza récord de survival.
    
    Args:
        score: Puntuación survival
        initials: Iniciales del jugador (3 chars)
        
    Returns:
        True si es nuevo récord
    """
    stats = load_stats()
    if score > stats["survival_record"]:
        stats["survival_record"] = score
        stats["survival_initials"] = initials[:3].upper()
        save_stats(stats)
        return True
    return False


def update_history_progress(chapter, rank):
    """Actualiza progreso del modo historia"""
    stats = load_stats()
    if chapter > stats["history_progress"]:
        stats["history_progress"] = chapter
        stats["history_rank"] = rank
        save_stats(stats)


def get_stats_summary():
    """Retorna resumen de estadísticas para mostrar"""
    stats = load_stats()
    return {
        "games": stats["total_games"],
        "cases": stats["total_cases_solved"],
        "streak": f"{stats['best_streak']} ({stats['best_streak_initials']})",
        "survival": f"{stats['survival_record']} ({stats['survival_initials']})",
    }


# --- WiFi Config ---

def get_wifi_config():
    """Obtiene configuración WiFi guardada"""
    config = load_config()
    if config["wifi_configured"]:
        return config["wifi_ssid"], config["wifi_pass"]
    return None, None


def save_wifi_config(ssid, password):
    """Guarda configuración WiFi"""
    config = load_config()
    config["wifi_ssid"] = ssid
    config["wifi_pass"] = password
    config["wifi_configured"] = True
    return save_config(config)


def clear_wifi_config():
    """Borra configuración WiFi guardada"""
    config = load_config()
    config["wifi_ssid"] = ""
    config["wifi_pass"] = ""
    config["wifi_configured"] = False
    return save_config(config)


def is_wifi_configured():
    """Comprueba si hay WiFi configurada"""
    config = load_config()
    return config["wifi_configured"]


# --- API Config ---

# API Key por defecto (de prueba)
# Modelo: gemini-2.5-flash-lite (15 RPM, 1000 RPD - mejor para evitar error 429)
DEFAULT_API_KEY = "AIzaSyDcCfYRcuOM_7vqP3moss-_virH1dI4xBg"
DEFAULT_MODEL = "gemini-2.5-flash-lite"


def get_api_config():
    """
    Obtiene configuración de API.

    Permite usar API key/modelo personalizado del flash,
    pero auto-actualiza valores viejos obsoletos.

    Returns:
        Tupla (api_key, model)
    """
    config = load_config()
    key = config.get("api_key", "")
    model = config.get("api_model", "")

    # Lista de API keys viejas obsoletas (con cuota agotada/expiradas)
    OLD_KEYS = [
        "AIzaSyBSXc2L5sui5ilUAQVpw1vShTUxsFs6Kj0",  # Key vieja original
    ]

    # Lista de modelos viejos obsoletos (con cuota 0 o deprecados)
    OLD_MODELS = [
        "gemini-2.0-flash",  # Cuota 0 en free tier
        "gemini-1.5-flash",  # Deprecado
    ]

    # Si no hay key guardada O es una key vieja, usar la nueva por defecto
    if not key or key in OLD_KEYS:
        key = DEFAULT_API_KEY

    # Si no hay modelo guardado O es un modelo viejo, usar el nuevo por defecto
    if not model or model in OLD_MODELS:
        model = DEFAULT_MODEL

    return key, model


def save_api_config(api_key, model=None):
    """
    Guarda configuración de API.
    
    Args:
        api_key: API Key de Gemini
        model: Modelo a usar (opcional)
    """
    config = load_config()
    config["api_key"] = api_key
    if model:
        config["api_model"] = model
    return save_config(config)


def clear_api_config():
    """Restaura API a valores por defecto"""
    config = load_config()
    config["api_key"] = ""
    config["api_model"] = DEFAULT_MODEL
    return save_config(config)


def check_and_wipe_if_needed():
    """
    Verifica si es necesario hacer wipe de datos por actualización.

    Si data_version < 2.3, borra todos los datos guardados y crea
    config fresh con data_version 2.3.

    Returns:
        bool: True si se hizo wipe, False si no
    """
    config = load_config()
    current_data_version = config.get("data_version", "0.0")

    # Convertir versiones a float para comparar
    try:
        current_ver = float(current_data_version)
    except:
        current_ver = 0.0

    # Si data_version < 2.3, hacer wipe
    if current_ver < 2.3:
        print(f"[CONFIG] Data version {current_data_version} < 2.3 - Wiping data...")

        # Borrar todos los archivos de datos
        try:
            import os

            # Borrar config y stats
            try:
                os.remove(CONFIG_FILE)
                print("[CONFIG] Deleted config.json")
            except:
                pass

            try:
                os.remove(STATS_FILE)
                print("[CONFIG] Deleted stats.json")
            except:
                pass

            # Borrar carrera
            try:
                os.remove("/career_save.json")
                print("[CONFIG] Deleted career_save.json")
            except:
                pass

            # Crear config fresh con nueva data_version
            fresh_config = DEFAULT_CONFIG.copy()
            save_config(fresh_config)
            print(f"[CONFIG] Created fresh config with data_version 2.3")

            return True

        except Exception as e:
            print(f"[CONFIG] Error during wipe: {e}")
            return False

    return False


# Test standalone
if __name__ == "__main__":
    print("=== Test Config/Stats ===")
    
    # Test config
    print("\n[Config]")
    config = load_config()
    print(f"Config actual: {config}")
    
    # Test stats
    print("\n[Stats]")
    stats = load_stats()
    print(f"Stats actuales: {stats}")
    
    # Test incremento
    print("\n[Incremento]")
    new_val = increment_stat("total_games")
    print(f"Total games ahora: {new_val}")
    
    # Test récord
    print("\n[Record]")
    is_record = check_streak_record(5, "MGC")
    print(f"Es record? {is_record}")
    
    # Resumen
    print("\n[Resumen]")
    summary = get_stats_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")
