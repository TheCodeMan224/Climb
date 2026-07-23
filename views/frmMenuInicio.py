"""Dashboard principal de Climb (estilo editorial premium)."""

from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes, clsMirror
from core.textos import TEXTOS
from data import clsInteraccionDB

_T = TEXTOS["dashboard"]
_COMUN = TEXTOS["comun"]  # proxy vivo: resuelve el idioma al leer


def _agentes():
    """Descripciones breves de los agentes en el idioma actual (se lee al render)."""
    return [
        ("Mirror", "coach_mirror", _T["ag_mirror"]),
        ("Editor", "coach_editor", _T["ag_editor"]),
        ("Archive", "coach_archive", _T["ag_archive"]),
        ("Clarity", "clarity_session", _T["ag_clarity"]),
    ]


class frmMenuInicio:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario

    async def _refrescar_diagnostico(self, e):
        try:
            await clsAgentes.refrescar_diagnostico_incremental(self.id_usuario)
            mensaje = _T["diag_actualizado"]
        except Exception:
            mensaje = _T["diag_error"]
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
        return f"{_COMUN['dias'][ahora.weekday()]} · {ahora.day} {_COMUN['meses'][ahora.month - 1]} {ahora.year}"

    def _fecha_corta(self, ts):
        try:
            d = datetime.strptime(str(ts)[:10], "%Y-%m-%d")
            return f"{d.day} {_COMUN['meses'][d.month - 1]}"
        except (ValueError, TypeError):
            return ""

    # --- Bloques ------------------------------------------------------------
    def _topbar(self):
        # El idioma se fija al crear la cuenta; por eso NO se ofrece cambiarlo aquí.
        # Para reactivar el cambio desde el menú en el futuro, basta con volver a
        # poner cmp.toggle_idioma(self.router) junto a la marca (toda la lógica sigue).
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[cmp.eyebrow(TEXTOS["comun"]["marca"], color=tema.AMBAR), cmp.eyebrow(self._fecha_hoy(), color=tema.HINT)],
        )

    def _hero(self, nombre, frase_pivote):
        controles = [
            cmp.eyebrow(_T["bitacora"]),
            ft.Container(height=10),
            ft.Text(_T["saludo"].format(nombre=nombre), size=52, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
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
        rutas = {"coach_archive": "/archive", "coach_mirror": "/mirror", "coach_editor": "/editor", "clarity_session": "/clarity"}
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
                            cmp.enlace_cta(_T["ir_mirror"], on_click=lambda e, n=nombre, d=descripcion: self._ir_patron_mirror(n, d)),
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
            proxima = _T["mision_completada"]
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
                    cmp.eyebrow(_T["mision_activa"], color=tema.AMBAR),
                    ft.Container(height=12),
                    ft.Text(mision.get("nombre_mision", ""), size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.TEXTO_SOBRE_NAVY),
                    ft.Container(height=22),
                    self._mission_dots(completadas, total),
                    ft.Container(height=22),
                    ft.Text(
                        _T["acciones_proxima"].format(completadas=completadas, total=total, proxima=proxima.upper()),
                        size=11,
                        weight=ft.FontWeight.W_600,
                        font_family=tema.FUENTE_SUBHEADER,
                        color=tema.TEXTO_SUAVE_SOBRE_NAVY,
                    ),
                    ft.Container(height=22),
                    ft.Row(controls=[cmp.boton_ambar(_T["ver_mision"], on_click=lambda e: self.router.navegar_a("/pacer"))]),
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
                    cmp.eyebrow(_T["tu_camino"], color=tema.AMBAR),
                    ft.Container(height=12),
                    ft.Text(camino.get("nombre_camino", ""), size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.TEXTO_SOBRE_NAVY),
                    ft.Container(height=14),
                    ft.Text(_T["sin_mision"], size=14, font_family=tema.FUENTE_BODY, color=tema.TEXTO_SUAVE_SOBRE_NAVY),
                    ft.Container(height=22),
                    ft.Row(controls=[cmp.boton_ambar(_T["generar_mision"], on_click=lambda e: self.router.navegar_a("/pacer"))]),
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
                            cmp.enlace_cta(_T["hablar"], on_click=lambda e, t=tipo_agente: self._abrir_agente(t)),
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
                    ft.Container(width=80, content=cmp.eyebrow(self._fecha_corta(logro.get("fecha_registro_logro")), color=tema.HINT)),
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
                                    cmp.eyebrow(logro.get("tipo_logro") or "", color=tema.HINT),
                                ],
                            ),
                            ft.Text(logro.get("descripcion_logro", ""), size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED),
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
            controles.append(cmp.section_header(_T["h_patrones"], contador=f"{len(patrones_top):02d}"))
            controles.append(ft.Container(height=14))
            for i, p in enumerate(patrones_top, start=1):
                controles.append(self._card_patron(f"{i:02d}", p.get("nombre", ""), p.get("descripcion", "")))

        # Mision activa; si no hay misión pero sí camino, ofrecer generarla.
        camino = clsInteraccionDB.obtener_camino_elegido(self.id_usuario)
        if estado_mision:
            controles.append(self._divisor())
            controles.append(cmp.section_header(_T["h_camino"]))
            controles.append(ft.Container(height=22))
            controles.append(self._banner_mision(estado_mision))
        elif camino:
            controles.append(self._divisor())
            controles.append(cmp.section_header(_T["h_camino"]))
            controles.append(ft.Container(height=22))
            controles.append(self._banner_camino_sin_mision(camino))

        # Agentes (siempre).
        controles.append(self._divisor())
        ags = _agentes()
        controles.append(cmp.section_header(_T["h_agentes"], contador=f"{len(ags):02d}"))
        controles.append(ft.Container(height=22))
        controles.append(
            ft.Row(spacing=16, controls=[
                self._card_agente("01", *ags[0]),
                self._card_agente("02", *ags[1]),
            ])
        )
        controles.append(ft.Container(height=16))
        controles.append(
            ft.Row(spacing=16, controls=[
                self._card_agente("03", *ags[2]),
                self._card_agente("04", *ags[3]),
            ])
        )

        # Del archivo: logros reales registrados por Archive (solo si existen).
        if logros_recientes:
            controles.append(self._divisor())
            controles.append(cmp.section_header(_T["h_archivo"], contador=f"{len(logros_recientes):02d}"))
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
                        cmp.enlace_cta(_T["refrescar"], on_click=self._refrescar_diagnostico),
                        cmp.eyebrow(_T["version"], color=tema.HINT),
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
