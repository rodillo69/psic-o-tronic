"""
OTA Update System for PSIC-O-TRONIC
Actualiza el firmware desde GitHub
"""

import ujson as json
import os
import gc
import machine

# Configuración del repositorio
GITHUB_USER = "rodillo69"
GITHUB_REPO = "psic-o-tronic"
GITHUB_BRANCH = "main"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/{}/{}/{}/".format(
    GITHUB_USER, GITHUB_REPO, GITHUB_BRANCH
)

# Archivo de versión local
VERSION_FILE = "/version.json"
REMOTE_VERSION_FILE = "version.json"

# Versión actual (fallback si no existe version.json)
CURRENT_VERSION = "1.0.0"

def get_local_version():
    """Obtiene la versión instalada localmente"""
    try:
        with open(VERSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("version", CURRENT_VERSION)
    except:
        return CURRENT_VERSION

def save_local_version(version, files_updated=None):
    """Guarda la versión local"""
    try:
        data = {
            "version": version,
            "files_updated": files_updated or []
        }
        with open(VERSION_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print("[OTA] Error guardando versión:", e)
        return False

def fetch_url(url, timeout=15):
    """Descarga contenido de una URL"""
    try:
        import urequests
        gc.collect()
        response = urequests.get(url, timeout=timeout)
        if response.status_code == 200:
            content = response.text
            response.close()
            return content
        else:
            response.close()
            return None
    except Exception as e:
        print("[OTA] Error fetch:", e)
        return None

def fetch_binary(url, timeout=30):
    """Descarga contenido binario de una URL"""
    try:
        import urequests
        gc.collect()
        response = urequests.get(url, timeout=timeout)
        if response.status_code == 200:
            content = response.content
            response.close()
            return content
        else:
            response.close()
            return None
    except Exception as e:
        print("[OTA] Error fetch binary:", e)
        return None

def check_for_updates(callback=None):
    """
    Verifica si hay actualizaciones disponibles.
    
    Args:
        callback: Función opcional para reportar progreso
        
    Returns:
        dict con info de actualización o None si no hay/error
        {
            "available": True/False,
            "current_version": "1.0.0",
            "new_version": "1.1.0",
            "files": ["file1.py", "file2.py"],
            "changelog": "Cambios...",
            "mandatory": False
        }
    """
    if callback:
        callback("Conectando...")
    
    # Obtener versión remota
    url = GITHUB_RAW_URL + REMOTE_VERSION_FILE
    print("[OTA] Checking:", url)
    
    content = fetch_url(url)
    if not content:
        print("[OTA] No se pudo obtener version.json remoto")
        return None
    
    try:
        remote_data = json.loads(content)
    except:
        print("[OTA] Error parseando version.json")
        return None
    
    current = get_local_version()
    remote = remote_data.get("version", "0.0.0")
    
    # Comparar versiones
    current_parts = [int(x) for x in current.split(".")]
    remote_parts = [int(x) for x in remote.split(".")]
    
    # Padding para comparar
    while len(current_parts) < 3:
        current_parts.append(0)
    while len(remote_parts) < 3:
        remote_parts.append(0)
    
    has_update = remote_parts > current_parts
    
    return {
        "available": has_update,
        "current_version": current,
        "new_version": remote,
        "files": remote_data.get("files", []),
        "changelog": remote_data.get("changelog", ""),
        "mandatory": remote_data.get("mandatory", False),
        "size_kb": remote_data.get("size_kb", 0)
    }

def download_file(filename, callback=None):
    """
    Descarga un archivo desde GitHub.
    
    Args:
        filename: Nombre del archivo a descargar
        callback: Función para reportar progreso
        
    Returns:
        True si éxito, False si error
    """
    url = GITHUB_RAW_URL + filename
    print("[OTA] Downloading:", filename)
    
    if callback:
        callback("Bajando " + filename[:12])
    
    gc.collect()
    
    content = fetch_url(url, timeout=30)
    if content is None:
        print("[OTA] Error descargando:", filename)
        return False
    
    # Guardar archivo
    try:
        # Backup del archivo existente
        backup_name = filename + ".bak"
        try:
            os.rename(filename, backup_name)
        except:
            pass  # No existe el original
        
        # Escribir nuevo archivo
        with open(filename, "w") as f:
            f.write(content)
        
        # Eliminar backup si todo OK
        try:
            os.remove(backup_name)
        except:
            pass
        
        print("[OTA] OK:", filename)
        return True
        
    except Exception as e:
        print("[OTA] Error guardando:", filename, e)
        # Restaurar backup
        try:
            os.remove(filename)
            os.rename(backup_name, filename)
        except:
            pass
        return False

def perform_update(update_info, callback=None):
    """
    Realiza la actualización completa.
    
    Args:
        update_info: Dict con info de actualización (de check_for_updates)
        callback: Función para reportar progreso
        
    Returns:
        (success: bool, message: str)
    """
    if not update_info or not update_info.get("available"):
        return False, "No hay actualizacion"
    
    files = update_info.get("files", [])
    if not files:
        return False, "Sin archivos"
    
    total = len(files)
    success_count = 0
    failed_files = []
    
    for i, filename in enumerate(files):
        if callback:
            callback("({}/{}) {}".format(i + 1, total, filename[:10]))
        
        gc.collect()
        
        if download_file(filename, callback):
            success_count += 1
        else:
            failed_files.append(filename)
    
    if success_count == total:
        # Todo OK - guardar nueva versión
        save_local_version(update_info["new_version"], files)
        return True, "OK v" + update_info["new_version"]
    elif success_count > 0:
        # Parcial
        save_local_version(update_info["new_version"], 
                          [f for f in files if f not in failed_files])
        return True, "Parcial {}/{}".format(success_count, total)
    else:
        return False, "Error descarga"

def reboot():
    """Reinicia el dispositivo"""
    print("[OTA] Reiniciando...")
    machine.reset()

# === Clase para integración con UI ===

class OTAManager:
    """Manager para integración con la UI del juego"""
    
    def __init__(self):
        self.update_info = None
        self.last_check = 0
        self.check_interval = 3600  # 1 hora entre checks automáticos
        self.is_checking = False
        self.is_updating = False
        self.status_msg = ""
    
    def should_auto_check(self):
        """Determina si es momento de verificar actualizaciones"""
        import time
        now = time.time()
        return (now - self.last_check) > self.check_interval
    
    def check_async(self, callback=None):
        """Inicia verificación de actualizaciones"""
        if self.is_checking or self.is_updating:
            return
        
        self.is_checking = True
        self.status_msg = "Verificando..."
        
        import time
        self.last_check = time.time()
        
        try:
            self.update_info = check_for_updates(callback)
            if self.update_info and self.update_info.get("available"):
                self.status_msg = "v" + self.update_info["new_version"] + " disponible"
            else:
                self.status_msg = "Al dia"
        except Exception as e:
            print("[OTA] Error check:", e)
            self.status_msg = "Error conexion"
            self.update_info = None
        
        self.is_checking = False
    
    def has_update(self):
        """Retorna True si hay actualización disponible"""
        return self.update_info and self.update_info.get("available", False)
    
    def get_update_info(self):
        """Retorna info de la actualización"""
        return self.update_info
    
    def perform_update(self, callback=None):
        """Ejecuta la actualización"""
        if self.is_updating or not self.has_update():
            return False, "No disponible"
        
        self.is_updating = True
        self.status_msg = "Actualizando..."
        
        try:
            success, msg = perform_update(self.update_info, callback)
            self.status_msg = msg
            if success:
                self.update_info = None
            return success, msg
        except Exception as e:
            self.status_msg = "Error: " + str(e)[:15]
            return False, str(e)
        finally:
            self.is_updating = False
    
    def get_current_version(self):
        """Retorna versión actual"""
        return get_local_version()

# Instancia global
ota_manager = OTAManager()
