"""Mirror · Pantalla 2: entrada ceremonial con el contexto del patrón.

Muestra el patrón a trabajar y el "contrato" de la sesión antes de empezar.
Lee el patrón seleccionado de router.mirror_patron.
"""

import flet as ft

import componentes as cmp
import tema
from core.textos import TEXTOS

_T = TEXTOS["mirror"]


class frmMirrorEntry:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.patron = router.mirror_patron

    def _cancelar(self, e):
        self.router.navegar_a("/mirror")

    def _empezar(self, e):
        self.router.navegar_a("/mirror/session")

    def construir(self):
        if not self.patron:
            return ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Text(_T["sin_patron"], size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                        cmp.boton_primario(_T["ir_mirror"], on_click=lambda e: self.router.navegar_a("/mirror")),
                    ],
                ),
            )

        agente = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                ft.Text("01", size=56, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                ft.Container(height=14),
                ft.Text(_T["nombre"], size=44, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ft.Container(height=18),
                cmp.hairline(width=48),
                ft.Container(height=22),
                ft.Container(
                    width=460,
                    content=ft.Text(
                        _T["descripcion"],
                        size=14, font_family=tema.FUENTE_BODY, color=tema.MUTED, text_align=ft.TextAlign.CENTER,
                    ),
                ),
            ],
        )

        patron_bloque = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                cmp.eyebrow(_T["patron_hoy"], color=tema.MUTED),
                ft.Container(height=24),
                ft.Container(
                    width=600,
                    padding=ft.Padding.only(left=28),
                    border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
                    content=ft.Text(f'"{self.patron.quote}"', size=24, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                ),
                ft.Container(height=20),
                cmp.eyebrow(self.patron.detected_meta, color=tema.HINT, size=11),
            ],
        )

        contrato = ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=36, vertical=32),
            content=ft.Column(
                spacing=16,
                controls=[
                    cmp.eyebrow(_T["antes_empezar"], color=tema.AMBAR),
                    ft.Text(_T["contrato_1"], size=15, font_family=tema.FUENTE_BODY, color=tema.NAVY),
                    ft.Text(_T["contrato_2"], size=15, font_family=tema.FUENTE_BODY, color=tema.NAVY),
                    ft.Container(
                        margin=ft.Margin.only(top=4),
                        padding=ft.Padding.only(top=18),
                        border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
                        content=ft.Text(_T["contrato_boundary"], size=14, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                    ),
                ],
            ),
        )

        acciones = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                cmp.enlace_cta(_T["cancelar"], on_click=self._cancelar),
                ft.ElevatedButton(
                    content=ft.Text(_T["empezar_la_sesion"], size=13, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                    on_click=self._empezar,
                    style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=38, vertical=18), elevation=0),
                ),
            ],
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=820,
                    padding=ft.Padding.symmetric(horizontal=64, vertical=44),
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            cmp.topbar(_T["topbar"], derecha=TEXTOS["comun"]["volver"], on_back=self._cancelar),
                            ft.Container(height=56),
                            agente,
                            ft.Container(height=56),
                            patron_bloque,
                            ft.Container(height=56),
                            contrato,
                            ft.Container(height=36),
                            acciones,
                            ft.Container(height=48),
                        ],
                    ),
                )
            ],
        )
