# ============================================================================
# ERROR_HANDLER.PY - Sistema Centralizado de Gestión de Errores
# PSIC-O-TRONIC - Manejo robusto de errores con logging y recuperación
# ============================================================================

import time
import gc

# Intentar importar json (MicroPython vs Python estándar)
try:
    import ujson as json
except ImportError:
    import json

# ============================================================================
# CATEGORÍAS DE ERROR
# ============================================================================

class ErrorCategory:
    """Categorías de errores para clasificación"""
    NETWORK = "network"      # Errores de red/WiFi
    API = "api"              # Errores de API (Gemini)
    STORAGE = "storage"      # Errores de almacenamiento
    HARDWARE = "hardware"    # Errores de hardware (LCD, botones)
    MEMORY = "memory"        # Errores de memoria
    DATA = "data"            # Errores de datos/JSON
    GAME = "game"            # Errores de lógica del juego
    UNKNOWN = "unknown"      # Errores desconocidos


class ErrorSeverity:
    """Severidad de errores"""
    INFO = 0       # Informativo, no requiere acción
    WARNING = 1    # Advertencia, puede continuar
    ERROR = 2      # Error, requiere atención
    CRITICAL = 3   # Crítico, requiere reinicio


# ============================================================================
# MENSAJES DE ERROR AMIGABLES
# ============================================================================

