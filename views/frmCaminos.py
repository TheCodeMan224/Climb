"""Los 3 caminos posibles para los proximos 30 dias."""

import json

import flet as ft

from core import clsAgentes
from data import clsInteraccionDB

AMBAR = "#BA7517"


class frmCaminos:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.caminos = (router.caminos_actual or {}).get("caminos", [])
        self.overlay = ft.Container(visible=False)
        self.botones = []

    async def _tomar_camino(self, indice):
        elegido = self.caminos[indice]
        alternativos = [c for i, c in enumerate(self.caminos) if i != indice]

        clsInteraccionDB.insertar_camino_elegido(
            self.id_usuario,
            elegido.get("nombre", ""),
            elegido.get("descripcion", ""),
            elegido.get("tradeoff_principal", ""),
            elegido.get("riesgo_principal", ""),
            elegido.get("tiempo_estimado_semanal", ""),
            elegido.get("patron_que_rompe", ""),
            json.dumps(alternativos, ensure_ascii=False),
        )

        # Loader breve mientras Pacer genera la primera mision.
        self.overlay.visible = True
        for b in self.botones:
            b.disabled = True
        self.router.page.update()

        try:
            mision = await clsAgentes.generar_mision_pacer(self.id_usuario)
            self.router.mision_actual = mision
        except Exception:
            self.router.mision_actual = None

        self.router.navegar_a("/menu_inicio")

    def _meta(self, etiqueta, valor):
        return ft.Column(
            spacing=2,
            expand=True,
            controls=[
                ft.Text(etiqueta, size=11, weight=ft.FontWeight.BOLD, color="#8C95B8"),
                ft.Text(valor, size=13, color="#DDE2F2"),
            ],
        )

    def _card_camino(self, indice, camino):
        boton = ft.ElevatedButton(
            "Tomar este camino",
            on_click=lambda e, i=indice: self.router.page.run_task(self._tomar_camino, i),
            style=ft.ButtonStyle(
                bgcolor=AMBAR,
                color="#FFFFFF",
                padding=ft.Padding.symmetric(horizontal=28, vertical=16),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )
        self.botones.append(boton)

        return ft.Container(
            padding=24,
            bgcolor="#141C36",
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=24, color="#00000044"),
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Text(camino.get("nombre", ""), size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
                    ft.Text(camino.get("descripcion", ""), size=14, color="#C9D0E6"),
                    ft.Divider(height=1, color="#2A3358"),
                    ft.Row(
                        controls=[
                            self._meta("Tradeoff principal", camino.get("tradeoff_principal", "")),
                            self._meta("Riesgo principal", camino.get("riesgo_principal", "")),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            self._meta("Tiempo estimado por semana", camino.get("tiempo_estimado_semanal", "")),
                            self._meta("Patrón que rompe", camino.get("patron_que_rompe", "")),
                        ]
                    ),
                    ft.Container(height=4),
                    boton,
                ],
            ),
        )

    def construir(self):
        self.overlay = ft.Container(
            visible=False,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.ProgressRing(width=22, height=22, color=AMBAR, stroke_width=3),
                    ft.Text("Preparando tu primera misión...", color="#AEB6D0"),
                ],
            ),
        )

        controles = [
            ft.Text("Tu plan para los próximos 30 días", size=34, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
            ft.Text("Tres caminos posibles. Tú decides cuál tomar.", size=16, color="#AEB6D0"),
            ft.Container(height=16),
        ]
        for indice, camino in enumerate(self.caminos):
            controles.append(self._card_camino(indice, camino))
            controles.append(ft.Container(height=14))
        controles.append(self.overlay)
        controles.append(ft.Container(height=40))

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=840,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=30),
                    content=ft.Column(spacing=4, controls=controles),
                )
            ],
        )
