"""Árbol de textos de interfaz en español para Climb.

Un solo dict, ES, con las mismas claves que core/textos_en.py. Los textos con
variables son plantillas con {placeholders}; quien llama usa .format().
"""

ES = {
    # -------------------------------------------------------------------- común
    "comun": {
        "marca": "Climb",
        "diagnostico_inicial": "Diagnóstico inicial",
        "volver_dashboard": "← Volver al dashboard",
        "ver_todos": "Ver todos  →",
        "dias": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
        "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
        "meses_largo": ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
        "volver": "← Volver",
        "tu": "Tú",
        "enviar": "ENVIAR  →",
        "idioma": "Idioma",
    },

    # ------------------------------------------------------------ fechas relativas
    "fechas": {
        "ahora": "justo ahora",
        "hace_min": "hace {n} min",
        "hace_horas": "hace {n}h",
        "hoy": "hoy",
        "ayer": "ayer",
        "hace_dias": "hace {n} días",
        "hace_semana": "hace 1 semana",
        "hace_semanas": "hace {n} semanas",
        "hace_mes": "hace {n} mes",
        "hace_meses": "hace {n} meses",
    },

    # ------------------------------------------------------------------ landing
    "landing": {
        "tagline": "La mano derecha de tu carrera",
        "comenzar": "Comenzar",
        "ya_tengo_cuenta": "Ya tengo cuenta — Iniciar sesión",
        "keywords": "CONTEXTO  ·  PATRÓN  ·  EJECUCIÓN",
    },

    # -------------------------------------------------------------------- login
    "login": {
        "ph_identificador": "tú@correo.com o usuario",
        "ph_clave": "••••••••",
        "err_incompleto": "Escribe tu correo o usuario y tu contraseña.",
        "err_credenciales": "Correo/usuario o contraseña incorrectos.",
        "eyebrow": "Acceso",
        "titulo": "Iniciar sesión",
        "subtitulo": "Inicia sesión con tu correo o tu nombre de usuario.",
        "lbl_identificador": "Correo o nombre de usuario",
        "lbl_clave": "Tu contraseña",
        "entrar": "Iniciar sesión",
        "olvide": "¿Olvidaste tu contraseña?",
        "ir_registro": "¿No tienes cuenta? Crea una",
    },

    # ---------------------------------------------------------------- registro
    "registro": {
        "ph_nombre": "Alex Carter",
        "ph_correo": "tú@correo.com",
        "ph_username": "alexcarter",
        "ph_clave": "Al menos 4 caracteres",
        "ph_clave2": "Repite tu contraseña",
        "err_sin_nombre": "Escribe tu nombre para continuar.",
        "err_correo_invalido": "Escribe un correo válido.",
        "err_correo_existe": "Ese correo ya está registrado.",
        "err_username_invalido": "Usuario: 3-20 caracteres, empieza con letra, solo letras, números, . y _",
        "err_username_existe": "Ese usuario ya está tomado. Prueba otro.",
        "err_clave_corta": "Tu contraseña debe tener al menos 4 caracteres.",
        "err_no_coinciden": "Las contraseñas no coinciden.",
        "sugerir_username": "Sugerir uno",
        "eyebrow": "Crear cuenta",
        "titulo": "Crea tu cuenta",
        "subtitulo": "Tu nombre es cómo Climb te saluda. Tu usuario y tu correo son cómo vuelves a entrar.",
        "lbl_nombre": "Tu nombre",
        "lbl_correo": "Correo",
        "lbl_username": "Nombre de usuario",
        "lbl_clave": "Crea una contraseña",
        "lbl_clave2": "Confirma tu contraseña",
        "crear": "Crear cuenta",
        "ir_login": "¿Ya tienes cuenta? Inicia sesión",
        "disclaimer_titulo": "Climb te da insumos, no respuestas",
        "disclaimer_cuerpo": (
            "Cada camino, cada patrón, cada misión es algo para pensar, no un veredicto que "
            "seguir. Las decisiones sobre tu carrera se quedan contigo, porque el contexto que "
            "más importa vive fuera de esta app: tu familia, tus finanzas, tu vida real."
        ),
        "disclaimer_check": "Entiendo. Las decisiones se quedan conmigo.",
        "leer_acuerdo": "Leer el acuerdo  →",
        "disclaimer_cerrar": "Entendido",
        "err_disclaimer": "Confirma que entiendes para continuar.",
    },

    # -------------------------------------------------------------- recuperar
    "recuperar": {
        "eyebrow": "Recuperar contraseña",
        "titulo": "Restablece tu contraseña",
        "subtitulo": "Escribe tu correo y te enviaremos un código para crear una nueva contraseña.",
        "lbl_correo": "Correo",
        "ph_correo": "tú@correo.com",
        "err_correo": "Escribe un correo válido.",
        "enviar": "Enviar código",
        "enviado": "Si existe una cuenta con ese correo, te enviamos un código. Revisa tu bandeja.",
        "err_envio": "No pudimos enviar el correo ahora. Inténtalo en un momento.",
        "titulo2": "Escribe tu código",
        "subtitulo2": "Pega el código de 6 dígitos que te enviamos y elige una nueva contraseña.",
        "lbl_codigo": "Código",
        "ph_codigo": "123456",
        "lbl_clave": "Nueva contraseña",
        "ph_clave": "Al menos 4 caracteres",
        "lbl_clave2": "Confirma la nueva contraseña",
        "ph_clave2": "Repite tu contraseña",
        "err_codigo": "Código incorrecto o vencido.",
        "err_clave_corta": "Tu contraseña debe tener al menos 4 caracteres.",
        "err_no_coinciden": "Las contraseñas no coinciden.",
        "restablecer": "Restablecer contraseña",
        "listo": "Contraseña actualizada. Ya puedes iniciar sesión.",
        "reenviar": "¿No llegó? Enviar de nuevo",
        "volver_login": "Volver a iniciar sesión",
    },

    # -------------------------------------------------------------- onboarding
    "onboarding": {
        "subtitulo": "Diagnóstico inicial",
        "hint": "Escribe lo que se te venga a la mente, sin filtro...",
        "anterior": "← ANTERIOR",
        "ultima": "Llega a la cima  →",
        "siguiente": "Siguiente  →",
        "err_vacio": "Escribe tu respuesta para continuar.",
        "progreso": "PREGUNTA {n:02d} / {total:02d}",
        "actos": [
            (
                "Acto I — Dónde estás hoy",
                "Aquí no hay respuestas correctas. Escribe como hablas, aunque salga desordenado. Solo quiero conocerte de verdad.",
                [
                    "¿Cómo te sientes con tu carrera ahora mismo? No lo que ven los demás, sino lo que de verdad sientes.",
                    "Cuando algo en el trabajo te frustra o te sientes estancado, ¿qué haces con eso? ¿Lo hablas, te lo guardas, trabajas más horas?",
                ],
            ),
            (
                "Acto II — De dónde vienes",
                "Ahora cuéntame tu historia. Sin currículum y sin formalidades, como si me lo contaras tomando un café.",
                [
                    "Cuéntame qué haces hoy. ¿Cuál es tu trabajo, en qué tipo de empresa y de qué eres responsable en el día a día?",
                    "Y para llegar ahí, ¿qué pasaste? Cuéntame tu camino hasta ahora, como se lo contarías a alguien en una cena, no en una entrevista.",
                ],
            ),
            (
                "Acto III — Lo que has construido",
                "Hablemos de lo que has logrado, y de cómo lo vives cuando todo depende de ti.",
                [
                    "¿Cuál es el logro del que te sientes más orgulloso? Cuéntame qué pasó y por qué ese te importa tanto.",
                    "Cuando tienes que presentar tu trabajo frente a personas importantes, o todo recae en ti, ¿cómo lo vives? ¿Te impulsa o te pesa?",
                ],
            ),
            (
                "Acto IV — Hacia dónde vas",
                "Y para cerrar, hacia dónde quieres ir desde aquí.",
                [
                    "¿Qué has intentado para crecer o para que te noten más? Cuéntame también lo que probaste y no funcionó; eso me dice mucho de ti.",
                    "Imagina tu carrera en tres años, sin límites de ningún tipo. ¿Cómo se ve? ¿Dónde estás, qué haces, cómo te sientes?",
                    "Antes de terminar, este espacio es tuyo. ¿Hay algo sobre tu carrera que cargas y que aún no me has dicho?",
                ],
            ),
        ],
    },

    # -------------------------------------------------------------------- scout
    "scout": {
        "subtitulo": "Diagnóstico inicial",
        "paso": "Paso 01 de 02",
        "nombre": "Scout",
        "quote": '"Tu explorador. Observa, mapea, conecta los puntos."',
        "que_va_a_pasar": "Lo que va a pasar",
        "parrafo": (
            "Voy a leer con calma lo que compartes y mapear los patrones de comportamiento que "
            "definen tu momento profesional: qué te impulsa, qué te frena y dónde está la "
            "brecha que aún no ves."
        ),
        "paso1_titulo": "Observa",
        "paso1_desc": "Lee tus respuestas sin juzgar. Solo registra.",
        "paso2_titulo": "Mapea",
        "paso2_desc": "Detecta patrones que se repiten en cómo te ves profesionalmente.",
        "paso3_titulo": "Conecta",
        "paso3_desc": "Devuelve un diagnóstico cualitativo que alimenta al resto del sistema.",
        "empezar": "COMENZAR EL DIAGNÓSTICO  →",
        "footer": "Observación  ·  Patrón  ·  Brecha",
    },

    # ----------------------------------------------------------------- progreso
    "progreso": {
        "mensajes": [
            "Leyendo tus respuestas...",
            "Identificando patrones...",
            "Construyendo tu perfil...",
            "Preparando tu diagnóstico...",
        ],
        "error": "Algo salió mal, inténtalo de nuevo",
        "regresar": "Volver",
    },

    # -------------------------------------------------------------- diagnóstico
    "diagnostico": {
        "saludo": "Esto es lo que vi en ti, {nombre}",
        "subtitulo": "Tu diagnóstico cualitativo",
        "rotulo": (
            "Esta es una lectura inicial de tu onboarding: un punto de partida para pensar, "
            "no un veredicto. Tú decides qué hacer con ella."
        ),
        "retrato_eres": "LO QUE ERES",
        "retrato_frena": "LO QUE TE FRENA",
        "retrato_brecha": "DÓNDE ESTÁ LA BRECHA",
        "h_visibilidad": "Tu visibilidad estratégica hoy",
        "h_patrones": "Los patrones que Scout detectó en tu voz",
        "h_siguiente": "Tu siguiente paso",
        "ver_plan": "Ver mi plan para los próximos 30 días",
        "generando_plan": "Generando tu plan…",
        "error": "Algo salió mal, inténtalo de nuevo",
    },

    # ------------------------------------------------------------------ caminos
    "caminos": {
        "titulo": "Tu plan para los próximos 30 días",
        "subtitulo": "Tres caminos posibles. Tú decides cuál tomar.",
        "rotulo": (
            "Climb te muestra opciones con sus costos y riesgos; no elige por ti. "
            "Es un insumo para que TÚ decidas, no una respuesta definitiva."
        ),
        "por_que_encaja": "POR QUÉ TE ENCAJA",
        "lbl_tradeoff": "Tradeoff principal",
        "lbl_riesgo": "Riesgo principal",
        "lbl_tiempo": "Tiempo estimado por semana",
        "lbl_patron": "Patrón que rompe",
        "lbl_supuesto": "Supuesto que pone a prueba",
        "tomar": "Tomar este camino",
        "preparando": "Preparando tu primera misión…",
    },

    # --------------------------------------------------------------- dashboard
    "dashboard": {
        "bitacora": "Bitácora diaria",
        "saludo": "Hola, {nombre}",
        "h_patrones": "Scout · Patrones detectados",
        "h_camino": "Camino · Activo",
        "h_agentes": "Tus agentes",
        "h_archivo": "Del archivo · Logros recientes",
        "mision_activa": "Misión activa",
        "tu_camino": "Tu camino",
        "sin_mision": "Aún no has generado tu primera misión.",
        "generar_mision": "Generar mi misión  →",
        "ver_mision": "Ver mi misión  →",
        "hablar": "Hablar  →",
        "ir_mirror": "Mirror  →",
        "acciones_proxima": "{completadas} DE {total} ACCIONES  ·  SIGUIENTE · {proxima}",
        "mision_completada": "Misión completada · genera la siguiente",
        "refrescar": "Actualizar diagnóstico  →",
        "version": "v0.1 · Beta",
        "diag_actualizado": "Diagnóstico actualizado",
        "diag_error": "No se pudo actualizar el diagnóstico",
        "ag_mirror": "Te ayuda a procesar tus patrones limitantes con preguntas socráticas.",
        "ag_editor": "Traduce tu impacto técnico a lenguaje ejecutivo sin perder tu voz.",
        "ag_archive": "Documenta tus logros profesionales para cuando importen.",
        "ag_clarity": "Te da perspectiva y te ayuda a pensar antes de decidir tu siguiente movimiento.",
    },

    # -------------------------------------------------------------------- pacer
    "pacer": {
        "sin_mision": "Aún no se ha generado ninguna misión.",
        "acciones_completadas": "{completadas} de {total} acciones completadas",
        "h_acciones": "Acciones concretas",
        "conexion": "Conexión con tu camino",
        "completar": "Completar misión  →",
        "generando": "Generando tu misión…",
        "generar_nueva": "Generar nueva misión",
        "regresar_menu": "‹ Volver al menú",
        "eyebrow": "Pacer · Tu semana",
        "titulo": "Tu misión de esta semana",
    },

    # -------------------------------------------------------- pacer completada
    "pacer_cierre": {
        "pensando": "Pacer está pensando tus siguientes pasos…",
        "sin_sugerencias": "No se pudieron sugerir misiones ahora.",
        "generar": "Generar una misión  →",
        "volver_dashboard": "Volver al dashboard",
        "n_acciones": "{n} acciones",
        "elegir": "Elegir  →",
        "eyebrow": "Misión completada",
        "titulo_fallback": "Misión completada",
        "intro": "Quedó registrada en tu camino. Esto es lo que puede venir después.",
        "h_elige": "Elige tu siguiente misión",
        "topbar": "Pacer · Cierre",
    },

    # -------------------------------------------------------------- Mirror
    "mirror": {
        "nombre": "Mirror",
        "descripcion": (
            "Trabaja los patrones limitantes de tu carrera profesional. A través de preguntas, "
            "te ayuda a verlos desde afuera para que dejen de funcionar en automático."
        ),
        "boundary_hero": (
            "Trabajo contigo solo lo profesional. Si la conversación se va hacia lo profundamente "
            "personal, te redirijo con respeto."
        ),
        "topbar": "Mirror",
        "h_pendientes": "Patrones pendientes",
        "pendientes_contador": "{n} detectados por Scout",
        "h_observacion": "En observación",
        "observacion_contador": "{n} patrones procesados",
        "h_nuevo": "Trabaja un patrón nuevo",
        "empezar_sesion_card": "Empezar sesión  →",
        "reanudar": "Retomar  →",
        "en_progreso_meta": "En progreso · {n} respondidas",
        "dejar_despues": "Dejar para después",
        "procesado_meta": "Procesado {fecha}  ·  {observado}",
        "retomar": "Retomar  →",
        "vacio_titulo": "Scout no tiene patrones nuevos esta semana.\nBuena señal.",
        "vacio_sub": "Sigue observando en segundo plano  ·  Te avisará cuando surja algo",
        "propio_eyebrow": "Tu propio patrón",
        "propio_intro": (
            "¿Hay algo que sientes operando en tu trabajo que Scout aún no ha detectado? "
            "Escríbelo como lo escuchas en tu cabeza."
        ),
        "propio_hint": 'Ej.: "Si digo que no a esta reunión, van a pensar que no me importa..."',
        "propio_aviso": "Mirror te llevará a una sesión con este patrón",
        "propio_boton": "EMPEZAR SESIÓN  →",
        "sin_patron": "No hay ningún patrón seleccionado.",
        "ir_mirror": "Ir a Mirror",
        "patron_hoy": "Patrón a trabajar hoy",
        "antes_empezar": "Antes de empezar",
        "contrato_1": (
            "Esta sesión va a ser una conversación de preguntas. No tengo respuestas prefabricadas; "
            "tú eres quien llegará a las suyas. Yo solo te ayudo a desarmar el patrón, con calma."
        ),
        "contrato_2": "Toma unos 10 a 15 minutos. Puedes parar cuando quieras.",
        "contrato_boundary": (
            "Trabajo contigo solo lo profesional: cómo aparece este patrón en tu carrera, en tu "
            "trabajo, en cómo te ves como profesional. Si la conversación se va hacia lo "
            "profundamente personal, te redirijo con respeto."
        ),
        "cancelar": "← Cancelar",
        "empezar_la_sesion": "EMPEZAR LA SESIÓN  →",
        "pregunta_cargando": "Mirror está preparando tu primera pregunta...",
        "escribiendo": "Mirror está escribiendo…",
        "session_hint": "Cuéntale a Mirror sobre tu trabajo...",
        "lbl_num": "PREGUNTA {n:02d}",
        "lbl_num_inicial": "Pregunta {n:02d}",
        "q_fallback_inicial": "Cuéntame: ¿cuándo aparece este patrón en tu trabajo, en concreto?",
        "q_fallback_seguir": "Sigamos: ¿qué más notas sobre cómo opera este patrón en tu trabajo?",
        "q_fallback_reanclar": "Volvamos a tu trabajo. ¿Cómo aparece este patrón en una situación laboral concreta?",
        "cierre_fallback": "Creo que ya tenemos suficiente para ver este patrón desde afuera.",
        "ver_camino": "{flecha} VER EL CAMINO RECORRIDO ({n} TURNOS)",
        "mirror_pregunta": "Mirror pregunta",
        "tu_respuesta": "Tu respuesta",
        "sin_patron_sesion": "No hay patrón en sesión.",
        "subtopbar": "·  Mirror  ·  Sesión",
        "ambito": "Ámbito · Carrera profesional",
        "patron": "Patrón",
        "terminar_sesion": "Terminar sesión y ver el espejo  →",
        "generando_espejo": "Generando el espejo…",
        "error_espejo": "No se pudo generar el espejo. Inténtalo de nuevo.",
        "boundary_eyebrow": "Mirror responde",
        "boundary_1": "Lo que compartes es importante, y justo por eso no soy yo quien debe acompañarte ahí.",
        "boundary_2": (
            "Trabajo solo con patrones profesionales: cómo aparecen en tu trabajo, en tu carrera. "
            "Para lo que estás viviendo, un profesional de salud mental te será mucho más útil que yo."
        ),
        "opcion_a": "Opción A",
        "opcion_b": "Opción B",
        "boundary_cerrar_titulo": "Terminar la sesión",
        "boundary_cerrar_desc": "Paramos aquí. El patrón queda guardado para que vuelvas a él cuando quieras.",
        "boundary_seguir_titulo": "Volver al patrón  →",
        "boundary_seguir_desc": "Volvemos a lo profesional. Te haré una nueva pregunta sobre el patrón.",
        "boundary_privacidad": "Tu decisión queda solo entre tú y la sesión.\nNada de lo que compartiste sale de aquí.",
        "ver_espejo": "VER EL ESPEJO  →",
        "sin_sesion_cerrar": "No hay ninguna sesión que cerrar.",
        "espejo_eyebrow": "El espejo",
        "espejo_titulo": "Esto es lo que vimos",
        "espejo_sub": "Tómate un momento antes de cerrar. Lo que sigue es para ti, no para tu archivo.",
        "espejo_lo_que_vimos": "Lo que vimos",
        "espejo_manifestacion": "Cómo aparece en tu trabajo",
        "espejo_recomendaciones": "Recomendaciones para mejorar",
        "espejo_pregunta_cierre": "¿Cómo quieres dejar esto?",
        "reson_titulo": "✓ ESTO RESONÓ",
        "reson_desc": "Scout seguirá observando si el patrón vuelve.",
        "explorar_titulo": "QUIERO SEGUIR EXPLORANDO",
        "explorar_desc": "Volvemos a la sesión para una pregunta más.",
        "no_reson_titulo": "NO RESONÓ",
        "no_reson_desc": "Scout recalibra. El patrón sigue activo.",
        "espejo_subtopbar": "·  Mirror · Cierre",
        "espejo_sesion_meta": "Sesión 01  ·  {n} minutos",
        "volver_a_mirror": "← Volver a Mirror",
    },

    # -------------------------------------------------------------- Editor
    "editor": {
        "marca": "Climb · Editor",
        "lbl_default": "Editor",
        "lbl_linkedin": "POST · LINKEDIN",
        "lbl_correo": "CORREO",
        "saludo_contexto": 'Veo tu logro «{titulo}». ¿Lo quieres como correo o como post de LinkedIn?',
        "saludo_sin_contexto": "¿Qué quieres escribir? Elige un formato para empezar.",
        "speaker_editor": "Editor",
        "chip_correo": "✍  Correo",
        "chip_linkedin": "💼  Post de LinkedIn",
        "chip_otro": "✎  Otro formato",
        "pedir_formato": "Dime el formato que quieres (por ejemplo: «una bio para mi perfil de Instagram»).",
        "hint_ajuste": "Pídele a Editor un ajuste...",
        "hint_formato": "Escribe el formato…",
        "pregunta_correo": "Perfecto, un correo. ¿De qué se trata y para quién es? Dime lo esencial y lo escribo.",
        "pregunta_linkedin": "Perfecto, un post de LinkedIn. ¿Qué logro o tema quieres compartir? Dame los detalles y lo escribo.",
        "pregunta_custom": "Perfecto, «{formato}». Dime lo esencial y lo escribo.",
        "nudge_formato": "Anotado. ¿En qué formato lo quieres? Elige Correo o Post de LinkedIn abajo, o dime tú el formato.",
        "redactando": "Editor está escribiendo…",
        "error_generar": "Algo salió mal. Inténtalo de nuevo.",
        "regenerar_instr": "Regenera el borrador desde cero, mismo formato y material.",
        "version_anterior_msg": "Volviste a la versión anterior.",
        "completar_sin_borrador": "Aún no hay borrador para marcar como completado.",
        "copiado": "Borrador copiado al portapapeles.",
        "preview_hace": "Justo ahora · 🌐",
        "preview_like": "👍 Me gusta",
        "preview_comentar": "💬 Comentar",
        "preview_compartir": "↗ Compartir",
        "preview_asunto": "Asunto",
        "preview_sin_asunto": "(sin asunto)",
        "copiar": "📋 Copiar",
        "preview_vacio_con_formato": "Tu borrador aparecerá aquí, listo para copiar.",
        "preview_vacio_sin_formato": "Elige un formato en el chat para empezar a escribir.",
        "tb_version_anterior": "← Versión anterior",
        "tb_regenerar": "↻ Regenerar todo",
        "tb_completar": "✓ Completar",
        "tooltip_volver": "Volver a Editor",
        "banner_basado": "Basado en · Archive",
    },

    # ----------------------------------------------------------- Editor home
    "editor_home": {
        "topbar": "Editor",
        "titulo": "Editor",
        "subtitulo": "Convierte tu trabajo profesional en contenido para mostrarle al mundo. Hablo con tu voz, no con la mía.",
        "nuevo": "＋  Nuevo borrador",
        "h_activos": "Borradores activos",
        "activos_contador": "{n} sin terminar",
        "h_completados": "Completados",
        "vacio": "Aún no tienes borradores en progreso. Crea uno nuevo para empezar.",
        "continuar": "Continuar  →",
        "ver": "Ver  →",
        "editado": "Editado {hace}",
        "lbl_linkedin": "POST · LINKEDIN",
        "lbl_correo": "CORREO",
        "pill_linkedin": "LinkedIn",
        "pill_correo": "Correo",
        "pill_texto": "Texto",
        "sin_contenido": "(sin contenido)",
        "lbl_fallback": "BORRADOR",
    },

    # ------------------------------------------------------------- Archive
    "archive": {
        "nombre": "Archive",
        "apertura": "Cuéntame qué pasó esta semana que valga la pena guardar. No tiene que ser algo enorme.",
        "descripcion": (
            "Tu cronista profesional. Documenta los logros que importan para que, cuando los "
            "necesites (entrevistas, evaluaciones, decisiones), estén listos."
        ),
        "speaker_archive": "Archive",
        "escribiendo": "Escribiendo…",
        "hint_chat": "Escribe lo que quieras compartir...",
        "sesion_meta": "SESIÓN · {n} TURNOS  ·  REUNIENDO CONTEXTO",
        "btn_si_generar": "Sí, genera la ficha",
        "btn_modificar": "Quiero cambiar algo",
        "modificar_msg": "Quiero cambiar algo más",
        "error_respuesta": "Algo salió mal al generar la respuesta. Inténtalo de nuevo.",
        "generando_ficha": "Generando tu ficha…",
        "error_ficha": "No se pudo generar la ficha. Inténtalo de nuevo.",
        "tu_respuesta": "Tu respuesta",
        "topbar": "Archive",
        "periodos": ["Todo", "Este mes", "Trimestre", "Año"],
        "documentar": "+ DOCUMENTAR UN LOGRO",
        "bitacora": "Bitácora de logros",
        "tu_archivo": "Tu archivo",
        "timeline_intro": (
            "Todo lo que documentaste con Archive. Encuéntralo cuando lo necesites: "
            "entrevistas, evaluaciones, propuestas."
        ),
        "stat_total": "Logros totales",
        "stat_trimestre": "Este trimestre",
        "stat_impacto": "Impacto registrado",
        "stat_tags": "Tags activos",
        "buscar": "Busca en el archivo...",
        "sin_metrica": "Sin métrica",
        "timeline_topbar": "El Archivo  ·  {n} logros documentados",
        "timeline_vacio": "Aún no has documentado ningún logro. Empieza con “+ Documentar un logro”.",
        "ficha_vacia": "No hay ficha que mostrar.",
        "ir_archive": "Ir a Archive",
        "recien_eyebrow": "Logro archivado",
        "recien_texto": "Tu logro quedó documentado. Así lo registramos.",
        "del_archivo_eyebrow": "Del archivo",
        "del_archivo_texto": "Un logro que documentaste con Archive.",
        "ficha_contexto": "Contexto",
        "ficha_mi_rol": "Mi rol específico",
        "ficha_aprendizaje": "Aprendizaje",
        "ficha_tags": "Tags",
        "volver_archivo": "← Volver al archivo",
        "redactar_editor": "REDACTAR CON EDITOR  →",
    },

    # ------------------------------------------------------------- Clarity
    "clarity": {
        "nombre": "Clarity",
        "topbar": "Clarity",
        "saludo": "Esto es lo que has construido, {nombre}",
        "encuadre": (
            "A veces, metido en el día a día, no ves lo lejos que has llegado. Yo sí. "
            "Te muestro lo que tienes antes de abrir la conversación."
        ),
        "boundary": (
            "Te ayudo a pensar antes de decidir tu siguiente movimiento profesional. "
            "No soy un espacio para temas personales; para eso, un profesional."
        ),
        "camino_activo": "Camino activo",
        "acciones_pacer": "{hechas} / {total} acciones",
        "ahora_tu": "Ahora tú",
        "invitacion": (
            "Ahora que viste dónde estás, ¿qué tienes en la cabeza hoy? Cuéntame qué situación "
            "quieres pensar antes de decidir tu siguiente movimiento."
        ),
        "hint_espejo": "Lo que tengas en mente...",
        "empezar": "EMPEZAR  →",
        "speaker_clarity": "Clarity",
        "topbar_sesion": "Clarity · Sesión",
        "hint_conversacion": "O dime si ya viste lo que necesitabas...",
        "anchor_default": "Pensando · Tu situación",
        "anchor": "Pensando · {tema}",
        "tu_espejo": "Tu espejo",
        "ver_completo": "Ver completo  →",
        "sigue_pensando": "Sigue pensando en voz alta",
        "pensando": "Clarity está pensando…",
        "error_turno": "Algo salió mal. Intentémoslo de nuevo.",
        "cerrando": "Cerrando la conversación…",
        "sin_conversacion": "No hay conversación que cerrar.",
        "ir_clarity": "Ir a Clarity",
        "tres_caminos": "Tres caminos",
        "puertas_titulo": "Lo que sigue depende de ti",
        "puertas_helper": "No tienes que elegir uno. Pero algo te ayuda a aterrizar lo que pensaste.",
        "p1_tag": "Terminar la sesión",
        "p1_titulo": "Quedarme con la claridad que gané",
        "p1_desc": "Viste lo que necesitabas. El sistema guarda esta conversación. Vuelves al dashboard.",
        "p2_tag": "Trabajar el patrón",
        "p2_titulo": "Llevar esto a una sesión con Mirror",
        "p2_desc": 'El reflejo de "{patron}" merece su propia sesión. Mirror lo desarma a fondo.',
        "p3_tag": "Sumar a tu misión",
        "p3_titulo": "Convertirlo en una acción de Pacer",
        "p3_desc": '"{accion}" puede volverse parte de tu misión activa.',
        "recomendada": "Recomendada",
        "seguir_conversando": "↻ Quiero seguir hablando",
        "puertas_subtopbar": "·  Clarity · Cierre",
        "sugerencia_pacer": "Sugerencia de Clarity: {accion}",
    },
}
