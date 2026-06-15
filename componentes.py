"""Componentes de UI reutilizables del lenguaje visual premium de Climb.

Centraliza la firma visual (hairline dorada, eyebrows, botones de esquina
recta, inputs con subrayado) para que las pantallas se vean consistentes.
"""

import flet as ft

import tema


# ----------------------------------------------------------------------------
# Tipografia auxiliar
# ----------------------------------------------------------------------------
def eyebrow(texto, color=tema.MUTED):
    """Etiqueta en mayusculas, DM Sans semibold. Va arriba de titulos/secciones."""
    return ft.Text(
        texto.upper(),
        size=11,
        weight=ft.FontWeight.W_600,
        font_family=tema.FUENTE_SUBHEADER,
        color=color,
    )


def hairline(color=tema.AMBAR, width=56):
    """La firma visual de Climb: una linea horizontal fina dorada."""
    return ft.Container(width=width, height=1, bgcolor=color)


# ----------------------------------------------------------------------------
# Botones
# ----------------------------------------------------------------------------
def _estilo_boton(bg, fg, radius=4):
    return ft.ButtonStyle(
        bgcolor=bg,
        color=fg,
        elevation=0,
        shape=ft.RoundedRectangleBorder(radius=radius),
        padding=ft.Padding.symmetric(horizontal=40, vertical=18),
        text_style=ft.TextStyle(
            font_family=tema.FUENTE_SUBHEADER,
            weight=ft.FontWeight.W_600,
            size=14,
        ),
    )


def boton_primario(texto, on_click=None):
    """CTA primario: navy, esquina casi recta, sin elevacion. Sobre fondo claro."""
    return ft.ElevatedButton(texto, on_click=on_click, style=_estilo_boton(tema.NAVY, tema.TEXTO_SOBRE_NAVY))


def boton_ambar(texto, on_click=None):
    """CTA sobre una card navy oscura: ambar con texto off-white."""
    return ft.ElevatedButton(texto, on_click=on_click, style=_estilo_boton(tema.AMBAR, tema.TEXTO_SOBRE_NAVY))


def enlace(texto, on_click=None, color=tema.BLUE):
    """Link secundario en azul, tipografia body."""
    return ft.TextButton(
        content=ft.Text(texto, size=13, font_family=tema.FUENTE_BODY, color=color),
        on_click=on_click,
    )


# ----------------------------------------------------------------------------
# Inputs con subrayado (sin caja Material)
# ----------------------------------------------------------------------------
def textfield_subrayado(hint="", password=False, can_reveal=False, **kwargs):
    """Crea un TextField limpio (sin borde Material) para envolver con subrayado.

    Devuelve el TextField; quien lo crea conserva la referencia para leer .value.
    """
    return ft.TextField(
        hint_text=hint,
        password=password,
        can_reveal_password=can_reveal,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding.symmetric(horizontal=0, vertical=6),
        text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=15, color=tema.TEXTO),
        hint_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=15, color=tema.HINT),
        cursor_color=tema.NAVY,
        bgcolor="transparent",
        **kwargs,
    )


def campo_etiquetado(label, textfield):
    """Label en mayuscula (eyebrow) + un TextField envuelto en subrayado navy."""
    return ft.Column(
        spacing=0,
        tight=True,
        controls=[
            eyebrow(label),
            ft.Container(height=6),
            ft.Container(
                content=textfield,
                border=ft.Border.only(bottom=ft.BorderSide(1, tema.NAVY)),
                padding=ft.Padding.only(bottom=2),
            ),
        ],
    )
