"""Mirror · Pantalla 1: Hub — patrones pendientes, en observación y propio."""

from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core import clsMirror
from data import clsInteraccionDB

_MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


class frmMirrorHub:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.campo_propio = None

    # --- Navegación ---------------------------------------------------------
    def _empezar(self, patron):
        self.router.mirror_patron = patron
        self.router.navegar_a("/mirror/entry")

    def _empezar_propio(self, e):
        quote = (self.campo_propio.value or "").strip()
        if not quote:
            return
        idp = clsInteraccionDB.insertar_patron_usuario(self.id_usuario, quote)
        clsInteraccionDB.registrar_texto_usuario(self.id_usuario, "mirror", quote)
        self._empezar(clsMirror.Patron(
            id=f"db:{idp}", quote=quote, source="user", detected_at=datetime.now(), status="pending",
        ))

    # --- Cards --------------------------------------------------------------
    def _card_pendiente(self, patron, idx):
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=22),
            border=ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            on_click=lambda e, p=patron: self._empezar(p),
            ink=True,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=42, content=ft.Text(f"{idx:02d}", size=22, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR)),
                    ft.Container(
                        expand=True,
                        padding=ft.Padding.only(left=22),
                        border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
                        content=ft.Column(spacing=8, controls=[
                            ft.Text(f'"{patron.quote}"', size=17, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                            cmp.eyebrow(patron.detected_meta, color=tema.HINT, size=10),
                        ]),
                    ),
                    ft.Container(width=16),
                    cmp.eyebrow("Empezar sesión  →", color=tema.BLUE, size=11),
                ],
            ),
        )

    def _card_observando(self, patron):
        if not patron.reframe:
            return ft.Container()
        procesado = f"{patron.detected_at.day:02d} {_MESES[patron.detected_at.month - 1]}"
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=26, vertical=22),
            margin=ft.Margin.only(bottom=14),
            content=ft.Column(spacing=16, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        cmp.eyebrow(f"Procesado {procesado}  ·  {patron.observed_meta}", color=tema.HINT, size=10),
                        cmp.enlace_cta("Retomar  →", on_click=lambda e, p=patron: self._empezar(p)),
                    ],
                ),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=ft.Padding.only(right=20),
                            content=ft.Text(f'"{patron.reframe.old_quote}"', size=14, italic=True, font_family=tema.FUENTE_SERIF, color=tema.GRIS_TACHADO, text_align=ft.TextAlign.RIGHT),
                        ),
                        ft.Container(width=28, content=ft.Text("→", size=16, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR, text_align=ft.TextAlign.CENTER)),
                        ft.Container(
                            expand=True,
                            padding=ft.Padding.only(left=20),
                            border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
                            content=ft.Text(f'"{patron.reframe.new_quote}"', size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY),
                        ),
                    ],
                ),
            ]),
        )

    def _bloque_vacio(self):
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=40, vertical=36),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    ft.Container(width=480, content=ft.Text("Scout no tiene patrones nuevos esta semana.\nBuena señal.", size=19, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY, text_align=ft.TextAlign.CENTER)),
                    cmp.eyebrow("Sigue observando en background  ·  Avisará cuando aparezca algo", color=tema.HINT, size=10),
                ],
            ),
        )

    def _bloque_propio(self):
        self.campo_propio = ft.TextField(
            hint_text='Ej: "Si digo que no a esta junta, van a pensar que no me importa..."',
            multiline=True,
            min_lines=2,
            max_lines=5,
            border=ft.InputBorder.NONE,
            bgcolor="transparent",
            cursor_color=tema.NAVY,
            text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=15, color=tema.NAVY),
            hint_style=ft.TextStyle(font_family=tema.FUENTE_SERIF, italic=True, size=15, color=tema.HINT),
            content_padding=ft.Padding.symmetric(horizontal=0, vertical=6),
        )
        return ft.Container(
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=30, vertical=28),
            content=ft.Column(spacing=0, controls=[
                cmp.eyebrow("Tu propio patrón", color=tema.AMBAR),
                ft.Container(height=10),
                ft.Text("¿Hay algo que estás sintiendo operando en tu trabajo que Scout aún no ha detectado? Escríbelo como lo escuchas en tu cabeza.", size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                ft.Container(height=22),
                ft.Container(
                    border=ft.Border.only(bottom=ft.BorderSide(1, tema.NAVY)),
                    padding=ft.Padding.only(bottom=10),
                    content=self.campo_propio,
                ),
                ft.Container(height=18),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        cmp.eyebrow("Mirror te llevará a una sesión con este patrón", color=tema.HINT, size=10),
                        ft.ElevatedButton(
                            content=ft.Text("EMPEZAR SESIÓN  →", size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                            on_click=self._empezar_propio,
                            style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=24, vertical=14), elevation=0),
                        ),
                    ],
                ),
            ]),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        pendientes, observando = clsMirror.cargar_hub(self.id_usuario)

        hero = ft.Row(
            spacing=24,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text("01", size=56, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                ft.Column(expand=True, spacing=10, controls=[
                    ft.Text("Mirror", size=44, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                    ft.Container(width=520, content=ft.Text("Trabaja patrones limitantes en tu carrera profesional. A través de preguntas, te ayuda a verlos desde fuera para que dejen de operar en automático.", size=14, font_family=tema.FUENTE_BODY, color=tema.MUTED)),
                    ft.Container(height=8),
                    ft.Container(
                        width=520,
                        padding=ft.Padding.only(left=16),
                        border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
                        content=ft.Text("Trabajo contigo solo en lo profesional. Si la conversación se mueve hacia lo personal profundo, te redirijo con respeto.", size=13, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                    ),
                ]),
            ],
        )

        controles = [
            cmp.topbar("Mirror", derecha="← Volver al dashboard", on_back=lambda e: self.router.navegar_a("/menu_inicio")),
            ft.Container(height=36),
            hero,
            cmp.section_divider(),
            cmp.section_head("Patrones pendientes", contador=f"{len(pendientes)} detectado{'s' if len(pendientes) != 1 else ''} por Scout"),
        ]
        if pendientes:
            for i, p in enumerate(pendientes, start=1):
                controles.append(self._card_pendiente(p, i))
        else:
            controles.append(self._bloque_vacio())

        controles.append(cmp.section_divider())
        controles.append(cmp.section_head("En observación", contador=f"{len(observando)} patrones procesados"))
        for p in observando:
            controles.append(self._card_observando(p))

        controles.append(cmp.section_divider())
        controles.append(cmp.section_head("Trabajar un patrón nuevo"))
        controles.append(self._bloque_propio())
        controles.append(ft.Container(height=40))

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=860,
                    padding=ft.Padding.symmetric(horizontal=56, vertical=44),
                    content=ft.Column(spacing=0, controls=controles),
                )
            ],
        )
