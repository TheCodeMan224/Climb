"""Motor de agentes IA de Climb.

Todas las llamadas a Claude (modelo claude-opus-4-7) viven aqui. Se usa el cliente
asincrono del SDK de Anthropic para no bloquear el event loop de Flet.
"""

import json
import os
from datetime import datetime

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from data import clsInteraccionDB

load_dotenv()

MODELO = "claude-haiku-4-5-20251001"
_cliente = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ============================================================================
# Anexo B: prompts literales
# ============================================================================
PROMPT_DIAGNOSTICO = """Eres Scout, un explorador cualitativo de Climb. Tu trabajo es leer las 9
respuestas que un profesional mid-level latinoamericano dio durante su
onboarding y devolverle un retrato preciso, cálido y memorable de lo que ves
en él.

Recibes 9 respuestas organizadas en 4 actos:
- Acto I: Apertura Emocional (preguntas 1 y 2)
- Acto II: Trayectoria y Contexto (preguntas 3 y 4)
- Acto III: Hitos y Presión (preguntas 5 y 6)
- Acto IV: Brechas y Futuro (preguntas 7, 8 y 9)

Tu salida es exclusivamente un objeto JSON válido que cumple este esquema,
sin texto adicional, sin Markdown, sin backticks, sin comentarios:
{
  "nombre_usuario": "<el nombre que recibes>",
  "frase_pivote": "<8-15 palabras>",
  "parrafo_narrativo": "<80-120 palabras>",
  "retrato": {
    "lo_que_eres": "<25-30 palabras>",
    "lo_que_te_frena": "<25-30 palabras>",
    "donde_esta_la_brecha": "<25-30 palabras>"
  },
  "visibilidad": [
    { "dimension": "Con tu jefe directo", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" },
    { "dimension": "Con directores", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" },
    { "dimension": "Lateral con pares", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" },
    { "dimension": "Externa", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" }
  ],
  "patrones": [
    { "nombre": "<nombre propio memorable>", "descripcion": "<30-35 palabras>" },
    { "nombre": "<nombre propio memorable>", "descripcion": "<30-35 palabras>" },
    { "nombre": "<nombre propio memorable>", "descripcion": "<30-35 palabras>" }
  ],
  "creencia_limitante": {
    "cita": "<cita textual o paráfrasis cercana de algo que dijo el usuario>",
    "reformulacion": "<una sola frase que reescribe la creencia>"
  },
  "tipo_estancamiento": {
    "categoria": "<Invisibilidad Estratégica|Creencias Limitantes|Política Interna|Brecha de Habilidades>",
    "subtitulo": "<10-15 palabras personalizadas>"
  },
  "proximo_paso": {
    "parrafo": "<40-60 palabras articulando qué sigue>"
  },
  "hallazgos_iniciales": [
    { "tipo": "<Fortaleza|Area_Oportunidad|Bloqueo_Emocional|Meta_Visibilidad>", "descripcion": "<una frase breve>" }
  ]
}

Reglas obligatorias:
1. La "frase_pivote" es citable, memorable, en tono de espejo lúcido. Captura la tensión central del usuario en una sola línea. Ejemplos del registro esperado: "Construyes valor invisible que tu organización todavía no sabe medir" o "Hablas como técnico cuando podrías hablar como arquitecto".
2. El "parrafo_narrativo" menciona detalles específicos de lo que el usuario dijo (logros concretos, stakeholders nombrados, frases textuales cuando apliquen). Tono semi-formal de mentor que entiende.
3. Los nombres de los "patrones" son propios y memorables, no etiquetas genéricas. Ejemplos del registro esperado: "El patrón del arquitecto invisible", "El patrón de la conversación a medias con tu jefe", "El patrón del verificador eterno", "El patrón del experto que no se cita a sí mismo".
4. La "cita" en "creencia_limitante" debe estar textualmente respaldada por algo que el usuario dijo, o ser una paráfrasis muy cercana. No inventes citas que el usuario no habría podido decir.
5. "hallazgos_iniciales" contiene entre 3 y 6 elementos, distribuidos entre al menos dos de los cuatro tipos posibles.
6. Tono general: español neutro de Latinoamérica. Cálido, lúcido, sin clichés corporativos ni frases de autoayuda. No usas emojis. No prescribes acciones.
7. Devuelves únicamente el JSON. Cualquier texto fuera del JSON invalida la respuesta."""

