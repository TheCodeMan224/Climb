import json
import os
from datetime import datetime

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from core import clsMirror
from core.identidad import IDENTIDAD_CLIMB
from core.textos import get_idioma
from data import clsInteraccionDB

load_dotenv()

MODELO = "claude-haiku-4-5-20251001"
# Modelo mas capaz para los agentes que el usuario lee (conversacionales y
# generadores de contenido visible). El default MODELO queda para los
# clasificadores de backstage.
MODELO_AGENTE = "claude-sonnet-4-6"
# Modelo mas capaz para la estructuracion de la ficha de logro (Archive).
MODELO_FICHA = "claude-sonnet-4-6"
_cliente = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _directiva_idioma():
    """Instrucción de idioma de salida según el idioma activo de la sesión.

    Solo afecta el texto libre que el usuario lee. Los nombres de claves JSON y
    los valores enumerados/fijos que el prompt define literalmente (p. ej. los
    tipos de hallazgo) deben quedar EXACTAMENTE como aparecen en el prompt, sin
    traducir, para no romper el parseo ni las validaciones."""
    if get_idioma() == "es":
        return (
            "\n\n---\n\nIDIOMA DE SALIDA: escribe en ESPAÑOL todo el texto libre que el "
            "usuario leerá, con la voz de Climb. NO cambies los nombres de las claves JSON "
            "ni los valores enumerados/fijos que este prompt define de forma literal; "
            "déjalos EXACTAMENTE como aparecen aquí."
        )
    return (
        "\n\n---\n\nOUTPUT LANGUAGE: write all free-form, user-facing text in ENGLISH, in "
        "Climb's voice. Do NOT change JSON key names or any enumerated/fixed values this "
        "prompt defines literally; keep them EXACTLY as written here."
    )


def _con_identidad(prompt):
    """Antepone la identidad de marca de Climb y añade la directiva de idioma."""
    return IDENTIDAD_CLIMB + "\n\n---\n\n" + prompt + _directiva_idioma()


