"""Onboarding: una pregunta a la vez, con barra de progreso por segmentos."""

import flet as ft

import componentes as cmp
import tema
from data import clsInteraccionDB

# Textos exactos de las 9 preguntas. No modificar (ver seccion 12).
# Cada acto: (titulo, intro narrativa, [preguntas]).
ACTOS = [
    (
        "Acto I: Apertura Emocional",
        "Empezamos por lo que sientes. El resto vendrá después.",
        [
            "¿Cómo te sientes respecto a tu momento profesional actual y qué emociones te genera pensar en tu carrera?",
            "Cuando experimentas frustración, estancamiento laboral o invisibilidad, ¿cómo lo procesas internamente?",
        ],
    ),
    (
        "Acto II: Trayectoria y Contexto",
        "Ahora cuéntanos de dónde vienes y qué haces hoy.",
        [
            "Cuéntanos brevemente sobre tu rol actual, tu industria y las responsabilidades principales que manejas.",
            "Si tuvieras que resumir tu trayectoria o pegar extractos clave de tu currículum, ¿cuál sería tu historia profesional?",
        ],
    ),
    (
        "Acto III: Hitos y Presión",
        "Hablemos de tus logros y de cómo respondes bajo presión.",
        [
            "¿Cuál consideras que ha sido tu mayor logro profesional hasta la fecha y por qué te enorgullece?",
            "¿Cómo reaccionas cuando tu trabajo es expuesto ante líderes clave o bajo situaciones de alta visibilidad o presión?",
        ],
    ),
    (
        "Acto IV: Brechas y Futuro",
        "Y para cerrar, hacia dónde quieres ir desde aquí.",
        [
            "¿Qué acciones o intentos previos has realizado para acelerar tu crecimiento o posicionamiento, y qué no funcionó?",
            "Si no tuvieras ninguna limitación de recursos, ¿cómo se ve tu situación profesional ideal a 3 años?",
            "Este es tu espacio libre de desahogo. ¿Hay algo más que te gustaría liberar sobre tus retos actuales que no hayamos cubierto?",
        ],
    ),
]


