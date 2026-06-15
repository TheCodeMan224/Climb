"""Archive · Pantalla 3: El Archivo — timeline editorial de todos los logros."""

import flet as ft

import componentes as cmp
import tema
from data import clsInteraccionDB

_PERIODOS = ["Todos", "Este mes", "Trimestre", "Año"]


class frmArchiveTimeline:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario

    # --- Eventos ------------------------------------------------------------
    def _documentar(self, e):
        self.router.navegar_a("/chat/coach_archive")

    def _abrir_logro(self, logro):
        # Reusa la ficha en modo lectura (sin botones de editar/archivar).
        self.router.logro_ficha = {**logro, "_guardado": True}
        self.router.navegar_a("/archive/ficha")

    # --- Entrada del timeline ----------------------------------------------
    def _entrada_logro(self, logro):
        metric = logro.get("metric_destacada")
        bloque_metric = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.END,
            spacing=2,
            controls=[
                ft.Text(metric["value"] if metric else "—", size=22, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR if metric else tema.HINT),
                cmp.eyebrow(metric["label"] if metric else "Sin métrica", color=tema.HINT, size=9),
            ],
        )

        contexto = logro.get("contexto", "")
        contexto_corto = contexto[:160] + ("..." if len(contexto) > 160 else "")

        cuerpo = ft.Column(
            spacing=0,
            controls=[
                cmp.eyebrow(logro.get("tipo", ""), color=tema.AMBAR, size=10),
                ft.Container(height=6),
                ft.Text(logro.get("titulo", ""), size=19, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ft.Container(height=8),
                ft.Text(contexto_corto, size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                ft.Container(height=10),
                ft.Row(wrap=True, spacing=6, run_spacing=6, controls=[cmp.tag_pill(t) for t in logro.get("tags", [])]),
            ],
        )

        return ft.Container(
            padding=ft.Padding.symmetric(vertical=22),
            border=ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            on_click=lambda e, lg=logro: self._abrir_logro(lg),
            ink=True,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(width=80, content=cmp.eyebrow(logro.get("fecha_corta", ""), color=tema.HINT)),
                    ft.Container(width=28),
                    ft.Container(expand=True, content=cuerpo),
                    ft.Container(width=28),
                    ft.Container(width=90, content=bloque_metric),
                ],
            ),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        stats = clsInteraccionDB.archivo_stats(self.id_usuario)
        agrupado = clsInteraccionDB.archivo_agrupado_por_mes(self.id_usuario)

        boton_doc = ft.ElevatedButton(
            content=ft.Text("+ DOCUMENTAR LOGRO", size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
            on_click=self._documentar,
            style=ft.ButtonStyle(
                bgcolor=tema.NAVY,
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=ft.Padding.symmetric(horizontal=22, vertical=14),
                elevation=0,
            ),
        )

        hero = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.END,
            controls=[
                ft.Column(spacing=10, controls=[
                    cmp.eyebrow("Bitácora de logros"),
                    ft.Text("Tu archivo", size=48, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ]),
                boton_doc,
            ],
        )

        fila_stats = ft.Container(
            padding=ft.Padding.symmetric(vertical=22),
            margin=ft.Margin.symmetric(vertical=20),
            border=ft.Border.symmetric(vertical=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(spacing=56, controls=[
                cmp.stat_block(str(stats["total"]), "Logros totales"),
                cmp.stat_block(str(stats["este_trimestre"]), "Este trimestre"),
                cmp.stat_block(stats["impacto"], "Impacto registrado"),
                cmp.stat_block(str(stats["tags"]), "Tags activos"),
            ]),
        )

        # Filtros visuales (placeholder; el filtrado real se puede conectar luego).
        buscador = ft.Container(
            width=240,
            border=ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            padding=ft.Padding.only(bottom=4),
            content=ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Icon(ft.Icons.SEARCH, color=tema.HINT, size=14),
                ft.TextField(
                    hint_text="Buscar en el archivo...",
                    border=ft.InputBorder.NONE, bgcolor="transparent", expand=True,
                    text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=13, color=tema.NAVY),
                    hint_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=13, color=tema.HINT),
                    content_padding=ft.Padding.symmetric(horizontal=0, vertical=6),
                ),
            ]),
        )
        filtros = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            wrap=True, spacing=16, run_spacing=12,
            controls=[
                ft.Row(spacing=6, controls=[cmp.filter_pill(p, activo=(i == 0)) for i, p in enumerate(_PERIODOS)]),
                buscador,
            ],
        )

        controles = [
            cmp.topbar(f"El Archivo  ·  {stats['total']} logros documentados", derecha="← Volver al dashboard", on_back=lambda e: self.router.navegar_a("/menu_inicio")),
            ft.Container(height=32),
            hero,
            ft.Container(
                margin=ft.Margin.only(top=12),
                width=480,
                content=ft.Text(
                    "Todo lo que documentaste con Archive. Búscalo cuando lo necesites — "
                    "entrevistas, reviews, propuestas.",
                    size=14, font_family=tema.FUENTE_BODY, color=tema.MUTED,
                ),
            ),
            fila_stats,
            filtros,
            ft.Container(height=18),
        ]

        if not agrupado:
            controles.append(
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=40),
                    content=ft.Text("Aún no has documentado logros. Empieza con “+ Documentar logro”.", size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                )
            )
        else:
            for mes, logros in agrupado.items():
                controles.append(cmp.month_header(mes))
                for logro in logros:
                    controles.append(self._entrada_logro(logro))

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
