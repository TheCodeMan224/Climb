"""Mirror · Pantalla 4: el espejo final / cierre ceremonial.

Muestra el reencuadre (viejo → nuevo) y tres bloques de cierre. Al "resonar",
persiste el patrón como 'observing' con su reframe.

NOTA(Claude): el reframe es MOCK por ahora. La generación real a partir de la
sesión se conecta en el TODO(Claude-R).
"""

import flet as ft

import componentes as cmp
import tema
from core import clsMirror
from core.textos import TEXTOS
from data import clsInteraccionDB

_T = TEXTOS["mirror"]


class frmMirrorEspejo:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.patron = router.mirror_patron
        # Reframe generado por la sesión (Claude) y minutos reales.
        self.reframe = router.mirror_reframe
        self.session_minutes = router.mirror_minutos or 1

    # --- Eventos ------------------------------------------------------------
    def _resono(self, e):
        if self.patron:
            reframe_json = clsMirror.reframe_a_json(self.reframe)
            if str(self.patron.id).startswith("db:"):
                clsInteraccionDB.marcar_patron_procesado(int(self.patron.id.split(":", 1)[1]), reframe_json)
            else:
                clsInteraccionDB.insertar_patron_procesado(
                    self.id_usuario, self.patron.quote, self.patron.source, reframe_json, scout_ref=self.patron.scout_ref,
                )
        self.router.mirror_patron = None
        self.router.navegar_a("/mirror")

    def _seguir(self, e):
        self.router.navegar_a("/mirror/session")

    def _no_resono(self, e):
        self.router.navegar_a("/mirror")

    # --- Bloques ------------------------------------------------------------
    def _bloque(self, label, contenido, italic=False):
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=32, vertical=28),
            content=ft.Column(spacing=14, controls=[
                cmp.eyebrow(label, color=tema.AMBAR),
                ft.Text(contenido, size=18 if italic else 15, italic=italic,
                        font_family=tema.FUENTE_SERIF if italic else tema.FUENTE_BODY, color=tema.NAVY),
            ]),
        )

    def _bloque_recomendaciones(self, items):
        filas = []
        for rec in items:
            filas.append(ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=12,
                controls=[
                    ft.Text("—", size=15, weight=ft.FontWeight.W_700, color=tema.AMBAR),
                    ft.Text(rec, size=15, font_family=tema.FUENTE_BODY, color=tema.NAVY, expand=True),
                ],
            ))
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=32, vertical=28),
            content=ft.Column(spacing=14, controls=[cmp.eyebrow(_T["espejo_recomendaciones"], color=tema.AMBAR), *filas]),
        )

    def _opcion(self, titulo, descripcion, on_click, destacado=False):
        return ft.Container(
            expand=True,
            bgcolor=tema.AMBAR_LIGHT if destacado else tema.SUPERFICIE,
            border=ft.Border.all(1, tema.AMBAR) if destacado else ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=18, vertical=20),
            on_click=on_click,
            ink=True,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Text(titulo, size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY),
                    ft.Text(descripcion, size=11, font_family=tema.FUENTE_BODY, color=tema.MUTED, text_align=ft.TextAlign.CENTER),
                ],
            ),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        if not self.patron or not self.reframe:
            return ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Text(_T["sin_sesion_cerrar"], size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                        cmp.boton_primario(_T["ir_mirror"], on_click=lambda e: self.router.navegar_a("/mirror")),
                    ],
                ),
            )

        rf = self.reframe

        intro = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                cmp.eyebrow(_T["espejo_eyebrow"], color=tema.AMBAR),
                ft.Container(height=14),
                ft.Text(_T["espejo_titulo"], size=44, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ft.Container(height=18),
                cmp.hairline(width=48),
                ft.Container(height=18),
                ft.Container(width=460, content=ft.Text(_T["espejo_sub"], size=16, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED, text_align=ft.TextAlign.CENTER)),
            ],
        )

        transformacion = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(expand=True, padding=ft.Padding.only(right=24), content=ft.Text(f'"{rf.old_quote}"', size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.GRIS_TACHADO, text_align=ft.TextAlign.RIGHT)),
                ft.Container(width=30, content=ft.Text("→", size=20, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR, text_align=ft.TextAlign.CENTER)),
                ft.Container(expand=True, padding=ft.Padding.only(left=24), border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)), content=ft.Text(f'"{rf.new_quote}"', size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY)),
            ],
        )

        acciones = ft.Container(
            padding=ft.Padding.only(top=32),
            border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Column(spacing=18, controls=[
                ft.Container(alignment=ft.Alignment.CENTER, content=cmp.eyebrow(_T["espejo_pregunta_cierre"], color=tema.MUTED)),
                ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                    self._opcion(_T["reson_titulo"], _T["reson_desc"], self._resono, destacado=True),
                    self._opcion(_T["explorar_titulo"], _T["explorar_desc"], self._seguir),
                    self._opcion(_T["no_reson_titulo"], _T["no_reson_desc"], self._no_resono),
                ]),
            ]),
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=820,
                    padding=ft.Padding.symmetric(horizontal=64, vertical=40),
                    content=ft.Column(spacing=0, controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                            ft.Row(spacing=8, controls=[cmp.eyebrow(TEXTOS["comun"]["marca"], color=tema.AMBAR), cmp.eyebrow(_T["espejo_subtopbar"], color=tema.HINT)]),
                            cmp.eyebrow(_T["espejo_sesion_meta"].format(n=self.session_minutes), color=tema.HINT, size=10),
                        ]),
                        ft.Container(height=44),
                        intro,
                        ft.Container(height=56),
                        transformacion,
                        ft.Container(height=56),
                        self._bloque(_T["espejo_lo_que_vimos"], rf.lo_que_vimos),
                        ft.Container(height=24),
                        self._bloque(_T["espejo_manifestacion"], rf.manifestacion),
                        ft.Container(height=24),
                        self._bloque_recomendaciones(rf.recomendaciones),
                        ft.Container(height=48),
                        acciones,
                        ft.Container(height=24),
                        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[cmp.enlace_cta(_T["volver_a_mirror"], on_click=lambda e: self.router.navegar_a("/mirror"))]),
                        ft.Container(height=48),
                    ]),
                )
            ],
        )
