"""Componentes de UI reutilizables del lenguaje visual premium de Climb.

Centraliza la firma visual (hairline dorada, eyebrows, botones de esquina
recta, inputs con subrayado) para que las pantallas se vean consistentes.
"""

import asyncio

import flet as ft

import tema
from core.textos import TEXTOS, get_idioma


async def revelar_texto(control, texto, delay=0.02):
    """Revela 'texto' en un Text control palabra por palabra (rápido y fluido).

    El control debe estar ya montado en la página. Silencia errores de update
    por si el control deja de existir (p. ej. el usuario navega a otra vista)."""
    palabras = (texto or "").split(" ")
    acumulado = ""
    for i, palabra in enumerate(palabras):
        acumulado = palabra if i == 0 else f"{acumulado} {palabra}"
        control.value = acumulado
        try:
            control.update()
        except Exception:
            return
        await asyncio.sleep(delay)
    control.value = texto
    try:
        control.update()
    except Exception:
        pass


# ----------------------------------------------------------------------------
# Tipografia auxiliar
# ----------------------------------------------------------------------------
def eyebrow(texto, color=tema.MUTED, size=11):
    """Etiqueta en mayusculas, DM Sans semibold. Va arriba de titulos/secciones."""
    return ft.Text(
        texto.upper(),
        size=size,
        weight=ft.FontWeight.W_600,
        font_family=tema.FUENTE_SUBHEADER,
        color=color,
    )


def toggle_idioma(router):
    """Selector compacto EN | ES. El idioma activo va resaltado; el otro cambia
    el idioma de toda la app y re-renderiza la vista actual."""
    actual = get_idioma()

    def pill(lang, etiqueta):
        activo = (lang == actual)
        contenedor = ft.Container(
            content=ft.Text(
                etiqueta,
                size=11,
                weight=ft.FontWeight.W_700,
                font_family=tema.FUENTE_SUBHEADER,
                color=tema.OFF_WHITE if activo else tema.MUTED,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=5),
            bgcolor=tema.NAVY if activo else "transparent",
            border_radius=13,
        )
        if not activo:
            contenedor.on_click = lambda e, l=lang: router.cambiar_idioma(l)
        return contenedor

    return ft.Container(
        padding=3,
        bgcolor=tema.SUPERFICIE,
        border=ft.Border.all(1, tema.BORDER_LIGHT),
        border_radius=16,
        content=ft.Row(spacing=2, tight=True, controls=[pill("en", "EN"), pill("es", "ES")]),
    )


def topbar(subtitulo, derecha="", on_back=None):
    """Barra superior editorial: 'Climb · {subtitulo}' a la izquierda y un
    link opcional a la derecha (p. ej. '← Volver al dashboard')."""
    izquierda = ft.Row(spacing=8, controls=[
        eyebrow(TEXTOS["comun"]["marca"], color=tema.AMBAR),
        eyebrow("·  " + subtitulo, color=tema.HINT),
    ])
    derecha_ctrl = enlace_cta(derecha, on_click=on_back) if derecha else ft.Container()
    return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[izquierda, derecha_ctrl])


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
        # Realce sutil (blanco) al pasar el mouse y más fuerte al presionar.
        overlay_color=ft.Colors.with_opacity(0.14, fg),
        shape=ft.RoundedRectangleBorder(radius=radius),
        padding=ft.Padding.symmetric(horizontal=40, vertical=18),
        text_style=ft.TextStyle(
            font_family=tema.FUENTE_SUBHEADER,
            weight=ft.FontWeight.W_600,
            size=14,
        ),
        mouse_cursor=ft.MouseCursor.CLICK,
        animation_duration=150,
    )


def _estilo_enlace(color):
    """Estilo de link con hover/clic visibles: realce tenue del color + cursor."""
    return ft.ButtonStyle(
        color=color,
        overlay_color=ft.Colors.with_opacity(0.12, color),
        shape=ft.RoundedRectangleBorder(radius=4),
        padding=ft.Padding.symmetric(horizontal=8, vertical=6),
        mouse_cursor=ft.MouseCursor.CLICK,
        animation_duration=150,
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
        style=_estilo_enlace(color),
    )


def enlace_cta(texto, on_click=None, color=tema.BLUE):
    """Link tipo CTA editorial: mayusculas, DM Sans semibold, con hover/clic."""
    return ft.TextButton(
        content=ft.Text(
            texto.upper(),
            size=11,
            weight=ft.FontWeight.W_600,
            font_family=tema.FUENTE_SUBHEADER,
            color=color,
        ),
        on_click=on_click,
        style=_estilo_enlace(color),
    )


