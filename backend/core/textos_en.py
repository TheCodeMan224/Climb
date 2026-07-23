"""English UI text tree for Climb.

One dict, EN, keyed by screen. Strings with variables are templates with
{placeholders}; callers use .format(). The i18n layer in core/textos.py exposes
this through a language-aware TEXTOS proxy.
"""

EN = {
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
        "idioma": "Language",
    },

    # ------------------------------------------------------------ fechas relativas
    "fechas": {
        "ahora": "just now",
        "hace_min": "{n} min ago",
        "hace_horas": "{n}h ago",
        "hoy": "today",
        "ayer": "yesterday",
        "hace_dias": "{n} days ago",
        "hace_semana": "1 week ago",
        "hace_semanas": "{n} weeks ago",
        "hace_mes": "{n} month ago",
        "hace_meses": "{n} months ago",
    },

    # ------------------------------------------------------------------ landing
    "landing": {
        "tagline": "Your career's right hand",
        "comenzar": "Get started",
        "ya_tengo_cuenta": "I already have an account — Sign in",
        "keywords": "CONTEXT  ·  PATTERN  ·  EXECUTION",
    },

    # -------------------------------------------------------------------- login
    "login": {
        "ph_identificador": "you@email.com or username",
        "ph_clave": "••••••••",
        "err_incompleto": "Enter your email or username and your password.",
        "err_credenciales": "Incorrect email/username or password.",
        "eyebrow": "Access",
        "titulo": "Sign in",
        "subtitulo": "Sign in with your email or your username.",
        "lbl_identificador": "Email or username",
        "lbl_clave": "Your password",
        "entrar": "Sign in",
        "olvide": "Forgot your password?",
        "ir_registro": "Don't have an account? Create one",
    },

    # ---------------------------------------------------------------- registro
    "registro": {
        "ph_nombre": "Alex Carter",
        "ph_correo": "you@email.com",
        "ph_username": "alexcarter",
        "ph_clave": "At least 4 characters",
        "ph_clave2": "Repeat your password",
        "err_sin_nombre": "Please enter your name to continue.",
        "err_correo_invalido": "Enter a valid email address.",
        "err_correo_existe": "That email is already registered.",
        "err_username_invalido": "Username: 3-20 chars, starts with a letter, only letters, numbers, . and _",
        "err_username_existe": "That username is taken. Try another.",
        "err_clave_corta": "Your password must be at least 4 characters.",
        "err_no_coinciden": "Passwords don't match.",
        "sugerir_username": "Suggest one",
        "eyebrow": "Create account",
        "titulo": "Create your account",
        "subtitulo": "Your name is how Climb greets you. Your username and email are how you sign back in.",
        "lbl_nombre": "Your name",
        "lbl_correo": "Email",
        "lbl_username": "Username",
        "lbl_clave": "Create a password",
        "lbl_clave2": "Confirm your password",
        "crear": "Create account",
        "ir_login": "Already have an account? Sign in",
        "disclaimer_titulo": "Climb gives you inputs, not answers",
        "disclaimer_cuerpo": (
            "Every path, every pattern, every mission is something to think with — not a "
            "verdict to follow. The decisions about your career stay with you, because the "
            "context that matters most lives outside this app: your family, your finances, "
            "your real life."
        ),
        "disclaimer_check": "I understand. The decisions stay with me.",
        "leer_acuerdo": "Read the agreement  →",
        "disclaimer_cerrar": "Got it",
        "err_disclaimer": "Please confirm you understand to continue.",
    },

    # -------------------------------------------------------------- recuperar
    "recuperar": {
        "eyebrow": "Password reset",
        "titulo": "Reset your password",
        "subtitulo": "Enter your email and we'll send you a code to set a new password.",
        "lbl_correo": "Email",
        "ph_correo": "you@email.com",
        "err_correo": "Enter a valid email address.",
        "enviar": "Send code",
        "enviado": "If an account exists for that email, we sent a code. Check your inbox.",
        "err_envio": "We couldn't send the email right now. Try again in a moment.",
        "titulo2": "Enter your code",
        "subtitulo2": "Paste the 6-digit code we emailed you and choose a new password.",
        "lbl_codigo": "Code",
        "ph_codigo": "123456",
        "lbl_clave": "New password",
        "ph_clave": "At least 4 characters",
        "lbl_clave2": "Confirm new password",
        "ph_clave2": "Repeat your password",
        "err_codigo": "Incorrect or expired code.",
        "err_clave_corta": "Your password must be at least 4 characters.",
        "err_no_coinciden": "Passwords don't match.",
        "restablecer": "Reset password",
        "listo": "Password updated. You can sign in now.",
        "reenviar": "Didn't get it? Send again",
        "volver_login": "Back to sign in",
    },

    # -------------------------------------------------------------- onboarding
    "onboarding": {
        "subtitulo": "Initial diagnosis",
        "hint": "Write whatever comes to mind, no filter...",
        "anterior": "← PREVIOUS",
        "ultima": "Reach the summit  →",
        "siguiente": "Next  →",
        "err_vacio": "Write your answer to continue.",
        "progreso": "QUESTION {n:02d} / {total:02d}",
        "actos": [
            (
                "Act I — Where you are today",
                "There are no right answers here. Write the way you talk, even if it comes out messy. I just want to really get to know you.",
                [
                    "How do you feel about your career right now? Not what others see, but what you really feel.",
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
        ],
    },

    # -------------------------------------------------------------------- scout
    "scout": {
        "subtitulo": "Initial diagnosis",
        "paso": "Step 01 of 02",
        "nombre": "Scout",
        "quote": '"Your scout. Observe, map, connect the dots."',
        "que_va_a_pasar": "What happens next",
        "parrafo": (
            "I'll read calmly through what you share and map the behavioral patterns that "
            "define your professional moment: what drives you, what holds you back, and "
            "where the gap you can't see yet is."
        ),
        "paso1_titulo": "Observe",
        "paso1_desc": "Reads your answers without judging. Just records.",
        "paso2_titulo": "Map",
        "paso2_desc": "Spots patterns that repeat in how you see yourself professionally.",
        "paso3_titulo": "Connect",
        "paso3_desc": "Returns a qualitative diagnosis that feeds the rest of the system.",
        "empezar": "START THE DIAGNOSIS  →",
        "footer": "Observation  ·  Pattern  ·  Gap",
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
        "saludo": "This is what I saw in you, {nombre}",
        "subtitulo": "Your qualitative diagnosis",
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
        "ag_mirror": "Helps you process your limiting patterns through Socratic questions.",
        "ag_editor": "Translates your technical impact into executive language without losing your voice.",
        "ag_archive": "Documents your professional wins for when they matter.",
        "ag_clarity": "Gives you perspective and helps you think before deciding your next move.",
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

    # -------------------------------------------------------------- Mirror
    "mirror": {
        "nombre": "Mirror",
        "descripcion": (
            "Works on limiting patterns in your professional career. Through questions, it "
            "helps you see them from the outside so they stop running on autopilot."
        ),
        "boundary_hero": (
            "I work with you only on the professional. If the conversation moves toward the "
            "deeply personal, I'll redirect you with respect."
        ),
        "topbar": "Mirror",
        "h_pendientes": "Pending patterns",
        "pendientes_contador": "{n} detected by Scout",
        "h_observacion": "Under observation",
        "observacion_contador": "{n} patterns processed",
        "h_nuevo": "Work on a new pattern",
        "empezar_sesion_card": "Start session  →",
        "reanudar": "Resume  →",
        "en_progreso_meta": "In progress · {n} answered",
        "dejar_despues": "Leave for later",
        "procesado_meta": "Processed {fecha}  ·  {observado}",
        "retomar": "Resume  →",
        "vacio_titulo": "Scout has no new patterns this week.\nGood sign.",
        "vacio_sub": "Still watching in the background  ·  It'll let you know when something comes up",
        "propio_eyebrow": "Your own pattern",
        "propio_intro": (
            "Is there something you feel operating in your work that Scout hasn't detected yet? "
            "Write it the way you hear it in your head."
        ),
        "propio_hint": 'E.g.: "If I say no to this meeting, they\'ll think I don\'t care..."',
        "propio_aviso": "Mirror will take you into a session with this pattern",
        "propio_boton": "START SESSION  →",
        "sin_patron": "No pattern selected.",
        "ir_mirror": "Go to Mirror",
        "patron_hoy": "Pattern to work on today",
        "antes_empezar": "Before we start",
        "contrato_1": (
            "This session is going to be a conversation of questions. I don't have pre-built "
            "answers — you're the one who'll reach yours. All I do is help you take the "
            "pattern apart, calmly."
        ),
        "contrato_2": "It'll take about 10 to 15 minutes. You can stop whenever you want.",
        "contrato_boundary": (
            "I work with you only on the professional — how this pattern shows up in your career, "
            "in your work, in how you see yourself as a professional. If the conversation moves "
            "toward the deeply personal, I'll redirect you with respect."
        ),
        "cancelar": "← Cancel",
        "empezar_la_sesion": "START THE SESSION  →",
        "pregunta_cargando": "Mirror is preparing your first question...",
        "escribiendo": "Mirror is typing…",
        "session_hint": "Tell Mirror about your work...",
        "lbl_num": "QUESTION {n:02d}",
        "lbl_num_inicial": "Question {n:02d}",
        "q_fallback_inicial": "Tell me: when does this pattern show up in your work, specifically?",
        "q_fallback_seguir": "Let's keep going: what else do you notice about how this pattern operates in your work?",
        "q_fallback_reanclar": "Let's get back to your work. How does this pattern show up in a concrete work situation?",
        "cierre_fallback": "I think we have enough now to see this pattern from the outside.",
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
        "boundary_eyebrow": "Mirror responds",
        "boundary_1": "What you're sharing is important, and that's exactly why I'm not the one who should be with you there.",
        "boundary_2": (
            "I work only with professional patterns — how they show up in your work, in your career. "
            "For what you're going through, a mental health professional will be far more useful than me."
        ),
        "opcion_a": "Option A",
        "opcion_b": "Option B",
        "boundary_cerrar_titulo": "End the session",
        "boundary_cerrar_desc": "We stop here. The pattern is saved so you can come back to it whenever you want.",
        "boundary_seguir_titulo": "Back to the pattern  →",
        "boundary_seguir_desc": "We return to the professional. I'll ask you a new question about the pattern.",
        "boundary_privacidad": "Your decision stays only between you and the session.\nNothing you shared leaves here.",
        "ver_espejo": "SEE THE MIRROR  →",
        "sin_sesion_cerrar": "There's no session to close.",
        "espejo_eyebrow": "The mirror",
        "espejo_titulo": "This is what we saw",
        "espejo_sub": "Take a moment before closing. What follows is for you, not for your archive.",
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
        "saludo_contexto": 'I see your win «{titulo}». Do you want it as an email or a LinkedIn post?',
        "saludo_sin_contexto": "What do you want to write? Pick a format to start.",
        "speaker_editor": "Editor",
        "chip_correo": "✍  Email",
        "chip_linkedin": "💼  LinkedIn post",
        "chip_otro": "✎  Other format",
        "pedir_formato": "Tell me the format you want (for example: «a bio for my Instagram profile»).",
        "hint_ajuste": "Ask Editor for a tweak...",
        "hint_formato": "Type the format…",
        "pregunta_correo": "Perfect, an email. What's it about and who's it for? Tell me the essentials and I'll write it.",
        "pregunta_linkedin": "Perfect, a LinkedIn post. What win or topic do you want to share? Give me the details and I'll write it.",
        "pregunta_custom": "Perfect, «{formato}». Tell me the essentials and I'll write it.",
        "nudge_formato": "Noted. What format do you want it in? Pick Email or LinkedIn post below, or tell me the format yourself.",
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
        "subtitulo": "Turn your professional work into content to show the world. I speak in your voice, not mine.",
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
        "apertura": "Tell me what happened this week that's worth saving. It doesn't have to be huge.",
        "descripcion": (
            "Your professional chronicler. It documents the wins that matter so that, when you "
            "need them — interviews, reviews, decisions — they're ready."
        ),
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
        "ficha_vacia": "There's no entry to show.",
        "ir_archive": "Go to Archive",
        "recien_eyebrow": "Win archived",
        "recien_texto": "Your win is documented. This is how we recorded it.",
        "del_archivo_eyebrow": "From the archive",
        "del_archivo_texto": "A win you documented with Archive.",
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
        "saludo": "This is what you've built, {nombre}",
        "encuadre": (
            "Sometimes, caught up in the day-to-day, you don't see how far you've come. I do. "
            "I'll show you what you've got before we open the conversation."
        ),
        "boundary": (
            "I help you think before deciding your next professional move. "
            "I'm not a space for personal matters — for that, a professional."
        ),
        "camino_activo": "Active path",
        "acciones_pacer": "{hechas} / {total} actions",
        "ahora_tu": "Now you",
        "invitacion": (
            "Now that you've seen where you are, what's on your mind today? Tell me what situation "
            "you want to think through before deciding your next move."
        ),
        "hint_espejo": "Whatever's on your mind...",
        "empezar": "START  →",
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
        "sin_conversacion": "There's no conversation to close.",
        "ir_clarity": "Go to Clarity",
        "tres_caminos": "Three paths",
        "puertas_titulo": "What comes next is up to you",
        "puertas_helper": "You don't have to pick one. But something helps you land what you thought through.",
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
