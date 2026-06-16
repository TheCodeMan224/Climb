"""Editor · Estudio de redacción en dos paneles.

Izquierda: el borrador (entregable) renderizado según el formato (LinkedIn / correo),
listo para copiar. Derecha: chat para iterarlo, con chips de ajuste dinámicos.
Puede abrirse enfocado en un logro que viene desde Archive (router.editor_contexto).
"""

import json
import traceback

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes
from data import clsInteraccionDB


class frmEditor:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.nombre = clsInteraccionDB.obtener_nombre_usuario(self.id_usuario) or router.nombre or "Tú"

        # Borrador a retomar (None = nuevo). Se consume del router.
        self.borrador_id = router.editor_borrador_id
        router.editor_borrador_id = None

        self.contexto = router.editor_contexto
        router.editor_contexto = None

        self.formato = None          # "linkedin" | "correo" | etiqueta libre
        self.es_correo = False       # cómo renderizar el preview
        self.borrador = ""
        self.asunto = ""
        self.turns = []              # (speaker, texto): "editor" | "user"
        self.historial = []          # pila de (borrador, asunto) para "Versión anterior"
        self.sugerencias = []
        self.esperando_formato = False  # True tras pulsar "Otro formato": el siguiente texto es el formato

        # Si retomamos un borrador guardado, cargamos su estado.
        if self.borrador_id:
            d = clsInteraccionDB.obtener_borrador_editor(self.borrador_id)
            if d:
                self.formato = d.get("formato") or None
                self.es_correo = bool(d.get("es_correo"))
                self.asunto = d.get("asunto") or ""
                self.borrador = d.get("borrador") or ""
                self.contexto = json.loads(d["contexto_json"]) if d.get("contexto_json") else None
                self.turns = [tuple(t) for t in json.loads(d["turns_json"])] if d.get("turns_json") else []

        self.contexto_texto = self._formatear_logro(self.contexto) if self.contexto else ""

        # Controles que se actualizan en vivo.
        self.panel_izq = ft.Container(expand=True)
        self.chat_list = ft.ListView(expand=True, spacing=18, padding=ft.Padding.symmetric(horizontal=24, vertical=20), auto_scroll=True)
        self.chips_row = ft.Row(wrap=True, spacing=8, run_spacing=8)
        self.lbl_formato = cmp.eyebrow("Editor", color=tema.HINT)
        self.campo = ft.TextField(
            hint_text="Pídele a Editor un ajuste...",
            expand=True, multiline=True, min_lines=1, max_lines=4,
            border=ft.InputBorder.NONE, bgcolor="transparent", cursor_color=tema.NAVY,
            text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=14, color=tema.NAVY),
            hint_style=ft.TextStyle(font_family=tema.FUENTE_SERIF, italic=True, size=14, color=tema.HINT),
            on_submit=self._enviar_input,
        )

    # --- Contexto del logro -------------------------------------------------
    def _formatear_logro(self, logro):
        partes = ["Logro a redactar (materia prima, no inventes datos):"]
        for clave, etiqueta in [("titulo", "Título"), ("tipo", "Tipo"), ("contexto", "Contexto"), ("mi_rol", "Mi rol"), ("aprendizaje", "Aprendizaje")]:
            if logro.get(clave):
                partes.append(f"- {etiqueta}: {logro[clave]}")
        metrics = logro.get("metrics") or []
        if metrics:
            partes.append("- Métricas: " + ", ".join(f"{m.get('value','')} ({m.get('label','')})" for m in metrics))
        if logro.get("tags"):
            partes.append("- Tags: " + ", ".join(logro["tags"]))
        return "\n".join(partes)

    # --- Panel izquierdo: preview estilado ---------------------------------
    def _avatar(self):
        iniciales = "".join(p[0] for p in self.nombre.split()[:2]).upper() or "Y"
        return ft.Container(width=46, height=46, border_radius=23, bgcolor=tema.NAVY,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(iniciales, size=15, weight=ft.FontWeight.W_700, color=tema.TEXTO_SOBRE_NAVY))

    def _preview_linkedin(self):
        return ft.Column(spacing=0, controls=[
            ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                self._avatar(),
                ft.Column(spacing=2, controls=[
                    ft.Text(self.nombre, size=15, weight=ft.FontWeight.W_700, color=tema.NAVY, font_family=tema.FUENTE_SUBHEADER),
                    cmp.eyebrow("Hace unos segundos · 🌐", color=tema.HINT, size=10),
                ]),
            ]),
            ft.Container(height=18),
            ft.Container(height=1, bgcolor=tema.BORDER_LIGHT),
            ft.Container(height=18),
            ft.Text(self.borrador, size=15, color=tema.NAVY, font_family=tema.FUENTE_BODY),
            ft.Container(height=18),
            ft.Container(height=1, bgcolor=tema.BORDER_LIGHT),
            ft.Container(height=12),
            ft.Row(spacing=24, controls=[
                cmp.eyebrow("👍 Me gusta", color=tema.HINT, size=10),
                cmp.eyebrow("💬 Comentar", color=tema.HINT, size=10),
                cmp.eyebrow("↗ Compartir", color=tema.HINT, size=10),
            ]),
        ])

    def _preview_correo(self):
        return ft.Column(spacing=0, controls=[
            cmp.eyebrow("Asunto", color=tema.MUTED, size=10),
            ft.Container(height=6),
            ft.Text(self.asunto or "(sin asunto)", size=18, weight=ft.FontWeight.W_700, color=tema.NAVY, font_family=tema.FUENTE_SUBHEADER),
            ft.Container(height=18),
            ft.Container(height=1, bgcolor=tema.BORDER_LIGHT),
            ft.Container(height=18),
            ft.Text(self.borrador, size=15, color=tema.NAVY, font_family=tema.FUENTE_BODY),
        ])

    def _render_preview(self):
        if not self.borrador:
            self.panel_izq.content = ft.Container(
                alignment=ft.Alignment.CENTER, padding=40,
                content=ft.Text("Tu borrador aparecerá aquí, listo para copiar." if self.formato
                                else "Elige un formato en el chat para empezar a redactar.",
                                size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED, text_align=ft.TextAlign.CENTER),
            )
            return
        cuerpo = self._preview_correo() if self.es_correo else self._preview_linkedin()
        self.panel_izq.content = ft.Column(spacing=14, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.END, controls=[
                cmp.enlace_cta("📋 Copiar", on_click=self._copiar),
            ]),
            ft.Container(
                bgcolor=tema.SUPERFICIE, border=ft.Border.all(1, tema.BORDER_LIGHT), border_radius=8,
                padding=ft.Padding.symmetric(horizontal=32, vertical=28), content=cuerpo,
            ),
        ])

    # --- Chat + chips -------------------------------------------------------
    def _render_chat(self):
        filas = []
        if not self.turns:
            saludo = (f"Veo tu logro «{self.contexto.get('titulo','')}». ¿Lo quieres como correo o como post de LinkedIn?"
                      if self.contexto else "¿Qué quieres redactar? Elige un formato para empezar.")
            filas.append(self._turno_chat("editor", saludo))
        for s, t in self.turns:
            filas.append(self._turno_chat(s, t))
        self.chat_list.controls = filas

    def _turno_chat(self, speaker, texto):
        es_editor = speaker == "editor"
        return ft.Column(spacing=6, controls=[
            cmp.eyebrow("Editor" if es_editor else "Tú", color=tema.AMBAR if es_editor else tema.MUTED, size=10),
            ft.Text(texto, size=14, color=tema.NAVY if es_editor else tema.MUTED,
                    italic=not es_editor, font_family=tema.FUENTE_BODY if es_editor else tema.FUENTE_SERIF),
        ])

    def _chip(self, etiqueta, on_click):
        return ft.OutlinedButton(
            content=ft.Text(etiqueta, size=12, font_family=tema.FUENTE_SUBHEADER, color=tema.BLUE),
            on_click=on_click,
            style=ft.ButtonStyle(side=ft.BorderSide(1, tema.BORDER_LIGHT), shape=ft.RoundedRectangleBorder(radius=4),
                                 padding=ft.Padding.symmetric(horizontal=12, vertical=8)),
        )

    def _render_chips(self):
        if not self.formato:
            self.chips_row.controls = [
                self._chip("✍  Correo", lambda e: self.router.page.run_task(self._set_formato, "correo")),
                self._chip("💼  Post de LinkedIn", lambda e: self.router.page.run_task(self._set_formato, "linkedin")),
                self._chip("✎  Otro formato", lambda e: self._pedir_formato_custom()),
            ]
        else:
            self.chips_row.controls = [
                self._chip(s, lambda e, x=s: self.router.page.run_task(self._enviar, x)) for s in self.sugerencias
            ]

    # --- Formato ------------------------------------------------------------
    def _es_correo(self, formato):
        f = (formato or "").strip().lower()
        return f in ("correo", "email", "mail") or "correo" in f or "email" in f

    def _label_formato(self, formato):
        f = (formato or "").strip().lower()
        if f == "linkedin":
            return "POST · LINKEDIN"
        if self._es_correo(formato):
            return "CORREO"
        return (formato or "EDITOR").upper()[:28]

    def _pedir_formato_custom(self):
        # El siguiente texto que escriba el usuario será el formato.
        self.esperando_formato = True
        self.turns.append(("editor", "Dime el formato que quieres (por ejemplo: «bio para mi perfil de Instagram»)."))
        self.campo.hint_text = "Escribe el formato…"
        self._render_chat()
        self.chips_row.controls = []
        self.router.page.update()

    async def _set_formato(self, formato):
        self.formato = formato
        self.es_correo = self._es_correo(formato)
        self.lbl_formato.value = self._label_formato(formato)
        # Si ya hay materia prima (contexto de Archive o algo que el usuario escribió),
        # redactamos. Si no, Editor pide el material en vez de inventar.
        tiene_brief = bool(self.contexto) or any(s == "user" for s, _ in self.turns)
        if tiene_brief:
            await self._generar()
            return
        if self.es_correo:
            pregunta = "Perfecto, un correo. ¿Sobre qué es y a quién va dirigido? Cuéntame lo esencial y lo redacto."
        elif (formato or "").lower() == "linkedin":
            pregunta = "Perfecto, un post de LinkedIn. ¿Qué logro o tema quieres compartir? Dame los datos y lo redacto."
        else:
            pregunta = f"Perfecto, «{formato}». Cuéntame lo esencial y lo redacto."
        self.turns.append(("editor", pregunta))
        self.sugerencias = []
        self._actualizar_todo()

    async def _enviar_input(self, e):
        texto = (self.campo.value or "").strip()
        if texto:
            self.campo.value = ""
            await self._enviar(texto)

    def _registrar_texto(self, instruccion):
        clsInteraccionDB.registrar_texto_usuario(self.id_usuario, "editor", instruccion)
        self.router.page.run_task(clsAgentes.actualizar_voice_profile_si_toca, self.id_usuario)

    async def _enviar(self, instruccion):
        instruccion = (instruccion or "").strip()
        if not instruccion:
            return

        # Caso 1: el usuario está definiendo un formato personalizado.
        if self.esperando_formato and not self.formato:
            self.esperando_formato = False
            self.campo.hint_text = "Pídele a Editor un ajuste..."
            self.turns.append(("user", instruccion))
            self._registrar_texto(instruccion)
            await self._set_formato(instruccion)
            return

        # Caso 2: aún no hay formato. Guardamos lo que escribió (no se ignora) y pedimos formato.
        if not self.formato:
            self.turns.append(("user", instruccion))
            self._registrar_texto(instruccion)
            self.turns.append(("editor", "Anotado. ¿En qué formato lo quieres? Elige Correo o Post de LinkedIn abajo, o dime tú el formato."))
            self._render_chat()
            self._render_chips()
            self.router.page.update()
            return

        # Caso 3: ya hay formato. Generamos/editamos el borrador.
        self.turns.append(("user", instruccion))
        self._registrar_texto(instruccion)
        await self._generar()

    async def _generar(self):
        self._render_chat()
        self.router.mostrar_carga("Editor está redactando…")
        try:
            res = await clsAgentes.editor_estudio(self.id_usuario, self.formato, self.contexto_texto, self.borrador, self.turns)
        except Exception:
            traceback.print_exc()
            self.router.ocultar_carga()
            self.turns.append(("editor", "Tuve un problema. Intenta de nuevo."))
            self._render_chat()
            self.router.page.update()
            return
        if self.borrador:
            self.historial.append((self.borrador, self.asunto))
        self.borrador = res["borrador"]
        self.asunto = res["asunto"]
        self.sugerencias = res["sugerencias"]
        self.turns.append(("editor", res["comentario"]))
        self._persistir()
        self._actualizar_todo()
        self.router.ocultar_carga()

    async def _regenerar(self, e=None):
        if self.formato:
            self.turns.append(("user", "Regenera el borrador desde cero, mismo formato y material."))
            await self._generar()

    def _version_anterior(self, e=None):
        if not self.historial:
            return
        self.borrador, self.asunto = self.historial.pop()
        self.turns.append(("editor", "Volví a la versión anterior."))
        self._persistir()
        self._actualizar_todo()

    # --- Persistencia -------------------------------------------------------
    def _persistir(self):
        """Crea o actualiza el borrador en la base de datos (solo si hay contenido)."""
        if not self.borrador:
            return
        contexto_json = json.dumps(self.contexto, ensure_ascii=False, default=str) if self.contexto else None
        turns_json = json.dumps(self.turns, ensure_ascii=False)
        if self.borrador_id is None:
            self.borrador_id = clsInteraccionDB.crear_borrador_editor(
                self.id_usuario, self.formato, self.es_correo, self.asunto, self.borrador, contexto_json, turns_json)
        else:
            clsInteraccionDB.actualizar_borrador_editor(
                self.borrador_id, self.formato, self.es_correo, self.asunto, self.borrador, turns_json)

    def _completar(self, e=None):
        if not self.borrador:
            self.router.page.show_dialog(ft.SnackBar(ft.Text("Aún no hay borrador para marcar como completado.")))
            self.router.page.update()
            return
        self._persistir()
        if self.borrador_id:
            clsInteraccionDB.marcar_borrador_estado(self.borrador_id, "completado")
        self.router.navegar_a("/editor")

    def _copiar(self, e=None):
        texto = (f"Asunto: {self.asunto}\n\n{self.borrador}" if (self.es_correo and self.asunto) else self.borrador)
        # clipboard.set es async en flet 0.85: lo agendamos.
        self.router.page.run_task(self.router.page.clipboard.set, texto or "")
        self.router.page.show_dialog(ft.SnackBar(ft.Text("Borrador copiado al portapapeles.")))
        self.router.page.update()

    def _actualizar_todo(self):
        self._render_preview()
        self._render_chat()
        self._render_chips()
        self.router.page.update()

    # --- Construcción -------------------------------------------------------
    def _boton_toolbar(self, etiqueta, on_click, primario=False):
        if primario:
            return ft.ElevatedButton(
                content=ft.Text(etiqueta, size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                on_click=on_click,
                style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=18, vertical=14), elevation=0),
            )
        return ft.OutlinedButton(
            content=ft.Text(etiqueta, size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY),
            on_click=on_click,
            style=ft.ButtonStyle(side=ft.BorderSide(1, tema.BORDER_LIGHT), shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=16, vertical=14)),
        )

    def construir(self):
        if self.formato:
            self.lbl_formato.value = self._label_formato(self.formato)
        self._render_preview()
        self._render_chat()
        self._render_chips()

        topbar = ft.Container(
            # right amplio: deja libre la esquina donde el overlay fija el chip del handle.
            padding=ft.Padding.only(left=28, top=18, right=168, bottom=18),
            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=tema.NAVY, tooltip="Volver a Editor", on_click=lambda e: self.router.navegar_a("/editor")),
                    cmp.eyebrow("Climb · Editor", color=tema.AMBAR),
                    self.lbl_formato,
                ]),
                ft.Row(spacing=10, controls=[
                    self._boton_toolbar("← Versión anterior", lambda e: self._version_anterior()),
                    self._boton_toolbar("↻ Regenerar todo", lambda e: self.router.page.run_task(self._regenerar)),
                    self._boton_toolbar("✓ Completar", lambda e: self._completar(), primario=True),
                ]),
            ]),
        )

        banner = None
        if self.contexto:
            banner = ft.Container(
                margin=ft.Margin.symmetric(horizontal=28),
                padding=ft.Padding.symmetric(horizontal=18, vertical=14),
                bgcolor=tema.SUPERFICIE, border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)), border_radius=4,
                content=ft.Row(spacing=10, controls=[
                    cmp.eyebrow("Basado en · Archivo", color=tema.HINT, size=10),
                    ft.Text(f'"{self.contexto.get("titulo","")}"', size=13, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                ]),
            )

        panel_izq = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[
            ft.Container(padding=ft.Padding.symmetric(horizontal=28, vertical=24), content=self.panel_izq),
        ])

        entrada = ft.Container(
            padding=ft.Padding.symmetric(horizontal=24, vertical=14),
            border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.END, controls=[
                self.campo,
                ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=tema.NAVY, on_click=self._enviar_input),
            ]),
        )
        panel_der = ft.Container(
            width=440,
            border=ft.Border.only(left=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Column(expand=True, spacing=0, controls=[
                self.chat_list,
                ft.Container(padding=ft.Padding.symmetric(horizontal=24, vertical=10), content=self.chips_row),
                entrada,
            ]),
        )

        cuerpo = ft.Row(expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH, spacing=0, controls=[panel_izq, panel_der])

        controles = [topbar]
        if banner:
            controles.append(banner)
        controles.append(ft.Container(expand=True, content=cuerpo))

        return ft.Column(expand=True, spacing=0, controls=controles)