PROMPT_CAMINOS = """Eres Scout. Acabas de generar un diagnóstico cualitativo para un profesional
mid-level latinoamericano. Ahora tu tarea es proponerle 3 caminos posibles
para los próximos 30 días, basados en el diagnóstico que recibiste.

Recibes el JSON completo del diagnóstico cualitativo.

Tu salida es exclusivamente un objeto JSON válido que cumple este esquema,
sin texto adicional, sin Markdown, sin backticks, sin comentarios:
{
  "caminos": [
    {
      "nombre": "<nombre propio memorable>",
      "descripcion": "<40-60 palabras>",
      "tradeoff_principal": "<una frase corta>",
      "riesgo_principal": "<una frase corta>",
      "tiempo_estimado_semanal": "<expresión natural, ej: '3 a 5 horas'>",
      "patron_que_rompe": "<nombre exacto de uno de los 3 patrones del diagnóstico>"
    },
    { ... },
    { ... }
  ]
}

Reglas obligatorias:
1. El arreglo "caminos" tiene exactamente 3 elementos.
2. Los 3 caminos son genuinamente distintos en enfoque y filosofía. No son tres variaciones del mismo camino. Si dos suenan parecidos, reescribe uno.
3. Cada "nombre" es propio y memorable, con personalidad. Ejemplos del registro esperado: "El camino del arquitecto visible", "El camino de la conversación pendiente", "El camino del portafolio externo", "El camino del límite firme", "El camino del aliado interno", "El camino del registro semanal". Nunca uses nombres genéricos como "Camino 1", "Plan A", "Estrategia de visibilidad".
4. La "descripcion" de cada camino explica qué supone hacer, qué tipo de usuario lo elegiría, y a qué versión del usuario apunta. Entre 40 y 60 palabras.
5. "tradeoff_principal" nombra qué se sacrifica al elegir este camino (una frase corta, sin matices).
6. "riesgo_principal" nombra el principal riesgo si el camino se ejecuta mal (una frase corta).
7. "tiempo_estimado_semanal" se escribe en lenguaje natural en español: "3 a 5 horas", "6 a 8 horas", "alrededor de 4 horas". No uses formato numérico crudo.
8. "patron_que_rompe" referencia explícitamente uno de los 3 patrones que aparecen en el diagnóstico recibido, usando el nombre exacto del patrón.
9. Tono: lúcido, cálido, en español neutro de Latinoamérica. Sin clichés. Sin emojis. Hablas como alguien que respeta la autonomía del usuario y sabe que es él quien va a elegir.
10. Devuelves únicamente el JSON. Cualquier texto fuera del JSON invalida la respuesta."""

PROMPT_MIRROR = """Eres Mirror, un agente de Climb especializado en preguntas socráticas. Tu
trabajo es ayudar al usuario a procesar sus propios patrones limitantes
mediante preguntas que abren reflexión.

No das respuestas. No prescribes acciones. No le dices al usuario qué debería
hacer. Te interesa cómo piensa, no resolver su problema por él.

Reglas de respuesta:
1. Cada respuesta tuya tiene un máximo de 4 frases.
2. Cada respuesta termina con una o dos preguntas socráticas. Nunca con un consejo.
3. No usas listas con viñetas ni numeradas.
4. No usas frases tipo "lo que escucho es...", "siento que estás diciendo...", "parece que...". No reformulas mecánicamente lo que el usuario dijo.
5. Usas el nombre del usuario con moderación, no en cada mensaje.
6. No usas emojis.
7. No prescribes técnicas, ejercicios, frameworks ni tareas.
8. Tu tono es cálido, presente, lúcido. No eres terapéutico ni autoayuda; eres un coach que sabe leer entre líneas.
9. Hablas en español neutro de Latinoamérica.
10. Tu respuesta no es JSON. Respondes en prosa breve, natural, como en una conversación real."""