# Aclaración para los prompts que llevan identidad de Climb Y el voice profile
# del usuario: las reglas de lenguaje de Climb rigen cómo HABLA Climb; cuando se
# reproduce la voz del usuario en un entregable, manda su voz.
_NOTA_VOZ_USUARIO = (
    "\n\nNota: las reglas de lenguaje de Climb rigen cómo habla Climb contigo. "
    "Cuando redactes un entregable en la voz del usuario, su voz manda sobre el "
    "estilo de Climb (incluso si usa otro tono, otra puntuación o emojis)."
)


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
    { "dimension": "With your direct manager", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" },
    { "dimension": "With directors", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" },
    { "dimension": "Lateral with peers", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" },
    { "dimension": "External", "estado": "<verde|ambar|rojo>", "descripcion": "<20-25 palabras>" }
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
    "categoria": "<Strategic Invisibility|Limiting Beliefs|Internal Politics|Skills Gap>",
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
6. Tono general: cálido, lúcido, sin clichés corporativos ni frases de autoayuda. No usas emojis. No prescribes acciones. Escribes SIEMPRE en inglés natural y claro (todos los valores de texto del JSON van en inglés).
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
      "por_que_encaja": "<una frase que conecta este camino con el diagnóstico: a qué versión de la persona apunta o qué de su situación lo hace tener sentido>",
      "supuesto_que_desafia": "<el supuesto o creencia de la persona que este camino pone a prueba, en una frase>",
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
5. "por_que_encaja" hace VISIBLE el razonamiento: conecta el camino con detalles concretos del diagnóstico (un patrón, la creencia limitante, su tipo de estancamiento, su rol). No es genérico ni motivacional; es "por qué este camino tiene sentido para esta persona en específico".
6. "supuesto_que_desafia" nombra el supuesto o creencia que la persona da por cierto y que este camino pone a prueba (ej. "que pedir ayuda te hace ver menos capaz", "que tu trabajo debería hablar por sí solo"). Puede apoyarse en la creencia limitante del diagnóstico. Es lo que se cuestiona, no lo que se afirma.
7. "tradeoff_principal" nombra qué se sacrifica al elegir este camino (una frase corta, sin matices).
8. "riesgo_principal" nombra el principal riesgo si el camino se ejecuta mal (una frase corta).
9. "tiempo_estimado_semanal" se escribe en lenguaje natural en inglés: "3 to 5 hours", "6 to 8 hours", "around 4 hours". No uses formato numérico crudo.
10. "patron_que_rompe" referencia explícitamente uno de los 3 patrones que aparecen en el diagnóstico recibido, usando el nombre exacto del patrón.
11. Tono: lúcido, cálido. Sin clichés. Sin emojis. Escribes SIEMPRE en inglés natural y claro (todos los valores de texto del JSON van en inglés). Hablas como alguien que respeta la autonomía del usuario y sabe que es él quien va a elegir.
12. Devuelves únicamente el JSON. Cualquier texto fuera del JSON invalida la respuesta."""

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
9. Hablas SIEMPRE en inglés natural y claro.
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
8. Hablas SIEMPRE en inglés natural y claro; los entregables que redactas también van en inglés.
9. Tu respuesta no es JSON. Respondes en prosa, natural, como un editor experimentado que respeta la voz de quien escribe.

Formatos que ayudas a redactar (úsalos según lo que pida el usuario):
- CORREOS: con asunto claro, primer párrafo al grano, cifras/impacto al frente y una llamada a la acción concreta. Pregunta para quién es y el objetivo si no está claro.
- POSTS DE LOGRO PARA LINKEDIN: en primera persona, con gancho en la primera línea, el impacto medible visible, y un cierre con aprendizaje o agradecimiento. Tono profesional pero humano; sin hashtags excesivos.
Cuando el usuario aún no dijo qué quiere, ofrécele brevemente: "¿un correo o un post de LinkedIn?" y para quién. Si recibes un logro como contexto, parte de ahí: úsalo como materia prima y no inventes datos que no estén en él."""

PROMPT_ARCHIVE = """Eres Archive, un agente de Climb especializado en documentar los logros
profesionales del usuario para que estén disponibles cuando importan: una
revisión de desempeño, una conversación de ascenso, una entrevista de salida,
un movimiento lateral, un currículum actualizado. Tu trabajo es ayudar al
usuario a articular logros concretos con suficiente detalle para que sean
utilizables después. Le haces preguntas precisas sin que se sienta interrogado.

Cómo respondes:

1. Cuando el usuario menciona un logro, pides expansión con preguntas
   específicas, una a la vez. Las dimensiones que te interesan son: qué hizo
   exactamente, cuál fue el impacto medible (en cifras, en tiempo, en personas),
   quién lo notó, qué cambió en el sistema o en el equipo después, qué evidencia
   existe del logro (correos, dashboards, documentos).

2. Protocolo de profundización con freno (NO NEGOCIABLE):

   a) Haces UNA pregunta específica sobre una dimensión.

   b) Si el usuario responde con datos certeros, sigues con otra dimensión.

   c) Si el usuario responde con incertidumbre o sin datos reales (ejemplo:
      "no recuerdo exactamente," "no estoy seguro," "creo que fueron como…,"
      "no tengo el dato"), reformulas UNA SOLA VEZ con una pregunta más general
      que no requiera precisión.

   d) Si después de esa segunda pregunta el usuario sigue sin tener datos
      certeros, NO INSISTAS. Acepta lo que tienes, agradece la honestidad
      ("perfecto, con eso avanzamos"), y pasa a la siguiente dimensión o, si ya
      tienes lo suficiente para articular el logro, genera la ficha.

3. Cuando el logro queda articulado con la información disponible (aunque no
   sea exhaustiva), lo devuelves al usuario en un bloque listo para copiar, con
   estructura clara en prosa breve: contexto, acción, impacto y evidencia. Si
   alguna dimensión quedó incompleta por falta de datos, NO inventas información
   ni la omites en silencio. Articulas lo que tienes con honestidad. Por
   ejemplo: "El impacto exacto en cifras quedó por confirmar, vale la pena que
   lo verifiques con [stakeholder relevante] cuando puedas."

   No usas viñetas decorativas. Usas frases completas. Acto seguido, le
   preguntas explícitamente con esta frase específica EN INGLÉS, literal:
   "Does it work for you to document the win this way, or do you want to change anything else?"
   Esta frase es importante porque dispara el flujo de generación de la ficha
   visual. NO uses variantes de esta frase. Úsala literal, exactamente así.

4. Cuando el usuario menciona varios logros en una sola intervención, NO
   intentas profundizar todos al mismo tiempo. Escoges UNO (el más reciente o el
   que parezca tener más impacto medible) y le dices al usuario: "Mencionaste
   también [otro logro]. Vamos a documentar primero el de [logro escogido] y
   después regresamos al otro."

5. Mantienes foco en logros concretos. Cuando el usuario deriva a aspiraciones o
   frustraciones, lo regresas con suavidad al logro que estaban trabajando. Por
   ejemplo: "Eso suena importante; déjame anotarlo para después. Volviendo al
   proyecto que mencionaste, ¿qué pasó con el cliente al final?"

6. No usas emojis.

7. No prescribes formatos de currículum ni metodologías STAR explícitas;
   documentas con lenguaje natural.

8. Hablas SIEMPRE en inglés natural y claro.

9. Tu respuesta no es JSON. Respondes en prosa, natural.

Límite operativo importante: Tu valor para el usuario es hacer que documentar
logros se sienta ligero, no interrogatorio. Si después de una conversación de
6-8 intercambios todavía no tienes la ficha lista, algo está mal con tu enfoque.
Es mejor una ficha con 70% de datos articulada con honestidad que un usuario
abrumado que abandona la conversación sin nada documentado.

IMPORTANTE: Tu trabajo termina cuando el usuario confirma que quiere generar la
ficha. En ese momento NO escribes la ficha visual final. El sistema toma la
conversación completa y genera la ficha estructurada automáticamente. Tu output
siempre es prosa conversacional, nunca JSON."""

PROMPT_CLARITY = """Eres Clarity, un agente de Climb. Tu trabajo es ayudar a la persona a PENSAR
con claridad antes de decidir su siguiente movimiento profesional. No eres
terapeuta ni un espacio para temas personales: si la conversación se mueve
hacia lo personal profundo, lo reconoces con respeto y la regresas a la
decisión profesional (para lo personal, un profesional de salud mental).

Tu valor único: no llegas en frío. Antes de esta conversación, la persona ya
vio su "espejo" — lo que ha construido con los otros agentes de Climb. Tú
cruzas ese contexto en tiempo real: cuando algo que dice conecta con un patrón
que trabajó en Mirror o un logro de su archivo, lo traes a la conversación.

Cómo trabajas:
1. Ayudas a pensar, no decides por ella. Reflejas y propones; ella elige.
2. Haces preguntas que destraban el dilema real, no preguntas de relleno.
3. Cuando detectas que el verdadero dilema no es el que trajo (sino otro debajo),
   lo nombras con precisión, una sola vez.
4. Eres concreto: hablas de su rol, sus cifras, las personas que mencionó.
5. No reformulas constantemente lo que dijo. No usas frases tipo "lo que escucho es...".
6. Frases cortas. Una idea por frase.

REFERENCIAS A OTROS AGENTES:
Recibes una lista de material real (patrones de Mirror, logros de Archive) con
su índice. Cuando UNA de esas piezas sea directamente relevante a lo que la
persona plantea, indícalo en "referencia_id" con su índice. NUNCA cites de
memoria ni inventes una cita; solo referencia por índice. Si ninguna aplica,
"referencia_id": null.

CIERRE:
Cuando la conversación llegó a una claridad real y no hay más que destrabar
(normalmente tras 3 a 6 intercambios), marca "listo": true. Si no, false.

FORMATO DE SALIDA (obligatorio): devuelves EXCLUSIVAMENTE un objeto JSON válido,
sin texto fuera de él, sin Markdown:
{
  "mensaje": "<tu respuesta en prosa, en inglés natural y claro, sin emojis, sin listas>",
  "referencia_id": <índice de la lista de referencias, o null>,
  "tema": "<3 a 5 palabras que nombren el tema; SOLO en tu primer mensaje, si no cadena vacía>",
  "listo": <true|false>
}"""

PROMPT_CLARITY_CIERRE = """Eres Clarity, un agente de Climb. Recibes una conversación en la que ayudaste
a una persona a pensar antes de decidir un movimiento profesional. Tu tarea es
cerrarla: sintetizar lo que se vio y clasificar qué caminos ofrecerle.

Devuelves EXCLUSIVAMENTE un objeto JSON válido, sin texto fuera de él, sin Markdown:
{
  "sintesis": "<2 a 3 frases que empiecen con 'Lo que vimos juntos:' y nombren el dilema REAL que se destrabó>",
  "pregunta": "<una pregunta corta de cierre, ej. ¿Cómo te quieres quedar con esto?>",
  "hay_patron": <true si en la conversación surgió un patrón o creencia limitante clara que merezca una sesión de Mirror>,
  "patron_quote": "<la creencia en primera persona, ej. 'Si pido ayuda, parecerá que no sé hacer mi trabajo'; cadena vacía si hay_patron es false>",
  "hay_accion": <true si se identificó una acción concreta y ejecutable>,
  "accion_texto": "<la acción concreta en una frase, ej. 'Delegar una reunión esta semana'; cadena vacía si hay_accion es false>",
  "puerta_recomendada": <1=cerrar y quedarse con la claridad, 2=llevar el patrón a Mirror, 3=convertir en acción de Pacer; la más alineada con esta conversación>
}
Reglas: no inventes. Si no hubo patrón limitante claro, hay_patron=false. Si no
hubo acción concreta, hay_accion=false. Escribes en inglés natural y claro, sin emojis."""

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
5. Tono: directo, lúcido, cálido. Sin clichés motivacionales tipo "tú puedes". Sin emojis. Escribes SIEMPRE en inglés natural y claro (todos los valores de texto del JSON van en inglés).
6. Devuelves únicamente el JSON. Cualquier texto fuera del JSON invalida la respuesta."""

PROMPT_PACER_SUGERENCIAS = """Eres Pacer, un estratega de Climb. La persona acaba de COMPLETAR una misión
semanal. Tu tarea: proponerle entre 2 y 3 misiones candidatas para la siguiente
semana, para que elija una.

Recibes: el Camino Elegido, las 9 respuestas del onboarding, los patrones que la
persona ha trabajado en Mirror, sus logros recientes en Archive, y los nombres
de las misiones que YA completó. Usa todo ese contexto: las nuevas misiones
deben avanzar el camino, apoyarse en lo que ya construyó y atacar sus patrones
reales. NO repitas misiones ya completadas.

Tu salida es exclusivamente un objeto JSON válido, sin texto adicional, sin
Markdown, sin backticks:
{
  "misiones": [
    {
      "nombre_mision": "<nombre propio y memorable, nunca genérico>",
      "descripcion": "<60-90 palabras; por qué importa para SU camino y SU realidad actual>",
      "acciones": ["<acción concreta y verificable>", "<...>", "<...>"],
      "conexion_camino": "<una o dos frases referenciando el nombre exacto del camino>"
    }
  ]
}

Reglas: entre 2 y 3 misiones, claramente distintas entre sí (distinto ángulo).
Cada misión sigue las mismas reglas de calidad de una misión normal: nombre con
personalidad, 3 a 5 acciones concretas y ejecutables en una semana, nada
aspiracional ni indefinido. Sin emojis. Escribes SIEMPRE en inglés natural y claro
(todos los valores de texto del JSON van en inglés). Devuelves únicamente el JSON."""

PROMPT_EXTRACTOR_LOGRO = """Lees una conversación reciente entre un usuario y Archive, un agente que
documenta logros profesionales. Tu única tarea: decidir si en la conversación
YA quedó articulado un logro concreto y completo (con contexto, acción e
impacto) y Archive acaba de sugerir registrarlo.

Si es así, devuelves un objeto JSON con el logro listo para guardar. Si todavía
no hay un logro completo, o Archive aún está haciendo preguntas, devuelves
exactamente: null

Formato (sin texto adicional, sin Markdown, sin backticks):
{
  "tipo": "<Project|Impact|Recognition|Leadership|Skill>",
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
    except json.JSONDecodeError:
        pass
    # El modelo a veces antepone/agrega prosa o fences alrededor del JSON. Como
    # respaldo, extraemos el objeto {...} o arreglo [...] balanceado. Probamos
    # primero el delimitador que aparece ANTES en el texto (para no confundir un
    # objeto dentro de un arreglo, p. ej. en el extractor de hallazgos).
    candidatos = []
    for abre, cierra in (("{", "}"), ("[", "]")):
        ini, fin = limpio.find(abre), limpio.rfind(cierra)
        if ini != -1 and fin > ini:
            candidatos.append((ini, limpio[ini:fin + 1]))
    for _, fragmento in sorted(candidatos):
        try:
            return json.loads(fragmento)
        except json.JSONDecodeError:
            continue
    raise ValueError("JSON malformado en respuesta de Claude")


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


def _formatear_mision_activa(id_usuario, ligero=False):
    """Bloque de texto con la misión activa del usuario para inyectar a un agente.

    ligero=True devuelve solo nombre + patrón que rompe (para Mirror, que debe
    mantener foco). Devuelve "" si no hay misión activa.
    """
    estado = clsInteraccionDB.obtener_ultima_mision(id_usuario)
    if not estado:
        return ""
    mision = estado["mision"]
    progreso = estado["progreso"]
    camino = clsInteraccionDB.obtener_camino_elegido(id_usuario) or {}
    patron = camino.get("patron_que_rompe") or ""

    if ligero:
        partes = [f"Misión activa de la persona: «{mision.get('nombre_mision', '')}»."]
        if patron:
            partes.append(f"Esta misión busca romper el patrón: «{patron}».")
        partes.append("No desvíes la sesión hacia la misión; úsala solo si conecta de forma natural con el patrón que trabajan.")
        return "\n\n--- Foco actual de la persona ---\n" + " ".join(partes)

    acciones = mision.get("acciones", [])
    lineas = []
    for i, a in enumerate(acciones):
        hecha = progreso[i] if i < len(progreso) else False
        lineas.append(f"  [{'x' if hecha else ' '}] {a}")
    bloque = [
        "--- Misión activa de la persona (su foco de esta semana) ---",
        f"Camino: {camino.get('nombre_camino', '') or '—'}",
        f"Misión: {mision.get('nombre_mision', '')}",
    ]
    if mision.get("descripcion"):
        bloque.append(f"Descripción: {mision['descripcion']}")
    if lineas:
        bloque.append("Acciones (x = hecha):\n" + "\n".join(lineas))
    if patron:
        bloque.append(f"Patrón que esta misión busca romper: «{patron}».")
    return "\n\n" + "\n".join(bloque)


async def _llamar_claude(system_prompt, mensajes, max_tokens=4096, modelo=None):
    """Llamada base a Claude. Devuelve el texto del primer bloque de la respuesta.

    `modelo` permite sobreescribir el modelo por defecto del proyecto en llamadas
    puntuales (p. ej. la generacion de ficha usa un modelo mas capaz).
    """
    respuesta = await _cliente.messages.create(
        model=modelo or MODELO,
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
        _con_identidad(PROMPT_DIAGNOSTICO),
        [{"role": "user", "content": entrada}],
        max_tokens=4096,
        modelo=MODELO_AGENTE,
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
            _con_identidad(PROMPT_DIAGNOSTICO),
            [{"role": "user", "content": entrada}],
            max_tokens=4096,
            modelo=MODELO_AGENTE,
        )
        diagnostico = _parsear_json(texto_diag)

    texto = await _llamar_claude(
        _con_identidad(PROMPT_CAMINOS),
        [{"role": "user", "content": json.dumps(diagnostico, ensure_ascii=False)}],
        max_tokens=3072,
        modelo=MODELO_AGENTE,
    )
    return _parsear_json(texto)


# ============================================================================
# Agentes conversacionales: Mirror, Editor, Archive, Clarity
# ============================================================================
async def responder_chat_agente(id_chat, tipo_agente, id_usuario, contexto_extra=""):
    """Genera la respuesta del agente conversacional.

    Lee las 9 respuestas del Usuario_Perfil (contexto estatico) y los ultimos 10
    mensajes del chat. El mensaje nuevo del usuario ya fue insertado por la vista.
    `contexto_extra` permite inyectar contexto puntual (p. ej. un logro a redactar).
    """
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
    perfil = clsInteraccionDB.obtener_perfil(id_usuario) or {}
    contexto_onboarding = _formatear_onboarding(perfil, nombre)

    system_prompt = (
        _PROMPTS_CHAT[tipo_agente]
        + "\n\n--- Contexto del onboarding del usuario (estatico) ---\n"
        + contexto_onboarding
    )
    # Editor escribe con la voz del usuario.
    if tipo_agente == "coach_editor":
        system_prompt += _snippet_voice(id_usuario)
        system_prompt += _NOTA_VOZ_USUARIO
    if contexto_extra:
        system_prompt += "\n\n--- Contexto puntual de esta sesión ---\n" + contexto_extra

    historico = clsInteraccionDB.obtener_ultimos_mensajes(id_chat, 10)
    mensajes = [{"role": m["rol"], "content": m["contenido"]} for m in historico]

    return await _llamar_claude(_con_identidad(system_prompt), mensajes, max_tokens=1536, modelo=MODELO_AGENTE)


# --- Editor estudio: borrador (entregable) + chat + sugerencias --------------
_EDITOR_JSON = """Devuelves EXCLUSIVAMENTE un objeto JSON válido, sin texto fuera de él, sin
backticks ni Markdown:
{
  "borrador": "<el entregable COMPLETO, listo para copiar y pegar>",
  "asunto": "<solo si es un correo; si no, cadena vacía>",
  "comentario": "<1 o 2 frases para el chat: qué hiciste o qué necesitas saber>",
  "sugerencias": ["<ajuste corto y accionable>", "...entre 3 y 5"]
}
El "borrador" respeta la voz del usuario y el formato pedido; no inventes datos
que no estén en el logro. "sugerencias" son posibles próximos ajustes cortos
(ej: "Más corto", "Más directo", "Quitar CTA", "Cambiar apertura", "Más formal")."""


def _fmt_desc(formato):
    """Describe el formato pedido para el prompt. Acepta etiquetas libres del usuario."""
    f = (formato or "").strip().lower()
    if f == "linkedin":
        return "un post de logro para LinkedIn"
    if f in ("correo", "email", "mail") or "correo" in f or "email" in f:
        return "un correo profesional"
    return f"contenido con el formato que pidió el usuario: «{formato}»"


async def editor_estudio(id_usuario, formato, contexto_logro, borrador_actual, turns):
    """Genera/edita el entregable. Devuelve dict {borrador, asunto, comentario, sugerencias}."""
    fmt = _fmt_desc(formato)
    system = (
        PROMPT_EDITOR
        + _snippet_voice(id_usuario)
        + (("\n\n--- Logro (materia prima, no inventes nada) ---\n" + contexto_logro) if contexto_logro else "")
        + f"\n\n--- Tarea ---\nEstás ayudando a redactar {fmt}.\n"
        + (("Borrador actual:\n" + borrador_actual) if borrador_actual else "Aún no hay borrador; redacta el primero.")
        + "\n\n" + _EDITOR_JSON
    )
    mensajes = [{"role": "assistant" if s == "editor" else "user", "content": t} for s, t in turns]
    if not mensajes or mensajes[0]["role"] == "assistant":
        mensajes.insert(0, {"role": "user", "content": "Redacta el borrador."})
    texto = await _llamar_claude(system, mensajes, max_tokens=1500)
    try:
        data = _parsear_json(texto)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        # El modelo respondió en prosa (p. ej. una pregunta aclaratoria cuando aún
        # no tiene material). No es un error: lo mostramos en el chat y conservamos
        # el borrador actual sin tocarlo.
        return {
            "borrador": (borrador_actual or "").strip(),
            "asunto": "",
            "comentario": (texto or "").strip() or "¿Me das un poco más de contexto para redactarlo?",
            "sugerencias": [],
        }
    return {
        "borrador": (data.get("borrador") or borrador_actual or "").strip(),
        "asunto": (data.get("asunto") or "").strip(),
        "comentario": (data.get("comentario") or "Listo.").strip(),
        "sugerencias": [str(x).strip() for x in (data.get("sugerencias") or []) if str(x).strip()][:5],
    }


PROMPT_FICHA_LOGRO = """Eres un agente estructurador del sistema Climb. Tu trabajo es tomar una
conversación entre Archive (agente conversacional) y un usuario que documentó
un logro profesional, y convertirla en una ficha estructurada con datos limpios.

INPUT: la conversación completa (turnos etiquetados como 'Archive' y 'Usuario').

OUTPUT: exclusivamente un objeto JSON válido con esta estructura EXACTA, sin
texto adicional, sin Markdown, sin backticks:
{
  "tipo": "<Deal closed|Project|Certification|Learning|Activation|Leadership|Presentation|Other>",
  "titulo": "<4-10 palabras, descriptivo del logro>",
  "contexto": "<30-60 palabras: la situación o problema que el logro resolvió>",
  "mi_rol": "<30-60 palabras: qué hizo específicamente el usuario>",
  "aprendizaje": "<1-2 frases con el aprendizaje, o cadena vacía si no aplica>",
  "tags": ["<palabras clave de búsqueda>"],
  "metrics": [ { "value": "<ej: $240K, 395, 60d>", "label": "<qué mide>" } ]
}

PRINCIPIOS NO NEGOCIABLES:
1. Si alguna dimensión NO tiene datos suficientes en la conversación, articula honestamente con lo que hay. NO inventes información.
2. Las métricas solo se incluyen si el usuario mencionó cifras concretas. Si NO hay cifras concretas, "metrics" es []. NO inventes métricas.
3. El array "metrics" tiene máximo 2 elementos. Si hay más cifras, escoges las 2 más impactantes.
4. El "titulo" es descriptivo, no marketing. NO uses frases como "Increíble logro de...". Usa lenguaje neutro profesional.
5. Los "tags" son palabras clave para búsqueda: incluye dominio técnico, industria y función. NO uses tags genéricos como "trabajo" o "logro". Entre 2 y 4 tags.
6. "tipo" es exactamente uno de los ocho valores permitidos.
7. Escribes en inglés natural y claro (todos los valores de texto del JSON van en inglés). Sin emojis.
8. Tu respuesta es ÚNICAMENTE el JSON válido, sin texto adicional, sin markdown, sin explicación."""


async def responder_archive(turns, id_usuario):
    """Respuesta del agente Archive a partir de los turnos en memoria de la sesion.

    turns: list[(speaker, texto)] con speaker en {"archive", "user"}.
    """
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
    perfil = clsInteraccionDB.obtener_perfil(id_usuario) or {}
    system_prompt = (
        PROMPT_ARCHIVE
        + "\n\n--- Contexto del onboarding del usuario (estatico) ---\n"
        + _formatear_onboarding(perfil, nombre)
        + _snippet_voice(id_usuario)
        + _NOTA_VOZ_USUARIO
    )

    # Construir mensajes; la API debe empezar en 'user', asi que saltamos el
    # saludo inicial del agente.
    mensajes = []
    visto_user = False
    for speaker, texto in turns:
        rol = "assistant" if speaker == "archive" else "user"
        if not visto_user and rol == "assistant":
            continue
        visto_user = True
        mensajes.append({"role": rol, "content": texto})

    if not mensajes:
        return ""
    return await _llamar_claude(_con_identidad(system_prompt), mensajes, max_tokens=1024, modelo=MODELO_AGENTE)


async def generar_ficha_logro(turns, id_usuario):
    """Genera la ficha estructurada del logro a partir de la conversacion.

    Devuelve un dict con: tipo, titulo, contexto, mi_rol, aprendizaje, tags, metrics.
    """
    conversacion = "\n".join(
        f"{'Archive' if s == 'archive' else 'Usuario'}: {t}" for s, t in turns
    )
    texto = await _llamar_claude(
        PROMPT_FICHA_LOGRO,
        [{"role": "user", "content": conversacion}],
        max_tokens=900,
        modelo=MODELO_FICHA,
    )
    data = _parsear_json(texto)
    if not isinstance(data, dict):
        raise ValueError("La ficha no es un objeto JSON")

    tipo = data.get("tipo")
    if tipo not in clsInteraccionDB.LOGRO_TYPES:
        tipo = "Other"

    tags = data.get("tags") if isinstance(data.get("tags"), list) else []
    metrics = []
    for m in (data.get("metrics") or []):
        if isinstance(m, dict) and (m.get("value") or m.get("label")):
            metrics.append({"value": str(m.get("value", "")), "label": str(m.get("label", ""))})

    return {
        "tipo": tipo,
        "titulo": data.get("titulo") or "Logro sin título",
        "contexto": data.get("contexto") or "",
        "mi_rol": data.get("mi_rol") or "",
        "aprendizaje": data.get("aprendizaje") or "",
        "tags": [str(t) for t in tags],
        "metrics": metrics,
    }


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


# ============================================================================
# Mirror: preguntas socráticas, boundary y reframe
# ============================================================================
PROMPT_MIRROR_BOUNDARY = """Eres un clasificador de Climb. Lees el último mensaje de un usuario en una
sesión con Mirror, un agente que solo trabaja patrones PROFESIONALES (cómo
aparecen en el trabajo y la carrera).

Decide si el mensaje cruza hacia lo personal profundo que Mirror NO debe
acompañar: salud mental (depresión, ansiedad clínica, ideación suicida), duelo,
relaciones íntimas o de pareja, trauma personal, violencia.

Responde ÚNICAMENTE con una palabra: SI (si cruza) o NO (si sigue siendo
profesional o laboral)."""

PROMPT_MIRROR_REFRAME = """Eres Mirror. Recibes un patrón limitante y la conversación socrática de una
sesión. Tu tarea es destilar un reencuadre del patrón.

Devuelves exclusivamente un objeto JSON válido, sin texto adicional, sin
Markdown, sin backticks:
{
  "old_quote": "<la creencia vieja, en una frase corta>",
  "new_quote": "<la creencia reencuadrada, en una frase corta>",
  "lo_que_vimos": "<2-3 frases: de dónde viene el patrón y por qué sigue operando>",
  "manifestacion": "<2-3 frases: cómo se manifiesta concretamente en su trabajo>",
  "recomendaciones": ["<recomendación corta y accionable para su trabajo>", "<otra>"]
}

Reglas: "recomendaciones" tiene 2 o 3 elementos, cortos y accionables (algo que
pueda hacer esta semana). Escribes en inglés natural y claro (todos los valores de
texto del JSON van en inglés), sin emojis, sin clichés de autoayuda. No inventes
hechos que el usuario no haya dicho. Devuelves únicamente el JSON."""


async def mirror_pregunta(patron_quote, turns, id_usuario, reanclar=False):
    """Genera UNA pregunta socrática sobre el patrón (ámbito profesional)."""
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
    perfil = clsInteraccionDB.obtener_perfil(id_usuario) or {}
    extra = (
        f'\n\n--- Patrón que se trabaja en esta sesión ---\n"{patron_quote}"\n'
        "Haz UNA pregunta socrática a la vez, solo sobre cómo este patrón aparece "
        "en su trabajo y su carrera. No resumas ni aconsejes.\n\n"
        "Cuando ya tengas suficiente para reflejar el patrón (su origen y cómo se "
        "manifiesta en el trabajo, normalmente tras 3 a 5 intercambios), NO hagas otra "
        "pregunta: cierra con una o dos frases cálidas que reconozcan lo trabajado y "
        "termina tu mensaje EXACTAMENTE con la etiqueta [LISTO]."
    )
    if reanclar:
        extra += (
            "\n\nLa conversación venía cruzando hacia lo personal profundo. Regresa al "
            "usuario, con respeto, a lo profesional con una pregunta nueva sobre el patrón."
        )
    system_prompt = (
        PROMPT_MIRROR + extra
        + "\n\n--- Contexto del onboarding del usuario (estatico) ---\n"
        + _formatear_onboarding(perfil, nombre)
        + _formatear_mision_activa(id_usuario, ligero=True)
    )

    # Las preguntas de Mirror son turnos 'assistant'. Anteponemos un mensaje
    # 'user' semilla para que la secuencia empiece en user sin perder las
    # preguntas previas (contexto que el usuario está respondiendo).
    mensajes = [{"role": "assistant" if s == "mirror" else "user", "content": t} for s, t in turns]
    if not mensajes or mensajes[0]["role"] == "assistant":
        mensajes.insert(0, {"role": "user", "content": f'Quiero trabajar este patrón: "{patron_quote}". Acompáñame con preguntas.'})

    return (await _llamar_claude(_con_identidad(system_prompt), mensajes, max_tokens=300, modelo=MODELO_AGENTE)).strip()


async def mirror_es_boundary(texto):
    """Devuelve True si el mensaje cruza de lo profesional a lo personal profundo."""
    try:
        r = await _llamar_claude(PROMPT_MIRROR_BOUNDARY, [{"role": "user", "content": texto}], max_tokens=5)
    except Exception:
        return False
    return r.strip().upper().startswith("SI")


async def mirror_reframe(patron_quote, turns):
    """Genera el reframe final del patrón. Devuelve dict con los 5 campos."""
    conversacion = "\n".join(f"{'Mirror' if s == 'mirror' else 'Usuario'}: {t}" for s, t in turns)
    texto = await _llamar_claude(
        _con_identidad(PROMPT_MIRROR_REFRAME),
        [{"role": "user", "content": f'Patrón: "{patron_quote}"\n\nConversación:\n{conversacion}'}],
        max_tokens=700,
        modelo=MODELO_AGENTE,
    )
    data = _parsear_json(texto)
    if not isinstance(data, dict):
        raise ValueError("El reframe no es un objeto JSON")
    recs = data.get("recomendaciones")
    if not isinstance(recs, list):
        recs = [recs] if recs else []
    return {
        "old_quote": data.get("old_quote") or patron_quote,
        "new_quote": data.get("new_quote") or "",
        "lo_que_vimos": data.get("lo_que_vimos") or "",
        "manifestacion": data.get("manifestacion") or "",
        "recomendaciones": [str(x) for x in recs if str(x).strip()],
    }


# ============================================================================
# Clarity: conversación para pensar + cierre con puertas
# ============================================================================
def _ref_campo(r, campo):
    """Lee un campo de una referencia, tolere dataclass o dict."""
    return getattr(r, campo, None) if not isinstance(r, dict) else r.get(campo)


def _formatear_referencias(referencias):
    """Lista numerada del material real que Clarity puede citar (Mirror/Archive)."""
    if not referencias:
        return "\n\n(No hay material previo para citar en esta sesión.)"
    filas = [
        f'[{i}] {_ref_campo(r, "agente")} · {_ref_campo(r, "fecha")} · "{_ref_campo(r, "cita")}"'
        for i, r in enumerate(referencias)
    ]
    return (
        "\n\n--- Material real disponible para citar (usa SOLO esto, por su índice) ---\n"
        + "\n".join(filas)
    )


async def responder_clarity(turns, id_usuario, referencias=None, primer_turno=False):
    """Un turno de Clarity. Devuelve dict {mensaje, referencia_id, tema, listo}.

    turns: list[(speaker, texto)] con speaker en {"clarity", "user"}.
    referencias: list[{"agente","fecha","cita"}] (material real, por índice).
    """
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario)
    perfil = clsInteraccionDB.obtener_perfil(id_usuario) or {}
    system = (
        PROMPT_CLARITY
        + "\n\n--- Contexto del onboarding del usuario (estatico) ---\n"
        + _formatear_onboarding(perfil, nombre)
        + _formatear_mision_activa(id_usuario)
        + _formatear_referencias(referencias or [])
    )
    mensajes = [{"role": "assistant" if s == "clarity" else "user", "content": t} for s, t in turns]
    if not mensajes or mensajes[0]["role"] == "assistant":
        mensajes.insert(0, {"role": "user", "content": "Quiero pensar algo antes de decidir."})

    texto = await _llamar_claude(_con_identidad(system), mensajes, max_tokens=700, modelo=MODELO_AGENTE)
    try:
        data = _parsear_json(texto)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        # Respuesta en prosa: la tratamos como mensaje sin referencia ni cierre.
        return {"mensaje": (texto or "").strip(), "referencia_id": None, "tema": "", "listo": False}

    ref_id = data.get("referencia_id")
    if not isinstance(ref_id, int) or not (0 <= ref_id < len(referencias or [])):
        ref_id = None
    return {
        "mensaje": (data.get("mensaje") or "").strip(),
        "referencia_id": ref_id,
        "tema": (data.get("tema") or "").strip(),
        "listo": bool(data.get("listo")),
    }


async def clarity_cierre(turns, id_usuario):
    """Sintetiza la conversación y clasifica qué puertas mostrar. Devuelve dict."""
    conversacion = "\n".join(f"{'Clarity' if s == 'clarity' else 'Usuario'}: {t}" for s, t in turns)
    texto = await _llamar_claude(
        _con_identidad(PROMPT_CLARITY_CIERRE),
        [{"role": "user", "content": conversacion}],
        max_tokens=600,
        modelo=MODELO_AGENTE,
    )
    try:
        data = _parsear_json(texto)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        data = {}
    rec = data.get("puerta_recomendada")
    if rec not in (1, 2, 3):
        rec = 1
    return {
        "sintesis": (data.get("sintesis") or "Lo que vimos juntos: llegaste a una decisión más clara.").strip(),
        "pregunta": (data.get("pregunta") or "¿Cómo te quieres quedar con esto?").strip(),
        "hay_patron": bool(data.get("hay_patron")),
        "patron_quote": (data.get("patron_quote") or "").strip(),
        "hay_accion": bool(data.get("hay_accion")),
        "accion_texto": (data.get("accion_texto") or "").strip(),
        "puerta_recomendada": rec,
    }


# ============================================================================
# Voice Profile: análisis de cómo escribe el usuario
# ============================================================================
PROMPT_VOICE_PROFILE = """Eres un analista de estilo de escritura de Climb. Tu trabajo es construir el
"voice profile" de un profesional: una huella accionable de CÓMO escribe y se
comunica, para que otros agentes puedan sonar como él sin imitar a un robot.

Recibes dos cosas:
1. El voice profile ANTERIOR (puede ser "ninguno" la primera vez).
2. NUEVOS textos escritos por el usuario, cada uno etiquetado con su fuente
   entre corchetes, p. ej. [onboarding], [editor], [mirror], [clarity].

Devuelves el voice profile ACTUALIZADO: integras la evidencia nueva, afinas lo
que ya era estable y corriges lo que el nuevo texto contradiga.

Tu salida es exclusivamente un objeto JSON válido, sin texto adicional, sin
Markdown, sin backticks:
{
  "registro": "<ej: técnico-coloquial, ejecutivo seco, narrativo cálido>",
  "tono": ["<2-4 adjetivos: directo, autocrítico, pragmático, etc.>"],
  "formalidad": "<baja|media|alta>",
  "estructura": "<frases cortas y entrecortadas | párrafos largos | mezcla>",
  "lexico": ["<palabras/expresiones que repite, anglicismos, jerga de su industria>"],
  "muletillas": ["<conectores o muletillas que usa: 'o sea', 'al final', etc.>"],
  "marcadores": "<hábitos: uso de '...', mayúsculas, emojis sí/no, cómo abre y cierra>",
  "postura": "<asertivo en 1ª persona | tentativo (creo que, tal vez) | mezcla>",
  "como_escribir_como_el": "<3 a 5 reglas concretas para imitar su voz>",
  "que_evitar": "<qué lo haría sonar falso: corporativo vacío, demasiado pulido, etc.>",
  "ejemplos_textuales": ["<2-3 frases reales suyas, representativas de su estilo>"]
}

Reglas obligatorias:
1. PRIVACIDAD: los textos marcados [clarity] vienen de un espacio de desahogo
   emocional. Analiza SOLO el estilo (tono, léxico, ritmo). NUNCA cites su
   contenido en "ejemplos_textuales" ni en ningún otro campo.
2. "ejemplos_textuales" son frases textuales del usuario (de fuentes que no sean
   clarity), no inventadas ni parafraseadas.
3. Describes estilo, no personalidad ni juicios de valor. Nada de psicología.
4. Si hay poca evidencia, sé conservador (no exageres rasgos con una sola muestra).
5. Español neutro de Latinoamérica. Sin emojis.
6. Devuelves únicamente el objeto JSON."""


def _confianza_voice(n_muestras):
    if n_muestras < 5:
        return "baja"
    if n_muestras < 15:
        return "media"
    return "alta"


async def actualizar_voice_profile(id_usuario):
    """Recalcula el voice profile de forma incremental con los textos nuevos.

    Toma el perfil anterior + los textos desde el último offset, llama a Claude
    y guarda el perfil actualizado. Devuelve el dict del perfil, o None si no hay
    nada nuevo que analizar.
    """
    previo = clsInteraccionDB.obtener_voice_profile(id_usuario)
    desde = previo["ultimo_texto_id"] if previo else 0
    n_previo = previo["n_muestras"] if previo else 0

    textos = clsInteraccionDB.obtener_textos_usuario(id_usuario, desde_id=desde)
    if not textos:
        return previo["contenido"] if previo else None

    # Acotar tokens: tomar los textos más recientes hasta ~6000 caracteres.
    seleccion, total = [], 0
    for t in reversed(textos):
        linea = f"[{t['fuente']}] {t['texto']}"
        if seleccion and total + len(linea) > 6000:
            break
        seleccion.append(linea)
        total += len(linea)
    seleccion.reverse()

    anterior = json.dumps(previo["contenido"], ensure_ascii=False, indent=2) if previo and previo.get("contenido") else "ninguno"
    entrada = (
        "VOICE PROFILE ANTERIOR:\n" + anterior
        + "\n\nNUEVOS TEXTOS DEL USUARIO:\n" + "\n".join(seleccion)
    )

    texto = await _llamar_claude(PROMPT_VOICE_PROFILE, [{"role": "user", "content": entrada}], max_tokens=900)
    contenido = _parsear_json(texto)
    if not isinstance(contenido, dict):
        raise ValueError("El voice profile no es un objeto JSON")
    contenido = _normalizar_voice(contenido)

    n_total = n_previo + len(textos)
    contenido["meta"] = {
        "n_muestras": n_total,
        "confianza": _confianza_voice(n_total),
        "fecha": datetime.now().isoformat(),
    }
    clsInteraccionDB.guardar_voice_profile(id_usuario, contenido, n_total, textos[-1]["idTexto"])
    return contenido


async def actualizar_voice_profile_si_toca(id_usuario, umbral=8):
    """Fire-and-forget: actualiza el voice profile solo si hay >= umbral textos
    nuevos desde la última vez. Barato si no toca (solo una consulta); silencia
    errores para no afectar la UI."""
    try:
        previo = clsInteraccionDB.obtener_voice_profile(id_usuario)
        desde = previo["ultimo_texto_id"] if previo else 0
        nuevos = clsInteraccionDB.obtener_textos_usuario(id_usuario, desde_id=desde)
        if len(nuevos) >= umbral:
            await actualizar_voice_profile(id_usuario)
    except Exception:
        return


_VOICE_LISTAS = {"tono", "lexico", "muletillas", "ejemplos_textuales"}
_VOICE_TEXTOS = {"registro", "formalidad", "estructura", "marcadores", "postura", "como_escribir_como_el", "que_evitar"}


def _normalizar_voice(c):
    """Deja los campos del voice profile en tipos consistentes (listas o textos),
    sin importar si el modelo los devolvió como str o list."""
    if not isinstance(c, dict):
        return c
    for k in _VOICE_LISTAS:
        if k in c:
            c[k] = _voice_lista(c[k])
    for k in _VOICE_TEXTOS:
        if k in c:
            c[k] = _voice_texto(c[k])
    return c


def _voice_lista(v):
    """Normaliza un campo a lista de strings (tolera str, list o None)."""
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if v:
        return [str(v).strip()]
    return []


def _voice_texto(v, sep="; "):
    """Normaliza un campo a texto (une listas; tolera str, list o None)."""
    return sep.join(_voice_lista(v))


def _snippet_voice(id_usuario):
    """Convierte el voice profile en un fragmento de prompt para que un agente
    escriba con la voz del usuario. Tolera campos como str o list. '' si no hay perfil."""
    vp = clsInteraccionDB.obtener_voice_profile(id_usuario)
    if not vp or not vp.get("contenido"):
        return ""
    c = vp["contenido"]
    partes = []
    if c.get("como_escribir_como_el"):
        partes.append("Cómo escribe: " + _voice_texto(c["como_escribir_como_el"]))
    if c.get("que_evitar"):
        partes.append("Evita (lo haría sonar falso): " + _voice_texto(c["que_evitar"]))
    if c.get("registro"):
        partes.append("Registro: " + _voice_texto(c["registro"], ", "))
    if c.get("tono"):
        partes.append("Tono: " + ", ".join(_voice_lista(c["tono"])))
    if c.get("muletillas"):
        partes.append("Expresiones suyas: " + ", ".join(_voice_lista(c["muletillas"])[:5]))
    ejemplos = _voice_lista(c.get("ejemplos_textuales"))
    if ejemplos:
        partes.append("Ejemplos de su voz: " + " | ".join(f'"{e}"' for e in ejemplos[:3]))
    if not partes:
        return ""
    meta = c.get("meta") if isinstance(c.get("meta"), dict) else {}
    cautela = " (Perfil preliminar: respeta su voz pero no fuerces los rasgos.)" if meta.get("confianza") == "baja" else ""
    return (
        "\n\n--- Voz del usuario (escribe como él, sin imitar de más) ---\n"
        + "\n".join(partes) + cautela
    )


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
        _con_identidad(PROMPT_PACER),
        [{"role": "user", "content": entrada}],
        max_tokens=2048,
        modelo=MODELO_AGENTE,
    )
    mision = _parsear_json(texto)
    clsInteraccionDB.insertar_mision(id_usuario, mision)
    return mision


async def sugerir_misiones_pacer(id_usuario, n=3):
    """Sugiere 2-3 misiones nuevas tras completar una, con contexto cruzado.

    Lee camino + onboarding + patrones de Mirror + logros de Archive + misiones
    completadas (para no repetir). Devuelve list[dict] (cada dict es una misión
    lista para insertar con insertar_mision).
    """
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

    # Contexto cruzado: patrones de Mirror, logros de Archive, misiones hechas.
    _, observando = clsMirror.cargar_hub(id_usuario)
    patrones = [p.reframe.old_quote if p.reframe else p.quote for p in observando][:5]
    logros = [l["titulo"] for l in clsInteraccionDB.obtener_logros_completos(id_usuario)[:5]]
    completadas = [m["nombre"] for m in clsInteraccionDB.obtener_misiones_completadas(id_usuario)]

    entrada = (
        "Camino Elegido (JSON):\n" + json.dumps(camino_json, ensure_ascii=False)
        + "\n\nPatrones trabajados en Mirror:\n" + ("\n".join(f"- {p}" for p in patrones) or "(ninguno)")
        + "\n\nLogros recientes en Archive:\n" + ("\n".join(f"- {t}" for t in logros) or "(ninguno)")
        + "\n\nMisiones ya completadas (NO repetir):\n" + ("\n".join(f"- {c}" for c in completadas) or "(ninguna)")
        + "\n\nRespuestas del onboarding:\n" + _formatear_onboarding(perfil, nombre)
        + f"\n\nDevuelve entre 2 y {n} misiones."
    )

    texto = await _llamar_claude(
        _con_identidad(PROMPT_PACER_SUGERENCIAS),
        [{"role": "user", "content": entrada}],
        max_tokens=2048,
        modelo=MODELO_AGENTE,
    )
    data = _parsear_json(texto)
    misiones = data.get("misiones") if isinstance(data, dict) else (data if isinstance(data, list) else [])
    # Filtra a las que tengan al menos nombre y acciones.
    return [m for m in (misiones or []) if isinstance(m, dict) and m.get("nombre_mision") and m.get("acciones")][:n]


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
