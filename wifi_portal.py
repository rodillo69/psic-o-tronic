# ============================================================================
# WIFI_PORTAL.PY - Portal Cautivo para Configuración
# PSIC-O-TRONIC - Configura WiFi, API Key y consulta progreso desde el móvil
# ============================================================================

import network
import socket
import time
import gc

# Nombre del Access Point
AP_SSID = "PSIC-O-TRONIC"
AP_PASSWORD = ""  # Sin contraseña

# Modelo por defecto
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_API_KEY = "AIzaSyBSXc2L5sui5ilUAQVpw1vShTUxsFs6Kj0"

# ============================================================================
# CSS STYLES
# ============================================================================

CSS_STYLES = """
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { 
        font-family: 'Courier New', monospace;
        background: linear-gradient(135deg, #001428 0%, #002040 50%, #001020 100%);
        color: #ffffff;
        min-height: 100vh;
        padding: 10px;
    }
    .container { max-width: 500px; margin: 0 auto; }
    
    /* Header */
    .header {
        text-align: center;
        border: 2px solid #4a90d9;
        padding: 15px;
        margin-bottom: 15px;
        background: linear-gradient(180deg, #003366 0%, #001428 100%);
        box-shadow: 0 0 20px rgba(74, 144, 217, 0.3);
    }
    .header h1 { 
        font-size: 22px;
        text-shadow: 0 0 10px #4a90d9;
        letter-spacing: 2px;
    }
    .header .version { 
        font-size: 11px; 
        color: #8ab4e8; 
        margin-top: 5px;
    }
    
    /* Navigation */
    .nav {
        display: flex;
        flex-wrap: wrap;
        margin-bottom: 15px;
        gap: 2px;
    }
    .nav a {
        flex: 1;
        min-width: 80px;
        padding: 12px 8px;
        text-align: center;
        background: #002040;
        color: #8ab4e8;
        text-decoration: none;
        border: 1px solid #4a90d9;
        font-size: 11px;
        transition: all 0.2s;
    }
    .nav a:hover {
        background: #003366;
        color: #ffffff;
    }
    .nav a.active {
        background: #004080;
        color: #ffffff;
        border-color: #66b3ff;
        box-shadow: 0 0 10px rgba(74, 144, 217, 0.5);
    }
    
    /* Sections */
    .section {
        background: rgba(0, 32, 64, 0.8);
        border: 1px solid #4a90d9;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 5px;
    }
    h2 {
        color: #66b3ff;
        margin-bottom: 12px;
        font-size: 15px;
        border-bottom: 1px solid #4a90d9;
        padding-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Cards */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin-bottom: 15px;
    }
    .card {
        background: #001428;
        border: 1px solid #335577;
        padding: 12px;
        text-align: center;
        border-radius: 5px;
    }
    .card-value {
        font-size: 24px;
        color: #66ff66;
        font-weight: bold;
    }
    .card-label {
        font-size: 11px;
        color: #8ab4e8;
        margin-top: 5px;
    }
    .card.highlight { border-color: #66ff66; }
    .card.warning { border-color: #ffaa00; }
    .card.warning .card-value { color: #ffaa00; }
    
    /* Stats List */
    .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px dotted #335577;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: #8ab4e8; }
    .stat-value { color: #ffffff; font-weight: bold; }
    
    /* Progress Bar */
    .progress-container {
        background: #001020;
        border: 1px solid #335577;
        height: 20px;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #004080 0%, #0066cc 100%);
        transition: width 0.3s;
    }
    .progress-text {
        text-align: center;
        font-size: 12px;
        margin-top: 5px;
        color: #8ab4e8;
    }
    
    /* Badges */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 10px 0;
    }
    .badge {
        background: #003366;
        border: 1px solid #4a90d9;
        padding: 4px 8px;
        font-size: 10px;
        border-radius: 3px;
        color: #66b3ff;
    }
    .badge.active {
        background: #004080;
        border-color: #66ff66;
        color: #66ff66;
    }
    .badge.locked {
        background: #1a1a1a;
        border-color: #444;
        color: #666;
    }
    
    /* Forms */
    .network-list {
        max-height: 150px;
        overflow-y: auto;
        margin-bottom: 10px;
        border: 1px solid #335577;
    }
    .network {
        padding: 10px;
        border-bottom: 1px solid #002040;
        cursor: pointer;
        transition: background 0.2s;
    }
    .network:hover { background: #003366; }
    .network:last-child { border-bottom: none; }
    .signal { float: right; color: #66ff66; font-family: monospace; }
    
    label {
        display: block;
        margin-bottom: 5px;
        color: #8ab4e8;
        font-size: 13px;
    }
    input[type="text"], input[type="password"], select {
        width: 100%;
        padding: 12px;
        margin-bottom: 12px;
        background: #001428;
        border: 1px solid #4a90d9;
        color: #ffffff;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        border-radius: 3px;
    }
    input:focus, select:focus {
        outline: none;
        box-shadow: 0 0 10px rgba(74, 144, 217, 0.5);
        border-color: #66b3ff;
    }
    
    button, .btn {
        display: block;
        width: 100%;
        padding: 12px;
        background: linear-gradient(180deg, #004080 0%, #003366 100%);
        border: 2px solid #4a90d9;
        color: #ffffff;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-decoration: none;
        text-align: center;
        border-radius: 3px;
        margin-top: 5px;
        transition: all 0.2s;
    }
    button:hover, .btn:hover {
        background: linear-gradient(180deg, #0055aa 0%, #004080 100%);
        box-shadow: 0 0 15px rgba(74, 144, 217, 0.5);
    }
    .btn-secondary {
        background: #002040;
        border-color: #8ab4e8;
        font-size: 12px;
    }
    .btn-danger {
        background: linear-gradient(180deg, #661111 0%, #440000 100%);
        border-color: #ff6666;
        color: #ff6666;
    }
    .btn-danger:hover {
        background: linear-gradient(180deg, #881111 0%, #660000 100%);
        color: #ffffff;
    }
    .btn-danger:disabled {
        background: #1a1a1a;
        border-color: #444;
        color: #666;
        cursor: not-allowed;
    }
    
    /* Status */
    .status {
        text-align: center;
        padding: 12px;
        margin-top: 15px;
        border-radius: 5px;
    }
    .error { 
        background: rgba(255, 0, 0, 0.1);
        color: #ff6666; 
        border: 1px solid #ff6666; 
    }
    .success { 
        background: rgba(0, 255, 0, 0.1);
        color: #66ff66; 
        border: 1px solid #66ff66; 
    }
    
    /* Info boxes */
    .info-box {
        background: #001020;
        border-left: 3px solid #4a90d9;
        padding: 10px;
        margin: 10px 0;
        font-size: 12px;
        line-height: 1.5;
    }
    .warning-box {
        background: #201000;
        border-left: 3px solid #ffaa00;
        padding: 10px;
        margin: 10px 0;
        font-size: 12px;
        color: #ffd080;
    }
    
    /* Lists */
    .item-list {
        max-height: 200px;
        overflow-y: auto;
    }
    .item-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px;
        border-bottom: 1px solid #002040;
    }
    .item-row:last-child { border-bottom: none; }
    .item-name { color: #ffffff; }
    .item-info { color: #8ab4e8; font-size: 11px; }
    
    /* Help sections */
    .help-section {
        margin-bottom: 15px;
    }
    .help-section h3 {
        color: #66b3ff;
        font-size: 13px;
        margin-bottom: 8px;
    }
    .help-section p {
        font-size: 12px;
        line-height: 1.6;
        color: #cccccc;
        margin-bottom: 8px;
    }
    .help-section ul {
        margin-left: 15px;
        font-size: 12px;
        color: #cccccc;
    }
    .help-section li {
        margin: 5px 0;
    }
    code {
        background: #001020;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 11px;
        color: #66ff66;
    }
    
    /* Collapsible */
    .collapsible {
        background: #002040;
        border: 1px solid #4a90d9;
        padding: 10px;
        cursor: pointer;
        margin-bottom: 2px;
        border-radius: 3px;
    }
    .collapsible:hover { background: #003366; }
    .collapsible::after {
        content: '+';
        float: right;
        color: #4a90d9;
    }
    .collapsible.open::after { content: '-'; }
    .collapse-content {
        display: none;
        padding: 10px;
        background: #001428;
        border: 1px solid #335577;
        border-top: none;
        margin-bottom: 10px;
    }
    .collapse-content.show { display: block; }
    
    p { margin: 8px 0; line-height: 1.5; font-size: 13px; }
    a { color: #4a90d9; }
    .small { font-size: 11px; color: #8ab4e8; }
    .center { text-align: center; }
    
    /* Loading/Spinner */
    .loading-container {
        text-align: center;
        padding: 20px;
    }
    .spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 3px solid #001428;
        border-top: 3px solid #4a90d9;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .loading-text {
        margin-top: 10px;
        color: #8ab4e8;
        font-size: 12px;
    }
    .loading-progress {
        width: 100%;
        height: 6px;
        background: #001428;
        border-radius: 3px;
        margin-top: 10px;
        overflow: hidden;
    }
    .loading-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4a90d9, #66b3ff, #4a90d9);
        background-size: 200% 100%;
        animation: progress 1.5s linear infinite;
        border-radius: 3px;
    }
    @keyframes progress {
        0% { background-position: 100% 0; }
        100% { background-position: -100% 0; }
    }
    .scan-time {
        font-size: 11px;
        color: #666;
        margin-top: 5px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #001428; }
    ::-webkit-scrollbar-thumb { background: #4a90d9; border-radius: 3px; }
</style>
<script>
function toggleCollapse(el) {
    el.classList.toggle('open');
    var content = el.nextElementSibling;
    content.classList.toggle('show');
}
</script>
"""