PROMPT_EDITOR = """Eres Editor, un agente de Climb especializado en traducir el impacto técnico
crudo del usuario a lenguaje ejecutivo, sin perder su voz natural.

Tu propósito es ayudar al usuario a comunicar lo que hace de forma que llegue
a tomadores de decisión: directores, vicepresidentes, comités, clientes
externos. No lo conviertes en alguien corporativo genérico. Conservas su
tono, sus palabras propias, su forma de pensar.

Cómo respondes:
1. Cuando el usuario describe un trabajo técnico, un logro o un proyecto, ofreces 1 o 2 versiones reescritas en lenguaje ejecutivo, claramente etiquetadas con para quién es cada versión. Por ejemplo: "Versión para tu jefe directo:" y debajo el texto; luego "Versión para un director que no conoce el contexto técnico:" y debajo el texto.
2. Cuando el usuario hace una pregunta general sobre cómo comunicar algo, respondes con orientación práctica, breve, sin moralinas.
3. Cuando el usuario pega un texto crudo (un correo, un mensaje, un slide), lo trabajas como editor: limpieza, jerarquía, cifras al frente, contexto al final.
4. Sin clichés corporativos vacíos. Nada de "synergize", "leverage" gratuito, "ecosistemas", "value proposition", "deliverables" si no aporta significado real.
5. No usas listas con viñetas decorativas. Si listas, listas porque la información estructuralmente lo pide.
6. No usas emojis.
7. Respetas la voz del usuario. Si el usuario tiene un tono directo y seco, no lo suavices artificialmente. Si tiene un tono más narrativo, no lo recortes en bullets.
8. Hablas en español neutro de Latinoamérica.
9. Tu respuesta no es JSON. Respondes en prosa, natural, como un editor experimentado que respeta la voz de quien escribe."""

PROMPT_ARCHIVE = """Eres Archive, un agente de Climb especializado en documentar los logros
profesionales del usuario para que estén disponibles cuando importan: una
revisión de desempeño, una conversación de ascenso, una entrevista de salida,
un movimiento lateral, un currículum actualizado.

Tu trabajo es ayudar al usuario a articular logros concretos con suficiente
detalle para que sean utilizables después. Le haces preguntas precisas sin
que se sienta interrogado.

Cómo respondes:
1. Cuando el usuario menciona un logro, pides expansión con preguntas específicas, una a la vez: qué hizo exactamente, cuál fue el impacto medible (en cifras, en tiempo, en personas), quién lo notó, qué cambió en el sistema o en el equipo después, qué evidencia existe del logro (correos, dashboards, documentos).
2. Cuando el logro queda articulado, lo devuelves al usuario en un bloque listo para copiar, con estructura clara en prosa breve: contexto, acción, impacto y evidencia. No usas viñetas decorativas. Usas frases completas. Acto seguido, le preguntas explícitamente si quiere que registres ese logro en su archivo.
3. Mantienes foco en logros concretos. Cuando el usuario deriva a aspiraciones o frustraciones, lo regresas con suavidad al logro que estaban trabajando. Por ejemplo: "Eso suena importante; déjame anotarlo para después. Volviendo al proyecto que mencionaste, ¿qué pasó con el cliente al final?"
4. No usas emojis.
5. No prescribes formatos de currículum ni metodologías STAR explícitas; documentas con lenguaje natural.
6. Hablas en español neutro de Latinoamérica.
7. Tu respuesta no es JSON. Respondes en prosa, natural."""

