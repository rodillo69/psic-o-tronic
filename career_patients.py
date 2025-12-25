# ============================================================================
# CAREER_PATIENTS.PY - Generacion de pacientes y sesiones con IA
# PSIC-O-TRONIC - Modo Mi Consulta
# ============================================================================

import urequests
import ujson
import random
import gc

from career_data import (
    create_paciente_template, create_mensaje_template,
    MIN_SESIONES, MAX_SESIONES
)

# Importar sistema de errores
try:
    from error_handler import (
        ErrorHandler, report_error, map_http_error
    )
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False

# API Key por defecto (fallback)
DEFAULT_API_KEY = "AIzaSyDcCfYRcuOM_7vqP3moss-_virH1dI4xBg"
DEFAULT_MODEL = "gemini-2.5-flash-lite"


def _get_api_url():
    """Obtiene URL de la API con la key configurada"""
    try:
        from config import get_api_config
        api_key, model = get_api_config()
    except:
        api_key = DEFAULT_API_KEY
        model = DEFAULT_MODEL
    
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"


def _clean_for_prompt(text):
    """Limpia texto para enviar al prompt (quita acentos y n con virgulilla)"""
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


def _call_gemini(prompt):
    """
    Llama a la API de Gemini.
    
    Returns:
        Dict parseado o None si error
    """
    gc.collect()
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        payload_str = ujson.dumps(payload)
        
        res = urequests.post(
            _get_api_url(),
            data=payload_str,
            headers={'Content-Type': 'application/json'}
        )
        
        if res.status_code == 200:
            response_text = res.text
            res.close()

            data = ujson.loads(response_text)
            text_res = data['candidates'][0]['content']['parts'][0]['text']
            text_res = text_res.replace("```json", "").replace("```", "").strip()

            result = ujson.loads(text_res)
            gc.collect()
            return result
        else:
            status = res.status_code
            res.close()

            if status == 403:
                print(f"[GEMINI] API KEY BLOCKED! Error 403 - API key reportada como filtrada")
            else:
                print(f"[GEMINI] Error HTTP {status}")

            if ERROR_HANDLER_AVAILABLE:
                error_type = map_http_error(status)
                report_error(error_type, f"career_patients HTTP {status}")

            return None
            
    except MemoryError as e:
        gc.collect()
        print(f"[GEMINI] MemoryError: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("memory_critical", "career_patients", e)
        return None
        
    except ValueError as e:
        print(f"[GEMINI] JSON Error: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("json_parse_error", "career_patients", e)
        gc.collect()
        return None
        
    except OSError as e:
        print(f"[GEMINI] Network Error: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("wifi_disconnected", str(e), e)
        gc.collect()
        return None
        
    except Exception as e:
        print(f"[GEMINI] Error: {e}")
        if ERROR_HANDLER_AVAILABLE:
            report_error("unknown_error", f"_call_gemini: {type(e).__name__}", e)
        gc.collect()
        return None


def generate_doctor_name(titulo):
    """
    Genera nombre de doctor gracioso/faltoso.
    
    Args:
        titulo: "Doctor", "Doctora" o "Doctore"
    
    Returns:
        String con nombre o None si error
    """
    prompt = f"""Genera un nombre GRACIOSO y ligeramente FALTOSO para un {titulo.lower()} de psicologia.
El nombre debe ser absurdo pero creible como nombre espanol.
Ejemplos de estilo: "Facundo Desgracias", "Remedios Pastillas", "Armando Lio"

Responde SOLO con este JSON (sin markdown):
{{"nombre": "Nombre Apellido"}}

El nombre completo debe tener maximo 16 caracteres."""
    
    result = _call_gemini(prompt)
    if result and "nombre" in result:
        return result["nombre"][:16]
    return None


def generate_rank_name(nivel):
    """
    Genera nombre de rango para un nivel.
    
    Args:
        nivel: Nivel del jugador (1+)
    
    Returns:
        String con nombre de rango
    """
    if nivel == 1:
        return "Becario"
    
    # Rangos base segun nivel
    if nivel <= 3:
        base = "basico"
    elif nivel <= 6:
        base = "intermedio"
    elif nivel <= 10:
        base = "avanzado"
    elif nivel <= 15:
        base = "experto"
    else:
        base = "legendario"
    
    prompt = f"""Genera un titulo/rango GRACIOSO para un psicologo de nivel {base}.
Nivel actual: {nivel}
Debe reflejar progresion desde "Becario" (nivel 1).
Ejemplos: "Interno Cafetero", "Residente Cutre", "Adjunto Matasanos", "Jefe de Locos"

Responde SOLO con JSON (sin markdown):
{{"rango": "Nombre del Rango"}}

Maximo 14 caracteres."""
    
    result = _call_gemini(prompt)
    if result and "rango" in result:
        return result["rango"][:14]
    
    # Fallback
    fallbacks = ["Interno", "Residente", "Adjunto", "Titular", "Jefe", "Director", "Eminencia"]
    idx = min(nivel - 1, len(fallbacks) - 1)
    return fallbacks[idx]


def generate_new_patient(nivel_dificultad=1, pacientes_existentes=None, tipo_paciente="normal"):
    """
    Genera un nuevo paciente con IA.
    
    Args:
        nivel_dificultad: 1-10, afecta complejidad del caso
        pacientes_existentes: Lista de pacientes actuales para evitar repetir
        tipo_paciente: Tipo especial de paciente (normal, vip, agresivo, etc)
    
    Returns:
        Dict con datos del paciente o None si error
    """
    sesiones = random.randint(MIN_SESIONES, MAX_SESIONES)
    
    dificultad_text = "facil" if nivel_dificultad <= 3 else \
                      "medio" if nivel_dificultad <= 6 else "dificil"
    
    # Modificar según tipo de paciente
    tipo_text = ""
    if tipo_paciente == "vip":
        tipo_text = "El paciente es alguien IMPORTANTE y RICO (politico, famoso, empresario). Actua con aires de superioridad."
    elif tipo_paciente == "agresivo":
        tipo_text = "El paciente es MUY AGRESIVO e IMPACIENTE. Amenaza constantemente. Insulta."
    elif tipo_paciente == "hipocondriaco":
        tipo_text = "El paciente es HIPOCONDRIACO. Cree tener mil enfermedades. Muy preocupado."
    elif tipo_paciente == "moroso":
        tipo_text = "El paciente es MOROSO y POBRE. Siempre con excusas para no pagar."
    elif tipo_paciente == "influencer":
        tipo_text = "El paciente es INFLUENCER. Todo lo sube a redes. Muy dramatico."
    elif tipo_paciente == "paranoico":
        tipo_text = "El paciente es PARANOICO. Cree que todos conspiran contra el."
    elif tipo_paciente == "silencioso":
        tipo_text = "El paciente es MUY CALLADO. Respuestas muy cortas. Misterioso."
    elif tipo_paciente == "mentiroso":
        tipo_text = "El paciente MIENTE constantemente. Contradice lo que dijo antes."
    elif tipo_paciente == "misterioso":
        tipo_text = "El paciente es MISTERIOSO. No sabemos nada de el. Muy raro."
    elif tipo_paciente == "urgente":
        tipo_text = "El paciente tiene URGENCIA. Todo es para ya. Muy estresado."
    
    # Construir lista de exclusion
    exclusion_text = ""
    if pacientes_existentes:
        nombres = [_clean_for_prompt(p.get("nombre", "")) for p in pacientes_existentes]
        problemas = [_clean_for_prompt(p.get("problema_corto", "")) for p in pacientes_existentes]
        exclusion_text = f"""
PACIENTES YA EXISTENTES (NO REPETIR):
- Nombres usados: {", ".join(nombres)}
- Problemas usados: {", ".join(problemas)}

GENERA UN PACIENTE COMPLETAMENTE DIFERENTE con nombre y problema NUEVOS.
"""
    
    prompt = f"""Genera un PACIENTE UNICO para un juego de psicologo con humor negro.
Dificultad: {dificultad_text}
Sesiones necesarias: {sesiones}
{tipo_text}
{exclusion_text}
El paciente tiene un problema psicologico ABSURDO pero que suena real.
Estilo humor: South Park, Padre de Familia, absurdo espanol.

DATOS DEL PACIENTE:
- nombre: Nombre gracioso (ej: Paco Frito, Mari Loca, Eutanasio)
- edad: Numero + palabra graciosa (ej: "47 maduros", "23 tiernos", "65 crujientes")
- sexo: Variado y a veces absurdo. Opciones normales: "Hombre", "Mujer". 
  Opciones absurdas (usar a veces): "Helicoptero", "Dependiendo el dia", "Que es eso?",
  "Hombre (dice el)", "Ni idea", "Fluido como el agua", "Cosa", "Ex-hombre", "Preguntale a mi madre"
- ocupacion: Trabajo absurdo o normal con twist (ej: "Funcionario sin funcion", "Influencer de gatos",
  "Cata-quesos profesional", "Coach de coaches", "Parado activo")
- problema_corto: Descripcion breve del problema
- problema_detalle: Historia de fondo
- personalidad: Como se comporta
- cierre_curado: Frase graciosa de que paso cuando se curo (se mostara al ganar)
- cierre_huye: Frase graciosa de que paso cuando huyo (se mostrara al perder)

Responde SOLO con JSON (sin markdown):
{{
  "nombre": "Nombre Paciente",
  "edad": "X anyos",
  "sexo": "Genero",
  "ocupacion": "Trabajo",
  "problema_corto": "Descripcion muy corta",
  "problema_detalle": "Historia de fondo del problema",
  "personalidad": "Como se comporta el paciente",
  "cierre_curado": "Ya no hace X. Ahora hace Y",
  "cierre_huye": "Se fue a Z. Sigue haciendo X"
}}

LIMITES ESTRICTOS:
- nombre: max 14 caracteres
- edad: max 14 caracteres
- sexo: max 18 caracteres
- ocupacion: max 20 caracteres
- problema_corto: max 30 caracteres  
- problema_detalle: max 100 caracteres
- personalidad: max 50 caracteres
- cierre_curado: max 40 caracteres
- cierre_huye: max 40 caracteres

Espanol de Espana, con acentos y ene. Se creativo y gamberro."""
    
    result = _call_gemini(prompt)
    
    if result:
        paciente = create_paciente_template()
        paciente["nombre"] = result.get("nombre", "Anonimo")[:14]
        paciente["edad"] = result.get("edad", "? años")[:14]
        paciente["sexo"] = result.get("sexo", "???")[:18]
        paciente["ocupacion"] = result.get("ocupacion", "Desconocida")[:20]
        paciente["problema_corto"] = result.get("problema_corto", "Problema")[:30]
        paciente["problema_detalle"] = result.get("problema_detalle", "")[:100]
        paciente["personalidad"] = result.get("personalidad", "Normal")[:50]
        paciente["sesiones_totales"] = sesiones
        paciente["sesiones_completadas"] = 0
        paciente["progreso"] = 0
        paciente["tolerancia"] = 3  # Errores antes de huir
        paciente["historial"] = []
        paciente["tipo"] = tipo_paciente
        # Cierres narrativos
        paciente["cierre_curado"] = result.get("cierre_curado", "Se curo milagrosamente")[:40]
        paciente["cierre_huye"] = result.get("cierre_huye", "Huyo a otro psicologo")[:40]
        
        # Contexto para IA (sin acentos para prompts futuros)
        paciente["contexto_ia"] = _clean_for_prompt(
            f"Paciente: {paciente['nombre']}, {paciente['edad']}, {paciente['sexo']}. "
            f"Ocupacion: {paciente['ocupacion']}. "
            f"Problema: {paciente['problema_corto']}. "
            f"Personalidad: {paciente['personalidad']}"
        )
        
        return paciente
    
    return None


def generate_session_message(paciente, historial_respuestas, nivel_dificultad=1):
    """
    Genera mensaje de sesion para un paciente existente.
    
    Args:
        paciente: Dict con datos del paciente
        historial_respuestas: Lista de respuestas anteriores
        nivel_dificultad: 1-10
    
    Returns:
        Dict con mensaje o None si error
    """
    sesion_num = paciente["sesiones_completadas"] + 1
    progreso = paciente["progreso"]
    
    # Construir contexto del historial REAL
    if not historial_respuestas:
        historial_text = "Primera sesion con este paciente."
    else:
        # Pasar las últimas 3 decisiones REALES
        historial_text = f"Sesiones previas: {len(historial_respuestas)}.\n"
        historial_text += "HISTORIAL DE DECISIONES (importante para coherencia):\n"
        for h in historial_respuestas[-3:]:
            opcion = _clean_for_prompt(h.get("opcion_texto", "?"))
            resultado = "funciono" if h.get("correcto") else "fallo"
            historial_text += f"- Sesion {h.get('sesion', '?')}: Doctor dijo '{opcion}' -> {resultado}\n"
        historial_text += f"Progreso actual: {'positivo' if progreso > 0 else 'negativo' if progreso < 0 else 'neutro'}."
    
    # Dificultad de las opciones
    if nivel_dificultad <= 2:
        diff_text = "Una opcion es claramente mejor que las otras."
    elif nivel_dificultad <= 5:
        diff_text = "Las opciones estan equilibradas, hay que pensar."
    else:
        diff_text = "Todas las opciones parecen igual de malas, muy dificil."
    
    contexto = _clean_for_prompt(paciente.get("contexto_ia", ""))
    
    prompt = f"""Eres guionista de un juego de humor negro sobre un psicologo cutre.

PACIENTE: {contexto}
SESION: {sesion_num} de {paciente['sesiones_totales']}
{historial_text}

GENERA:
1. Un MENSAJE del paciente pidiendo consejo sobre su problema especifico
2. Cuatro RESPUESTAS del doctor que sean consejos DIRECTOS al problema planteado

REGLAS CRITICAS:
- Las 4 opciones DEBEN responder directamente a lo que pregunta el paciente
- Si el paciente pregunta "que hago con X", las opciones son consejos sobre X
- Las respuestas son malas/absurdas pero COHERENTES con la pregunta
- La correcta es la mas retorcida pero sutil
- {diff_text}
- Si hay historial, el paciente DEBE reaccionar a lo que paso antes (ej: "Doctor, segui su consejo de gritar y...")

EJEMPLO:
Mensaje: "Mi jefe me grita, que hago?"
Opciones: ["Gritale tu mas", "Llora en silencio", "Dimite hoy", "Echale laxante"]
(Todas responden a QUE HACER con el jefe)

Responde SOLO con JSON (sin markdown):
{{
  "mensaje": "Doctor, [problema concreto y pregunta]",
  "opciones": ["Consejo 1", "Consejo 2", "Consejo 3", "Consejo 4"],
  "correcta": 0,
  "feedback_ok": "Resultado sarcastico de 2 lineas",
  "feedback_mal": "Consecuencia comica de 2 lineas"
}}

LIMITES:
- mensaje: max 120 caracteres
- cada opcion: max 18 caracteres
- feedback_ok: max 60 caracteres (2 lineas de 20)
- feedback_mal: max 60 caracteres (2 lineas de 20)

Espanol de Espana con acentos. NUNCA signos al inicio de frase."""
    
    result = _call_gemini(prompt)
    
    if result:
        mensaje = create_mensaje_template()
        mensaje["paciente_id"] = paciente["id"]
        mensaje["contenido"] = result.get("mensaje", "Hola doctor...")[:120]
        mensaje["opciones"] = [o[:18] for o in result.get("opciones", ["?", "?", "?", "?"])[:4]]
        mensaje["correcta"] = result.get("correcta", 0) % 4
        mensaje["feedback_correcto"] = result.get("feedback_ok", "Bien hecho")[:60]
        mensaje["feedback_incorrecto"] = result.get("feedback_mal", "Eso fue mal")[:60]
        
        # Limpiar signos al inicio
        mensaje["contenido"] = _clean_leading_punctuation(mensaje["contenido"])
        mensaje["opciones"] = [_clean_leading_punctuation(o) for o in mensaje["opciones"]]
        
        return mensaje
    
    return None


def _clean_leading_punctuation(text):
    """Quita signos de puntuacion al inicio"""
    if not text:
        return text
    while len(text) > 0 and text[0] in '!?¡¿':
        text = text[1:]
    return text.strip()


def generate_emergency_message(paciente, nivel_dificultad=1):
    """
    Genera mensaje de emergencia (mas dramatico).
    
    Args:
        paciente: Dict con datos del paciente
        nivel_dificultad: 1-10
    
    Returns:
        Dict con mensaje o None si error
    """
    contexto = _clean_for_prompt(paciente.get("contexto_ia", ""))
    
    prompt = f"""Eres guionista de un juego de humor negro sobre un psicologo cutre.

PACIENTE EN CRISIS: {contexto}

Es fuera de horario. El paciente tiene una EMERGENCIA absurda pero urgente.

GENERA:
1. MENSAJE de emergencia con una PREGUNTA urgente y concreta
2. Cuatro RESPUESTAS del doctor que sean consejos DIRECTOS a esa emergencia

REGLAS CRITICAS:
- El mensaje debe pedir ayuda sobre algo CONCRETO
- Las 4 opciones DEBEN responder a como resolver esa emergencia
- Las respuestas son malas/absurdas pero COHERENTES con la crisis
- Humor negro pero la emergencia no es grave de verdad

EJEMPLO:
Mensaje: "Doctor! Mi suegra viene a cenar y me da panico. Que hago?"
Opciones: ["Finge tu muerte", "Envenena sopa", "Huye de casa", "Dile que estas mal"]
(Todas responden a QUE HACER con la suegra)

Responde SOLO con JSON (sin markdown):
{{
  "mensaje": "Doctor! [emergencia absurda y pregunta]",
  "opciones": ["Consejo 1", "Consejo 2", "Consejo 3", "Consejo 4"],
  "correcta": 0,
  "feedback_ok": "Crisis resuelta retorcidamente",
  "feedback_mal": "Crisis empeora comicamente"
}}

LIMITES:
- mensaje: max 120 caracteres
- cada opcion: max 18 caracteres
- feedback: max 25 caracteres

Espanol de Espana. NUNCA signos al inicio."""
    
    result = _call_gemini(prompt)
    
    if result:
        mensaje = create_mensaje_template()
        mensaje["paciente_id"] = paciente["id"]
        mensaje["contenido"] = result.get("mensaje", "Doctor!")[:120]
        mensaje["opciones"] = [o[:18] for o in result.get("opciones", ["?", "?", "?", "?"])[:4]]
        mensaje["correcta"] = result.get("correcta", 0) % 4
        mensaje["feedback_correcto"] = result.get("feedback_ok", "Ok")[:25]
        mensaje["feedback_incorrecto"] = result.get("feedback_mal", "Mal")[:25]
        
        mensaje["contenido"] = _clean_leading_punctuation(mensaje["contenido"])
        mensaje["opciones"] = [_clean_leading_punctuation(o) for o in mensaje["opciones"]]
        
        return mensaje
    
    return None


def generate_intro_message(paciente):
    """
    Genera primer mensaje de un paciente nuevo.
    
    Args:
        paciente: Dict con datos del paciente
    
    Returns:
        Dict con mensaje o None si error
    """
    contexto = _clean_for_prompt(paciente.get("contexto_ia", ""))
    problema = _clean_for_prompt(paciente.get("problema_corto", ""))
    
    prompt = f"""Eres guionista de un juego de humor negro sobre un psicologo cutre.

PACIENTE NUEVO: {contexto}
PROBLEMA: {problema}

GENERA:
1. MENSAJE donde el paciente se presenta y explica su problema con una PREGUNTA concreta
2. Cuatro RESPUESTAS del doctor que sean consejos DIRECTOS a esa pregunta

REGLAS CRITICAS:
- El mensaje debe terminar con una pregunta o peticion de consejo
- Las 4 opciones DEBEN responder directamente a lo que pregunta
- Las respuestas son malas/absurdas pero COHERENTES con la pregunta
- Humor estilo South Park / Bored to Death

EJEMPLO:
Mensaje: "Hola doctor, tengo miedo a los payasos. Que puedo hacer?"
Opciones: ["Hazte payaso", "Contrata uno", "Ve al circo", "Ignoralo"]
(Todas responden a QUE HACER con el miedo)

Responde SOLO con JSON (sin markdown):
{{
  "mensaje": "Hola doctor, [presenta problema y pregunta]",
  "opciones": ["Consejo 1", "Consejo 2", "Consejo 3", "Consejo 4"],
  "correcta": 0,
  "feedback_ok": "Buen comienzo retorcido",
  "feedback_mal": "Mal comienzo comico"
}}

LIMITES:
- mensaje: max 120 caracteres
- cada opcion: max 18 caracteres
- feedback: max 25 caracteres

Espanol de Espana. NUNCA signos al inicio."""
    
    result = _call_gemini(prompt)
    
    if result:
        mensaje = create_mensaje_template()
        mensaje["paciente_id"] = paciente["id"]
        mensaje["contenido"] = result.get("mensaje", "Hola doctor...")[:120]
        mensaje["opciones"] = [o[:18] for o in result.get("opciones", ["?", "?", "?", "?"])[:4]]
        mensaje["correcta"] = result.get("correcta", 0) % 4
        mensaje["feedback_correcto"] = result.get("feedback_ok", "Ok")[:25]
        mensaje["feedback_incorrecto"] = result.get("feedback_mal", "Mal")[:25]
        
        mensaje["contenido"] = _clean_leading_punctuation(mensaje["contenido"])
        mensaje["opciones"] = [_clean_leading_punctuation(o) for o in mensaje["opciones"]]
        
        return mensaje
    
    return None


# Test standalone
if __name__ == "__main__":
    print("=== Test Career Patients ===")
    
    # Test nombre doctor
    print("\n[Test Nombre Doctor]")
    nombre = generate_doctor_name("Doctor")
    print(f"Nombre: {nombre}")
    
    # Test rango
    print("\n[Test Rango]")
    for nivel in [1, 3, 5, 8, 12]:
        rango = generate_rank_name(nivel)
        print(f"Nivel {nivel}: {rango}")
