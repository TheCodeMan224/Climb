"""Pantalla narrativa que introduce a Scout antes del análisis. No ejecuta backend.

El botón principal navega a /progreso, donde corre el diagnóstico cualitativo.
"""

import flet as ft

import componentes as cmp
import tema


class frmScoutReflection:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario

    # --- Bloques ------------------------------------------------------------
    def _topbar(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=8, controls=[
                    cmp.eyebrow("Climb", color=tema.AMBAR),
                    cmp.eyebrow("·  Diagnóstico inicial", color=tema.HINT),
                ]),
                cmp.eyebrow("Paso 01 de 02", color=tema.HINT),
            ],
        )

    def _divisor(self):
        return ft.Container(height=1, bgcolor=tema.BORDER_LIGHT, margin=ft.Margin.symmetric(vertical=28))

    def _paso(self, numero, titulo, descripcion):
        return ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Text(numero, size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                cmp.eyebrow(titulo, color=tema.MUTED, size=11),
                ft.Text(descripcion, size=13, color=tema.BLUE, font_family=tema.FUENTE_BODY, text_align=ft.TextAlign.CENTER),
            ],
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        intro = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                ft.Text("00", size=40, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                ft.Container(height=10),
                ft.Text("Scout", size=52, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ft.Container(height=18),
                cmp.hairline(width=40),
                ft.Container(height=22),
                ft.Text('"Tu explorador. Observa, mapea, conecta los puntos."',
                        size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(height=40),
                cmp.eyebrow("Qué va a pasar", color=tema.MUTED, size=11),
                ft.Container(height=18),
                ft.Container(
                    width=640,
                    content=ft.Text(
                        "Voy a leer con calma lo que compartas y mapear los patrones "
                        "conductuales que definen tu momento profesional: lo que te impulsa, "
                        "lo que te frena y dónde está la brecha que aún no ves.",
                        size=16, color=tema.BLUE, font_family=tema.FUENTE_BODY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
            ],
        )

        pasos = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=40,
            controls=[
                self._paso("01", "Observa", "Lee tus respuestas sin juzgar. Solo registra."),
                self._paso("02", "Mapea", "Identifica patrones que se repiten en cómo te ves a ti mismo profesionalmente."),
                self._paso("03", "Conecta", "Devuelve un diagnóstico cualitativo que alimenta al resto del sistema."),
            ],
        )

        cta = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[cmp.boton_primario("EMPEZAR EL DIAGNÓSTICO  →", on_click=lambda e: self.router.navegar_a("/progreso"))],
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=1040,
                    padding=ft.Padding.symmetric(horizontal=56, vertical=44),
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            self._topbar(),
                            ft.Container(height=60),
                            intro,
                            self._divisor(),
                            pasos,
                            self._divisor(),
                            ft.Container(height=10),
                            cta,
                            ft.Container(height=40),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[cmp.eyebrow("Observación  ·  Patrón  ·  Brecha", color=tema.HINT, size=11)],
                            ),
                            ft.Container(height=24),
                        ],
                    ),
                )
            ],
        )
