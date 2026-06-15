"""Archive · Pantalla 2: ficha visual del logro (solo lectura).

Se muestra tras generar la ficha (ya guardada) o al abrir un logro existente
desde el timeline. La generación y el guardado ocurren en el chat de Archive.
"""

from datetime import datetime

import flet as ft

import componentes as cmp
import tema

_MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


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
            cmp.field_block("Contexto", f.get("contexto", "")),
            cmp.field_block("Mi rol específico", f.get("mi_rol", "") or "—"),
        ]
        if f.get("metrics"):
            cuerpo.append(cmp.metrics_row(f["metrics"]))
        if f.get("aprendizaje"):
            cuerpo.append(cmp.field_block("Aprendizaje", f["aprendizaje"]))
        if f.get("tags"):
            cuerpo.extend([
                cmp.eyebrow("Tags", size=10),
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
                        ft.Text("No hay una ficha para mostrar.", size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                        cmp.boton_primario("Ir a Archive", on_click=lambda e: self.router.navegar_a("/archive")),
                    ],
                ),
            )

        if self.recien_generado:
            intro_eyebrow, intro_texto = "Logro archivado", "Tu logro quedó documentado. Así lo registramos."
            boton_archivo = ft.ElevatedButton(
                content=ft.Text("VER MI ARCHIVO  →", size=13, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                on_click=lambda e: self.router.navegar_a("/archive"),
                style=ft.ButtonStyle(
                    bgcolor=tema.NAVY,
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=ft.Padding.symmetric(horizontal=28, vertical=16),
                    elevation=0,
                ),
            )
            acciones = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    cmp.enlace_cta("← Volver al chat de Archive", on_click=lambda e: self.router.navegar_a("/chat/coach_archive")),
                    boton_archivo,
                ],
            )
        else:
            intro_eyebrow, intro_texto = "Del archivo", "Un logro que documentaste con Archive."
            acciones = ft.Row(controls=[cmp.enlace_cta("← Volver al archivo", on_click=lambda e: self.router.navegar_a("/archive"))])

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
                            cmp.topbar("Archive", derecha="← Volver al dashboard", on_back=lambda e: self.router.navegar_a("/menu_inicio")),
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