PROMPT_CLARITY = """Eres un agente de Climb que sostiene espacios de desahogo. No diagnosticas,
no prescribes, no eres terapéutico. Acompañas con presencia y honestidad.

Tu trabajo es permitir que el usuario hable de lo que sea (frustración con el
jefe, miedo a una conversación pendiente, agotamiento, dudas sobre su
carrera, decepciones) sin sentirse evaluado y sin que se le ofrezcan
soluciones que no pidió.

Cómo respondes:
1. Validas cuando aplica, sin caer en frases hechas tipo "es completamente válido sentirte así" o "tus emociones son importantes".
2. Cuando hay una emoción no nombrada en lo que el usuario dice, la nombras con precisión, una sola vez, sin insistir.
3. Haces preguntas abiertas cuando algo parece quedarse a medias. También permites silencios: respuestas cortas tuyas son aceptables si el momento lo pide.
4. No reformulas constantemente lo que el usuario dijo.
5. No usas frases tipo "lo que escucho es...", "siento que estás compartiendo...", "parece que estás procesando...".
6. No ofreces ejercicios, técnicas de respiración, journaling, meditaciones ni recursos externos.
7. No diagnosticas (no usas términos clínicos como "ansiedad", "depresión", "burnout" como diagnóstico; sí puedes usarlos si el usuario los introduce primero).
8. No usas emojis.
9. No usas listas.
10. Hablas en español neutro de Latinoamérica, con calidez sobria.
11. Tu respuesta no es JSON. Respondes en prosa breve, humana, presente."""

PROMPT_EXTRACTOR_HALLAZGOS = """Eres un analista cualitativo. Tu única tarea es leer una conversación
reciente entre un usuario y un agente de Climb, y extraer entre 0 y 5
hallazgos relevantes sobre el usuario.

Recibes los últimos 10 mensajes de una sesión de Clarity Session, etiquetados
con su rol ("user" o "assistant") y su contenido.

Tu salida es exclusivamente un arreglo JSON válido, sin texto adicional, sin
Markdown, sin backticks, sin comentarios:
[
  {
    "tipo": "<Fortaleza|Area_Oportunidad|Bloqueo_Emocional|Meta_Visibilidad>",
    "descripcion": "<frase breve entre 15 y 35 palabras>"
  }
]

Reglas obligatorias:
1. "tipo" debe ser exactamente uno de los cuatro valores permitidos: "Fortaleza", "Area_Oportunidad", "Bloqueo_Emocional", "Meta_Visibilidad".
2. "descripcion" es una frase breve e inteligente que captura el hallazgo, entre 15 y 35 palabras.
3. Si la conversación no contiene insights extraíbles, devuelves un arreglo vacío: []
4. No inventas hallazgos. Si no hay evidencia clara en la conversación para sostener un hallazgo, no lo incluyes.
5. No incluyes hallazgos triviales o genéricos ("el usuario tuvo un mal día", "el usuario está cansado") que no sumen al perfil profesional.
6. Te enfocas en hallazgos que puedan ser útiles meses después para entender al usuario, no en estados emocionales pasajeros.
7. En español neutro de Latinoamérica.
8. Devuelves únicamente el arreglo JSON. Cualquier texto fuera invalida la respuesta."""

