"""Clarity · Pantalla 3: puertas de salida.

Tras el cierre, Clarity sintetiza y ofrece caminos. La puerta 01 (cerrar)
siempre aparece; 02 (Mirror) si surgió un patrón; 03 (Pacer) si hubo una acción
concreta. La acción de Pacer SOLO se sugiere (no se inserta en la misión).
"""

from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes, clsClarity, clsMirror
from data import clsInteraccionDB


class frmClarityPuertas:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.cierre = router.clarity_cierre or {}

    # --- Acciones de las puertas -------------------------------------------
    def _cerrar(self, e=None):
        # Extrae hallazgos en background y consolida el voice profile, como el cierre clásico.
        id_chat = clsInteraccionDB.obtener_o_crear_chat(self.id_usuario, "clarity_session")
        self.router.page.run_task(clsAgentes.procesar_cierre_clarity_async, id_chat, self.id_usuario)
        self.router.page.run_task(clsAgentes.actualizar_voice_profile, self.id_usuario)
        self.router.clarity_cierre = None
        self.router.clarity_turns = None
        self.router.navegar_a("/menu_inicio")

    def _a_mirror(self, e=None):
        quote = self.cierre.get("patron_quote") or ""
        self.router.mirror_patron = clsMirror.Patron(
            id="clarity:patron", quote=quote, source="user",
            detected_at=datetime.now(), status="pending",
        )
        self.router.clarity_cierre = None
        self.router.navegar_a("/mirror/entry")

    def _a_pacer(self, e=None):
        # Solo sugerir: llevamos al Pacer y mostramos la acción como sugerencia.
        accion = self.cierre.get("accion_texto") or ""
        self.router.navegar_a("/pacer")
        if accion:
            self.router.page.show_dialog(ft.SnackBar(ft.Text(f"Sugerencia de Clarity: {accion}")))
            self.router.page.update()

    # --- Cards de puerta ----------------------------------------------------
    def _puerta(self, numero, tag, titulo, desc, on_click, recomendada=False):
        meta = [cmp.eyebrow(tag, color=tema.MUTED, size=10)]
        if recomendada:
            meta.append(ft.Container(
                border=ft.Border.all(1, tema.AMBAR), border_radius=3,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                content=cmp.eyebrow("Recomendada", color=tema.AMBAR, size=10)))
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.AMBAR) if recomendada else ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6, padding=ft.Padding.symmetric(horizontal=28, vertical=24),
            margin=ft.Margin.only(bottom=14), on_click=on_click, ink=True,
            content=ft.Row(spacing=24, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Container(width=36, content=ft.Text(numero, size=22, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR)),
                ft.Column(expand=True, spacing=8, controls=[
                    ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=meta),
                    ft.Text(titulo, size=19, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                    ft.Text(desc, size=13, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                ]),
                ft.Text("→", size=18, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
            ]),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        if not self.cierre:
            return ft.Column(expand=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Text("No hay una conversación para cerrar.", size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                ft.Container(height=16),
                cmp.boton_primario("Ir a Clarity", on_click=lambda e: self.router.navegar_a("/clarity")),
            ])

        c = self.cierre
        rec = c.get("puerta_recomendada", 1)

        final_turn = ft.Container(
            padding=ft.Padding.only(bottom=32), margin=ft.Margin.only(bottom=24),
            border=ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Column(spacing=0, controls=[
                cmp.eyebrow("Clarity", color=tema.AMBAR, size=11),
                ft.Container(height=12),
                ft.Container(width=600, content=ft.Text(c.get("sintesis", ""), size=17, color=tema.NAVY, font_family=tema.FUENTE_BODY)),
                ft.Container(height=14),
                ft.Container(width=600, content=ft.Text(c.get("pregunta", ""), size=18, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY)),
            ]),
        )

        intro = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, controls=[
            cmp.hairline(width=56),
            ft.Container(height=18),
            cmp.eyebrow("Tres caminos", color=tema.MUTED),
            ft.Container(height=14),
            ft.Text("Lo que sigue depende de ti", size=28, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
            ft.Container(height=14),
            ft.Container(width=460, content=ft.Text(
                "No tienes que elegir uno. Pero algo te ayuda a aterrizar lo que pensaste.",
                size=14, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED, text_align=ft.TextAlign.CENTER)),
        ])

        puertas = [self._puerta(
            "01", "Cerrar la sesión", "Quedarme con la claridad obtenida",
            "Ya viste lo que necesitabas. El sistema guarda esta conversación. Vuelves al dashboard.",
            self._cerrar, recomendada=(rec == 1))]
        if c.get("hay_patron"):
            puertas.append(self._puerta(
                "02", "Trabajar el patrón", "Llevar esto a una sesión con Mirror",
                f'El reflejo de "{c.get("patron_quote","")}" merece su propia sesión. Mirror lo desarma a profundidad.',
                self._a_mirror, recomendada=(rec == 2)))
        if c.get("hay_accion"):
            puertas.append(self._puerta(
                "03", "Sumar a tu misión", "Convertir en una acción de tu Pacer",
                f'"{c.get("accion_texto","")}" puede volverse parte de tu misión activa.',
                self._a_pacer, recomendada=(rec == 3)))

        seguir = ft.Container(
            padding=ft.Padding.only(top=22), margin=ft.Margin.only(top=10),
            border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                cmp.enlace_cta("↻ Quiero seguir conversando", on_click=lambda e: self.router.navegar_a("/clarity/conversacion")),
            ]),
        )

        controles = [
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=8, controls=[cmp.eyebrow("Climb", color=tema.AMBAR), cmp.eyebrow("·  Clarity · Cierre", color=tema.HINT)]),
            ]),
            ft.Container(height=40),
            final_turn,
            intro,
            ft.Container(height=32),
            *puertas,
            seguir,
            ft.Container(height=40),
        ]

        return ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Container(width=820, padding=ft.Padding.symmetric(horizontal=56, vertical=40), content=ft.Column(spacing=0, controls=controles)),
        ])