# ============================================================================
# HTML GENERATORS
# ============================================================================

def get_html_header(active_tab="inicio"):
    """Genera header HTML con navegación"""
    tabs = [
        ("inicio", "/", "Inicio"),
        ("carrera", "/carrera", "Mi Consulta"),
        ("config", "/config", "Config"),
        ("ayuda", "/ayuda", "Ayuda"),
    ]
    
    nav_html = ""
    for tab_id, url, name in tabs:
        active = "active" if tab_id == active_tab else ""
        nav_html += f'<a href="{url}" class="{active}">{name}</a>'
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PSIC-O-TRONIC</title>
    {CSS_STYLES}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PSIC-O-TRONIC</h1>
            <div class="version">Sistema de Diagnostico Psiquiatrico v2.0</div>
        </div>
        <div class="nav">{nav_html}</div>
"""

HTML_FOOTER = """
    </div>
</body>
</html>
"""


def get_career_data():
    """Obtiene datos del modo carrera"""
    try:
        from career_data import load_career
        return load_career()
    except:
        return None


def get_game_stats():
    """Obtiene estadísticas de juego"""
    try:
        from config import load_stats
        return load_stats()
    except:
        return None


def generate_inicio_page():
    """Genera página de inicio/dashboard"""
    career = get_career_data()
    stats = get_game_stats()
    
    # Estadísticas generales
    if career:
        nivel = career.get("jugador", {}).get("nivel", 1)
        xp = career.get("jugador", {}).get("xp", 0)
        dinero = career.get("economia", {}).get("dinero", 0)
        curados = career.get("jugador", {}).get("stats", {}).get("pacientes_curados", 0)
        nombre = career.get("jugador", {}).get("nombre", "")
        titulo = career.get("jugador", {}).get("titulo", "")
        rango = career.get("jugador", {}).get("rango", "Becario")
    else:
        nivel = 1
        xp = 0
        dinero = 0
        curados = 0
        nombre = ""
        titulo = ""
        rango = "Sin iniciar"
    
    if stats:
        partidas = stats.get("total_games", 0)
        survival_record = stats.get("survival_record", 0)
    else:
        partidas = 0
        survival_record = 0
    
    # WiFi status
    try:
        from config import get_wifi_config
        ssid, _ = get_wifi_config()
        wifi_status = f"Configurada: {ssid}" if ssid else "No configurada"
    except:
        wifi_status = "No configurada"
    
    html = get_html_header("inicio") + f'''
        <div class="section">
            <h2>Dashboard</h2>
            <div class="card-grid">
                <div class="card highlight">
                    <div class="card-value">{nivel}</div>
                    <div class="card-label">Nivel</div>
                </div>
                <div class="card">
                    <div class="card-value">{dinero}E</div>
                    <div class="card-label">Dinero</div>
                </div>
                <div class="card">
                    <div class="card-value">{curados}</div>
                    <div class="card-label">Curados</div>
                </div>
                <div class="card">
                    <div class="card-value">{partidas}</div>
                    <div class="card-label">Partidas</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Perfil</h2>
            <div class="stat-row">
                <span class="stat-label">Doctor/a</span>
                <span class="stat-value">{titulo} {nombre if nombre else 'Sin crear'}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Rango</span>
                <span class="stat-value">{rango}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">XP Total</span>
                <span class="stat-value">{xp}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Record Survival</span>
                <span class="stat-value">{survival_record} casos</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Estado del Sistema</h2>
            <div class="stat-row">
                <span class="stat-label">WiFi</span>
                <span class="stat-value">{wifi_status}</span>
            </div>
            <div class="info-box">
                Usa las pestanas de arriba para explorar tu progreso, 
                configurar WiFi o ver las instrucciones del juego.
            </div>
        </div>
    ''' + HTML_FOOTER
    
    return html


def generate_carrera_page():
    """Genera página de Mi Consulta con info detallada"""
    career = get_career_data()
    
    # Verificar si hay datos válidos de carrera
    if not career:
        html = get_html_header("carrera") + '''
            <div class="section">
                <h2>Mi Consulta</h2>
                <div class="warning-box">
                    <strong>Sin datos de carrera</strong><br><br>
                    No hay datos de carrera guardados. 
                    Inicia el modo Mi Consulta desde el dispositivo para crear tu perfil.
                </div>
                <div class="info-box">
                    <strong>Como empezar:</strong><br>
                    1. Desde el menu principal, selecciona "Mi Consulta"<br>
                    2. Crea tu perfil de doctor<br>
                    3. Empieza a atender pacientes!
                </div>
            </div>
        ''' + HTML_FOOTER
        return html
    
    # Verificar si hay jugador creado (nombre)
    jugador = career.get("jugador", {})
    nombre = jugador.get("nombre", "")
    
    if not nombre:
        html = get_html_header("carrera") + '''
            <div class="section">
                <h2>Mi Consulta</h2>
                <div class="warning-box">
                    <strong>Consulta no iniciada</strong><br><br>
                    Debes crear tu perfil de doctor antes de ver tus estadisticas.
                </div>
                <div class="info-box">
                    <strong>Como crear tu consulta:</strong><br>
                    1. Desde el dispositivo, entra en "Mi Consulta"<br>
                    2. Sigue el tutorial inicial<br>
                    3. Escribe tu nombre de doctor<br>
                    4. Ya puedes empezar a jugar!
                </div>
            </div>
        ''' + HTML_FOOTER
        return html
    
    # Datos del jugador
    stats = jugador.get("stats", {})
    economia = career.get("economia", {})
    
    nivel = jugador.get("nivel", 1)
    xp = jugador.get("xp", 0)
    rango = jugador.get("rango", "Becario")
    
    # XP para siguiente nivel
    xp_base = 100
    xp_next = xp_base * (nivel ** 1.5)
    xp_actual_nivel = xp - (xp_base * ((nivel - 1) ** 1.5)) if nivel > 1 else xp
    pct = min(100, int((xp_actual_nivel / (xp_next - (xp_base * ((nivel - 1) ** 1.5) if nivel > 1 else 0))) * 100)) if xp_next > 0 else 0
    
    # Estadísticas
    curados = stats.get("pacientes_curados", 0)
    abandonados = stats.get("pacientes_abandonados", 0)
    correctas = stats.get("sesiones_correctas", 0)
    incorrectas = stats.get("sesiones_incorrectas", 0)
    dinero_total = economia.get("dinero_total_ganado", 0)
    dinero_gastado = economia.get("dinero_gastado", 0)
    
    # Rachas
    racha_actual = stats.get("racha_aciertos_actual", 0)
    mejor_racha = stats.get("mejor_racha_aciertos", 0)
    
    # Logros
    logros = career.get("logros", {})
    logros_desbloqueados = logros.get("desbloqueados", [])
    num_logros = len(logros_desbloqueados)
    
    # Mejoras
    mejoras = career.get("mejoras", {})
    mejoras_compradas = [m for m, v in mejoras.items() if v]
    num_mejoras = len(mejoras_compradas)
    
    # Inventario
    inventario = career.get("inventario", [])
    num_items = sum(item.get("cantidad", 0) for item in inventario)
    
    # Bata actual
    bata = career.get("bata_actual", "clasica")
    
    # Prestigio
    prestigio = career.get("prestigio", {})
    nivel_prestigio = prestigio.get("nivel", 0)
    
    # Generar badges de logros
    logros_badges = ""
    for logro_id in logros_desbloqueados[:10]:  # Mostrar max 10
        logros_badges += f'<span class="badge active">{logro_id[:12]}</span>'
    if num_logros > 10:
        logros_badges += f'<span class="badge">+{num_logros - 10} mas</span>'
    
    # Generar badges de mejoras
    mejoras_badges = ""
    for mejora in mejoras_compradas[:8]:
        mejoras_badges += f'<span class="badge active">{mejora[:10]}</span>'
    if num_mejoras > 8:
        mejoras_badges += f'<span class="badge">+{num_mejoras - 8} mas</span>'
    
    html = get_html_header("carrera") + f'''
        <div class="section">
            <h2>Progreso</h2>
            <div class="card-grid">
                <div class="card highlight">
                    <div class="card-value">Nv.{nivel}</div>
                    <div class="card-label">{rango}</div>
                </div>
                <div class="card">
                    <div class="card-value">{economia.get("dinero", 0)}E</div>
                    <div class="card-label">Dinero</div>
                </div>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {pct}%"></div>
            </div>
            <div class="progress-text">XP: {xp} / Siguiente nivel: {int(xp_next)}</div>
            {"<div class='center'><span class='badge warning'>Prestigio " + str(nivel_prestigio) + "</span></div>" if nivel_prestigio > 0 else ""}
        </div>
        
        <div class="section">
            <h2>Estadisticas</h2>
            <div class="stat-row">
                <span class="stat-label">Pacientes curados</span>
                <span class="stat-value" style="color:#66ff66">{curados}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Pacientes perdidos</span>
                <span class="stat-value" style="color:#ff6666">{abandonados}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Sesiones correctas</span>
                <span class="stat-value">{correctas}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Sesiones incorrectas</span>
                <span class="stat-value">{incorrectas}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Racha actual</span>
                <span class="stat-value">{racha_actual}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Mejor racha</span>
                <span class="stat-value">{mejor_racha}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Economia</h2>
            <div class="stat-row">
                <span class="stat-label">Dinero ganado total</span>
                <span class="stat-value">{dinero_total}E</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Dinero gastado</span>
                <span class="stat-value">{dinero_gastado}E</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Items en inventario</span>
                <span class="stat-value">{num_items}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>Logros ({num_logros})</h2>
            <div class="badge-container">
                {logros_badges if logros_badges else '<span class="badge locked">Sin logros aun</span>'}
            </div>
        </div>
        
        <div class="section">
            <h2>Mejoras ({num_mejoras})</h2>
            <div class="badge-container">
                {mejoras_badges if mejoras_badges else '<span class="badge locked">Sin mejoras aun</span>'}
            </div>
        </div>
        
        <div class="section">
            <h2>Personalizacion</h2>
            <div class="stat-row">
                <span class="stat-label">Bata equipada</span>
                <span class="stat-value">{bata.title()}</span>
            </div>
        </div>
    ''' + HTML_FOOTER
    
    return html


def get_signal_bars(rssi):
    """Convierte RSSI a barras de señal"""
    if rssi >= -50:
        return "####"
    elif rssi >= -60:
        return "###-"
    elif rssi >= -70:
        return "##--"
    elif rssi >= -80:
        return "#---"
    else:
        return "----"


def scan_networks():
    """Escanea redes WiFi disponibles"""
    try:
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        
        # El escaneo puede tardar 2-5 segundos
        start = time.time()
        networks = sta.scan()
        scan_time = time.time() - start
        
        unique = []
        seen = set()
        for net in networks:
            ssid = net[0].decode('utf-8', 'ignore')
            if ssid and ssid not in seen:
                seen.add(ssid)
                unique.append({
                    'ssid': ssid,
                    'rssi': net[3],
                    'secure': net[4] > 0
                })
        
        # Ordenar por señal (mejor primero)
        unique.sort(key=lambda x: x['rssi'], reverse=True)
        
        return unique[:10], round(scan_time, 1)
    except Exception as e:
        print(f"[WIFI] Scan error: {e}")
        return [], 0


def generate_config_page(networks=None, scan_time=0, current_ssid="", current_key="", current_model="", message=None, is_error=False):
    """Genera página de configuración (WiFi + API)"""
    if networks is None:
        networks, scan_time = scan_networks()
    
    status_html = ""
    if message:
        status_class = "error" if is_error else "success"
        status_html = f'<div class="status {status_class}">{message}</div>'
    
    # Lista de redes con tiempo de escaneo
    net_html = ""
    if networks:
        for net in networks:
            ssid_escaped = net['ssid'].replace('"', '&quot;').replace("'", "&#39;")
            lock = "[S]" if net['secure'] else "[A]"
            bars = get_signal_bars(net['rssi'])
            net_html += f'''<div class="network" onclick="document.getElementById('ssid').value='{ssid_escaped}'">
                {lock} {net['ssid']} <span class="signal">{bars}</span>
            </div>'''
        # Mostrar info del escaneo
        scan_info = f'<p class="scan-time">Se encontraron {len(networks)} redes en {scan_time}s</p>'
    else:
        net_html = '''<div class="loading-container">
            <div class="spinner"></div>
            <div class="loading-text">No se encontraron redes</div>
            <p class="small">Pulsa "Actualizar" para buscar de nuevo</p>
        </div>'''
        scan_info = ""
    
    # Modelo actual
    model_options = ""
    models = [
        ("gemini-2.0-flash", "Gemini 2.0 Flash (Rapido)"),
        ("gemini-1.5-flash", "Gemini 1.5 Flash"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro (Mejor)"),
    ]
    for model_id, model_name in models:
        selected = "selected" if model_id == current_model else ""
        model_options += f'<option value="{model_id}" {selected}>{model_name}</option>'
    
    html = get_html_header("config") + f'''
        <div class="section">
            <h2>Conexion WiFi</h2>
            <p class="small">Selecciona una red o escribe el nombre manualmente.</p>
            <div class="network-list">
                {net_html}
            </div>
            {scan_info if networks else ""}
            <form method="POST" action="/connect">
                <label>Nombre de la red (SSID)</label>
                <input type="text" id="ssid" name="ssid" value="{current_ssid}" placeholder="Nombre de la red">
                
                <label>Contrasena</label>
                <input type="password" name="password" placeholder="Contrasena WiFi">
                
                <button type="submit">Conectar WiFi</button>
            </form>
            <a href="/config" class="btn btn-secondary">Actualizar lista</a>
        </div>
        
        <div class="section">
            <h2>API de Gemini</h2>
            <div class="info-box">
                La API Key es necesaria para generar los casos clinicos.
                <strong>Es GRATIS</strong> (hasta 1500 peticiones/dia).
            </div>

            <div class="warning-box" style="margin-bottom:15px;">
                <strong>Como obtener tu API Key (5 pasos):</strong><br>
                1. Abre <a href="https://aistudio.google.com/apikey" target="_blank" style="color:#66ff66;">Google AI Studio</a> en tu movil<br>
                2. Inicia sesion con tu cuenta de Google<br>
                3. Pulsa "Create API Key" (crear clave de API)<br>
                4. Selecciona un proyecto o crea uno nuevo<br>
                5. Copia la clave (empieza con "AIzaSy...") y pegala aqui abajo
            </div>

            <form method="POST" action="/api">
                <label>API Key</label>
                <input type="text" name="api_key" value="{current_key}" placeholder="AIzaSy...">

                <label>Modelo</label>
                <select name="model">
                    {model_options}
                </select>

                <button type="submit">Guardar API</button>
            </form>
        </div>
        
        <div class="section">
            <h2>Gestion de Datos</h2>
            <div class="warning-box">
                <strong>Atencion:</strong> Los datos borrados NO se pueden recuperar.
            </div>
            
            <div class="collapsible" onclick="toggleCollapse(this)">Borrar Mi Consulta</div>
            <div class="collapse-content">
                <p>Borra todo el progreso del modo carrera.</p>
                <form method="POST" action="/delete" onsubmit="return confirm('Seguro? Esta accion NO se puede deshacer.');">
                    <input type="hidden" name="target" value="career">
                    <button type="submit" class="btn-danger">Borrar Carrera</button>
                </form>
            </div>
            
            <div class="collapsible" onclick="toggleCollapse(this)">Borrar Estadisticas</div>
            <div class="collapse-content">
                <p>Borra records de Clasico y Survival.</p>
                <form method="POST" action="/delete" onsubmit="return confirm('Seguro? Esta accion NO se puede deshacer.');">
                    <input type="hidden" name="target" value="stats">
                    <button type="submit" class="btn-danger">Borrar Stats</button>
                </form>
            </div>
            
            <div class="collapsible" onclick="toggleCollapse(this)">Reset de Fabrica</div>
            <div class="collapse-content">
                <p>Borra TODO y deja el dispositivo como nuevo.</p>
                <form method="POST" action="/delete" onsubmit="return confirm('ATENCION: Borraras TODO. Continuar?');">
                    <input type="hidden" name="target" value="all">
                    <button type="submit" class="btn-danger">Reset Total</button>
                </form>
            </div>
        </div>
        
        {status_html}
    ''' + HTML_FOOTER
    
    return html


def generate_ayuda_page():
    """Genera página de ayuda/instrucciones"""
    html = get_html_header("ayuda") + '''
        <div class="section">
            <h2>Controles</h2>
            <div class="stat-row">
                <span class="stat-label">[^] Arriba</span>
                <span class="stat-value">Navegar, subir</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">[v] Abajo</span>
                <span class="stat-value">Navegar, bajar</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">[OK] Seleccionar</span>
                <span class="stat-value">Confirmar, continuar</span>
            </div>
            <div class="info-box">
                Los LEDs de los botones indican que acciones estan disponibles.
            </div>
        </div>
        
        <div class="section">
            <h2>Modos de Juego</h2>
            
            <div class="help-section">
                <h3>Clasico</h3>
                <p>Completa un numero fijo de casos (3, 5, 7 o 10). 
                Tienes vidas limitadas. Pierde una vida por cada fallo.</p>
            </div>
            
            <div class="help-section">
                <h3>Survival</h3>
                <p>Aguanta el maximo de casos posible. Un solo fallo 
                y se acaba. Tu record se guarda con tus iniciales.</p>
            </div>
            
            <div class="help-section">
                <h3>Mi Consulta (Carrera)</h3>
                <p>El modo principal. Atiende pacientes, gana dinero, 
                sube de nivel y desbloquea mejoras y logros.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Como Jugar</h2>
            <p>Los pacientes te escriben con sus problemas. 
            Debes elegir la respuesta mas <strong>PSICOTICA</strong> 
            pero que suene "profesional".</p>
            
            <div class="info-box">
                <strong>Acierto:</strong> El paciente progresa (+1)<br>
                <strong>Fallo:</strong> El paciente retrocede (-1)<br>
                <strong>3 fallos seguidos:</strong> El paciente huye
            </div>
            
            <p>Para curar a un paciente, completa todas sus sesiones 
            con progreso positivo (barra verde).</p>
        </div>
        
        <div class="section">
            <h2>El Camello (Tienda)</h2>
            <p>Compra farmacos con efectos especiales:</p>
            <ul>
                <li><strong>Aspirina (10E):</strong> Revela respuesta correcta</li>
                <li><strong>Prozac (25E):</strong> Protege de 1 fallo</li>
                <li><strong>Valium (30E):</strong> Reduce 1 sesion</li>
                <li><strong>Orfidal (50E):</strong> Paciente olvida ultimo fallo</li>
                <li><strong>Rivotril (60E):</strong> Cura instantanea</li>
                <li><strong>Y mas...</strong></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Mejoras de Consulta</h2>
            <p>Compra mejoras permanentes para tu consulta:</p>
            <ul>
                <li><strong>Sofa Comodo:</strong> Pacientes toleran mas fallos</li>
                <li><strong>Diploma Falso:</strong> Mas dinero por sesion</li>
                <li><strong>Ruleta:</strong> Desbloquea minijuego de apuestas</li>
                <li><strong>Mesa Crafting:</strong> Combina farmacos</li>
                <li><strong>Y muchas mas...</strong></li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Sistemas Avanzados</h2>
            <ul>
                <li><strong>Logros:</strong> Desbloquea recompensas por hazanas</li>
                <li><strong>Misiones:</strong> Objetivos diarios y semanales</li>
                <li><strong>Rachas:</strong> Bonus por aciertos consecutivos</li>
                <li><strong>Prestigio:</strong> Reinicia a nivel 20 con bonus permanente</li>
                <li><strong>Batas:</strong> Personaliza tu aspecto con bonificadores</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Creditos</h2>
            <div class="center">
                <p><strong>PSIC-O-TRONIC v2.0</strong></p>
                <p class="small">Juego de humor negro con IA generativa</p>
                <p class="small">Casos generados con Gemini AI (Google)</p>
                <p class="small">Hardware: ESP32-S3 + LCD 20x4</p>
                <br>
                <p>Creado por <strong>Miguel</strong></p>
                <p class="small">github.com/migue/psic-o-tronic</p>
            </div>
        </div>
    ''' + HTML_FOOTER
    
    return html


def generate_success_page(ssid, ip):
    """Genera página de éxito"""
    return get_html_header("config") + f'''
        <div class="section">
            <div class="status success">
                <h2 style="margin:0">Conectado!</h2>
                <p>Red: <strong>{ssid}</strong></p>
                <p>IP: <strong>{ip}</strong></p>
            </div>
            <div class="info-box">
                El dispositivo se reiniciara automaticamente para aplicar los cambios.
            </div>
        </div>
    ''' + HTML_FOOTER


def generate_error_page(message):
    """Genera página de error"""
    return get_html_header("config") + f'''
        <div class="section">
            <div class="status error">
                <h2 style="margin:0">Error</h2>
                <p>{message}</p>
            </div>
            <a href="/config" class="btn">Reintentar</a>
        </div>
    ''' + HTML_FOOTER


# ============================================================================
# WIFI FUNCTIONS
# ============================================================================

def try_connect_wifi(ssid, password, timeout=15):
    """Intenta conectar a una red WiFi"""
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    
    if sta.isconnected():
        sta.disconnect()
        time.sleep(1)
    
    print(f"[WIFI] Connecting to: {ssid}")
    sta.connect(ssid, password)
    
    start = time.time()
    while not sta.isconnected():
        if time.time() - start > timeout:
            sta.active(False)
            return False, "Timeout - No se pudo conectar"
        time.sleep(0.5)
    
    ip = sta.ifconfig()[0]
    print(f"[WIFI] Connected! IP: {ip}")
    return True, ip


def parse_post_data(request):
    """Parsea datos POST de un request HTTP"""
    try:
        body_start = request.find('\r\n\r\n')
        if body_start == -1:
            return {}
        
        body = request[body_start + 4:]
        params = {}
        
        for pair in body.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                value = value.replace('+', ' ')
                value = value.replace('%40', '@')
                value = value.replace('%2F', '/')
                value = value.replace('%3A', ':')
                value = value.replace('%2B', '+')
                value = value.replace('%3D', '=')
                value = value.replace('%26', '&')
                value = value.replace('%3F', '?')
                value = value.replace('%23', '#')
                params[key] = value
        
        return params
    except Exception as e:
        print(f"[WIFI] Parse error: {e}")
        return {}


# ============================================================================
# PORTAL SERVER
# ============================================================================

class WiFiPortal:
    """Servidor web para portal cautivo"""
    
    def __init__(self, lcd_callback=None):
        self.ap = None
        self.server = None
        self.running = False
        self.lcd_callback = lcd_callback
    
    def update_lcd(self, lines):
        """Actualiza el LCD si hay callback"""
        if self.lcd_callback:
            self.lcd_callback(lines)
    
    def start_ap(self):
        """Inicia el Access Point"""
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=0)
        
        time.sleep(2)
        
        ip = self.ap.ifconfig()[0]
        print(f"[WIFI] AP started: {AP_SSID}")
        print(f"[WIFI] AP IP: {ip}")
        
        return ip
    
    def stop_ap(self):
        """Detiene el Access Point"""
        if self.ap:
            self.ap.active(False)
            self.ap = None
    
    def start_server(self, port=80):
        """Inicia el servidor HTTP"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('0.0.0.0', port))
        self.server.listen(5)
        self.server.setblocking(False)
        self.running = True
        print(f"[WIFI] Server listening on port {port}")
    
    def handle_request(self, client, request):
        """Procesa una petición HTTP"""
        first_line = request.split('\r\n')[0]
        parts = first_line.split(' ')
        
        if len(parts) < 2:
            return False
        
        method = parts[0]
        path = parts[1].split('?')[0]
        
        print(f"[WIFI] {method} {path}")
        
        # Cargar configuración actual
        from config import get_wifi_config, save_wifi_config, get_api_config, save_api_config
        current_ssid, _ = get_wifi_config()
        current_key, current_model = get_api_config()
        
        response = ""
        
        # Rutas de captive portal (redirigir a inicio)
        captive_paths = ['/generate_204', '/hotspot-detect.html', '/ncsi.txt', 
                        '/connecttest.txt', '/redirect', '/success.txt',
                        '/canonical.html', '/mobile/status.php']
        
        if path in captive_paths:
            response = generate_inicio_page()
        
        # Página de inicio
        elif path == '/' or path == '/inicio':
            response = generate_inicio_page()
        
        # Página de carrera
        elif path == '/carrera':
            response = generate_carrera_page()
        
        # Página de configuración
        elif path == '/config':
            networks, scan_time = scan_networks()
            response = generate_config_page(networks, scan_time, current_ssid, current_key, current_model)
        
        # Página de ayuda
        elif path == '/ayuda':
            response = generate_ayuda_page()
        
        # Conectar WiFi
        elif path == '/connect' and method == 'POST':
            data = parse_post_data(request)
            ssid = data.get('ssid', '')
            password = data.get('password', '')
            
            if not ssid:
                response = generate_config_page(None, 0, "", current_key, current_model,
                                               "Debes introducir un nombre de red", True)
            else:
                self.update_lcd([
                    "Conectando a:",
                    ssid[:20],
                    "Espera...",
                    ""
                ])
                
                success, result = try_connect_wifi(ssid, password)
                
                if success:
                    save_wifi_config(ssid, password)
                    response = generate_success_page(ssid, result)
                    
                    # Enviar respuesta
                    try:
                        client.send('HTTP/1.1 200 OK\r\n')
                        client.send('Content-Type: text/html; charset=utf-8\r\n')
                        client.send(f'Content-Length: {len(response)}\r\n')
                        client.send('\r\n')
                        client.send(response)
                    except:
                        pass
                    
                    try:
                        client.close()
                    except:
                        pass
                    
                    self.running = False
                    return True
                else:
                    response = generate_config_page(None, 0, ssid, current_key, current_model,
                                                   f"Error: {result}", True)
        
        # Guardar API
        elif path == '/api' and method == 'POST':
            data = parse_post_data(request)
            api_key = data.get('api_key', '').strip()
            model = data.get('model', DEFAULT_MODEL)
            
            if api_key:
                save_api_config(api_key, model)
                response = generate_config_page(None, 0, current_ssid, api_key, model,
                                               "API Key guardada correctamente", False)
            else:
                response = generate_config_page(None, 0, current_ssid, current_key, current_model,
                                               "Debes introducir una API Key", True)
        
        # Borrar datos
        elif path == '/delete' and method == 'POST':
            data = parse_post_data(request)
            target = data.get('target', '')
            
            message = ""
            is_error = False
            
            try:
                import os
                if target == 'career':
                    try:
                        os.remove('/career_save.json')
                        message = "Datos de carrera borrados"
                    except:
                        message = "No habia datos de carrera"
                elif target == 'stats':
                    try:
                        os.remove('/stats.json')
                        message = "Estadisticas borradas"
                    except:
                        message = "No habia estadisticas"
                elif target == 'all':
                    for f in ['/career_save.json', '/stats.json', '/config.json']:
                        try:
                            os.remove(f)
                        except:
                            pass
                    message = "Todos los datos borrados"
                else:
                    message = "Objetivo no valido"
                    is_error = True
            except Exception as e:
                message = f"Error: {str(e)}"
                is_error = True
            
            response = generate_config_page(None, 0, current_ssid, current_key, current_model,
                                           message, is_error)
        
        # Otras rutas -> inicio
        else:
            response = generate_inicio_page()
        
        # Enviar respuesta
        try:
            client.send('HTTP/1.1 200 OK\r\n')
            client.send('Content-Type: text/html; charset=utf-8\r\n')
            client.send(f'Content-Length: {len(response)}\r\n')
            client.send('\r\n')
            client.send(response)
        except Exception as e:
            print(f"[WIFI] Send error: {e}")
        
        try:
            client.close()
        except:
            pass
        
        return False
    
    def run(self, check_button=None):
        """Ejecuta el portal cautivo"""
        ap_ip = self.start_ap()
        
        self.update_lcd([
            "PORTAL WiFi",
            "Conecta a la red:",
            f"  {AP_SSID}",
            f"  IP: {ap_ip}"
        ])
        
        self.start_server()
        
        result = {"connected": False}
        
        try:
            while self.running:
                if check_button and check_button():
                    print("[WIFI] Cancelled by button")
                    break
                
                try:
                    client, addr = self.server.accept()
                    print(f"[WIFI] Client: {addr}")
                    
                    request = client.recv(2048).decode('utf-8', 'ignore')
                    
                    if request:
                        success = self.handle_request(client, request)
                        if success:
                            result["connected"] = True
                            break
                    
                except OSError:
                    pass
                
                time.sleep(0.1)
                gc.collect()
                
        except Exception as e:
            print(f"[WIFI] Error: {e}")
        
        finally:
            if self.server:
                self.server.close()
            self.stop_ap()
        
        return result


# ============================================================================
# PUBLIC API
# ============================================================================

def run_wifi_portal(lcd_callback=None, check_button=None):
    """Función helper para ejecutar el portal"""
    portal = WiFiPortal(lcd_callback=lcd_callback)
    return portal.run(check_button=check_button)


def connect_saved_wifi(timeout=10):
    """Intenta conectar con WiFi guardada"""
    from config import get_wifi_config
    ssid, password = get_wifi_config()
    
    if not ssid:
        return False, "No hay WiFi configurada"
    
    return try_connect_wifi(ssid, password, timeout)


if __name__ == "__main__":
    print("Iniciando portal cautivo...")
    result = run_wifi_portal()
    print(f"Resultado: {result}")
