"""Pantalla de bienvenida de Climb."""

import flet as ft

import componentes as cmp
import tema


class frmLanding:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario

    def construir(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=[tema.OFF_WHITE, tema.SECTION_BG],
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    # Logo Climb en dorado
                    ft.Text(
                        "Climb",
                        size=104,
                        weight=ft.FontWeight.W_700,
                        font_family=tema.FUENTE_DISPLAY,
                        color=tema.AMBAR,
                    ),
                    ft.Container(height=28),
                    cmp.hairline(width=56),
                    ft.Container(height=28),
                    # Tagline en serif italic
                    ft.Text(
                        "La mano derecha de tu carrera profesional",
                        size=19,
                        italic=True,
                        font_family=tema.FUENTE_SERIF,
                        color=tema.MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=44),
                    cmp.boton_primario("Comenzar", on_click=lambda e: self.router.navegar_a("/pre_onboarding")),
                    ft.Container(height=22),
                    cmp.enlace("Ya tengo cuenta — Iniciar sesión", on_click=lambda e: self.router.navegar_a("/login")),
                    ft.Container(height=56),
                    # Keywords footer
                    ft.Text(
                        "CONTEXTO  ·  PATRÓN  ·  EJECUCIÓN",
                        size=11,
                        weight=ft.FontWeight.W_600,
                        font_family=tema.FUENTE_SUBHEADER,
                        color=tema.HINT,
                    ),
                ],
            ),
        )
