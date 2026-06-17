"""Centralized UI text for Climb (English).

All user-facing strings live here. The "voice" strings (Climb's personality:
taglines, agent descriptions, Mirror's contract, the onboarding questions, etc.)
are grouped as V_* constants below; the neutral UI chrome lives inline in TEXTOS.

Convention:
- TEXTOS: dict by screen. Neutral chrome inline; voice values reference the V_*.
- Strings with variables are templates with {placeholders}; callers use .format().
"""

# ════════════════════════════════════════════════════════════════════════════
# VOICE STRINGS — Climb's personality (kept as named constants for easy tuning)
# ════════════════════════════════════════════════════════════════════════════

# --- Onboarding: 4 acts / 9 questions ---
ACTOS = [
    (
        "Act I — Where you are today",
        "There are no right answers here. Write the way you talk, even if it comes out messy. I just want to really get to know you.",
        [
            "How do you feel about your career right now? Not the LinkedIn version — the real one.",
            "When something at work frustrates you or you feel stuck, what do you do with it? Talk it out, keep it in, work more hours?",
        ],
    ),
    (
        "Act II — Where you come from",
        "Now tell me your story. No résumé and no formalities — like you'd tell me over coffee.",
        [
            "Tell me what you do today. What's your job, what kind of company, and what are you responsible for day to day?",
            "And to get there, what did you go through? Tell me your path so far, the way you'd tell someone at dinner, not in an interview.",
        ],
    ),
    (
        "Act III — What you've built",
        "Let's talk about what you've achieved, and how you live it when it all rests on you.",
        [
            "What's the achievement you're most proud of? Tell me what happened and why that one matters so much to you.",
            "When you have to present your work in front of important people, or it all falls on you, how do you experience it? Does it lift you or weigh on you?",
        ],
    ),
    (
        "Act IV — Where you're headed",
        "And to close, where you want to go from here.",
        [
            "What have you tried to grow or to get noticed more? Tell me what you tried that didn't work too — that tells me a lot about you.",
            "Picture your career in three years, with no limits of any kind. What does it look like? Where are you, what are you doing, how do you feel?",
            "Before we wrap up, this space is yours. Is there anything about your career you're carrying that you haven't told me yet?",
        ],
    ),
]

# --- Landing ---
V_LANDING_TAGLINE = "Your career's right hand"
V_LANDING_KEYWORDS = "CONTEXT  ·  PATTERN  ·  EXECUTION"

# --- Onboarding (CTA with the "Climb" brand metaphor) ---
V_ONB_ULTIMA = "Reach the summit  →"

# --- Scout ---
V_SCOUT_QUOTE = '"Your scout. Observe, map, connect the dots."'
V_SCOUT_PARRAFO = (
    "I'll read calmly through what you share and map the behavioral patterns that "
    "define your professional moment: what drives you, what holds you back, and "
    "where the gap you can't see yet is."
)
V_SCOUT_PASO1_DESC = "Reads your answers without judging. Just records."
V_SCOUT_PASO2_DESC = "Spots patterns that repeat in how you see yourself professionally."
V_SCOUT_PASO3_DESC = "Returns a qualitative diagnosis that feeds the rest of the system."
V_SCOUT_FOOTER = "Observation  ·  Pattern  ·  Gap"

# --- Diagnosis ---
V_DIAG_SALUDO = "This is what I saw in you, {nombre}"

# --- Dashboard: agent descriptions ---
V_AG_MIRROR = "Helps you process your limiting patterns through Socratic questions."
V_AG_EDITOR = "Translates your technical impact into executive language without losing your voice."
V_AG_ARCHIVE = "Documents your professional wins for when they matter."
V_AG_CLARITY = "Gives you perspective and helps you think before deciding your next move."