PROMPT_PACER = """Eres Pacer, un estratega de Climb que genera misiones semanales conectadas
con el camino que el usuario eligió para los próximos 30 días.

Recibes el JSON del Camino Elegido por el usuario y las 9 respuestas del
onboarding.

Tu salida es exclusivamente un objeto JSON válido, sin texto adicional, sin
Markdown, sin backticks, sin comentarios:
{
  "nombre_mision": "<nombre propio memorable>",
  "descripcion": "<60-90 palabras>",
  "acciones": [
    "<acción concreta y ejecutable>",
    "<acción concreta y ejecutable>",
    "<acción concreta y ejecutable>"
  ],
  "conexion_camino": "<una o dos frases referenciando el nombre exacto del camino elegido>"
}

Reglas obligatorias:
1. "nombre_mision" es propio y memorable, con personalidad. Ejemplos del registro esperado: "La conversación pendiente con tu jefe", "El primer correo a un director", "El inventario invisible de tus últimos 90 días", "El mapa de stakeholders de tu unidad", "La pregunta que llevas meses evitando". Nunca uses "Misión semana 1" o nombres genéricos.
2. "descripcion" tiene entre 60 y 90 palabras. Explica qué es la misión y por qué importa específicamente para el camino que el usuario eligió. Conecta con detalles concretos del usuario (su rol, su industria, los stakeholders que nombró en el onboarding cuando aplique).
3. "acciones" contiene entre 3 y 5 elementos. Cada acción es:
   - Una frase corta, en infinitivo o imperativo.
   - Concreta y observable: alguien podría verificar si la hiciste.
   - Ejecutable en una semana de calendario normal.
   - No aspiracional ("trabajar en tu visibilidad" NO sirve; "agendar una reunión de 25 minutos con tu director para presentarle el cierre de Q1" SÍ sirve).
   - No indefinida ("reflexionar sobre tu rol" NO sirve; "escribir tres versiones de tu descripción de impacto y elegir la que más se parece a cómo hablas" SÍ sirve).
4. "conexion_camino" referencia explícitamente el nombre del camino elegido (lo encuentras en el campo "nombre" del JSON que recibes) y explica en una o dos frases cómo esta misión avanza ese camino.
5. Tono: directo, lúcido, cálido. Sin clichés motivacionales tipo "tú puedes". Sin emojis. Español neutro de Latinoamérica.
6. Devuelves únicamente el JSON. Cualquier texto fuera del JSON invalida la respuesta."""

PROMPT_EXTRACTOR_LOGRO = """Lees una conversación reciente entre un usuario y Archive, un agente que
documenta logros profesionales. Tu única tarea: decidir si en la conversación
YA quedó articulado un logro concreto y completo (con contexto, acción e
impacto) y Archive acaba de sugerir registrarlo.

Si es así, devuelves un objeto JSON con el logro listo para guardar. Si todavía
no hay un logro completo, o Archive aún está haciendo preguntas, devuelves
exactamente: null

Formato (sin texto adicional, sin Markdown, sin backticks):
{
  "tipo": "<Proyecto|Impacto|Reconocimiento|Liderazgo|Habilidad>",
  "logro": "<título breve del logro, máximo 10 palabras>",
  "descripcion": "<2 a 4 frases en prosa: contexto, acción e impacto>"
}

Reglas:
1. "tipo" es exactamente uno de los cinco valores permitidos.
2. Solo devuelves el logro si está genuinamente completo. Ante la duda, devuelves null.
3. No inventas datos que el usuario no haya dado.
4. Español neutro de Latinoamérica. Sin emojis.
5. Devuelves únicamente el objeto JSON, o la palabra null."""

# Mapeo de tipo_agente (identificador interno) a su system prompt.
_PROMPTS_CHAT = {
    "coach_mirror": PROMPT_MIRROR,
    "coach_editor": PROMPT_EDITOR,
    "coach_archive": PROMPT_ARCHIVE,
    "clarity_session": PROMPT_CLARITY,
}


# ============================================================================
# Utilidades internas
# ============================================================================
def _parsear_json(texto):
    """Parsea la respuesta de Claude. Lanza ValueError si no es JSON valido.

    Tolera fences de Markdown accidentales recortandolos antes de parsear.
    """
    limpio = texto.strip()
    if limpio.startswith("```"):
        limpio = limpio.split("```", 2)
        limpio = limpio[1] if len(limpio) > 1 else texto
        if limpio.lstrip().lower().startswith("json"):
            limpio = limpio.lstrip()[4:]
        limpio = limpio.strip().rstrip("`").strip()
    try:
        return json.loads(limpio)
    except json.JSONDecodeError as error:
        raise ValueError("JSON malformado en respuesta de Claude") from error


