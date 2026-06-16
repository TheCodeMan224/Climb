"""Dashboard principal de Climb (estilo editorial premium)."""

from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes, clsMirror
from data import clsInteraccionDB

# Descripciones breves (texto literal a usar, ver seccion 7.8). No modificar.
AGENTES = [
    ("Mirror", "coach_mirror", "Te ayuda a procesar tus patrones limitantes con preguntas socráticas."),
    ("Editor", "coach_editor", "Traduce tu impacto técnico a lenguaje ejecutivo sin perder tu voz."),
    ("Archive", "coach_archive", "Documenta tus logros profesionales para cuando importen."),
    ("Clarity", "clarity_session", "Tu espacio para desahogarte y procesar lo que sea."),
]

_DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
_MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


class frmMenuInicio:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario

    async def _refrescar_diagnostico(self, e):
        try:
            await clsAgentes.refrescar_diagnostico_incremental(self.id_usuario)
            mensaje = "Diagnóstico actualizado"
        except Exception:
            mensaje = "No se pudo actualizar el diagnóstico"
        # Aprovechar el refresco para actualizar también el voice profile.
        try:
            await clsAgentes.actualizar_voice_profile(self.id_usuario)
        except Exception:
            pass
        self.router.page.show_dialog(ft.SnackBar(ft.Text(mensaje)))
        self.router.page.update()

    # --- Helpers de fecha ---------------------------------------------------
    def _fecha_hoy(self):
        ahora = datetime.now()
        return f"{_DIAS[ahora.weekday()]} · {ahora.day} {_MESES[ahora.month - 1]} {ahora.year}"

    def _fecha_corta(self, ts):
        try:
            d = datetime.strptime(str(ts)[:10], "%Y-%m-%d")
            return f"{d.day} {_MESES[d.month - 1]}"
        except (ValueError, TypeError):
            return ""

    # --- Bloques ------------------------------------------------------------
    def _topbar(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[cmp.eyebrow("Climb", color=tema.AMBAR), cmp.eyebrow(self._fecha_hoy(), color=tema.HINT)],
        )

    def _hero(self, nombre, frase_pivote):
        controles = [
            cmp.eyebrow("Bitácora del día"),
            ft.Container(height=10),
            ft.Text(f"Hola, {nombre}", size=52, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
        ]
        if frase_pivote:
            controles.append(ft.Container(height=14))
            controles.append(
                ft.Container(
                    width=520,
                    content=ft.Text(frase_pivote, size=16, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
                )
            )
        return ft.Column(spacing=0, controls=controles)

    def _divisor(self):
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=34),
            alignment=ft.Alignment.CENTER_LEFT,
            content=cmp.hairline(width=56),
        )

    def _abrir_agente(self, tipo_agente):
        # Archive y Mirror tienen su propio flujo editorial; el resto, chat genérico.
        rutas = {"coach_archive": "/archive", "coach_mirror": "/mirror"}
        self.router.navegar_a(rutas.get(tipo_agente, f"/chat/{tipo_agente}"))

    def _ir_patron_mirror(self, nombre, descripcion):
        # Lleva el patrón de Scout seleccionado directo a la entrada de Mirror.
        self.router.mirror_patron = clsMirror.Patron(
            id=f"scout:{nombre}",
            quote=descripcion or nombre,
            source="scout",
            detected_at=datetime.now(),
            status="pending",
            scout_ref=nombre,
        )
        self.router.navegar_a("/mirror/entry")

    def _card_patron(self, num, nombre, descripcion):
        # Version compacta: numero + nombre en una linea, descripcion breve y link.
        return ft.Container(
            border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
            padding=ft.Padding.only(left=16, top=2, bottom=2),
            margin=ft.Margin.only(bottom=12),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(num, size=14, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                            ft.Text(nombre, size=15, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY, expand=True),
                            cmp.enlace_cta("Mirror  →", on_click=lambda e, n=nombre, d=descripcion: self._ir_patron_mirror(n, d)),
                        ],
                    ),
                    ft.Text(descripcion, size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ],
            ),
        )

    def _mission_dots(self, completadas, total):
        if total <= 0:
            return ft.Container(height=0)
        barras = [
            ft.Container(
                expand=True,
                height=3,
                border_radius=1,
                bgcolor=tema.AMBAR if i < completadas else ft.Colors.with_opacity(0.20, tema.OFF_WHITE),
            )
            for i in range(total)
        ]
        return ft.Row(controls=barras, spacing=6)

    def _banner_mision(self, estado):
        mision = estado["mision"]
        progreso = estado["progreso"]
        acciones = mision.get("acciones", [])
        total = len(acciones)
        completadas = sum(1 for p in progreso if p)

        if completadas >= total and total > 0:
            proxima = "Misión completada · genera la siguiente"
        else:
            pendientes = [a for a, hecha in zip(acciones, progreso) if not hecha]
            proxima = pendientes[0] if pendientes else (acciones[0] if acciones else "")

        return ft.Container(
            bgcolor=tema.NAVY,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=36, vertical=32),
            content=ft.Column(
                spacing=0,
                controls=[
                    cmp.eyebrow("Misión activa", color=tema.AMBAR),
                    ft.Container(height=12),
                    ft.Text(mision.get("nombre_mision", ""), size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.TEXTO_SOBRE_NAVY),
                    ft.Container(height=22),
                    self._mission_dots(completadas, total),
                    ft.Container(height=22),
                    ft.Text(
                        f"{completadas} DE {total} ACCIONES  ·  PRÓXIMA · {proxima.upper()}",
                        size=11,
                        weight=ft.FontWeight.W_600,
                        font_family=tema.FUENTE_SUBHEADER,
                        color=tema.TEXTO_SUAVE_SOBRE_NAVY,
                    ),
                    ft.Container(height=22),
                    ft.Row(controls=[cmp.boton_ambar("Ver mi misión  →", on_click=lambda e: self.router.navegar_a("/pacer"))]),
                ],
            ),
        )

    def _banner_camino_sin_mision(self, camino):
        return ft.Container(
            bgcolor=tema.NAVY,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=36, vertical=32),
            content=ft.Column(
                spacing=0,
                controls=[
                    cmp.eyebrow("Tu camino", color=tema.AMBAR),
                    ft.Container(height=12),
                    ft.Text(camino.get("nombre_camino", ""), size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.TEXTO_SOBRE_NAVY),
                    ft.Container(height=14),
                    ft.Text("Aún no has generado tu primera misión.", size=14, font_family=tema.FUENTE_BODY, color=tema.TEXTO_SUAVE_SOBRE_NAVY),
                    ft.Container(height=22),
                    ft.Row(controls=[cmp.boton_ambar("Generar mi misión  →", on_click=lambda e: self.router.navegar_a("/pacer"))]),
                ],
            ),
        )

    def _card_agente(self, num, nombre, tipo_agente, descripcion):
        return ft.Container(
            expand=True,
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=6,
            padding=26,
            content=ft.Row(
                spacing=18,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(width=48, content=ft.Text(num, size=28, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR, no_wrap=True)),
                    ft.Column(
                        expand=True,
                        spacing=0,
                        controls=[
                            ft.Text(nombre, size=20, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                            ft.Container(height=8),
                            ft.Text(descripcion, size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                            ft.Container(height=12),
                            cmp.enlace_cta("Hablar  →", on_click=lambda e, t=tipo_agente: self._abrir_agente(t)),
                        ],
                    ),
                ],
            ),
        )

    def _fila_logro(self, logro, ultimo):
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=16),
            border=None if ultimo else ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(width=80, content=cmp.eyebrow(self._fecha_corta(logro.get("fechaRegistroLogro")), color=tema.HINT)),
                    ft.Container(width=20),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(logro.get("logro", ""), size=14, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY, expand=True),
                                    cmp.eyebrow(logro.get("tipoLogro") or "", color=tema.HINT),
                                ],
                            ),
                            ft.Text(logro.get("descripcionLogro", ""), size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                        ],
                    ),
                ],
            ),
        )

    # --- Construccion -------------------------------------------------------
    def construir(self):
        nombre = clsInteraccionDB.obtener_nombre_usuario(self.id_usuario) or self.router.nombre or ""

        # Datos del perfil consolidado (si ya hubo diagnostico).
        resumen_raw = clsInteraccionDB.obtener_ultimo_resumen(self.id_usuario)
        frase_pivote = ""
        patrones = []
        if resumen_raw:
            import json
            resumen = json.loads(resumen_raw)
            frase_pivote = resumen.get("voice_profile", {}).get("tono_natural", "")
            patrones = resumen.get("patrones_consolidados", [])

        estado_mision = clsInteraccionDB.obtener_ultima_mision(self.id_usuario)
        logros_recientes = clsInteraccionDB.obtener_logros(self.id_usuario)[:4]  # mas recientes primero

        controles = [self._topbar(), ft.Container(height=36), self._hero(nombre, frase_pivote)]

        # Patrones detectados (compacto, maximo 2).
        patrones_top = patrones[:2]
        if patrones_top:
            controles.append(self._divisor())
            controles.append(cmp.section_header("Scout · Patrones detectados", contador=f"{len(patrones_top):02d}"))
            controles.append(ft.Container(height=14))
            for i, p in enumerate(patrones_top, start=1):
                controles.append(self._card_patron(f"{i:02d}", p.get("nombre", ""), p.get("descripcion", "")))

        # Mision activa; si no hay misión pero sí camino, ofrecer generarla.
        camino = clsInteraccionDB.obtener_camino_elegido(self.id_usuario)
        if estado_mision:
            controles.append(self._divisor())
            controles.append(cmp.section_header("Camino · Activo"))
            controles.append(ft.Container(height=22))
            controles.append(self._banner_mision(estado_mision))
        elif camino:
            controles.append(self._divisor())
            controles.append(cmp.section_header("Camino · Activo"))
            controles.append(ft.Container(height=22))
            controles.append(self._banner_camino_sin_mision(camino))

        # Agentes (siempre).
        controles.append(self._divisor())
        controles.append(cmp.section_header("Tus agentes", contador=f"{len(AGENTES):02d}"))
        controles.append(ft.Container(height=22))
        controles.append(
            ft.Row(spacing=16, controls=[
                self._card_agente("01", *AGENTES[0]),
                self._card_agente("02", *AGENTES[1]),
            ])
        )
        controles.append(ft.Container(height=16))
        controles.append(
            ft.Row(spacing=16, controls=[
                self._card_agente("03", *AGENTES[2]),
                self._card_agente("04", *AGENTES[3]),
            ])
        )

        # Del archivo: logros reales registrados por Archive (solo si existen).
        if logros_recientes:
            controles.append(self._divisor())
            controles.append(cmp.section_header("Del archivo · Logros recientes", contador=f"{len(logros_recientes):02d}"))
            controles.append(ft.Container(height=4))
            for i, l in enumerate(logros_recientes):
                controles.append(self._fila_logro(l, ultimo=(i == len(logros_recientes) - 1)))

        # Footer.
        controles.append(
            ft.Container(
                padding=ft.Padding.only(top=24),
                margin=ft.Margin.only(top=32),
                border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        cmp.enlace_cta("Refrescar diagnóstico  →", on_click=self._refrescar_diagnostico),
                        cmp.eyebrow("v0.1 · Beta", color=tema.HINT),
                    ],
                ),
            )
        )
        controles.append(ft.Container(height=40))

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=880,
                    padding=ft.Padding.symmetric(horizontal=48, vertical=40),
                    content=ft.Column(spacing=0, controls=controles),
                )
            ],
        )