# --- Mirror ---
V_MIRROR_DESCRIPCION = (
    "Works on limiting patterns in your professional career. Through questions, it "
    "helps you see them from the outside so they stop running on autopilot."
)
V_MIRROR_BOUNDARY_HERO = (
    "I work with you only on the professional. If the conversation moves toward the "
    "deeply personal, I'll redirect you with respect."
)
V_MIRROR_CONTRATO_1 = (
    "This session is going to be a conversation of questions. I don't have pre-built "
    "answers — you're the one who'll reach yours. All I do is help you take the "
    "pattern apart, calmly."
)
V_MIRROR_CONTRATO_2 = "It'll take about 10 to 15 minutes. You can stop whenever you want."
V_MIRROR_CONTRATO_BOUNDARY = (
    "I work with you only on the professional — how this pattern shows up in your career, "
    "in your work, in how you see yourself as a professional. If the conversation moves "
    "toward the deeply personal, I'll redirect you with respect."
)
V_MIRROR_PROPIO_INTRO = (
    "Is there something you feel operating in your work that Scout hasn't detected yet? "
    "Write it the way you hear it in your head."
)
V_MIRROR_PROPIO_HINT = 'E.g.: "If I say no to this meeting, they\'ll think I don\'t care..."'
V_MIRROR_VACIO_TITULO = "Scout has no new patterns this week.\nGood sign."
V_MIRROR_Q_INICIAL = "Tell me: when does this pattern show up in your work, specifically?"
V_MIRROR_Q_SEGUIR = "Let's keep going: what else do you notice about how this pattern operates in your work?"
V_MIRROR_Q_REANCLAR = "Let's get back to your work. How does this pattern show up in a concrete work situation?"
V_MIRROR_CIERRE_FALLBACK = "I think we have enough now to see this pattern from the outside."
V_MIRROR_BOUNDARY_1 = "What you're sharing is important, and that's exactly why I'm not the one who should be with you there."
V_MIRROR_BOUNDARY_2 = (
    "I work only with professional patterns — how they show up in your work, in your career. "
    "For what you're going through, a mental health professional will be far more useful than me."
)
V_MIRROR_BOUNDARY_PRIVACIDAD = "Your decision stays only between you and the session.\nNothing you shared leaves here."
V_MIRROR_ESPEJO_SUB = "Take a moment before closing. What follows is for you, not for your archive."

# --- Editor (conversational) ---
V_EDITOR_SALUDO_CONTEXTO = 'I see your win «{titulo}». Do you want it as an email or a LinkedIn post?'
V_EDITOR_PEDIR_FORMATO = "Tell me the format you want (for example: «a bio for my Instagram profile»)."
V_EDITOR_PREGUNTA_CORREO = "Perfect, an email. What's it about and who's it for? Tell me the essentials and I'll write it."
V_EDITOR_PREGUNTA_LINKEDIN = "Perfect, a LinkedIn post. What win or topic do you want to share? Give me the details and I'll write it."
V_EDITOR_PREGUNTA_CUSTOM = "Perfect, «{formato}». Tell me the essentials and I'll write it."
V_EDITOR_NUDGE_FORMATO = "Noted. What format do you want it in? Pick Email or LinkedIn post below, or tell me the format yourself."
V_EDITORHOME_SUBTITULO = "Turn your professional work into content to show the world. I speak in your voice, not mine."

# --- Archive ---
V_ARCHIVE_APERTURA = (
    "Tell me what happened this week that's worth saving. It doesn't have to be huge."
)
V_ARCHIVE_DESCRIPCION = (
    "Your professional chronicler. It documents the wins that matter so that, when you "
    "need them — interviews, reviews, decisions — they're ready."
)
V_ARCHIVE_RECIEN_TEXTO = "Your win is documented. This is how we recorded it."
V_ARCHIVE_DEL_ARCHIVO_TEXTO = "A win you documented with Archive."

# --- Clarity ---
V_CLARITY_SALUDO = "This is what you've built, {nombre}"
V_CLARITY_ENCUADRE = (
    "Sometimes, caught up in the day-to-day, you don't see how far you've come. I do. "
    "I'll show you what you've got before we open the conversation."
)
V_CLARITY_BOUNDARY = (
    "I help you think before deciding your next professional move. "
    "I'm not a space for personal matters — for that, a professional."
)
V_CLARITY_INVITACION = (
    "Now that you've seen where you are, what's on your mind today? Tell me what situation "
    "you want to think through before deciding your next move."
)
V_CLARITY_PUERTAS_HELPER = "You don't have to pick one. But something helps you land what you thought through."