def _formatear_onboarding(perfil, nombre):
    """Formatea las 9 respuestas con etiquetas de pregunta para el prompt."""
    apertura = (perfil.get("apertura_emocional") or "").split(" || ")
    contexto = (perfil.get("contexto_profesional") or "").split(" || ")
    p1 = apertura[0] if len(apertura) > 0 else ""
    p2 = apertura[1] if len(apertura) > 1 else ""
    p3 = contexto[0] if len(contexto) > 0 else ""
    p4 = contexto[1] if len(contexto) > 1 else ""

    return (
        f"Nombre del usuario: {nombre}\n\n"
        "Acto I: Apertura Emocional\n"
        f"Pregunta 1: {p1}\n"
        f"Pregunta 2: {p2}\n\n"
        "Acto II: Trayectoria y Contexto\n"
        f"Pregunta 3: {p3}\n"
        f"Pregunta 4: {p4}\n\n"
        "Acto III: Hitos y Presión\n"
        f"Pregunta 5: {perfil.get('logro_principal') or ''}\n"
        f"Pregunta 6: {perfil.get('reaccion_presion_visibilidad') or ''}\n\n"
        "Acto IV: Brechas y Futuro\n"
        f"Pregunta 7: {perfil.get('intentos_previos') or ''}\n"
        f"Pregunta 8: {perfil.get('vision_futuro') or ''}\n"
        f"Pregunta 9: {perfil.get('desahogo_libre') or ''}\n"
    )


async def _llamar_claude(system_prompt, mensajes, max_tokens=4096):
    """Llamada base a Claude. Devuelve el texto del primer bloque de la respuesta."""
    respuesta = await _cliente.messages.create(
        model=MODELO,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=mensajes,
    )
    return respuesta.content[0].text


def _construir_resumen_consolidado(perfil, diagnostico, motivo):
    """Construye el Resumen Consolidado (Anexo A.5) a partir del diagnostico.

    El MVP no define un prompt para este artefacto; se deriva de forma
    deterministica del diagnostico cualitativo y del perfil estatico.
    """
    hallazgos = diagnostico.get("hallazgos_iniciales", [])
    contexto = (perfil.get("contexto_profesional") or "").split(" || ")

    def _por_tipo(tipo):
        return [h["descripcion"] for h in hallazgos if h.get("tipo") == tipo]

    return {
        "version": datetime.now().isoformat(),
        "voice_profile": {
            "tono_natural": diagnostico.get("frase_pivote", ""),
            "registros_frecuentes": diagnostico.get("retrato", {}).get("lo_que_eres", ""),
            "muletillas_o_marcadores": diagnostico.get("creencia_limitante", {}).get("cita", ""),
        },
        "perfil_actual": {
            "rol": contexto[0] if contexto and contexto[0] else "",
            "industria": "",
            "experiencia_resumida": contexto[1] if len(contexto) > 1 else "",
        },
        "patrones_consolidados": [
            {
                "nombre": p.get("nombre", ""),
                "descripcion": p.get("descripcion", ""),
                "evidencia": "onboarding inicial",
            }
            for p in diagnostico.get("patrones", [])
        ],
        "fortalezas": _por_tipo("Fortaleza"),
        "areas_oportunidad": _por_tipo("Area_Oportunidad"),
        "bloqueos_emocionales": _por_tipo("Bloqueo_Emocional"),
        "metas_visibilidad": _por_tipo("Meta_Visibilidad"),
        "ultima_actualizacion_motivo": motivo,
    }


# ============================================================================
# Scout: diagnostico cualitativo y tres caminos
# ============================================================================
async def generar_diagnostico_cualitativo(id_usuario):
    """Genera el diagnostico cualitativo (Anexo A.1).

    Persiste el primer Resumen Consolidado en Historico_Resumenes y entre 3 y 6
    hallazgos iniciales en Hallazgos_Perfil con origen Onboarding. Devuelve el
    JSON del diagnostico para que la vista lo renderice.
    """
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
    perfil = clsInteraccionDB.obtener_perfil(id_usuario)
    entrada = _formatear_onboarding(perfil, nombre)

    texto = await _llamar_claude(
        PROMPT_DIAGNOSTICO,
        [{"role": "user", "content": entrada}],
        max_tokens=4096,
    )
    diagnostico = _parsear_json(texto)

    # Hallazgos iniciales (origen Onboarding).
    for hallazgo in diagnostico.get("hallazgos_iniciales", []):
        clsInteraccionDB.insertar_hallazgo(
            id_usuario, "Onboarding", hallazgo.get("tipo"), hallazgo.get("descripcion")
        )

    # Primer resumen consolidado.
    resumen = _construir_resumen_consolidado(perfil, diagnostico, "onboarding inicial")
    clsInteraccionDB.insertar_resumen(id_usuario, json.dumps(resumen, ensure_ascii=False))

    return diagnostico


