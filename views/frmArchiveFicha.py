"""Archive · Pantalla 2: ficha visual del logro (solo lectura).

Se muestra tras generar la ficha (ya guardada) o al abrir un logro existente
desde el timeline. La generación y el guardado ocurren en el chat de Archive.
"""

from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core.textos import TEXTOS

_T = TEXTOS["archive"]
_MESES = TEXTOS["comun"]["meses_largo"]


class frmArchiveFicha:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.ficha = router.logro_ficha or {}
        self.recien_generado = bool(self.ficha.get("_recien_generado"))

    # --- Card de la ficha ---------------------------------------------------
    def _card(self):
        f = self.ficha
        fecha = f.get("fecha") or datetime.now()
        fecha_str = f"{fecha.day:02d} {_MESES[fecha.month - 1]} {fecha.year}"

        cuerpo = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    cmp.eyebrow(fecha_str, color=tema.HINT),
                    ft.Container(
                        border=ft.Border.all(1, tema.AMBAR),
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=3,
                        content=cmp.eyebrow(f.get("tipo", ""), color=tema.AMBAR),
                    ),
                ],
            ),
            ft.Container(height=22),
            ft.Text(f.get("titulo", ""), size=32, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
            ft.Container(height=28),
            cmp.field_block(_T["ficha_contexto"], f.get("contexto", "")),
            cmp.field_block(_T["ficha_mi_rol"], f.get("mi_rol", "") or "—"),
        ]
        if f.get("metrics"):
            cuerpo.append(cmp.metrics_row(f["metrics"]))
        if f.get("aprendizaje"):
            cuerpo.append(cmp.field_block(_T["ficha_aprendizaje"], f["aprendizaje"]))
        if f.get("tags"):
            cuerpo.extend([
                cmp.eyebrow(_T["ficha_tags"], size=10),
                ft.Container(height=10),
                ft.Row(wrap=True, spacing=8, run_spacing=8, controls=[cmp.tag_pill(t) for t in f["tags"]]),
            ])
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=44, vertical=40),
            content=ft.Column(spacing=0, controls=cuerpo),
        )

    def _redactar(self, e):
        # Pasa este logro a Editor para redactar (correo / LinkedIn) con tu voz.
        self.router.editor_contexto = self.ficha
        self.router.editor_borrador_id = None  # sesión nueva enfocada en el logro
        self.router.navegar_a("/editor/estudio")

    def _boton_redactar(self):
        return ft.ElevatedButton(
            content=ft.Text(_T["redactar_editor"], size=13, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
            on_click=self._redactar,
            style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=28, vertical=16), elevation=0),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        if not self.ficha:
            return ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Text(_T["ficha_vacia"], size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                        cmp.boton_primario(_T["ir_archive"], on_click=lambda e: self.router.navegar_a("/archive")),
                    ],
                ),
            )

        if self.recien_generado:
            intro_eyebrow, intro_texto = _T["recien_eyebrow"], _T["recien_texto"]
            acciones = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    cmp.enlace_cta(_T["volver_archivo"], on_click=lambda e: self.router.navegar_a("/archive")),
                    self._boton_redactar(),
                ],
            )
        else:
            intro_eyebrow, intro_texto = _T["del_archivo_eyebrow"], _T["del_archivo_texto"]
            acciones = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    cmp.enlace_cta(_T["volver_archivo"], on_click=lambda e: self.router.navegar_a("/archive")),
                    self._boton_redactar(),
                ],
            )

        intro = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                cmp.eyebrow(intro_eyebrow, color=tema.AMBAR),
                ft.Container(height=14),
                cmp.hairline(width=40),
                ft.Container(height=14),
                ft.Text(intro_texto, size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED, text_align=ft.TextAlign.CENTER),
            ],
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=760,
                    padding=ft.Padding.symmetric(horizontal=56, vertical=44),
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            cmp.topbar(_T["topbar"], derecha=TEXTOS["comun"]["volver_dashboard"], on_back=lambda e: self.router.navegar_a("/menu_inicio")),
                            ft.Container(height=44),
                            intro,
                            ft.Container(height=36),
                            self._card(),
                            ft.Container(height=28),
                            acciones,
                            ft.Container(height=48),
                        ],
                    ),
                )
            ],
        )
