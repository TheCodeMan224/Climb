"""Pantalla narrativa que introduce a Scout. No ejecuta backend."""

import flet as ft
import tema


class frmScoutReflection:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario

    def construir(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=40,
            content=ft.Container(
                width=560,
                padding=48,
                bgcolor=tema.SUPERFICIE,
                border_radius=22,
                shadow=ft.BoxShadow(blur_radius=50, color="#00000055"),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=22,
                    controls=[
                        ft.Text(
                            "Conoce a Scout",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            font_family=tema.FUENTE_DISPLAY,
                            color=tema.TEXTO,
                        ),
                        ft.Text(
                            "Scout es tu explorador. Va a leer con calma todo lo que "
                            "compartiste y a mapear los patrones conductuales que "
                            "definen tu momento profesional: lo que te impulsa, lo que "
                            "te frena y dónde está la brecha que aún no ves.",
                            size=17,
                            color=tema.TEXTO,
                            text_align=ft.TextAlign.CENTER,
                            font_family=tema.FUENTE_BODY,
                        ),
                        ft.Text(
                            "Tus respuestas serán analizadas para construir tu "
                            "diagnóstico cualitativo.",
                            size=15,
                            italic=True,
                            color=tema.TEXTO_SUAVE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Iniciar Diagnóstico Cualitativo",
                            on_click=lambda e: self.router.navegar_a("/progreso"),
                            style=ft.ButtonStyle(
                                bgcolor=tema.NAVY,
                                color=tema.TEXTO_SOBRE_NAVY,
                                padding=ft.Padding.symmetric(horizontal=36, vertical=20),
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                    ],
                ),
            ),
        )
