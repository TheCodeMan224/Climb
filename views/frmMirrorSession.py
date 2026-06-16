"""Mirror · Pantalla 3: sesión socrática activa (focus mode) + boundary inline.

Muestra el patrón ancla, la pregunta socrática y el input. Si una respuesta
cruza del ámbito profesional a lo personal profundo, el centro se reemplaza por
el bloque boundary (redirección con respeto).

NOTA(Claude): las preguntas y la detección de boundary son MOCK por ahora; ver
los TODO marcados (Claude-Q, Claude-B).
"""

from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes, clsMirror
from data import clsInteraccionDB

_PREGUNTA_CARGANDO = "Mirror está preparando tu primera pregunta..."


class frmMirrorSession:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.patron = router.mirror_patron

        self.turns = []
        self.question_number = 1
        self.current_question = _PREGUNTA_CARGANDO
        self.historial_visible = False
        self.boundary_triggered = False
        self.cierre = False
        self.cierre_texto = ""
        self._inicio = datetime.now()

        self.txt_pregunta = ft.Text(self.current_question, size=28, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY)
        self.lbl_num = cmp.eyebrow(f"Pregunta {self.question_number:02d}", color=tema.HINT, size=10)
        self.col_historial = ft.Column(spacing=0, visible=False)
        self.col_centro = ft.Column(spacing=0)
        self.footer = ft.Container()
        self.lbl_camino = ft.Text("", size=11, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.BLUE)
        self.campo = ft.TextField(
            hint_text="Cuéntale a Mirror sobre tu trabajo...",
            multiline=True, min_lines=3, max_lines=8, expand=True,
            border=ft.InputBorder.NONE, bgcolor="transparent", cursor_color=tema.NAVY,
            text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=16, color=tema.NAVY),
            hint_style=ft.TextStyle(font_family=tema.FUENTE_SERIF, italic=True, size=16, color=tema.HINT),
            content_padding=ft.Padding.symmetric(horizontal=0, vertical=6),
        )

    # --- Carga inicial: primera pregunta -----------------------------------
    async def al_cargar(self):
        if not self.patron or self.turns:
            return
        try:
            q = await clsAgentes.mirror_pregunta(self.patron.quote, [], self.id_usuario)
        except Exception:
            q = "Cuéntame: ¿cuándo aparece este patrón en tu trabajo, concretamente?"
        self.current_question = q
        await cmp.revelar_texto(self.txt_pregunta, q)

    # --- Eventos ------------------------------------------------------------
    async def _enviar(self, e):
        texto = (self.campo.value or "").strip()
        if not texto:
            return
        self.turns.append(("mirror", self.current_question))
        self.turns.append(("user", texto))
        clsInteraccionDB.registrar_texto_usuario(self.id_usuario, "mirror", texto)
        self.router.page.run_task(clsAgentes.actualizar_voice_profile_si_toca, self.id_usuario)
        self.campo.value = ""
        self.campo.disabled = True
        self.txt_pregunta.value = "Mirror está escribiendo…"
        self.router.page.update()

        try:
            es_boundary = await clsAgentes.mirror_es_boundary(texto)
        except Exception:
            es_boundary = False

        revelar = None
        if es_boundary:
            self.boundary_triggered = True
        else:
            try:
                q = await clsAgentes.mirror_pregunta(self.patron.quote, self.turns, self.id_usuario)
            except Exception:
                q = "Sigamos: ¿qué más notas de cómo este patrón opera en tu trabajo?"
            if "[LISTO]" in q:
                # Mirror considera que ya tiene suficiente: cierra la conversación.
                self.cierre = True
                self.cierre_texto = q.replace("[LISTO]", "").strip() or "Creo que ya tenemos suficiente para ver este patrón desde fuera."
            else:
                self.question_number += 1
                self.current_question = q
                self.lbl_num.value = f"PREGUNTA {self.question_number:02d}"
                revelar = q

        self.campo.disabled = False
        self._render_centro()
        self.footer.visible = not (self.boundary_triggered or self.cierre)
        self._render_historial()
        self.router.page.update()
        if revelar is not None:
            await cmp.revelar_texto(self.txt_pregunta, revelar)

    def _cerrar_boundary(self, e):
        # El patrón queda guardado (pending) para retomarlo cuando quiera.
        self.router.navegar_a("/mirror")

    async def _continuar_boundary(self, e):
        self.boundary_triggered = False
        self.txt_pregunta.value = "Mirror está escribiendo…"
        self._render_centro()
        self.footer.visible = True
        self.router.page.update()
        try:
            q = await clsAgentes.mirror_pregunta(self.patron.quote, self.turns, self.id_usuario, reanclar=True)
        except Exception:
            q = "Volvamos a tu trabajo. ¿Cómo aparece este patrón en una situación laboral concreta?"
        self.question_number += 1
        self.current_question = q
        self.lbl_num.value = f"PREGUNTA {self.question_number:02d}"
        self.router.page.update()
        await cmp.revelar_texto(self.txt_pregunta, q)

    def _toggle_historial(self, e):
        self.historial_visible = not self.historial_visible
        self._render_historial()
        self.router.page.update()

    async def _terminar(self, e):
        self.router.mostrar_carga("Generando el espejo…")
        try:
            rf = await clsAgentes.mirror_reframe(self.patron.quote, self.turns)
        except Exception:
            self.router.ocultar_carga()
            self.router.page.show_dialog(ft.SnackBar(ft.Text("No pude generar el espejo. Intenta de nuevo.")))
            self.router.page.update()
            return
        self.router.mirror_reframe = clsMirror.MirrorReframe(**rf)
        self.router.mirror_minutos = max(1, int((datetime.now() - self._inicio).total_seconds() // 60))
        self.router.navegar_a("/mirror/espejo")

    # --- Render -------------------------------------------------------------
    def _render_historial(self):
        self.lbl_camino.value = f"{'▾' if self.historial_visible else '▸'} VER EL CAMINO RECORRIDO ({len(self.turns)} TURNOS)"
        self.col_historial.visible = self.historial_visible and bool(self.turns)
        filas = []
        for speaker, texto in self.turns:
            es_mirror = speaker == "mirror"
            filas.append(ft.Container(
                margin=ft.Margin.only(bottom=22),
                content=ft.Column(spacing=6, controls=[
                    cmp.eyebrow("Mirror" if es_mirror else "Tú", color=tema.AMBAR if es_mirror else tema.MUTED, size=10),
                    ft.Container(width=560, content=ft.Text(
                        f'"{texto}"' if es_mirror else texto, size=13, italic=es_mirror,
                        font_family=tema.FUENTE_SERIF if es_mirror else tema.FUENTE_BODY,
                        color=tema.NAVY if es_mirror else tema.MUTED)),
                    ft.Container(height=12),
                    ft.Container(width=16, height=1, bgcolor=tema.BORDER_LIGHT),
                ]),
            ))
        self.col_historial.controls = filas

    def _bloque_pregunta(self):
        boton_enviar = ft.ElevatedButton(
            content=ft.Text("ENVIAR  →", size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
            on_click=self._enviar,
            style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=24, vertical=14), elevation=0),
        )
        return ft.Column(spacing=0, controls=[
            ft.Column(spacing=0, controls=[
                cmp.eyebrow("Mirror pregunta", color=tema.AMBAR),
                ft.Container(height=18),
                ft.Container(width=620, content=self.txt_pregunta),
            ]),
            ft.Container(height=48),
            ft.Column(spacing=0, controls=[
                cmp.eyebrow("Tu respuesta", color=tema.MUTED),
                ft.Container(height=14),
                ft.Container(padding=ft.Padding.only(bottom=12), content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.END, controls=[self.campo, boton_enviar])),
                cmp.subrayado_bicolor(),
            ]),
        ])

    def _opcion_boundary(self, etiqueta, titulo, descripcion, on_click, primaria=False):
        return ft.Container(
            expand=True,
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.NAVY) if primaria else ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=22, vertical=24),
            on_click=on_click,
            ink=True,
            content=ft.Column(spacing=8, controls=[
                cmp.eyebrow(etiqueta, color=tema.MUTED, size=10),
                ft.Text(titulo, size=17, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ft.Text(descripcion, size=12, font_family=tema.FUENTE_BODY, color=tema.MUTED),
            ]),
        )

    def _bloque_boundary(self):
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=40, vertical=36),
            content=ft.Column(spacing=0, controls=[
                ft.Container(
                    padding=ft.Padding.only(left=20),
                    border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
                    content=ft.Column(spacing=18, controls=[
                        cmp.eyebrow("Mirror responde", color=tema.AMBAR),
                        ft.Text("Lo que estás compartiendo es importante, y precisamente por eso no soy yo quien debe acompañarte ahí.", size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                        ft.Text("Yo trabajo solo con patrones profesionales — cómo aparecen en tu trabajo, en tu carrera. Para lo que estás viviendo, un profesional de salud mental va a ser muchísimo más útil que yo.", size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                    ]),
                ),
                ft.Container(height=32),
                ft.Row(spacing=14, controls=[
                    self._opcion_boundary("Opción A", "Cerrar la sesión", "Terminamos aquí. El patrón queda guardado para retomarlo cuando quieras.", self._cerrar_boundary),
                    self._opcion_boundary("Opción B", "Regresar al patrón  →", "Volvemos a lo profesional. Te hago una pregunta nueva sobre el patrón.", self._continuar_boundary, primaria=True),
                ]),
                ft.Container(height=24),
                ft.Text("Tu decisión queda solo entre tú y la sesión.\nNada de lo que compartiste sale de aquí.", size=13, italic=True, font_family=tema.FUENTE_SERIF, color=tema.HINT, text_align=ft.TextAlign.CENTER),
            ]),
        )

    def _bloque_cierre(self):
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=40, vertical=36),
            content=ft.Column(spacing=0, controls=[
                ft.Container(
                    padding=ft.Padding.only(left=20),
                    border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
                    content=ft.Column(spacing=14, controls=[
                        cmp.eyebrow("Mirror", color=tema.AMBAR),
                        ft.Text(self.cierre_texto, size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                    ]),
                ),
                ft.Container(height=28),
                ft.Row(controls=[
                    ft.ElevatedButton(
                        content=ft.Text("VER EL ESPEJO  →", size=13, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                        on_click=self._terminar,
                        style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=32, vertical=18), elevation=0),
                    ),
                ]),
            ]),
        )

    def _render_centro(self):
        if self.boundary_triggered:
            self.col_centro.controls = [self._bloque_boundary()]
        elif self.cierre:
            self.col_centro.controls = [self._bloque_cierre()]
        else:
            self.col_centro.controls = [self._bloque_pregunta()]

    # --- Construcción -------------------------------------------------------
    def construir(self):
        if not self.patron:
            return ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Text("No hay un patrón en sesión.", size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                        cmp.boton_primario("Ir a Mirror", on_click=lambda e: self.router.navegar_a("/mirror")),
                    ],
                ),
            )

        self._render_historial()
        self._render_centro()

        topbar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=8, controls=[cmp.eyebrow("Climb", color=tema.AMBAR), cmp.eyebrow("·  Mirror  ·  Sesión", color=tema.HINT)]),
                ft.Container(
                    border=ft.Border.all(1, tema.BORDER_LIGHT),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=5),
                    border_radius=3,
                    content=cmp.eyebrow("Ámbito · Carrera profesional", color=tema.AMBAR, size=11),
                ),
            ],
        )

        ancla = ft.Container(
            padding=ft.Padding.symmetric(vertical=14),
            border=ft.Border.symmetric(vertical=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    cmp.eyebrow("Patrón", color=tema.AMBAR, size=10),
                    ft.Container(width=14),
                    ft.Container(expand=True, content=ft.Text(f'"{self.patron.quote}"', size=14, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED)),
                    ft.Container(width=14),
                    self.lbl_num,
                ],
            ),
        )

        self.footer = ft.Container(
            padding=ft.Padding.only(top=24),
            border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
            visible=not self.boundary_triggered,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.TextButton(content=self.lbl_camino, on_click=self._toggle_historial, style=ft.ButtonStyle(padding=ft.Padding.symmetric(horizontal=0, vertical=4), overlay_color="transparent")),
                    cmp.enlace_cta("Terminar sesión y ver el espejo  →", on_click=self._terminar, color=tema.AMBAR),
                ],
            ),
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=820,
                    padding=ft.Padding.symmetric(horizontal=64, vertical=36),
                    content=ft.Column(spacing=0, controls=[
                        topbar,
                        ft.Container(height=14),
                        ancla,
                        ft.Container(height=24),
                        self.col_historial,
                        ft.Container(height=32),
                        self.col_centro,
                        ft.Container(height=36),
                        self.footer,
                    ]),
                )
            ],
        )
