"""Animacion teatral mientras Claude genera el diagnostico cualitativo."""

import asyncio

import flet as ft

from core import clsAgentes

MENSAJES = [
    "Leyendo tus respuestas...",
    "Identificando patrones...",
    "Construyendo tu perfil...",
    "Preparando tu diagnóstico...",
]

DURACION_MINIMA = 8.0  # segundos


class frmProgreso:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.texto_estado = ft.Text(
            MENSAJES[0], size=18, color="#C9D0E6", text_align=ft.TextAlign.CENTER
        )
        self.contenedor_error = ft.Column(visible=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    async def _animacion(self):
        """Recorre los mensajes en tiempos prediseniados; min 8 segundos en total."""
        paso = DURACION_MINIMA / len(MENSAJES)
        for mensaje in MENSAJES:
            self.texto_estado.value = mensaje
            self.router.page.update()
            await asyncio.sleep(paso)

    async def _llamada_claude(self):
        return await clsAgentes.generar_diagnostico_cualitativo(self.id_usuario)

    async def al_cargar(self):
        """Dispara animacion y llamada a Claude en paralelo; navega cuando ambas terminan."""
        try:
            _, diagnostico = await asyncio.gather(
                self._animacion(),
                self._llamada_claude(),
            )
        except Exception:
            self._mostrar_error()
            return

        self.router.diagnostico_actual = diagnostico
        self.router.navegar_a("/diagnostico")

    def _mostrar_error(self):
        self.texto_estado.visible = False
        self.contenedor_error.visible = True
        self.contenedor_error.controls = [
            ft.Text(
                "Tuvimos un problema, intenta de nuevo",
                size=18,
                color="#E0633F",
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=12),
            ft.ElevatedButton(
                "Regresar",
                on_click=lambda e: self.router.navegar_a("/scout_reflection"),
                style=ft.ButtonStyle(
                    bgcolor="#BA7517",
                    color="#FFFFFF",
                    padding=ft.Padding.symmetric(horizontal=30, vertical=16),
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
            ),
        ]
        self.router.page.update()

    def construir(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30,
                controls=[
                    ft.ProgressRing(width=56, height=56, color="#BA7517", stroke_width=4),
                    self.texto_estado,
                    self.contenedor_error,
                ],
            ),
        )
