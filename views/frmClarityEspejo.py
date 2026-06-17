"""Clarity · Pantalla 1: espejo de lo construido + invitación a conversar.

Momento A: el espejo (lo que la persona ha construido con los otros agentes).
Momento B: la invitación a pensar en voz alta. El texto inicial arranca la
conversación (/clarity/conversacion).
"""

import flet as ft

import componentes as cmp
import tema
from core import clsClarity
from core.textos import TEXTOS

_T = TEXTOS["clarity"]


class frmClarityEspejo:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.campo = None

    # --- Navegación ---------------------------------------------------------
    def _empezar(self, e=None):
        texto = (self.campo.value or "").strip()
        if not texto:
            return
        self.router.clarity_inicial = texto
        self.router.clarity_turns = None
        self.router.navegar_a("/clarity/conversacion")

    def _cta_bloque(self, bloque):
        if bloque.cta_patron:
            nombre, descripcion = bloque.cta_patron
            return cmp.enlace_cta(bloque.cta_texto, on_click=lambda e: self._ir_patron(nombre, descripcion))
        return cmp.enlace_cta(bloque.cta_texto, on_click=lambda e, r=bloque.cta_ruta: self.router.navegar_a(r))

    def _ir_patron(self, nombre, descripcion):
        from datetime import datetime
        from core import clsMirror
        self.router.mirror_patron = clsMirror.Patron(
            id=f"scout:{nombre}", quote=descripcion or nombre, source="scout",
            detected_at=datetime.now(), status="pending", scout_ref=nombre,
        )
        self.router.navegar_a("/mirror/entry")

    # --- Bloques del espejo -------------------------------------------------
    def _frase(self, bloque):
        spans = []
        for texto, es_dato in bloque.segmentos:
            if es_dato:
                spans.append(ft.TextSpan(texto, ft.TextStyle(
                    color=tema.AMBAR, font_family=tema.FUENTE_DISPLAY, size=20, weight=ft.FontWeight.W_700)))
            else:
                spans.append(ft.TextSpan(texto))
        base_italic = not bloque.tiene_datos
        return ft.Text(
            spans=spans, size=17,
            color=tema.MUTED if base_italic else tema.NAVY,
            italic=base_italic,
            font_family=tema.FUENTE_SERIF if base_italic else tema.FUENTE_BODY,
        )

    def _bloque(self, bloque, ultimo):
        dot = ft.Container(
            width=9, height=9, border_radius=5,
            bgcolor=tema.AMBAR if bloque.tiene_datos else tema.OFF_WHITE,
            border=None if bloque.tiene_datos else ft.Border.all(1.5, tema.GRIS_TACHADO),
        )
        contenido = [
            ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                dot,
                ft.Text(bloque.numero, size=14, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                cmp.eyebrow(bloque.agente, color=tema.MUTED, size=11),
            ]),
            ft.Container(height=10),
            ft.Container(padding=ft.Padding.only(left=21), content=self._frase(bloque)),
        ]
        if bloque.cta_texto:
            contenido.append(ft.Container(padding=ft.Padding.only(left=21, top=8), content=self._cta_bloque(bloque)))
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=18),
            border=None if ultimo else ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Column(spacing=0, controls=contenido),
        )

    def _barra_progreso(self, hechas, total):
        fill = max(int(round((hechas / total) * 100)), 0) if total else 0
        segmentos = []
        if fill > 0:
            segmentos.append(ft.Container(expand=fill, height=3, border_radius=2, bgcolor=tema.AMBAR))
        if fill < 100:
            segmentos.append(ft.Container(expand=(100 - fill), height=3, border_radius=2, bgcolor=ft.Colors.with_opacity(0.18, tema.OFF_WHITE)))
        return ft.Row(expand=True, spacing=2, controls=segmentos)

    def _banner_pacer(self, pacer):
        return ft.Container(
            bgcolor=tema.NAVY, border_radius=6,
            padding=ft.Padding.symmetric(horizontal=30, vertical=26),
            margin=ft.Margin.only(top=8, bottom=8),
            content=ft.Column(spacing=0, controls=[
                cmp.eyebrow(_T["camino_activo"], color=tema.AMBAR),
                ft.Container(height=12),
                ft.Text(pacer.nombre, size=24, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.TEXTO_SOBRE_NAVY),
                ft.Container(height=20),
                ft.Row(spacing=18, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    self._barra_progreso(pacer.hechas, pacer.total),
                    cmp.eyebrow(_T["acciones_pacer"].format(hechas=pacer.hechas, total=pacer.total), color=tema.TEXTO_SUAVE_SOBRE_NAVY, size=11),
                ]),
            ]),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        espejo = clsClarity.cargar_espejo(self.id_usuario)

        hero = ft.Row(spacing=22, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
            ft.Text("04", size=56, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
            ft.Column(expand=True, spacing=14, controls=[
                ft.Text(_T["saludo"].format(nombre=espejo.nombre), size=38, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ft.Container(width=540, content=ft.Text(
                    _T["encuadre"],
                    size=16, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED)),
                ft.Container(
                    width=520, padding=ft.Padding.only(left=14),
                    border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
                    content=ft.Text(
                        _T["boundary"],
                        size=13, italic=True, font_family=tema.FUENTE_SERIF, color=tema.HINT)),
            ]),
        ])

        # Espejo: espina dorsal (borde gold izquierdo) + bloques.
        espina = ft.Container(
            padding=ft.Padding.only(left=28),
            border=ft.Border.only(left=ft.BorderSide(1, tema.AMBAR)),
            content=ft.Column(spacing=0, controls=[
                self._bloque(b, ultimo=(i == len(espejo.bloques) - 1))
                for i, b in enumerate(espejo.bloques)
            ]),
        )

        self.campo = ft.TextField(
            hint_text=_T["hint_espejo"],
            expand=True, multiline=True, min_lines=2, max_lines=6,
            border=ft.InputBorder.NONE, bgcolor="transparent", cursor_color=tema.NAVY,
            text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=16, color=tema.NAVY),
            hint_style=ft.TextStyle(font_family=tema.FUENTE_SERIF, italic=True, size=16, color=tema.HINT),
            on_submit=self._empezar,
        )

        transicion = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, controls=[
            cmp.hairline(width=56),
            ft.Container(height=18),
            cmp.eyebrow(_T["ahora_tu"], color=tema.MUTED),
            ft.Container(height=22),
            ft.Container(width=540, content=ft.Text(
                _T["invitacion"],
                size=22, italic=True, font_family=tema.FUENTE_SERIF, color=tema.NAVY, text_align=ft.TextAlign.CENTER)),
        ])

        entrada = ft.Column(spacing=0, controls=[
            ft.Container(
                border=ft.Border.only(bottom=ft.BorderSide(1, tema.NAVY)),
                padding=ft.Padding.only(bottom=12),
                content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.END, controls=[
                    self.campo,
                    ft.ElevatedButton(
                        content=ft.Text(_T["empezar"], size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                        on_click=self._empezar,
                        style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=24, vertical=16), elevation=0)),
                ]),
            ),
            cmp.subrayado_bicolor(),
        ])

        controles = [
            cmp.topbar(_T["topbar"], derecha=TEXTOS["comun"]["volver_dashboard"], on_back=lambda e: self.router.navegar_a("/menu_inicio")),
            ft.Container(height=36),
            hero,
        ]
        if espejo.pacer:
            controles.append(ft.Container(height=24))
            controles.append(self._banner_pacer(espejo.pacer))
        controles.append(ft.Container(height=28))
        controles.append(espina)
        controles.append(ft.Container(height=48))
        controles.append(transicion)
        controles.append(ft.Container(height=24))
        controles.append(entrada)
        controles.append(ft.Container(height=44))

        return ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[ft.Container(width=880, padding=ft.Padding.symmetric(horizontal=56, vertical=40),
                                   content=ft.Column(spacing=0, controls=controles))],
        )
