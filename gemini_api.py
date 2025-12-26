# ============================================================================
# GEMINI_API.PY - Comunicación con API de Gemini
# PSIC-O-TRONIC - Generación de casos clínicos
# ============================================================================

import urequests
import ujson
import gc

# Importar sistema de errores
try:
    from error_handler import (
        ErrorHandler, report_error, map_http_error, check_memory
    )
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False

# API Key por defecto (fallback)
# Modelo: gemini-2.5-flash-lite (15 RPM, 1000 RPD - mejor para evitar error 429)
DEFAULT_API_KEY = "AIzaSyDcCfYRcuOM_7vqP3moss-_virH1dI4xBg"
DEFAULT_MODEL = "gemini-2.5-flash-lite"

def get_api_url():
    """Obtiene la URL de la API con la key configurada"""
    try:
        from config import get_api_config
        api_key, model = get_api_config()
    except:
        api_key = DEFAULT_API_KEY
        model = DEFAULT_MODEL
    
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

# Prompt base (sin caracteres problemáticos para JSON)
PROMPT_BASE = """# IDENTIDAD
Eres PSIC-O-TRONIC, un busca maldito conectado a la linea psiquiatrica de emergencias.

# MISION
Genera un caso clinico ficticio de HUMOR NEGRO EXTREMO para un juego de decisiones.

# ESTILO DE HUMOR
Inspirado en South Park, Padre de Familia, Rick and Morty:
- Satira social brutal sin filtros
- Absurdo extremo con logica retorcida
- Cinismo despiadado sobre la condicion humana
- Parodia cruel de tabues y comportamientos
- Muy directo, macabro, gamberro

# CATEGORIAS TEMATICAS (ROTA ENTRE ELLAS)
1. FAMILIAR/RELACIONES: Dinamica toxica, herencias, suegros
2. LABORAL/PROFESIONAL: Jefes psicopatas, incompetencia
3. EXISTENCIAL/IDENTIDAD: Crisis extremas, delirios
4. SOCIAL/VECINDARIO: Guerra de vecinos, comunidades
5. ADICCIONES/OBSESIONES: Coleccionismo enfermizo
6. CRIMEN/MORAL: Crimenes menores escalados
7. SALUD/CUERPO: Hipocondria, automutilacion absurda
8. DIGITAL/TECNOLOGIA: Acoso online, influencers
9. RELIGION/CREENCIAS: Sectas absurdas, fanatismo
10. SEXUAL (moderado): Fetiches raros, confusiones

# CONSTRUCCION DEL CASO
- Remitente: Nombre absurdo del paciente (max 14 caracteres)
- Mensaje: El PACIENTE escribe DIRECTAMENTE al doctor en PRIMERA PERSONA
  * Debe empezar con Buenas doctor o Hola doctor
  * DEBE INCLUIR una PREGUNTA o PETICION de consejo concreta
  * Max 150 caracteres, detalles retorcidos
  * Puedes usar acentos y la letra n con virgulilla
- Opciones: 4 CONSEJOS del psicologo que responden DIRECTAMENTE a la pregunta del paciente

# REGLA CRITICA DE COHERENCIA
Las 4 opciones DEBEN ser respuestas directas al problema planteado en el mensaje.
Si el paciente pregunta "que hago con X", las 4 opciones son consejos sobre X.
Aunque las respuestas sean absurdas, deben tener SENTIDO como respuesta a la pregunta.

EJEMPLO BUENO:
Mensaje: "Doctor, mi suegra me odia. Como me la quito de encima?"
Opciones: ["Casate con ella", "Finge tu muerte", "Envenenala", "Mudala a Cuenca"]
(Las 4 responden a COMO quitarse a la suegra)

EJEMPLO MALO:
Mensaje: "Doctor, mi suegra me odia. Como me la quito de encima?"
Opciones: ["Compra un gato", "Vete al gym", "Lee un libro", "Hazte vegano"]
(Las opciones NO tienen relacion con la suegra)

# REGLAS DE DIFICULTAD
1. LAS 4 OPCIONES DEBEN SER TODAS MALAS/PSICOTICAS - ninguna debe parecer "buena"
2. La opcion correcta es la MAS RETORCIDA pero de forma SUTIL
3. Las incorrectas son: una demasiado suave, otra contraproducente, otra absurda
4. El jugador debe DUDAR entre al menos 2-3 opciones
5. Mezcla el orden: la correcta puede estar en cualquier posicion (0,1,2,3)

# OTRAS REGLAS
- Feedback WIN: Consecuencia retorcida exitosa (max 20 chars)
- Feedback LOSE: Despido/demanda absurda (max 20 chars)
- NADIE MUERE en el feedback
- Lenguaje: ESPANOL DE ESPANA, coloquial, gamberro
- NUNCA empieces frases con signos de puntuacion

"""