def section_header(texto, contador=None):
    """Eyebrow de seccion a la izquierda + contador opcional (HINT) a la derecha."""
    controles = [eyebrow(texto)]
    if contador is not None:
        controles.append(eyebrow(contador, color=tema.HINT))
    return ft.Row(controls=controles, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)


# ----------------------------------------------------------------------------
# Bloques editoriales de Archive (ficha / timeline)
# ----------------------------------------------------------------------------
def field_block(label, contenido):
    """Etiqueta (eyebrow) + valor. Para los campos de una ficha."""
    return ft.Column(
        spacing=0,
        controls=[
            eyebrow(label, size=10),
            ft.Container(height=8),
            ft.Text(contenido, size=15, font_family=tema.FUENTE_BODY, color=tema.NAVY),
            ft.Container(height=26),
        ],
    )


def tag_pill(label):
    """Etiqueta tipo 'pill' para tags."""
    return ft.Container(
        bgcolor=tema.SECTION_BG,
        padding=ft.Padding.symmetric(horizontal=12, vertical=5),
        border_radius=3,
        content=ft.Text(label, size=11, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.MUTED),
    )


def metrics_row(metrics):
    """Fila de metricas de impacto: valor grande (Syne ambar) + etiqueta. metrics: list[{value,label}]."""
    celdas = [
        ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Text(m.get("value", ""), size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                    eyebrow(m.get("label", ""), size=10),
                ],
            ),
        )
        for m in metrics
    ]
    return ft.Container(
        padding=ft.Padding.symmetric(vertical=22),
        margin=ft.Margin.only(top=10, bottom=10),
        border=ft.Border.symmetric(vertical=ft.BorderSide(1, tema.BORDER_LIGHT)),
        content=ft.Row(controls=celdas, spacing=16),
    )


def stat_block(valor, label):
    """Estadistica: numero grande (Syne ambar) + etiqueta."""
    return ft.Column(
        spacing=6,
        controls=[
            ft.Text(valor, size=28, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
            eyebrow(label, size=10),
        ],
    )


def filter_pill(label, activo=False, on_click=None):
    """Pill de filtro; navy relleno si esta activo, contorno sutil si no."""
    return ft.Container(
        bgcolor=tema.NAVY if activo else "transparent",
        border=None if activo else ft.Border.all(1, tema.BORDER_LIGHT),
        padding=ft.Padding.symmetric(horizontal=14, vertical=7),
        border_radius=3,
        on_click=on_click,
        content=ft.Text(
            label.upper(), size=11, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER,
            color=tema.TEXTO_SOBRE_NAVY if activo else tema.MUTED,
        ),
    )


def month_header(label):
    """Encabezado de mes en el timeline: eyebrow ambar + linea que se extiende."""
    return ft.Container(
        margin=ft.Margin.only(top=28, bottom=4),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                eyebrow(label, color=tema.AMBAR),
                ft.Container(width=14),
                ft.Container(expand=True, height=1, bgcolor=tema.BORDER_LIGHT),
            ],
        ),
    )


def section_divider():
    """Divisor entre secciones: 40px dorado + resto en borde sutil."""
    return ft.Container(
        margin=ft.Margin.symmetric(vertical=24),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=40, height=1, bgcolor=tema.AMBAR),
                ft.Container(expand=True, height=1, bgcolor=tema.BORDER_LIGHT),
            ],
        ),
    )


def section_head(texto, contador=None, on_ver_todos=None):
    """Encabezado de sección (eyebrow ámbar) + contador y/o link 'Ver todos →'."""
    acciones = []
    if contador:
        acciones.append(eyebrow(contador, color=tema.HINT))
    if on_ver_todos:
        acciones.append(enlace_cta(TEXTOS["comun"]["ver_todos"], on_click=on_ver_todos))
    derecha = ft.Row(spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=acciones) if acciones else ft.Container()
    return ft.Container(
        margin=ft.Margin.only(bottom=18),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[eyebrow(texto, color=tema.AMBAR), derecha],
        ),
    )


def subrayado_bicolor():
    """Subrayado mixto de inputs: 56px dorado + resto en borde sutil."""
    return ft.Row(
        spacing=0,
        controls=[
            ft.Container(width=56, height=1, bgcolor=tema.AMBAR),
            ft.Container(expand=True, height=1, bgcolor=tema.BORDER_LIGHT),
        ],
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
