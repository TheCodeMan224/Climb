"""Superficie propia de Pacer: la mision semanal."""

import flet as ft

from core import clsAgentes

AMBAR = "#BA7517"


class frmPacer:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.cuerpo = ft.Column(spacing=14)
        self.boton_generar = None

    # --- Render de la mision -----------------------------------------------
    def _render_mision(self):
        mision = self.router.mision_actual
        self.cuerpo.controls.clear()

        if not mision:
            self.cuerpo.controls.append(
                ft.Text("Aún no hay una misión generada.", size=16, color="#AEB6D0")
            )
            return

        acciones = mision.get("acciones", [])[:5]  # maximo 5
        self.cuerpo.controls.extend(
            [
                ft.Text(mision.get("nombre_mision", ""), size=26, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
                ft.Text(mision.get("descripcion", ""), size=15, color="#C9D0E6"),
                ft.Container(height=6),
                ft.Text("Acciones concretas", size=16, weight=ft.FontWeight.BOLD, color="#BA7517", font_family="Syne"),
            ]
        )
        for accion in acciones:
            self.cuerpo.controls.append(
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="#3FB37F", size=18),
                        ft.Text(accion, size=14, color="#DDE2F2", expand=True),
                    ],
                )
            )
        self.cuerpo.controls.append(ft.Container(height=8))
        self.cuerpo.controls.append(
            ft.Container(
                padding=18,
                bgcolor="#1B2A55",
                border_radius=12,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text("Conexión con tu camino", size=13, color="#AEB6D0"),
                        ft.Text(mision.get("conexion_camino", ""), size=14, color="#FFFFFF"),
                    ],
                ),
            )
        )

    # --- Eventos ------------------------------------------------------------
    async def al_cargar(self):
        # Si no hay mision en memoria (p. ej. tras reabrir la app), generarla.
        if not self.router.mision_actual:
            await self._generar()

    async def _generar(self, e=None):
        if self.boton_generar:
            self.boton_generar.disabled = True
            self.boton_generar.text = "Generando..."
            self.router.page.update()
        try:
            mision = await clsAgentes.generar_mision_pacer(self.id_usuario)
            self.router.mision_actual = mision
        except Exception:
            pass
        self._render_mision()
        if self.boton_generar:
            self.boton_generar.disabled = False
            self.boton_generar.text = "Generar nueva misión"
        self.router.page.update()

    # --- Construccion -------------------------------------------------------
    def construir(self):
        self._render_mision()
        self.boton_generar = ft.ElevatedButton(
            "Generar nueva misión",
            on_click=lambda e: self.router.page.run_task(self._generar),
            style=ft.ButtonStyle(
                bgcolor=AMBAR,
                color="#FFFFFF",
                padding=ft.Padding.symmetric(horizontal=26, vertical=16),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )
        boton_menu = ft.OutlinedButton(
            "Regresar al menú",
            on_click=lambda e: self.router.navegar_a("/menu_inicio"),
            style=ft.ButtonStyle(color="#C9D0E6", padding=ft.Padding.symmetric(horizontal=26, vertical=16)),
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=800,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=30),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Tu misión de esta semana", size=32, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
                            ft.Container(height=16),
                            ft.Container(
                                padding=26,
                                bgcolor="#141C36",
                                border_radius=16,
                                content=self.cuerpo,
                            ),
                            ft.Container(height=20),
                            ft.Row(spacing=14, controls=[self.boton_generar, boton_menu]),
                            ft.Container(height=40),
                        ],
                    ),
                )
            ],
        )