JSON_TEMPLATE = '{"tema_corto":"X","remitente":"Nombre","mensaje":"Hola doctor...","opciones":["Op1","Op2","Op3","Op4"],"correcta":0,"feedback_win":"Exito","feedback_lose":"Fallo"}'


class GeminiOracle:
    """
    Oráculo que genera casos clínicos usando Gemini AI.
    """
    
    def __init__(self):
        self.history = []  # Historial de temas para evitar repetición
        self.max_history = 5
        self.last_error = None
    
    def _clean_for_prompt(self, text):
        """Limpia texto para enviar al prompt (quita acentos y ñ)"""
        if not text:
            return ""
        replacements = [
            ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'),
            ('Á', 'A'), ('É', 'E'), ('Í', 'I'), ('Ó', 'O'), ('Ú', 'U'),
            ('ñ', 'n'), ('Ñ', 'N'), ('ü', 'u'), ('Ü', 'U'),
        ]
        result = str(text)
        for old, new in replacements:
            result = result.replace(old, new)
        return result
    
    def _build_prompt(self, mode="classic", story_modifier=""):
        """
        Construye el prompt completo.
        
        Args:
            mode: "classic", "survival", "story"
            story_modifier: Modificador adicional para modo historia
            
        Returns:
            String con prompt completo
        """
        # Limpiar historial de acentos
        clean_history = [self._clean_for_prompt(t) for t in self.history]
        history_txt = ", ".join(clean_history) if clean_history else "ninguno"
        
        mode_text = ""
        if mode == "survival":
            mode_text = "\n# MODO SURVIVAL\nLos casos deben ser variados e impredecibles.\n"
        elif mode == "story":
            mode_text = story_modifier  # Ya viene limpio de story_data.py
        
        prompt = (
            PROMPT_BASE +
            mode_text +
            f"# EVITA REPETIR\nTemas ya usados: [{history_txt}]\n\n"
            "# FORMATO DE SALIDA\n"
            "Responde SOLO con este JSON (sin markdown, sin ```):\n" +
            JSON_TEMPLATE
        )
        
        return prompt
    
    def get_scenario(self, mode="classic", story_modifier=""):
        """
        Obtiene un nuevo escenario de Gemini.

        Args:
            mode: Modo de juego
            story_modifier: Modificador para modo historia

        Returns:
            Dict con escenario o escenario de error
        """
        gc.collect()

        prompt = self._build_prompt(mode, story_modifier)

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            # DEBUG: Mostrar configuración
            from config import get_api_config
            api_key, api_model = get_api_config()
            print(f"[GEMINI] Using API key: ...{api_key[-20:]}")
            print(f"[GEMINI] Using model: {api_model}")

            payload_str = ujson.dumps(payload)

            api_url = get_api_url()
            print(f"[GEMINI] POST to: {api_url[:80]}...")

            res = urequests.post(
                api_url,
                data=payload_str,
                headers={'Content-Type': 'application/json'},
                timeout=15  # Timeout de 15 segundos para evitar bloqueos
            )

            print(f"[GEMINI] Response status: {res.status_code}")
            
            if res.status_code == 200:
                response_text = res.text
                res.close()
                
                # Parsear respuesta
                data = ujson.loads(response_text)
                text_res = data['candidates'][0]['content']['parts'][0]['text']
                text_res = text_res.replace("```json", "").replace("```", "").strip()
                
                scenario = ujson.loads(text_res)
                
                # Limpiar signos de puntuación al inicio de textos
                scenario = self._clean_scenario(scenario)
                
                # Guardar tema en historial
                if 'tema_corto' in scenario:
                    self.history.append(scenario['tema_corto'])
                    if len(self.history) > self.max_history:
                        self.history.pop(0)
                
                self.last_error = None
                gc.collect()
                return scenario
                
            else:
                status = res.status_code

                # DEBUG: Mostrar cuerpo del error
                try:
                    error_body = res.text[:500]  # Primeros 500 chars
                    print(f"[GEMINI] Error body: {error_body}")
                except:
                    pass

                res.close()

                # Usar error handler si disponible
                if ERROR_HANDLER_AVAILABLE:
                    error_type = map_http_error(status)
                    report_error(error_type, f"HTTP {status}")

                if status == 400:
                    self.last_error = "HTTP 400: API Key inválida o prompt mal formado"
                elif status == 401:
                    self.last_error = "HTTP 401: API Key no autorizada"
                elif status == 403:
                    self.last_error = "API_KEY_BLOCKED"  # Marca especial para 403
                    print(f"[GEMINI] API KEY BLOCKED! Key: ...{api_key[-20:]}")
                    # Retornar escenario explicativo para 403
                    return {
                        "tema_corto": "error_403",
                        "remitente": "SISTEMA",
                        "mensaje": "API Key de Gemini bloqueada. Google la detecto como filtrada. Necesitas configurar una nueva.",
                        "opciones": ["Abrir Portal Web", "Reintentar", "Volver al Menu"],
                        "correcta": 0,
                        "feedback_win": "Abriendo portal...",
                        "feedback_lose": "Cancelado"
                    }
                elif status == 429:
                    self.last_error = "HTTP 429: Límite de peticiones excedido"
                    print(f"[GEMINI] RATE LIMIT! Key: ...{api_key[-20:]}, Model: {api_model}")
                elif status == 500:
                    self.last_error = "HTTP 500: Error del servidor"
                else:
                    self.last_error = f"HTTP {status}: Error desconocido"

                print(f"[GEMINI] Error: {self.last_error}")
                return None
                
        except MemoryError as e:
            gc.collect()
            self.last_error = "Memoria llena - Reinicia el dispositivo"
            if ERROR_HANDLER_AVAILABLE:
                report_error("memory_critical", "En get_scenario", e)
            return None
            
        except ValueError as e:
            self.last_error = "Respuesta JSON inválida de la API"
            if ERROR_HANDLER_AVAILABLE:
                report_error("json_parse_error", "Gemini response", e)
            return None
            
        except OSError as e:
            self.last_error = "Sin conexión WiFi o timeout"
            if ERROR_HANDLER_AVAILABLE:
                report_error("wifi_disconnected", str(e), e)
            return None
            
        except Exception as e:
            self.last_error = f"Error: {type(e).__name__}"
            if ERROR_HANDLER_AVAILABLE:
                report_error("unknown_error", f"get_scenario: {type(e).__name__}", e)
            return None
    
    def _clean_leading_punctuation(self, text):
        """Quita signos de puntuación al inicio de un texto"""
        if not text:
            return text
        text = str(text)
        # Quitar ! ? del inicio con bucle (mas compatible con MicroPython)
        while len(text) > 0 and text[0] in '!?':
            text = text[1:]
        return text.strip()
    
    def _clean_scenario(self, scenario):
        """Limpia signos de puntuación al inicio de todos los textos"""
        if 'mensaje' in scenario:
            scenario['mensaje'] = self._clean_leading_punctuation(scenario['mensaje'])
        if 'opciones' in scenario:
            scenario['opciones'] = [self._clean_leading_punctuation(o) for o in scenario['opciones']]
        if 'feedback_win' in scenario:
            scenario['feedback_win'] = self._clean_leading_punctuation(scenario['feedback_win'])
        if 'feedback_lose' in scenario:
            scenario['feedback_lose'] = self._clean_leading_punctuation(scenario['feedback_lose'])
        return scenario
    
    def _error_scenario(self, error_msg):
        """Genera escenario de error"""
        return {
            "tema_corto": "error",
            "remitente": "SISTEMA",
            "mensaje": f"Error: {error_msg}. Pulsa OK para reintentar.",
            "opciones": ["Reintentar", "Continuar", "Volver"],
            "correcta": 0,
            "feedback_win": "Reconectando...",
            "feedback_lose": "Sin suerte"
        }
    
    def is_error_scenario(self, scenario):
        """Comprueba si es un escenario de error"""
        return scenario.get("tema_corto") == "error"
    
    def clear_history(self):
        """Limpia el historial de temas"""
        self.history = []


