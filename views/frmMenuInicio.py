"""Dashboard principal de Climb."""

import flet as ft

from core import clsAgentes
from data import clsInteraccionDB

AMBAR = "#BA7517"

# Descripciones breves (texto literal a usar, ver seccion 7.8). No modificar.
AGENTES = [
    ("Mirror", "coach_mirror", "Te ayuda a procesar tus patrones limitantes con preguntas socráticas."),
    ("Editor", "coach_editor", "Traduce tu impacto técnico a lenguaje ejecutivo sin perder tu voz."),
    ("Archive", "coach_archive", "Documenta tus logros profesionales para cuando importen."),
    ("Clarity", "clarity_session", "Tu espacio para desahogarte y procesar lo que sea."),
]


class frmMenuInicio:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.boton_refrescar = None

    async def _refrescar_diagnostico(self, e):
        self.boton_refrescar.disabled = True
        self.boton_refrescar.text = "Actualizando..."
        self.router.page.update()
        try:
            await clsAgentes.refrescar_diagnostico_incremental(self.id_usuario)
            mensaje = "Diagnóstico actualizado"
        except Exception:
            mensaje = "No se pudo actualizar el diagnóstico"
        self.boton_refrescar.disabled = False
        self.boton_refrescar.text = "Refrescar Diagnóstico"
        self.router.page.show_dialog(ft.SnackBar(ft.Text(mensaje)))
        self.router.page.update()

    def _card_agente(self, nombre, tipo_agente, descripcion):
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor="#141C36",
            border_radius=14,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(nombre, size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
                    ft.Text(descripcion, size=13, color="#AEB6D0"),
                    ft.Container(height=4),
                    ft.ElevatedButton(
                        "Hablar",
                        on_click=lambda e, t=tipo_agente: self.router.navegar_a(f"/chat/{t}"),
                        style=ft.ButtonStyle(
                            bgcolor=AMBAR,
                            color="#FFFFFF",
                            padding=ft.Padding.symmetric(horizontal=22, vertical=14),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                ],
            ),
        )

    def construir(self):
        nombre = clsInteraccionDB.obtener_nombre_usuario(self.id_usuario) or self.router.nombre or ""
        camino = clsInteraccionDB.obtener_camino_elegido(self.id_usuario)
        nombre_camino = camino.get("nombre_camino") if camino else "Aún no has elegido un camino"

        self.boton_refrescar = ft.OutlinedButton(
            "Refrescar Diagnóstico",
            on_click=self._refrescar_diagnostico,
            style=ft.ButtonStyle(color="#C9D0E6", padding=ft.Padding.symmetric(horizontal=24, vertical=16)),
        )

        # Tarjetas de agentes en dos filas de dos.
        fila_agentes_1 = ft.Row(
            spacing=16,
            controls=[self._card_agente(*AGENTES[0]), self._card_agente(*AGENTES[1])],
        )
        fila_agentes_2 = ft.Row(
            spacing=16,
            controls=[self._card_agente(*AGENTES[2]), self._card_agente(*AGENTES[3])],
        )

        seccion_camino = ft.Container(
            padding=24,
            bgcolor="#1B2A55",
            border_radius=16,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Text("Tu camino", size=14, color="#AEB6D0"),
                            ft.Text(nombre_camino, size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
                        ],
                    ),
                    ft.ElevatedButton(
                        "Ver mi misión",
                        on_click=lambda e: self.router.navegar_a("/pacer"),
                        style=ft.ButtonStyle(
                            bgcolor=AMBAR,
                            color="#FFFFFF",
                            padding=ft.Padding.symmetric(horizontal=24, vertical=16),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                ],
            ),
        )

        controles = [
            ft.Text(f"Hola, {nombre}", size=38, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
            ft.Container(height=10),
            ft.Text("Tus agentes", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
            ft.Container(height=8),
            fila_agentes_1,
            ft.Container(height=16),
            fila_agentes_2,
            ft.Container(height=24),
            seccion_camino,
            ft.Container(height=24),
            ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[self.boton_refrescar]),
            ft.Container(height=40),
        ]

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=900,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=30),
                    content=ft.Column(spacing=4, controls=controles),
                )
            ],
        )
