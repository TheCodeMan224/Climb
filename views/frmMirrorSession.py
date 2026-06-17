"""Mirror · Pantalla 3: sesión socrática activa (focus mode) + boundary inline.

Muestra el patrón ancla, la pregunta socrática y el input. Si una respuesta
cruza del ámbito profesional a lo personal profundo, el centro se reemplaza por
el bloque boundary (redirección con respeto).

NOTA(Claude): las preguntas y la detección de boundary son MOCK por ahora; ver
los TODO marcados (Claude-Q, Claude-B).
"""

import traceback
from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes, clsMirror
from core.textos import TEXTOS
from data import clsInteraccionDB

_T = TEXTOS["mirror"]
_PREGUNTA_CARGANDO = _T["pregunta_cargando"]


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
        self.lbl_num = cmp.eyebrow(_T["lbl_num_inicial"].format(n=self.question_number), color=tema.HINT, size=10)
        self.col_historial = ft.Column(spacing=0, visible=False)
        self.col_centro = ft.Column(spacing=0)
        self.footer = ft.Container()
        self.lbl_camino = ft.Text("", size=11, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.BLUE)
        self.campo = ft.TextField(
            hint_text=_T["session_hint"],
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
            q = _T["q_fallback_inicial"]
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
        self.txt_pregunta.value = _T["escribiendo"]
        self.router.page.update()

        try:
            es_boundary = await clsAgentes.mirror_es_boundary(texto)
        except Exception:
            traceback.print_exc()
            es_boundary = False

        revelar = None
        if es_boundary:
            self.boundary_triggered = True
        else:
            try:
                q = await clsAgentes.mirror_pregunta(self.patron.quote, self.turns, self.id_usuario)
            except Exception:
                traceback.print_exc()  # error real en consola para diagnóstico
                q = _T["q_fallback_seguir"]
            if "[LISTO]" in q:
                # Mirror considera que ya tiene suficiente: cierra la conversación.
                self.cierre = True
                self.cierre_texto = q.replace("[LISTO]", "").strip() or _T["cierre_fallback"]
            else:
                self.question_number += 1
                self.current_question = q
                self.lbl_num.value = _T["lbl_num"].format(n=self.question_number)
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
        self.txt_pregunta.value = _T["escribiendo"]
        self._render_centro()
        self.footer.visible = True
        self.router.page.update()
        try:
            q = await clsAgentes.mirror_pregunta(self.patron.quote, self.turns, self.id_usuario, reanclar=True)
        except Exception:
            q = _T["q_fallback_reanclar"]
        self.question_number += 1
        self.current_question = q
        self.lbl_num.value = _T["lbl_num"].format(n=self.question_number)
        self.router.page.update()
        await cmp.revelar_texto(self.txt_pregunta, q)

    def _toggle_historial(self, e):
        self.historial_visible = not self.historial_visible
        self._render_historial()
        self.router.page.update()

    async def _terminar(self, e):
        self.router.mostrar_carga(_T["generando_espejo"])
        try:
            rf = await clsAgentes.mirror_reframe(self.patron.quote, self.turns)
        except Exception:
            traceback.print_exc()
            self.router.ocultar_carga()
            self.router.page.show_dialog(ft.SnackBar(ft.Text(_T["error_espejo"])))
            self.router.page.update()
            return
        self.router.mirror_reframe = clsMirror.MirrorReframe(**rf)
        self.router.mirror_minutos = max(1, int((datetime.now() - self._inicio).total_seconds() // 60))
        self.router.navegar_a("/mirror/espejo")

    # --- Render -------------------------------------------------------------
    def _render_historial(self):
        self.lbl_camino.value = _T["ver_camino"].format(flecha='▾' if self.historial_visible else '▸', n=len(self.turns))
        self.col_historial.visible = self.historial_visible and bool(self.turns)
        filas = []
        for speaker, texto in self.turns:
            es_mirror = speaker == "mirror"
            filas.append(ft.Container(
                margin=ft.Margin.only(bottom=22),
                content=ft.Column(spacing=6, controls=[
                    cmp.eyebrow(_T["nombre"] if es_mirror else TEXTOS["comun"]["tu"], color=tema.AMBAR if es_mirror else tema.MUTED, size=10),
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
            content=ft.Text(TEXTOS["comun"]["enviar"], size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
            on_click=self._enviar,
            style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=24, vertical=14), elevation=0),
        )
        return ft.Column(spacing=0, controls=[
            ft.Column(spacing=0, controls=[
                cmp.eyebrow(_T["mirror_pregunta"], color=tema.AMBAR),
                ft.Container(height=18),
                ft.Container(width=620, content=self.txt_pregunta),
            ]),
            ft.Container(height=48),
            ft.Column(spacing=0, controls=[
                cmp.eyebrow(_T["tu_respuesta"], color=tema.MUTED),
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
                        cmp.eyebrow(_T["boundary_eyebrow"], color=tema.AMBAR),
                        ft.Text(_T["boundary_1"], size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                        ft.Text(_T["boundary_2"], size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                    ]),
                ),
                ft.Container(height=32),
                ft.Row(spacing=14, controls=[
                    self._opcion_boundary(_T["opcion_a"], _T["boundary_cerrar_titulo"], _T["boundary_cerrar_desc"], self._cerrar_boundary),
                    self._opcion_boundary(_T["opcion_b"], _T["boundary_seguir_titulo"], _T["boundary_seguir_desc"], self._continuar_boundary, primaria=True),
                ]),
                ft.Container(height=24),
                ft.Text(_T["boundary_privacidad"], size=13, italic=True, font_family=tema.FUENTE_SERIF, color=tema.HINT, text_align=ft.TextAlign.CENTER),
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
                        cmp.eyebrow(_T["nombre"], color=tema.AMBAR),
                        ft.Text(self.cierre_texto, size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                    ]),
                ),
                ft.Container(height=28),
                ft.Row(controls=[
                    ft.ElevatedButton(
                        content=ft.Text(_T["ver_espejo"], size=13, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
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
                        ft.Text(_T["sin_patron_sesion"], size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                        cmp.boton_primario(_T["ir_mirror"], on_click=lambda e: self.router.navegar_a("/mirror")),
                    ],
                ),
            )

        self._render_historial()
        self._render_centro()

        topbar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=8, controls=[cmp.eyebrow(TEXTOS["comun"]["marca"], color=tema.AMBAR), cmp.eyebrow(_T["subtopbar"], color=tema.HINT)]),
                ft.Container(
                    border=ft.Border.all(1, tema.BORDER_LIGHT),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=5),
                    border_radius=3,
                    content=cmp.eyebrow(_T["ambito"], color=tema.AMBAR, size=11),
                ),
            ],
        )

        ancla = ft.Container(
            padding=ft.Padding.symmetric(vertical=14),
            border=ft.Border.symmetric(vertical=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    cmp.eyebrow(_T["patron"], color=tema.AMBAR, size=10),
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
                    cmp.enlace_cta(_T["terminar_sesion"], on_click=self._terminar, color=tema.AMBAR),
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
