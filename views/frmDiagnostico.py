"""Las 9 secciones ceremoniales del diagnostico cualitativo."""

import flet as ft
import tema

from core import clsAgentes
from core.textos import TEXTOS

_T = TEXTOS["diagnostico"]


class frmDiagnostico:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.diag = router.diagnostico_actual or {}
        self.boton_plan = None

    # --- Evento: generar los tres caminos -----------------------------------
    async def _ver_plan(self, e):
        self.boton_plan.disabled = True
        self.router.mostrar_carga(_T["generando_plan"])
        try:
            caminos = await clsAgentes.generar_tres_caminos(self.id_usuario, self.diag)
        except Exception:
            self.router.ocultar_carga()
            self.boton_plan.text = _T["error"]
            self.boton_plan.disabled = False
            self.router.page.update()
            return
        self.router.caminos_actual = caminos
        self.router.navegar_a("/caminos")

    # --- Helpers de seccion -------------------------------------------------
    def _card_retrato(self, titulo, texto, color):
        return ft.Container(
            expand=True,
            padding=18,
            bgcolor=tema.SUPERFICIE,
            border_radius=12,
            border=ft.Border.only(left=ft.BorderSide(5, color)),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(titulo, size=13, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(texto, size=14, color=tema.TEXTO),
                ],
            ),
        )

    def _fila_visibilidad(self, dim):
        color = tema.COLOR_SEMAFORO.get(dim.get("estado"), tema.MUTED)
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=10),
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(width=14, height=14, bgcolor=color, border_radius=7, margin=ft.Margin.only(top=3)),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(dim.get("dimension", ""), size=15, weight=ft.FontWeight.BOLD, color=tema.TEXTO),
                            ft.Text(dim.get("descripcion", ""), size=13, color=tema.TEXTO_SUAVE),
                        ],
                    ),
                ],
            ),
        )

    def _card_patron(self, patron):
        return ft.Container(
            padding=18,
            bgcolor=tema.SUPERFICIE,
            border_radius=12,
            border=ft.Border.only(left=ft.BorderSide(5, tema.NAVY)),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(patron.get("nombre", ""), size=16, weight=ft.FontWeight.BOLD, color=tema.NAVY, font_family=tema.FUENTE_SUBHEADER),
                    ft.Text(patron.get("descripcion", ""), size=14, color=tema.TEXTO),
                ],
            ),
        )

    def _subheader(self, texto):
        return ft.Text(texto, size=20, weight=ft.FontWeight.BOLD, color=tema.TEXTO, font_family=tema.FUENTE_SUBHEADER)

    # --- Construccion -------------------------------------------------------
    def construir(self):
        d = self.diag
        nombre = d.get("nombre_usuario") or self.router.nombre or ""
        retrato = d.get("retrato", {})
        creencia = d.get("creencia_limitante", {})
        estancamiento = d.get("tipo_estancamiento", {})
        proximo = d.get("proximo_paso", {})

        secciones = []

        # Seccion 1 - Header
        secciones.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Text(
                                _T["saludo"].format(nombre=nombre),
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                font_family=tema.FUENTE_DISPLAY,
                                color=tema.TEXTO,
                            ),
                            ft.Text(_T["subtitulo"], size=15, italic=True, color=tema.TEXTO_SUAVE),
                        ],
                    ),
                    ft.OutlinedButton(
                        _T["descargar_pdf"],
                        on_click=lambda e: None,  # mockup, sin funcionalidad real
                        style=ft.ButtonStyle(color=tema.BLUE),
                    ),
                ],
            )
        )

        # Rótulo de IA responsable: esto es una lectura inicial, no un veredicto.
        secciones.append(ft.Container(height=12))
        secciones.append(
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                bgcolor=tema.SECTION_BG,
                border_radius=8,
                border=ft.Border.only(left=ft.BorderSide(3, tema.AMBAR)),
                content=ft.Text(
                    _T["rotulo"],
                    size=13, italic=True, color=tema.NAVY, font_family=tema.FUENTE_SERIF),
            )
        )

        # Seccion 2 - Frase pivote hero
        secciones.append(ft.Container(height=10))
        secciones.append(
            ft.Text(
                d.get("frase_pivote", ""),
                size=30,
                weight=ft.FontWeight.BOLD,
                font_family=tema.FUENTE_DISPLAY,
                color=tema.BLUE,
            )
        )

        # Seccion 3 - Parrafo narrativo intimo
        secciones.append(ft.Container(height=6))
        secciones.append(
            ft.Text(d.get("parrafo_narrativo", ""), size=16, color=tema.TEXTO, font_family=tema.FUENTE_BODY),
        )

        # Seccion 4 - Retrato en 3 cards
        secciones.append(ft.Container(height=18))
        secciones.append(
            ft.Row(
                spacing=14,
                controls=[
                    self._card_retrato(_T["retrato_eres"], retrato.get("lo_que_eres", ""), tema.NAVY),
                    self._card_retrato(_T["retrato_frena"], retrato.get("lo_que_te_frena", ""), tema.CORAL),
                    self._card_retrato(_T["retrato_brecha"], retrato.get("donde_esta_la_brecha", ""), tema.AMBAR),
                ],
            )
        )

        # Seccion 5 - Visibilidad en 4 dimensiones
        secciones.append(ft.Container(height=24))
        secciones.append(self._subheader(_T["h_visibilidad"]))
        for dim in d.get("visibilidad", []):
            secciones.append(self._fila_visibilidad(dim))

        # Seccion 6 - Tres patrones detectados
        secciones.append(ft.Container(height=24))
        secciones.append(self._subheader(_T["h_patrones"]))
        for patron in d.get("patrones", []):
            secciones.append(ft.Container(height=8))
            secciones.append(self._card_patron(patron))

        # Seccion 7 - La creencia limitante
        secciones.append(ft.Container(height=24))
        secciones.append(
            ft.Container(
                padding=20,
                bgcolor=tema.SECTION_BG,
                border_radius=10,
                border=ft.Border.only(left=ft.BorderSide(5, tema.BLUE)),
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(
                            creencia.get("cita", ""),
                            size=18,
                            italic=True,
                            font_family=tema.FUENTE_SERIF,
                            color=tema.TEXTO,
                        ),
                        ft.Text(creencia.get("reformulacion", ""), size=15, color=tema.TEXTO, font_family=tema.FUENTE_BODY),
                    ],
                ),
            )
        )

        # Seccion 8 - Tipo de estancamiento + subtitulo
        secciones.append(ft.Container(height=24))
        secciones.append(
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        estancamiento.get("categoria", ""),
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        font_family=tema.FUENTE_SUBHEADER,
                        color=tema.TEXTO,
                    ),
                    ft.Text(estancamiento.get("subtitulo", ""), size=15, color=tema.TEXTO_SUAVE),
                ],
            )
        )

        # Seccion 9 - Proximo paso con CTA
        self.boton_plan = ft.ElevatedButton(
            _T["ver_plan"],
            on_click=self._ver_plan,
            style=ft.ButtonStyle(
                bgcolor=tema.AMBAR,
                color=tema.TEXTO_SOBRE_NAVY,
                padding=ft.Padding.symmetric(horizontal=30, vertical=20),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )
        secciones.append(ft.Container(height=24))
        secciones.append(
            ft.Container(
                padding=28,
                bgcolor=tema.NAVY,
                border_radius=16,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text(_T["h_siguiente"], size=22, weight=ft.FontWeight.BOLD, color=tema.TEXTO_SOBRE_NAVY, font_family=tema.FUENTE_SUBHEADER),
                        ft.Text(proximo.get("parrafo", ""), size=15, color=tema.TEXTO_SOBRE_NAVY),
                        ft.Container(height=4),
                        self.boton_plan,
                    ],
                ),
            )
        )
        secciones.append(ft.Container(height=50))

        # La columna raiz hace expand=True como hija directa de la pagina (que es
        # un Column flex) y scroll=AUTO; asi obtiene una altura acotada y el
        # scroll funciona de forma fiable. El ancho fijo se centra dentro.
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=900,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=30),
                    content=ft.Column(spacing=4, controls=secciones),
                )
            ],
        )