# ════════════════════════════════════════════════════════════════════════════
# END VOICE STRINGS
# ════════════════════════════════════════════════════════════════════════════


TEXTOS = {
    # -------------------------------------------------------------------- común
    "comun": {
        "marca": "Climb",
        "diagnostico_inicial": "Initial diagnosis",
        "volver_dashboard": "← Back to dashboard",
        "ver_todos": "See all  →",
        "dias": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "meses": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "meses_largo": ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"],
        "volver": "← Back",
        "tu": "You",
        "enviar": "SEND  →",
    },

    # ------------------------------------------------------------------ landing
    "landing": {
        "tagline": V_LANDING_TAGLINE,
        "comenzar": "Get started",
        "ya_tengo_cuenta": "I already have an account — Sign in",
        "keywords": V_LANDING_KEYWORDS,
    },

    # -------------------------------------------------------------------- login
    "login": {
        "ph_nombre": "Alex Carter",
        "ph_numero": "4821",
        "ph_clave": "••••••••",
        "err_incompleto": "Fill in your name, number and password.",
        "err_credenciales": "Incorrect username or password.",
        "eyebrow": "Access",
        "titulo": "Sign in",
        "subtitulo": "Sign in with the username we gave you when you created your account.",
        "lbl_nombre": "Your name",
        "lbl_numero": "Number",
        "lbl_clave": "Your password",
        "entrar": "Sign in",
        "ir_registro": "Don't have an account? Create one",
    },

    # ---------------------------------------------------------------- registro
    "registro": {
        "ph_nombre": "Alex Carter",
        "ph_clave": "At least 4 characters",
        "ph_clave2": "Repeat your password",
        "err_sin_nombre": "Please enter your name to continue.",
        "err_clave_corta": "Your password must be at least 4 characters.",
        "err_no_coinciden": "Passwords don't match.",
        "dlg_titulo": "Your account is ready",
        "dlg_eyebrow": "Your username",
        "dlg_aviso": "Keep it safe: you'll need it to sign in next time.",
        "dlg_continuar": "Continue",
        "eyebrow": "Create account",
        "titulo": "Create your account",
        "subtitulo": "Choose a name and a password. We'll give you a unique username to log back in.",
        "lbl_nombre": "Your name",
        "lbl_clave": "Create a password",
        "lbl_clave2": "Confirm your password",
        "crear": "Create account",
        "ir_login": "Already have an account? Sign in",
    },

    # -------------------------------------------------------------- onboarding
    "onboarding": {
        "subtitulo": "Initial diagnosis",
        "hint": "Write whatever comes to mind, no filter...",
        "anterior": "← PREVIOUS",
        "ultima": V_ONB_ULTIMA,
        "siguiente": "Next  →",
        "err_vacio": "Write your answer to continue.",
        "progreso": "QUESTION {n:02d} / {total:02d}",
    },

    # -------------------------------------------------------------------- scout
    "scout": {
        "subtitulo": "Initial diagnosis",
        "paso": "Step 01 of 02",
        "nombre": "Scout",
        "quote": V_SCOUT_QUOTE,
        "que_va_a_pasar": "What happens next",
        "parrafo": V_SCOUT_PARRAFO,
        "paso1_titulo": "Observe",
        "paso1_desc": V_SCOUT_PASO1_DESC,
        "paso2_titulo": "Map",
        "paso2_desc": V_SCOUT_PASO2_DESC,
        "paso3_titulo": "Connect",
        "paso3_desc": V_SCOUT_PASO3_DESC,
        "empezar": "START THE DIAGNOSIS  →",
        "footer": V_SCOUT_FOOTER,
    },

    # ----------------------------------------------------------------- progreso
    "progreso": {
        "mensajes": [
            "Reading your answers...",
            "Identifying patterns...",
            "Building your profile...",
            "Preparing your diagnosis...",
        ],
        "error": "Something went wrong, try again",
        "regresar": "Go back",
    },

    # -------------------------------------------------------------- diagnóstico
    "diagnostico": {
        "saludo": V_DIAG_SALUDO,
        "subtitulo": "Your qualitative diagnosis",
        "descargar_pdf": "Download PDF",
        "rotulo": (
            "This is an initial read from your onboarding: a starting point to think with, "
            "not a verdict. You decide what to do with it."
        ),
        "retrato_eres": "WHAT YOU ARE",
        "retrato_frena": "WHAT HOLDS YOU BACK",
        "retrato_brecha": "WHERE THE GAP IS",
        "h_visibilidad": "Your strategic visibility today",
        "h_patrones": "The patterns Scout detected in your voice",
        "h_siguiente": "Your next step",
        "ver_plan": "See my plan for the next 30 days",
        "generando_plan": "Generating your plan…",
        "error": "Something went wrong, try again",
    },

    # ------------------------------------------------------------------ caminos
    "caminos": {
        "titulo": "Your plan for the next 30 days",
        "subtitulo": "Three possible paths. You decide which to take.",
        "rotulo": (
            "Climb shows you options with their costs and risks; it doesn't choose for you. "
            "It's an input for YOU to decide, not a definitive answer."
        ),
        "por_que_encaja": "WHY IT FITS YOU",
        "lbl_tradeoff": "Main tradeoff",
        "lbl_riesgo": "Main risk",
        "lbl_tiempo": "Estimated time per week",
        "lbl_patron": "Pattern it breaks",
        "lbl_supuesto": "Assumption this path tests",
        "tomar": "Take this path",
        "preparando": "Preparing your first mission…",
    },

    # --------------------------------------------------------------- dashboard
    "dashboard": {
        "bitacora": "Daily log",
        "saludo": "Hi, {nombre}",
        "h_patrones": "Scout · Detected patterns",
        "h_camino": "Path · Active",
        "h_agentes": "Your agents",
        "h_archivo": "From the archive · Recent wins",
        "mision_activa": "Active mission",
        "tu_camino": "Your path",
        "sin_mision": "You haven't generated your first mission yet.",
        "generar_mision": "Generate my mission  →",
        "ver_mision": "See my mission  →",
        "hablar": "Talk  →",
        "ir_mirror": "Mirror  →",
        "acciones_proxima": "{completadas} OF {total} ACTIONS  ·  NEXT · {proxima}",
        "mision_completada": "Mission complete · generate the next one",
        "refrescar": "Refresh diagnosis  →",
        "version": "v0.1 · Beta",
        "diag_actualizado": "Diagnosis updated",
        "diag_error": "Couldn't update the diagnosis",
        "ag_mirror": V_AG_MIRROR,
        "ag_editor": V_AG_EDITOR,
        "ag_archive": V_AG_ARCHIVE,
        "ag_clarity": V_AG_CLARITY,
    },

    # -------------------------------------------------------------------- pacer
    "pacer": {
        "sin_mision": "No mission generated yet.",
        "acciones_completadas": "{completadas} of {total} actions completed",
        "h_acciones": "Concrete actions",
        "conexion": "Connection with your path",
        "completar": "Complete mission  →",
        "generando": "Generating your mission…",
        "generar_nueva": "Generate new mission",
        "regresar_menu": "‹ Back to menu",
        "eyebrow": "Pacer · Your week",
        "titulo": "Your mission this week",
    },

    # -------------------------------------------------------- pacer completada
    "pacer_cierre": {
        "pensando": "Pacer is thinking through your next steps…",
        "sin_sugerencias": "Couldn't suggest missions right now.",
        "generar": "Generate a mission  →",
        "volver_dashboard": "Back to dashboard",
        "n_acciones": "{n} actions",
        "elegir": "Choose  →",
        "eyebrow": "Mission complete",
        "titulo_fallback": "Mission complete",
        "intro": "It's recorded in your path. Here's what can come next.",
        "h_elige": "Choose your next mission",
        "topbar": "Pacer · Closing",
    },

    # ======================================================================
    # AGENTES
    # ======================================================================

    # -------------------------------------------------------------- Mirror
    "mirror": {
        "nombre": "Mirror",
        "descripcion": V_MIRROR_DESCRIPCION,
        "boundary_hero": V_MIRROR_BOUNDARY_HERO,
        # Hub
        "topbar": "Mirror",
        "h_pendientes": "Pending patterns",
        "pendientes_contador": "{n} detected by Scout",
        "h_observacion": "Under observation",
        "observacion_contador": "{n} patterns processed",
        "h_nuevo": "Work on a new pattern",
        "empezar_sesion_card": "Start session  →",
        "procesado_meta": "Processed {fecha}  ·  {observado}",
        "retomar": "Resume  →",
        "vacio_titulo": V_MIRROR_VACIO_TITULO,
        "vacio_sub": "Still watching in the background  ·  It'll let you know when something comes up",
        "propio_eyebrow": "Your own pattern",
        "propio_intro": V_MIRROR_PROPIO_INTRO,
        "propio_hint": V_MIRROR_PROPIO_HINT,
        "propio_aviso": "Mirror will take you into a session with this pattern",
        "propio_boton": "START SESSION  →",
        # Entry
        "sin_patron": "No pattern selected.",
        "ir_mirror": "Go to Mirror",
        "patron_hoy": "Pattern to work on today",
        "antes_empezar": "Before we start",
        "contrato_1": V_MIRROR_CONTRATO_1,
        "contrato_2": V_MIRROR_CONTRATO_2,
        "contrato_boundary": V_MIRROR_CONTRATO_BOUNDARY,
        "cancelar": "← Cancel",
        "empezar_la_sesion": "START THE SESSION  →",
        # Session
        "pregunta_cargando": "Mirror is preparing your first question...",
        "escribiendo": "Mirror is typing…",
        "session_hint": "Tell Mirror about your work...",
        "lbl_num": "QUESTION {n:02d}",
        "lbl_num_inicial": "Question {n:02d}",
        "q_fallback_inicial": V_MIRROR_Q_INICIAL,
        "q_fallback_seguir": V_MIRROR_Q_SEGUIR,
        "q_fallback_reanclar": V_MIRROR_Q_REANCLAR,
        "cierre_fallback": V_MIRROR_CIERRE_FALLBACK,
        "ver_camino": "{flecha} SEE THE PATH TAKEN ({n} TURNS)",
        "mirror_pregunta": "Mirror asks",
        "tu_respuesta": "Your answer",
        "sin_patron_sesion": "No pattern in session.",
        "subtopbar": "·  Mirror  ·  Session",
        "ambito": "Scope · Professional career",
        "patron": "Pattern",
        "terminar_sesion": "End session and see the mirror  →",
        "generando_espejo": "Generating the mirror…",
        "error_espejo": "Couldn't generate the mirror. Try again.",
        # Boundary inline
        "boundary_eyebrow": "Mirror responds",
        "boundary_1": V_MIRROR_BOUNDARY_1,
        "boundary_2": V_MIRROR_BOUNDARY_2,
        "opcion_a": "Option A",
        "opcion_b": "Option B",
        "boundary_cerrar_titulo": "End the session",
        "boundary_cerrar_desc": "We stop here. The pattern is saved so you can come back to it whenever you want.",
        "boundary_seguir_titulo": "Back to the pattern  →",
        "boundary_seguir_desc": "We return to the professional. I'll ask you a new question about the pattern.",
        "boundary_privacidad": V_MIRROR_BOUNDARY_PRIVACIDAD,
        # Cierre
        "ver_espejo": "SEE THE MIRROR  →",
        # Espejo (pantalla 4)
        "sin_sesion_cerrar": "There's no session to close.",
        "espejo_eyebrow": "The mirror",
        "espejo_titulo": "This is what we saw",
        "espejo_sub": V_MIRROR_ESPEJO_SUB,
        "espejo_lo_que_vimos": "What we saw",
        "espejo_manifestacion": "How it shows up in your work",
        "espejo_recomendaciones": "Recommendations to improve",
        "espejo_pregunta_cierre": "How do you want to leave this?",
        "reson_titulo": "✓ THIS RESONATED",
        "reson_desc": "Scout will keep watching if the pattern comes back.",
        "explorar_titulo": "I WANT TO KEEP EXPLORING",
        "explorar_desc": "We go back to the session for one more question.",
        "no_reson_titulo": "IT DIDN'T RESONATE",
        "no_reson_desc": "Scout recalibrates. The pattern stays active.",
        "espejo_subtopbar": "·  Mirror · Closing",
        "espejo_sesion_meta": "Session 01  ·  {n} minutes",
        "volver_a_mirror": "← Back to Mirror",
    },

    # -------------------------------------------------------------- Editor
    "editor": {
        "marca": "Climb · Editor",
        "lbl_default": "Editor",
        "lbl_linkedin": "POST · LINKEDIN",
        "lbl_correo": "EMAIL",
        "saludo_contexto": V_EDITOR_SALUDO_CONTEXTO,
        "saludo_sin_contexto": "What do you want to write? Pick a format to start.",
        "speaker_editor": "Editor",
        "chip_correo": "✍  Email",
        "chip_linkedin": "💼  LinkedIn post",
        "chip_otro": "✎  Other format",
        "pedir_formato": V_EDITOR_PEDIR_FORMATO,
        "hint_ajuste": "Ask Editor for a tweak...",
        "hint_formato": "Type the format…",
        "pregunta_correo": V_EDITOR_PREGUNTA_CORREO,
        "pregunta_linkedin": V_EDITOR_PREGUNTA_LINKEDIN,
        "pregunta_custom": V_EDITOR_PREGUNTA_CUSTOM,
        "nudge_formato": V_EDITOR_NUDGE_FORMATO,
        "redactando": "Editor is writing…",
        "error_generar": "Something went wrong. Try again.",
        "regenerar_instr": "Regenerate the draft from scratch, same format and material.",
        "version_anterior_msg": "Reverted to the previous version.",
        "completar_sin_borrador": "There's no draft to mark as complete yet.",
        "copiado": "Draft copied to clipboard.",
        "preview_hace": "Just now · 🌐",
        "preview_like": "👍 Like",
        "preview_comentar": "💬 Comment",
        "preview_compartir": "↗ Share",
        "preview_asunto": "Subject",
        "preview_sin_asunto": "(no subject)",
        "copiar": "📋 Copy",
        "preview_vacio_con_formato": "Your draft will appear here, ready to copy.",
        "preview_vacio_sin_formato": "Pick a format in the chat to start writing.",
        "tb_version_anterior": "← Previous version",
        "tb_regenerar": "↻ Regenerate all",
        "tb_completar": "✓ Complete",
        "tooltip_volver": "Back to Editor",
        "banner_basado": "Based on · Archive",
    },

    # ----------------------------------------------------------- Editor home
    "editor_home": {
        "topbar": "Editor",
        "titulo": "Editor",
        "subtitulo": V_EDITORHOME_SUBTITULO,
        "nuevo": "＋  New draft",
        "h_activos": "Active drafts",
        "activos_contador": "{n} unfinished",
        "h_completados": "Completed",
        "vacio": "You don't have any drafts in progress yet. Create a new one to start.",
        "continuar": "Continue  →",
        "ver": "View  →",
        "editado": "Edited {hace}",
        "lbl_linkedin": "POST · LINKEDIN",
        "lbl_correo": "EMAIL",
        "pill_linkedin": "LinkedIn",
        "pill_correo": "Email",
        "pill_texto": "Text",
        "sin_contenido": "(no content)",
        "lbl_fallback": "DRAFT",
    },

    # ------------------------------------------------------------- Archive
    "archive": {
        "nombre": "Archive",
        "apertura": V_ARCHIVE_APERTURA,
        "descripcion": V_ARCHIVE_DESCRIPCION,
        "speaker_archive": "Archive",
        "escribiendo": "Typing…",
        "hint_chat": "Write whatever you want to share...",
        "sesion_meta": "SESSION · {n} TURNS  ·  GATHERING CONTEXT",
        "btn_si_generar": "Yes, generate the entry",
        "btn_modificar": "I want to change something",
        "modificar_msg": "I want to change something else",
        "error_respuesta": "Something went wrong generating the response. Try again.",
        "generando_ficha": "Generating your entry…",
        "error_ficha": "Couldn't generate the entry. Try again.",
        "tu_respuesta": "Your answer",
        "topbar": "Archive",
        # Timeline
        "periodos": ["All", "This month", "Quarter", "Year"],
        "documentar": "+ DOCUMENT A WIN",
        "bitacora": "Wins log",
        "tu_archivo": "Your archive",
        "timeline_intro": (
            "Everything you documented with Archive. Find it when you need it — "
            "interviews, reviews, proposals."
        ),
        "stat_total": "Total wins",
        "stat_trimestre": "This quarter",
        "stat_impacto": "Impact recorded",
        "stat_tags": "Active tags",
        "buscar": "Search the archive...",
        "sin_metrica": "No metric",
        "timeline_topbar": "The Archive  ·  {n} wins documented",
        "timeline_vacio": "You haven't documented any wins yet. Start with “+ Document a win”.",
        # Ficha
        "ficha_vacia": "There's no entry to show.",
        "ir_archive": "Go to Archive",
        "recien_eyebrow": "Win archived",
        "recien_texto": V_ARCHIVE_RECIEN_TEXTO,
        "del_archivo_eyebrow": "From the archive",
        "del_archivo_texto": V_ARCHIVE_DEL_ARCHIVO_TEXTO,
        "ficha_contexto": "Context",
        "ficha_mi_rol": "My specific role",
        "ficha_aprendizaje": "Takeaway",
        "ficha_tags": "Tags",
        "volver_archivo": "← Back to the archive",
        "redactar_editor": "WRITE WITH EDITOR  →",
    },

    # ------------------------------------------------------------- Clarity
    "clarity": {
        "nombre": "Clarity",
        "topbar": "Clarity",
        # Espejo (pantalla 1)
        "saludo": V_CLARITY_SALUDO,
        "encuadre": V_CLARITY_ENCUADRE,
        "boundary": V_CLARITY_BOUNDARY,
        "camino_activo": "Active path",
        "acciones_pacer": "{hechas} / {total} actions",
        "ahora_tu": "Now you",
        "invitacion": V_CLARITY_INVITACION,
        "hint_espejo": "Whatever's on your mind...",
        "empezar": "START  →",
        # Conversación (pantalla 2)
        "speaker_clarity": "Clarity",
        "topbar_sesion": "Clarity · Session",
        "hint_conversacion": "Or tell me if you already saw what you needed...",
        "anchor_default": "Thinking · Your situation",
        "anchor": "Thinking · {tema}",
        "tu_espejo": "Your mirror",
        "ver_completo": "See full  →",
        "sigue_pensando": "Keep thinking out loud",
        "pensando": "Clarity is thinking…",
        "error_turno": "Something went wrong. Let's try again.",
        "cerrando": "Closing the conversation…",
        # Puertas (pantalla 3)
        "sin_conversacion": "There's no conversation to close.",
        "ir_clarity": "Go to Clarity",
        "tres_caminos": "Three paths",
        "puertas_titulo": "What comes next is up to you",
        "puertas_helper": V_CLARITY_PUERTAS_HELPER,
        "p1_tag": "End the session",
        "p1_titulo": "Keep the clarity I got",
        "p1_desc": "You saw what you needed. The system saves this conversation. You go back to the dashboard.",
        "p2_tag": "Work the pattern",
        "p2_titulo": "Take this to a session with Mirror",
        "p2_desc": 'The reflection of "{patron}" deserves its own session. Mirror takes it apart in depth.',
        "p3_tag": "Add to your mission",
        "p3_titulo": "Turn it into a Pacer action",
        "p3_desc": '"{accion}" can become part of your active mission.',
        "recomendada": "Recommended",
        "seguir_conversando": "↻ I want to keep talking",
        "puertas_subtopbar": "·  Clarity · Closing",
        "sugerencia_pacer": "Clarity's suggestion: {accion}",
    },
}
