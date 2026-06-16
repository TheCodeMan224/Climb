"""Onboarding: una pregunta a la vez, con barra de progreso por segmentos."""

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes
from data import clsInteraccionDB

# Cada acto: (titulo, intro narrativa, [preguntas]). Títulos e intros son solo
# de cara al usuario; el guardado a BD es posicional (no depende de estos textos).
ACTOS = [
    (
        "Acto I — Dónde estás hoy",
        "No hay respuestas correctas aquí. Escríbeme como hablas, aunque salga desordenado. Solo quiero conocerte de verdad.",
        [
            "¿Cómo te sientes con tu carrera en este momento? No la versión de LinkedIn, la de verdad.",
            "Cuando algo del trabajo te frustra o sientes que no avanzas, ¿qué haces con eso? ¿Lo hablas, te lo guardas, trabajas más horas?",
        ],
    ),
    (
        "Acto II — De dónde vienes",
        "Ahora cuéntame tu historia. Sin currículum y sin formalidades, como si me lo contaras tomando un café.",
        [
            "Cuéntame qué haces hoy. ¿En qué trabajas, en qué tipo de empresa, y de qué eres responsable en el día a día?",
            "Y para llegar ahí, ¿por dónde pasaste? Cuéntame tu camino hasta hoy, como se lo contarías a alguien en una cena, no en una entrevista.",
        ],
    ),
    (
        "Acto III — Lo que has construido",
        "Hablemos de lo que has logrado, y de cómo lo vives cuando todo depende de ti.",
        [
            "¿Cuál es el logro del que te sientes más orgulloso? Cuéntame qué pasó y por qué ese te importa tanto.",
            "Cuando te toca presentar tu trabajo frente a gente importante, o todo recae sobre ti, ¿cómo lo vives? ¿Te crece o te pesa?",
        ],
    ),
    (
        "Acto IV — Hacia dónde vas",
        "Y para cerrar, hacia dónde quieres ir desde aquí.",
        [
            "¿Qué has intentado para crecer o para que te noten más? Cuéntame también lo que probaste y no funcionó, eso me dice mucho de ti.",
            "Imagina tu carrera en tres años, sin límites de ningún tipo. ¿Cómo se ve? ¿Dónde estás, qué haces, cómo te sientes?",
            "Antes de cerrar, este espacio es tuyo. ¿Hay algo de tu carrera que traes cargando y que no me has contado todavía?",
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
        # Primera muestra para el voice profile (y siembra inicial del perfil).
        for respuesta in self.respuestas:
            clsInteraccionDB.registrar_texto_usuario(self.id_usuario, "onboarding", respuesta)
        self.router.page.run_task(clsAgentes.actualizar_voice_profile, self.id_usuario)
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
