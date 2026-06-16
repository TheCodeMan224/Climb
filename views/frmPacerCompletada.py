"""Pacer · cierre de misión: celebra lo logrado y sugiere las siguientes.

Se llega aquí tras pulsar "Completar misión". Pacer sugiere 2-3 misiones nuevas
(con contexto cruzado de Mirror, Archive e historial); al elegir una, se vuelve
la misión activa.
"""

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes
from data import clsInteraccionDB


class frmPacerCompletada:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.mision = router.pacer_completada or {}
        router.pacer_completada = None
        self.sugerencias = []
        self.cont_sugerencias = ft.Column(spacing=14)

    # --- Carga de sugerencias (Claude) -------------------------------------
    async def al_cargar(self):
        self.router.mostrar_carga("Pacer está pensando tus siguientes pasos…")
        try:
            self.sugerencias = await clsAgentes.sugerir_misiones_pacer(self.id_usuario)
        except Exception:
            self.sugerencias = []
        self._render_sugerencias()
        self.router.ocultar_carga()
        self.router.page.update()

    def _elegir(self, mision):
        clsInteraccionDB.insertar_mision(self.id_usuario, mision)
        self.router.navegar_a("/pacer")

    def _render_sugerencias(self):
        self.cont_sugerencias.controls.clear()
        if not self.sugerencias:
            self.cont_sugerencias.controls.append(
                ft.Column(spacing=16, controls=[
                    ft.Text("No pude sugerir misiones ahora mismo.", size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                    ft.Row(spacing=20, controls=[
                        cmp.boton_primario("Generar una misión  →", on_click=lambda e: self.router.navegar_a("/pacer")),
                        cmp.enlace("Volver al dashboard", on_click=lambda e: self.router.navegar_a("/menu_inicio")),
                    ]),
                ])
            )
            return
        for i, m in enumerate(self.sugerencias, start=1):
            self.cont_sugerencias.controls.append(self._card_sugerencia(i, m))

    def _card_sugerencia(self, num, mision):
        acciones = mision.get("acciones", [])
        return ft.Container(
            bgcolor=tema.SUPERFICIE, border=ft.Border.all(1, tema.BORDER_LIGHT), border_radius=6,
            padding=ft.Padding.symmetric(horizontal=28, vertical=24), margin=ft.Margin.only(bottom=14),
            on_click=lambda e, mm=mision: self._elegir(mm), ink=True,
            content=ft.Row(spacing=22, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Container(width=36, content=ft.Text(f"{num:02d}", size=22, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR)),
                ft.Column(expand=True, spacing=8, controls=[
                    ft.Text(mision.get("nombre_mision", ""), size=19, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                    ft.Text(mision.get("descripcion", ""), size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                    cmp.eyebrow(f"{len(acciones)} acciones", color=tema.HINT, size=10),
                ]),
                cmp.enlace_cta("Elegir  →", on_click=lambda e, mm=mision: self._elegir(mm)),
            ]),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        self._render_sugerencias()

        intro = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, controls=[
            cmp.eyebrow("Misión completada", color=tema.AMBAR),
            ft.Container(height=14),
            cmp.hairline(width=48),
            ft.Container(height=18),
            ft.Text(self.mision.get("nombre_mision", "Misión completada"), size=40, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY, text_align=ft.TextAlign.CENTER),
            ft.Container(height=14),
            ft.Container(width=480, content=ft.Text(
                "Quedó registrada en tu camino. Esto es lo que puede seguir.",
                size=16, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED, text_align=ft.TextAlign.CENTER)),
        ])

        return ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[ft.Container(width=820, padding=ft.Padding.symmetric(horizontal=56, vertical=44), content=ft.Column(spacing=0, controls=[
                cmp.topbar("Pacer · Cierre", derecha="← Volver al dashboard", on_back=lambda e: self.router.navegar_a("/menu_inicio")),
                ft.Container(height=44),
                intro,
                ft.Container(height=44),
                cmp.section_head("Elige tu siguiente misión"),
                ft.Container(height=8),
                self.cont_sugerencias,
                ft.Container(height=40),
            ]))],
        )
