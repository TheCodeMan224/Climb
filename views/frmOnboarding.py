"""Cuestionario de 9 preguntas de Scout, organizado en 4 actos."""

import flet as ft

from data import clsInteraccionDB

# Textos exactos de las 9 preguntas. No modificar (ver seccion 12).
ACTOS = [
    (
        "Acto I: Apertura Emocional",
        [
            "¿Cómo te sientes respecto a tu momento profesional actual y qué emociones te genera pensar en tu carrera?",
            "Cuando experimentas frustración, estancamiento laboral o invisibilidad, ¿cómo lo procesas internamente?",
        ],
    ),
    (
        "Acto II: Trayectoria y Contexto",
        [
            "Cuéntanos brevemente sobre tu rol actual, tu industria y las responsabilidades principales que manejas.",
            "Si tuvieras que resumir tu trayectoria o pegar extractos clave de tu currículum, ¿cuál sería tu historia profesional?",
        ],
    ),
    (
        "Acto III: Hitos y Presión",
        [
            "¿Cuál consideras que ha sido tu mayor logro profesional hasta la fecha y por qué te enorgullece?",
            "¿Cómo reaccionas cuando tu trabajo es expuesto ante líderes clave o bajo situaciones de alta visibilidad o presión?",
        ],
    ),
    (
        "Acto IV: Brechas y Futuro",
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
        self.campos = []  # 9 TextFields en orden de pregunta.

    def _campo(self):
        campo = ft.TextField(
            multiline=True,
            min_lines=2,
            max_lines=5,
            border_color="#39406A",
            focused_border_color="#BA7517",
            color="#FFFFFF",
            cursor_color="#BA7517",
        )
        self.campos.append(campo)
        return campo

    def _terminar(self, e):
        respuestas = [(c.value or "").strip() for c in self.campos]
        p1, p2, p3, p4, p5, p6, p7, p8, p9 = respuestas

        # Mapeo declarado en la seccion 5.2.
        apertura_emocional = f"{p1} || {p2}"
        contexto_profesional = f"{p3} || {p4}"

        clsInteraccionDB.guardar_perfil(
            self.id_usuario,
            apertura_emocional,
            contexto_profesional,
            p5,  # logro_principal
            p6,  # reaccion_presion_visibilidad
            p7,  # intentos_previos
            p8,  # vision_futuro
            p9,  # desahogo_libre
        )
        self.router.navegar_a("/scout_reflection")

    def construir(self):
        bloques = [
            ft.Text(
                "Cuéntale a Scout quién eres",
                size=34,
                weight=ft.FontWeight.BOLD,
                font_family="Syne",
                color="#FFFFFF",
            ),
            ft.Text(
                "Nueve preguntas en cuatro actos. Tómate tu tiempo.",
                size=16,
                color="#AEB6D0",
            ),
            ft.Container(height=10),
        ]

        for titulo_acto, preguntas in ACTOS:
            bloques.append(
                ft.Text(
                    titulo_acto,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#BA7517",
                    font_family="Syne",
                )
            )
            for pregunta in preguntas:
                bloques.append(ft.Text(pregunta, size=15, color="#DDE2F2"))
                bloques.append(self._campo())
                bloques.append(ft.Container(height=6))
            bloques.append(ft.Container(height=14))

        bloques.append(
            ft.ElevatedButton(
                "Terminar",
                on_click=self._terminar,
                style=ft.ButtonStyle(
                    bgcolor="#BA7517",
                    color="#FFFFFF",
                    padding=ft.Padding.symmetric(horizontal=40, vertical=20),
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
            )
        )
        bloques.append(ft.Container(height=40))

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=800,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=30),
                    content=ft.Column(spacing=8, controls=bloques),
                )
            ],
        )