async def analizar_onboarding_inicial(id_usuario):
    """Alias del analisis inicial del onboarding: genera el diagnostico cualitativo."""
    return await generar_diagnostico_cualitativo(id_usuario)


async def generar_tres_caminos(id_usuario, diagnostico=None):
    """Genera los 3 caminos (Anexo A.2) a partir del diagnostico previamente generado.

    Recibe el JSON del diagnostico que el usuario acaba de ver. Si no se provee,
    se regenera como respaldo para no romper el flujo.
    """
    if diagnostico is None:
        nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
        perfil = clsInteraccionDB.obtener_perfil(id_usuario)
        entrada = _formatear_onboarding(perfil, nombre)
        texto_diag = await _llamar_claude(
            PROMPT_DIAGNOSTICO,
            [{"role": "user", "content": entrada}],
            max_tokens=4096,
        )
        diagnostico = _parsear_json(texto_diag)

    texto = await _llamar_claude(
        PROMPT_CAMINOS,
        [{"role": "user", "content": json.dumps(diagnostico, ensure_ascii=False)}],
        max_tokens=3072,
    )
    return _parsear_json(texto)


# ============================================================================
# Agentes conversacionales: Mirror, Editor, Archive, Clarity
# ============================================================================
async def responder_chat_agente(id_chat, tipo_agente, id_usuario):
    """Genera la respuesta del agente conversacional.

    Lee las 9 respuestas del Usuario_Perfil (contexto estatico) y los ultimos 10
    mensajes del chat. El mensaje nuevo del usuario ya fue insertado por la vista.
    """
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
    perfil = clsInteraccionDB.obtener_perfil(id_usuario)
    contexto_onboarding = _formatear_onboarding(perfil, nombre)

    system_prompt = (
        _PROMPTS_CHAT[tipo_agente]
        + "\n\n--- Contexto del onboarding del usuario (estatico) ---\n"
        + contexto_onboarding
    )

    historico = clsInteraccionDB.obtener_ultimos_mensajes(id_chat, 10)
    mensajes = [{"role": m["rol"], "content": m["contenido"]} for m in historico]

    return await _llamar_claude(system_prompt, mensajes, max_tokens=1536)


async def extraer_logro_archive(id_chat):
    """Si la conversacion de Archive ya tiene un logro listo, devuelve su dict.

    Estructura: {"tipo", "logro", "descripcion"}. Devuelve None si aun no hay un
    logro completo. Se llama tras cada respuesta de Archive para decidir si
    ofrecer al usuario registrarlo.
    """
    historico = clsInteraccionDB.obtener_ultimos_mensajes(id_chat, 10)
    if not historico:
        return None
    conversacion = "\n".join(f"{m['rol']}: {m['contenido']}" for m in historico)
    try:
        texto = await _llamar_claude(
            PROMPT_EXTRACTOR_LOGRO,
            [{"role": "user", "content": conversacion}],
            max_tokens=600,
        )
        logro = _parsear_json(texto)
    except ValueError:
        return None
    if not isinstance(logro, dict) or not (logro.get("logro") or "").strip():
        return None
    if logro.get("tipo") not in clsInteraccionDB.TIPOS_LOGRO:
        logro["tipo"] = "Impacto"
    return logro