# Instancia global del oráculo
_oracle = None

def get_oracle():
    """Obtiene la instancia global del oráculo"""
    global _oracle
    if _oracle is None:
        _oracle = GeminiOracle()
    return _oracle


def get_scenario(mode="classic", story_modifier=""):
    """Helper para obtener escenario"""
    return get_oracle().get_scenario(mode, story_modifier)


# Test standalone
if __name__ == "__main__":
    import network
    import time
    
    print("=== Test Gemini API ===")
    
    # Conectar WiFi primero
    from config import get_wifi_config
    ssid, password = get_wifi_config()
    
    if ssid:
        print(f"Conectando a {ssid}...")
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.connect(ssid, password)
        
        while not sta.isconnected():
            time.sleep(0.5)
        
        print(f"OK: {sta.ifconfig()[0]}")
        
        # Test obtener escenario
        print("\nObteniendo escenario...")
        oracle = get_oracle()
        scenario = oracle.get_scenario()
        
        if oracle.is_error_scenario(scenario):
            print(f"ERROR: {oracle.last_error}")
        else:
            print(f"\nTema: {scenario.get('tema_corto')}")
            print(f"Remitente: {scenario.get('remitente')}")
            print(f"Mensaje: {scenario.get('mensaje')[:50]}...")
            print(f"Opciones: {scenario.get('opciones')}")
    else:
        print("No hay WiFi configurada. Ejecuta wifi_portal primero.")
