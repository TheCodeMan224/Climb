"""Los 3 caminos posibles para los proximos 30 dias."""

import json

import flet as ft
import tema

from core import clsAgentes
from data import clsInteraccionDB


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

        # Overlay de carga mientras Pacer genera la primera mision.
        self.router.mostrar_carga("Preparando tu primera misión…")
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
                ft.Text(etiqueta, size=11, weight=ft.FontWeight.BOLD, color=tema.TEXTO_SUAVE),
                ft.Text(valor, size=13, color=tema.TEXTO),
            ],
        )

    def _card_camino(self, indice, camino):
        boton = ft.ElevatedButton(
            "Tomar este camino",
            on_click=lambda e, i=indice: self.router.page.run_task(self._tomar_camino, i),
            style=ft.ButtonStyle(
                bgcolor=tema.NAVY,
                color=tema.TEXTO_SOBRE_NAVY,
                padding=ft.Padding.symmetric(horizontal=28, vertical=16),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )
        self.botones.append(boton)

        por_que = ft.Container(
            padding=ft.Padding.only(left=14),
            border=ft.Border.only(left=ft.BorderSide(3, tema.AMBAR)),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text("POR QUÉ ENCAJA CONTIGO", size=11, weight=ft.FontWeight.BOLD, color=tema.AMBAR),
                    ft.Text(camino.get("por_que_encaja", ""), size=13, color=tema.TEXTO, font_family=tema.FUENTE_BODY),
                ],
            ),
        )

        return ft.Container(
            padding=24,
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=24, color="#00000044"),
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Text(camino.get("nombre", ""), size=22, weight=ft.FontWeight.BOLD, color=tema.TEXTO, font_family=tema.FUENTE_SUBHEADER),
                    ft.Text(camino.get("descripcion", ""), size=14, color=tema.TEXTO),
                    por_que,
                    ft.Divider(height=1, color=tema.BORDER_LIGHT),
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
                    ft.Row(
                        controls=[
                            self._meta("Supuesto que este camino pone a prueba", camino.get("supuesto_que_desafia", "")),
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
                    ft.ProgressRing(width=22, height=22, color=tema.AMBAR, stroke_width=3),
                    ft.Text("Preparando tu primera misión...", color=tema.TEXTO_SUAVE),
                ],
            ),
        )

        controles = [
            ft.Text("Tu plan para los próximos 30 días", size=34, weight=ft.FontWeight.BOLD, color=tema.TEXTO, font_family=tema.FUENTE_DISPLAY),
            ft.Text("Tres caminos posibles. Tú decides cuál tomar.", size=16, color=tema.TEXTO_SUAVE),
            ft.Container(
                margin=ft.Margin.only(top=10),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                bgcolor=tema.SECTION_BG,
                border_radius=8,
                border=ft.Border.only(left=ft.BorderSide(3, tema.AMBAR)),
                content=ft.Text(
                    "Climb te muestra opciones con sus costos y riesgos; no elige por ti. "
                    "Es un insumo para que TÚ decidas, no una respuesta definitiva.",
                    size=13, italic=True, color=tema.TEXTO_SUAVE, font_family=tema.FUENTE_SERIF),
            ),
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