ERROR_MESSAGES = {
    # Network errors
    "wifi_disconnected": {
        "titulo": "SIN WIFI",
        "mensaje": "Conexion perdida",
        "accion": "Reconecta WiFi",
        "categoria": ErrorCategory.NETWORK,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": True
    },
    "wifi_timeout": {
        "titulo": "TIMEOUT WIFI",
        "mensaje": "Red muy lenta",
        "accion": "Acercate al router",
        "categoria": ErrorCategory.NETWORK,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    "dns_error": {
        "titulo": "ERROR DNS",
        "mensaje": "No resuelve nombre",
        "accion": "Verifica internet",
        "categoria": ErrorCategory.NETWORK,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": True
    },
    
    # API errors
    "api_key_invalid": {
        "titulo": "API KEY MAL",
        "mensaje": "Key invalida",
        "accion": "Reconfigura API",
        "categoria": ErrorCategory.API,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": False
    },
    "api_rate_limit": {
        "titulo": "LIMITE API",
        "mensaje": "Demasiadas peticiones",
        "accion": "Espera 1 minuto",
        "categoria": ErrorCategory.API,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    "api_server_error": {
        "titulo": "ERROR SERVIDOR",
        "mensaje": "Gemini no responde",
        "accion": "Reintenta luego",
        "categoria": ErrorCategory.API,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": True
    },
    "api_bad_response": {
        "titulo": "RESPUESTA MAL",
        "mensaje": "JSON invalido",
        "accion": "Reintentando...",
        "categoria": ErrorCategory.API,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    
    # Storage errors
    "storage_full": {
        "titulo": "MEMORIA LLENA",
        "mensaje": "Sin espacio",
        "accion": "Borra datos",
        "categoria": ErrorCategory.STORAGE,
        "severidad": ErrorSeverity.CRITICAL,
        "recuperable": False
    },
    "storage_corrupt": {
        "titulo": "DATOS CORRUPTOS",
        "mensaje": "Archivo danado",
        "accion": "Reset partida",
        "categoria": ErrorCategory.STORAGE,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": False
    },
    "storage_read_error": {
        "titulo": "ERROR LECTURA",
        "mensaje": "No lee archivo",
        "accion": "Reinicia",
        "categoria": ErrorCategory.STORAGE,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": True
    },
    "storage_write_error": {
        "titulo": "ERROR ESCRITURA",
        "mensaje": "No guarda datos",
        "accion": "Verifica espacio",
        "categoria": ErrorCategory.STORAGE,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": True
    },
    
    # Memory errors
    "memory_low": {
        "titulo": "POCA MEMORIA",
        "mensaje": "RAM casi llena",
        "accion": "Reinicia pronto",
        "categoria": ErrorCategory.MEMORY,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    "memory_critical": {
        "titulo": "SIN MEMORIA",
        "mensaje": "RAM agotada",
        "accion": "Reinicia ahora",
        "categoria": ErrorCategory.MEMORY,
        "severidad": ErrorSeverity.CRITICAL,
        "recuperable": False
    },
    
    # Hardware errors
    "lcd_error": {
        "titulo": "ERROR LCD",
        "mensaje": "Pantalla falla",
        "accion": "Revisa conexion",
        "categoria": ErrorCategory.HARDWARE,
        "severidad": ErrorSeverity.CRITICAL,
        "recuperable": False
    },
    "button_stuck": {
        "titulo": "BOTON ATASCADO",
        "mensaje": "Boton pulsado",
        "accion": "Suelta el boton",
        "categoria": ErrorCategory.HARDWARE,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    
    # Data errors
    "json_parse_error": {
        "titulo": "ERROR JSON",
        "mensaje": "Datos mal formato",
        "accion": "Reintentando...",
        "categoria": ErrorCategory.DATA,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    "missing_data": {
        "titulo": "FALTAN DATOS",
        "mensaje": "Campos vacios",
        "accion": "Regenerando...",
        "categoria": ErrorCategory.DATA,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    
    # Game errors
    "patient_error": {
        "titulo": "ERROR PACIENTE",
        "mensaje": "No genera paciente",
        "accion": "Reintentando...",
        "categoria": ErrorCategory.GAME,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    "session_error": {
        "titulo": "ERROR SESION",
        "mensaje": "Sesion fallida",
        "accion": "Volviendo...",
        "categoria": ErrorCategory.GAME,
        "severidad": ErrorSeverity.WARNING,
        "recuperable": True
    },
    
    # Generic
    "unknown_error": {
        "titulo": "ERROR",
        "mensaje": "Algo salio mal",
        "accion": "Reintenta",
        "categoria": ErrorCategory.UNKNOWN,
        "severidad": ErrorSeverity.ERROR,
        "recuperable": True
    }
}


# ============================================================================
# CLASE PRINCIPAL DE GESTIÓN DE ERRORES
# ============================================================================

class ErrorHandler:
    """Gestor centralizado de errores"""
    
    # Archivo de log
    LOG_FILE = "/error_log.json"
    MAX_LOG_ENTRIES = 50
    
    # Singleton
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # Estado actual
        self.current_error = None
        self.error_count = 0
        self.retry_count = 0
        self.max_retries = 3
        
        # Historial de errores (en memoria)
        self.error_history = []
        self.max_history = 20
        
        # Estadísticas por categoría
        self.stats = {
            ErrorCategory.NETWORK: 0,
            ErrorCategory.API: 0,
            ErrorCategory.STORAGE: 0,
            ErrorCategory.HARDWARE: 0,
            ErrorCategory.MEMORY: 0,
            ErrorCategory.DATA: 0,
            ErrorCategory.GAME: 0,
            ErrorCategory.UNKNOWN: 0
        }
        
        # Callbacks
        self._on_error_callback = None
        self._on_recover_callback = None
        
        # Cargar log existente
        self._load_log()
    
    def set_callbacks(self, on_error=None, on_recover=None):
        """
        Configura callbacks para eventos de error.
        
        Args:
            on_error: Función llamada cuando ocurre un error (error_info)
            on_recover: Función llamada cuando se recupera de un error
        """
        self._on_error_callback = on_error
        self._on_recover_callback = on_recover
    
    def report(self, error_type, details="", exception=None):
        """
        Reporta un error al sistema.
        
        Args:
            error_type: Tipo de error (clave de ERROR_MESSAGES)
            details: Detalles adicionales
            exception: Excepción original si existe
            
        Returns:
            Dict con información del error
        """
        # Obtener información del error
        error_info = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["unknown_error"]).copy()
        error_info["type"] = error_type
        error_info["details"] = details
        error_info["timestamp"] = time.time()
        error_info["retry_count"] = self.retry_count
        
        if exception:
            error_info["exception"] = f"{type(exception).__name__}: {str(exception)}"
        
        # Actualizar estadísticas
        categoria = error_info.get("categoria", ErrorCategory.UNKNOWN)
        self.stats[categoria] = self.stats.get(categoria, 0) + 1
        self.error_count += 1
        
        # Guardar en historial
        self._add_to_history(error_info)
        
        # Log
        self._log_error(error_info)
        
        # Callback
        if self._on_error_callback:
            try:
                self._on_error_callback(error_info)
            except:
                pass  # No propagar errores del callback
        
        # Imprimir para debug
        print(f"[ERROR] {error_info['titulo']}: {error_info['mensaje']} ({details})")
        
        # Actualizar estado
        self.current_error = error_info
        
        return error_info
    
    def report_exception(self, exception, context=""):
        """
        Reporta una excepción automáticamente clasificada.
        
        Args:
            exception: La excepción capturada
            context: Contexto donde ocurrió
            
        Returns:
            Dict con información del error
        """
        # Clasificar excepción
        exc_type = type(exception).__name__
        exc_msg = str(exception)
        
        # Mapear tipo de excepción a tipo de error
        if exc_type == "MemoryError":
            error_type = "memory_critical"
        elif exc_type == "OSError":
            if "ECONNRESET" in exc_msg or "ETIMEDOUT" in exc_msg:
                error_type = "wifi_timeout"
            elif "ENOENT" in exc_msg:
                error_type = "storage_read_error"
            elif "ENOSPC" in exc_msg:
                error_type = "storage_full"
            else:
                error_type = "wifi_disconnected"
        elif exc_type == "ValueError":
            error_type = "json_parse_error"
        elif exc_type == "KeyError":
            error_type = "missing_data"
        else:
            error_type = "unknown_error"
        
        return self.report(error_type, f"{context}: {exc_msg}", exception)
    
    def clear(self):
        """Limpia el error actual (recuperación exitosa)"""
        if self.current_error and self._on_recover_callback:
            try:
                self._on_recover_callback()
            except:
                pass
        
        self.current_error = None
        self.retry_count = 0
    
    def can_retry(self):
        """
        Comprueba si se puede reintentar la operación.
        
        Returns:
            True si quedan reintentos
        """
        if not self.current_error:
            return True
        
        if not self.current_error.get("recuperable", False):
            return False
        
        return self.retry_count < self.max_retries
    
    def increment_retry(self):
        """Incrementa contador de reintentos"""
        self.retry_count += 1
        return self.retry_count
    
    def get_retry_delay(self):
        """
        Obtiene delay recomendado para reintento (backoff exponencial).
        
        Returns:
            Segundos a esperar
        """
        # Backoff: 1s, 2s, 4s, 8s...
        return min(2 ** self.retry_count, 30)
    
    def get_display_info(self):
        """
        Obtiene información formateada para mostrar en LCD.
        
        Returns:
            Dict con lineas para LCD 20x4
        """
        if not self.current_error:
            return None
        
        e = self.current_error
        
        return {
            "line0": e.get("titulo", "ERROR")[:20].center(20),
            "line1": e.get("mensaje", "")[:20].center(20),
            "line2": e.get("accion", "")[:20].center(20),
            "line3": "[OK] Reintentar" if e.get("recuperable") else "[OK] Volver"
        }
    
    def get_stats(self):
        """
        Obtiene estadísticas de errores.
        
        Returns:
            Dict con estadísticas
        """
        return {
            "total": self.error_count,
            "por_categoria": self.stats.copy(),
            "historial_reciente": len(self.error_history)
        }
    
    def get_history(self, limit=10):
        """
        Obtiene historial de errores recientes.
        
        Args:
            limit: Número máximo de entradas
            
        Returns:
            Lista de errores recientes
        """
        return self.error_history[-limit:]
    
    def check_memory(self):
        """
        Verifica estado de memoria y reporta si es bajo.
        
        Returns:
            Tuple (free_bytes, is_critical)
        """
        gc.collect()
        
        try:
            free = gc.mem_free()
            total = gc.mem_alloc() + free
            pct_free = (free * 100) // total
            
            if pct_free < 10:
                self.report("memory_critical", f"{free} bytes libres")
                return (free, True)
            elif pct_free < 20:
                self.report("memory_low", f"{free} bytes libres")
                return (free, False)
            
            return (free, False)
        except:
            return (0, False)
    
    def _add_to_history(self, error_info):
        """Añade error al historial en memoria"""
        # Copiar solo campos esenciales para ahorrar memoria
        entry = {
            "type": error_info.get("type"),
            "titulo": error_info.get("titulo"),
            "timestamp": error_info.get("timestamp"),
            "categoria": error_info.get("categoria")
        }
        
        self.error_history.append(entry)
        
        # Limitar tamaño
        while len(self.error_history) > self.max_history:
            self.error_history.pop(0)
    
    def _log_error(self, error_info):
        """Guarda error en archivo de log"""
        try:
            # Leer log existente
            log_data = self._load_log_file()
            
            # Añadir nuevo error
            entry = {
                "t": error_info.get("type"),
                "ts": int(error_info.get("timestamp", 0)),
                "d": error_info.get("details", "")[:50]  # Limitar detalles
            }
            
            log_data["errors"].append(entry)
            
            # Limitar tamaño del log
            while len(log_data["errors"]) > self.MAX_LOG_ENTRIES:
                log_data["errors"].pop(0)
            
            # Actualizar contadores
            log_data["total"] = log_data.get("total", 0) + 1
            
            # Guardar
            self._save_log_file(log_data)
            
        except Exception as e:
            print(f"[ERROR_HANDLER] No pudo guardar log: {e}")
    
    def _load_log_file(self):
        """Carga archivo de log"""
        try:
            with open(self.LOG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"errors": [], "total": 0}
    
    def _save_log_file(self, data):
        """Guarda archivo de log"""
        try:
            with open(self.LOG_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def _load_log(self):
        """Carga estadísticas del log al iniciar"""
        try:
            log_data = self._load_log_file()
            # Restaurar contador total
            self.error_count = log_data.get("total", 0)
        except:
            pass
    
    def clear_log(self):
        """Borra el log de errores"""
        try:
            with open(self.LOG_FILE, 'w') as f:
                json.dump({"errors": [], "total": 0}, f)
            self.error_count = 0
            self.error_history = []
            self.stats = {k: 0 for k in self.stats}
            print("[ERROR_HANDLER] Log borrado")
        except Exception as e:
            print(f"[ERROR_HANDLER] Error borrando log: {e}")


# ============================================================================
# DECORADOR PARA MANEJO AUTOMÁTICO DE ERRORES
# ============================================================================

def handle_errors(error_type="unknown_error", context="", retries=3):
    """
    Decorador para manejar errores automáticamente.
    
    Args:
        error_type: Tipo de error por defecto
        context: Contexto de la operación
        retries: Número de reintentos
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            handler = ErrorHandler()
            
            for attempt in range(retries):
                try:
                    result = func(*args, **kwargs)
                    handler.clear()  # Éxito, limpiar error
                    return result
                except Exception as e:
                    handler.report_exception(e, context or func.__name__)
                    
                    if attempt < retries - 1 and handler.can_retry():
                        handler.increment_retry()
                        delay = handler.get_retry_delay()
                        print(f"[RETRY] Intento {attempt + 2}/{retries} en {delay}s...")
                        time.sleep(delay)
                    else:
                        # Último intento fallido
                        return None
            
            return None
        return wrapper
    return decorator


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_error_handler():
    """Obtiene la instancia singleton del manejador de errores"""
    return ErrorHandler()


def report_error(error_type, details="", exception=None):
    """Atajo para reportar un error"""
    return ErrorHandler().report(error_type, details, exception)


def check_memory():
    """Atajo para verificar memoria"""
    return ErrorHandler().check_memory()


# ============================================================================
# HTTP ERROR MAPPER
# ============================================================================

def map_http_error(status_code):
    """
    Mapea código HTTP a tipo de error.
    
    Args:
        status_code: Código HTTP
        
    Returns:
        Tipo de error
    """
    if status_code == 400:
        return "api_key_invalid"
    elif status_code == 401:
        return "api_key_invalid"
    elif status_code == 403:
        return "api_key_invalid"
    elif status_code == 429:
        return "api_rate_limit"
    elif status_code >= 500:
        return "api_server_error"
    else:
        return "unknown_error"


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    # Test básico
    handler = ErrorHandler()
    
    print("=== Test Error Handler ===")
    
    # Reportar errores
    handler.report("wifi_disconnected", "Test de desconexión")
    handler.report("api_rate_limit", "Demasiadas peticiones")
    
    # Simular excepción
    try:
        raise ValueError("Test exception")
    except Exception as e:
        handler.report_exception(e, "test_function")
    
    # Mostrar estadísticas
    stats = handler.get_stats()
    print(f"\nEstadísticas: {stats}")
    
    # Mostrar historial
    history = handler.get_history()
    print(f"\nHistorial: {history}")
    
    # Info para LCD
    info = handler.get_display_info()
    if info:
        print(f"\nLCD:")
        for k, v in info.items():
            print(f"  {k}: '{v}'")
    
    print("\n=== Test OK ===")