class frmOnboarding:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario

        self.preguntas = [(t, intro, p) for t, intro, lista in ACTOS for p in lista]
        self.respuestas = ["" for _ in self.preguntas]
        self.indice = 0

        self.campo = None
        self.switcher = None
        self.error = ft.Text("", color=tema.CORAL, size=13)
        self.boton_anterior = None
        self.boton_siguiente = None
        self.fila_segmentos = ft.Row(spacing=6)
        self.lbl_progreso = ft.Text("", size=11, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.HINT)

    # --- Contenido de la pregunta actual (cabecera + numero + pregunta) ----
    def _contenido_pregunta(self):
        acto, intro, texto = self.preguntas[self.indice]
        primera_del_acto = self.indice == 0 or self.preguntas[self.indice - 1][0] != acto

        if primera_del_acto:
            cabecera = ft.Column(
                spacing=0,
                controls=[
                    cmp.eyebrow(acto),
                    ft.Container(height=12),
                    cmp.hairline(width=48),
                    ft.Container(height=18),
                    ft.Text(intro, size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                ],
            )
            sep = 24
        else:
            cabecera = cmp.eyebrow(acto)
            sep = 18

        return ft.Column(
            key=str(self.indice),
            spacing=0,
            controls=[
                cabecera,
                ft.Container(height=sep),
                ft.Text(f"{self.indice + 1:02d}", size=56, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                ft.Container(height=10),
                ft.Text(texto, size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
            ],
        )

    # --- Progreso por segmentos --------------------------------------------
    def _segmentos(self):
        return [
            ft.Container(expand=True, height=2, border_radius=1, bgcolor=tema.AMBAR if i <= self.indice else tema.BORDER_LIGHT)
            for i in range(len(self.preguntas))
        ]

    def _texto_progreso(self):
        return f"PREGUNTA {self.indice + 1:02d} / {len(self.preguntas):02d}"

    def _btn_anterior_contenido(self):
        color = tema.HINT if self.indice == 0 else tema.NAVY
        return ft.Text("← ANTERIOR", size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=color)

    # --- Estado/navegacion --------------------------------------------------
    def _guardar_actual(self):
        if self.campo is not None:
            self.respuestas[self.indice] = self.campo.value or ""

    def _refrescar(self):
        es_ultima = self.indice == len(self.preguntas) - 1
        self.switcher.content = self._contenido_pregunta()
        self.campo.value = self.respuestas[self.indice]
        self.error.value = ""
        self.boton_anterior.disabled = self.indice == 0
        self.boton_anterior.content = self._btn_anterior_contenido()
        self.boton_siguiente.content = "Llegar a la cima  →" if es_ultima else "Siguiente  →"
        self.fila_segmentos.controls = self._segmentos()
        self.lbl_progreso.value = self._texto_progreso()
        self.router.page.update()

    def _siguiente(self, e):
        self._guardar_actual()
        if not self.respuestas[self.indice].strip():
            self.error.value = "Escribe tu respuesta para continuar."
            self.router.page.update()
            return
        if self.indice == len(self.preguntas) - 1:
            self._terminar()
            return
        self.indice += 1
        self._refrescar()

    def _anterior(self, e):
        self._guardar_actual()
        if self.indice > 0:
            self.indice -= 1
            self._refrescar()

    def _terminar(self):
        p1, p2, p3, p4, p5, p6, p7, p8, p9 = self.respuestas
        apertura_emocional = f"{p1} || {p2}"
        contexto_profesional = f"{p3} || {p4}"
        clsInteraccionDB.guardar_perfil(
            self.id_usuario,
            apertura_emocional,
            contexto_profesional,
            p5, p6, p7, p8, p9,
        )
        self.router.navegar_a("/scout_reflection")

    # --- Construccion -------------------------------------------------------
    def construir(self):
        self.lbl_progreso.value = self._texto_progreso()
        self.fila_segmentos.controls = self._segmentos()
        self.switcher = ft.AnimatedSwitcher(
            content=self._contenido_pregunta(),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=220,
            reverse_duration=220,
            switch_in_curve=ft.AnimationCurve.EASE_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN,
        )

        # Campo persistente: ancho completo y expande para llenar el alto sobrante.
        self.campo = ft.TextField(
            value=self.respuestas[self.indice],
            hint_text="Escribe lo que te venga, sin filtro...",
            multiline=True,
            expand=True,
            autofocus=True,
            border_color=tema.BORDER_LIGHT,
            focused_border_color=tema.BLUE,
            border_radius=8,
            color=tema.TEXTO,
            cursor_color=tema.BLUE,
            text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=16, color=tema.TEXTO, height=1.6),
            hint_style=ft.TextStyle(font_family=tema.FUENTE_SERIF, italic=True, size=16, color=tema.HINT),
        )

        self.boton_anterior = ft.OutlinedButton(
            content=self._btn_anterior_contenido(),
            on_click=self._anterior,
            disabled=True,
            style=ft.ButtonStyle(
                side=ft.BorderSide(1, tema.BORDER_LIGHT),
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=ft.Padding.symmetric(horizontal=24, vertical=18),
            ),
        )
        self.boton_siguiente = cmp.boton_primario("Siguiente  →", on_click=self._siguiente)

        topbar = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[cmp.eyebrow("Climb", color=tema.AMBAR), cmp.eyebrow("Diagnóstico inicial", color=tema.HINT)],
        )

        # Columna que llena el viewport; el campo (expand) absorbe el alto sobrante,
        # así todo el formulario es visible sin necesidad de scroll de página.
        contenido = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=0,
            controls=[
                topbar,
                ft.Container(height=28),
                self.switcher,
                ft.Container(height=18),
                self.campo,
                ft.Container(height=8),
                self.error,
                ft.Container(height=14),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self.boton_anterior, self.boton_siguiente],
                ),
                ft.Container(height=20),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[self.lbl_progreso, self.fila_segmentos],
                ),
            ],
        )

        return ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(
                    width=720,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=36),
                    content=contenido,
                )
            ],
        )