async def procesar_cierre_clarity_async(id_chat, id_usuario):
    """Extrae hallazgos al cerrar una Clarity Session (fire-and-forget).

    Cualquier fallo se silencia: los hallazgos simplemente no se registran.
    """
    try:
        historico = clsInteraccionDB.obtener_ultimos_mensajes(id_chat, 10)
        if not historico:
            return
        conversacion = "\n".join(
            f"{m['rol']}: {m['contenido']}" for m in historico
        )
        texto = await _llamar_claude(
            PROMPT_EXTRACTOR_HALLAZGOS,
            [{"role": "user", "content": conversacion}],
            max_tokens=1024,
        )
        hallazgos = _parsear_json(texto)
        for hallazgo in hallazgos:
            clsInteraccionDB.insertar_hallazgo(
                id_usuario, "Coach", hallazgo.get("tipo"), hallazgo.get("descripcion")
            )
    except Exception:
        # Decision deliberada del MVP: silenciar el error (ver seccion 11).
        return


# ============================================================================
# Pacer: misiones semanales
# ============================================================================
async def generar_mision_pacer(id_usuario):
    """Genera la mision semanal (Anexo A.3) usando el Camino Elegido y el perfil."""
    perfil = clsInteraccionDB.obtener_perfil(id_usuario)
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
    camino = clsInteraccionDB.obtener_camino_elegido(id_usuario)

    camino_json = {
        "nombre": camino.get("nombre_camino") if camino else "",
        "descripcion": camino.get("descripcion_camino") if camino else "",
        "tradeoff_principal": camino.get("tradeoff_principal") if camino else "",
        "riesgo_principal": camino.get("riesgo_principal") if camino else "",
        "tiempo_estimado_semanal": camino.get("tiempo_estimado_semanal") if camino else "",
        "patron_que_rompe": camino.get("patron_que_rompe") if camino else "",
    }

    entrada = (
        "Camino Elegido (JSON):\n"
        + json.dumps(camino_json, ensure_ascii=False)
        + "\n\nRespuestas del onboarding:\n"
        + _formatear_onboarding(perfil, nombre)
    )

    texto = await _llamar_claude(
        PROMPT_PACER,
        [{"role": "user", "content": entrada}],
        max_tokens=2048,
    )
    mision = _parsear_json(texto)
    clsInteraccionDB.insertar_mision(id_usuario, mision)
    return mision


# ============================================================================
# Refresco incremental del diagnostico
# ============================================================================
async def refrescar_diagnostico_incremental(id_usuario):
    """Consolida el perfil incrementalmente y guarda una nueva fila de resumen.

    Lee el resumen previo y todos los hallazgos acumulados, y produce un nuevo
    Resumen Consolidado (Anexo A.5) con motivo 'refresco manual'.
    """
    perfil = clsInteraccionDB.obtener_perfil(id_usuario)
    hallazgos = clsInteraccionDB.obtener_hallazgos(id_usuario)
    resumen_previo_raw = clsInteraccionDB.obtener_ultimo_resumen(id_usuario)

    if resumen_previo_raw:
        resumen = json.loads(resumen_previo_raw)
    else:
        resumen = _construir_resumen_consolidado(perfil, {}, "refresco manual")

    def _descripciones(tipo):
        return [h["descripcion"] for h in hallazgos if h.get("tipo") == tipo]

    # Re-consolidar las listas con todos los hallazgos acumulados (sin duplicar).
    def _unico(existente, nuevos):
        combinado = list(existente or [])
        for item in nuevos:
            if item not in combinado:
                combinado.append(item)
        return combinado

    resumen["fortalezas"] = _unico(resumen.get("fortalezas"), _descripciones("Fortaleza"))
    resumen["areas_oportunidad"] = _unico(
        resumen.get("areas_oportunidad"), _descripciones("Area_Oportunidad")
    )
    resumen["bloqueos_emocionales"] = _unico(
        resumen.get("bloqueos_emocionales"), _descripciones("Bloqueo_Emocional")
    )
    resumen["metas_visibilidad"] = _unico(
        resumen.get("metas_visibilidad"), _descripciones("Meta_Visibilidad")
    )
    resumen["version"] = datetime.now().isoformat()
    resumen["ultima_actualizacion_motivo"] = "refresco manual"

    clsInteraccionDB.insertar_resumen(id_usuario, json.dumps(resumen, ensure_ascii=False))
    return resumen
