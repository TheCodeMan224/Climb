"""Archive · Pantalla 1: conversación editorial con el agente Archive.

Estética editorial (sin burbujas): cada turno es eyebrow del hablante + texto +
hairline divisoria. Cuando Archive emite la frase trigger, aparecen dos botones
('Sí, generar ficha' / 'Quiero modificar algo').
"""

import traceback
from datetime import datetime

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes
from core.textos import TEXTOS
from data import clsInteraccionDB

_T = TEXTOS["archive"]
_APERTURA = _T["apertura"]

# Fragmento de la frase trigger (en inglés) que el prompt obliga a Archive a usar literal.
_TRIGGER = "document the win this way"


class frmArchiveChat:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario

        # Turnos en memoria para esta sesión: (speaker, texto). speaker = "archive" | "user".
        self.turns = [("archive", _APERTURA)]

        self.turnos_col = ft.Column(spacing=0)
        self.panel_botones = ft.Container(visible=False)
        self.boton_enviar = None
        self.lbl_sesion = ft.Text("", size=11, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.HINT)
        self.campo = ft.TextField(
            hint_text=_T["hint_chat"],
            multiline=True,
            min_lines=1,
            max_lines=5,
            expand=True,
            border=ft.InputBorder.NONE,
            bgcolor="transparent",
            cursor_color=tema.NAVY,
            text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=15, color=tema.NAVY),
            hint_style=ft.TextStyle(font_family=tema.FUENTE_SERIF, italic=True, size=15, color=tema.HINT),
            content_padding=ft.Padding.symmetric(horizontal=0, vertical=6),
            on_submit=self._enviar,
        )

    # --- Render de turnos ---------------------------------------------------
    def _turno(self, speaker, texto):
        es_user = speaker == "user"
        return ft.Column(
            spacing=0,
            controls=[
                cmp.eyebrow(TEXTOS["comun"]["tu"] if es_user else _T["speaker_archive"], color=tema.MUTED if es_user else tema.AMBAR),
                ft.Container(height=10),
                ft.Container(
                    width=600,
                    content=ft.Text(
                        texto,
                        size=16,
                        color=tema.MUTED if es_user else tema.NAVY,
                        italic=es_user,
                        font_family=tema.FUENTE_SERIF if es_user else tema.FUENTE_BODY,
                    ),
                ),
                ft.Container(height=24),
                ft.Container(width=24, height=1, bgcolor=tema.BORDER_LIGHT),
                ft.Container(height=24),
            ],
        )

    def _turno_ref(self):
        """Turno de Archive con un Text referenciable (para 'escribiendo' + revelado)."""
        txt = ft.Text(_T["escribiendo"], size=16, color=tema.MUTED, italic=True, font_family=tema.FUENTE_BODY)
        col = ft.Column(spacing=0, controls=[
            cmp.eyebrow(_T["speaker_archive"], color=tema.AMBAR),
            ft.Container(height=10),
            ft.Container(width=600, content=txt),
            ft.Container(height=24),
            ft.Container(width=24, height=1, bgcolor=tema.BORDER_LIGHT),
            ft.Container(height=24),
        ])
        return col, txt

    def _render_turnos(self):
        self.turnos_col.controls = [self._turno(s, t) for s, t in self.turns]
        self.lbl_sesion.value = _T["sesion_meta"].format(n=len(self.turns))

    # --- Panel de confirmación (frase trigger) -----------------------------
    @staticmethod
    def _es_trigger(texto):
        return _TRIGGER in (texto or "").lower()

    def _mostrar_panel(self):
        self.panel_botones.visible = True
        self.panel_botones.content = ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ElevatedButton(
                    content=ft.Text(_T["btn_si_generar"], size=13, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                    on_click=self._si_generar,
                    style=ft.ButtonStyle(
                        bgcolor=tema.NAVY,
                        shape=ft.RoundedRectangleBorder(radius=4),
                        padding=ft.Padding.symmetric(horizontal=26, vertical=16),
                        elevation=0,
                    ),
                ),
                ft.OutlinedButton(
                    content=ft.Text(_T["btn_modificar"], size=13, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY),
                    on_click=self._quiero_modificar,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1, tema.BORDER_LIGHT),
                        shape=ft.RoundedRectangleBorder(radius=4),
                        padding=ft.Padding.symmetric(horizontal=22, vertical=16),
                    ),
                ),
            ],
        )

    def _ocultar_panel(self):
        self.panel_botones.visible = False
        self.panel_botones.content = None

    # --- Eventos ------------------------------------------------------------
    async def _mandar(self, texto):
        texto = (texto or "").strip()
        if not texto:
            return
        self._ocultar_panel()
        self.campo.value = ""
        self.campo.disabled = True
        if self.boton_enviar:
            self.boton_enviar.disabled = True
        self.turns.append(("user", texto))
        clsInteraccionDB.registrar_texto_usuario(self.id_usuario, "archive", texto)
        self.router.page.run_task(clsAgentes.actualizar_voice_profile_si_toca, self.id_usuario)
        self._render_turnos()
        self.router.page.update()

        # Turno "Escribiendo…" mientras esperamos.
        col_live, txt_live = self._turno_ref()
        self.turnos_col.controls.append(col_live)
        self.router.page.update()

        try:
            respuesta = await clsAgentes.responder_archive(self.turns, self.id_usuario)
        except Exception:
            traceback.print_exc()  # error real en consola para diagnóstico
            respuesta = _T["error_respuesta"]

        self.turns.append(("archive", respuesta))
        # Revelar gradualmente en el turno en vivo.
        txt_live.value = ""
        txt_live.italic = False
        txt_live.color = tema.NAVY
        await cmp.revelar_texto(txt_live, respuesta)

        self.campo.disabled = False
        if self.boton_enviar:
            self.boton_enviar.disabled = False
        self._render_turnos()
        if self._es_trigger(respuesta):
            self._mostrar_panel()
        self.router.page.update()

    async def _enviar(self, e):
        await self._mandar(self.campo.value)

    async def _quiero_modificar(self, e):
        await self._mandar(_T["modificar_msg"])

    async def _si_generar(self, e):
        self._ocultar_panel()
        self.router.mostrar_carga(_T["generando_ficha"])
        try:
            ficha = await clsAgentes.generar_ficha_logro(self.turns, self.id_usuario)
        except Exception:
            self.router.ocultar_carga()
            self.router.page.show_dialog(ft.SnackBar(ft.Text(_T["error_ficha"])))
            self.router.page.update()
            return

        # Se guarda al instante, junto con la conversación de origen.
        clsInteraccionDB.insertar_logro_completo(
            self.id_usuario,
            ficha.get("tipo", "Other"),
            ficha.get("titulo", ""),
            ficha.get("contexto", ""),
            ficha.get("mi_rol", ""),
            ficha.get("aprendizaje", ""),
            ficha.get("tags", []),
            ficha.get("metrics", []),
            conversacion=self.turns,
        )
        self.router.logro_ficha = {**ficha, "_guardado": True, "_recien_generado": True, "fecha": datetime.now()}
        self.router.navegar_a("/archive/ficha")

    # --- Construcción -------------------------------------------------------
    def construir(self):
        self._render_turnos()

        encabezado_agente = ft.Row(
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text("03", size=38, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(_T["nombre"], size=32, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                        ft.Container(
                            width=460,
                            content=ft.Text(
                                _T["descripcion"],
                                size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED,
                            ),
                        ),
                    ],
                ),
            ],
        )

        self.boton_enviar = ft.ElevatedButton(
            content=ft.Text(TEXTOS["comun"]["enviar"], size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
            on_click=self._enviar,
            style=ft.ButtonStyle(
                bgcolor=tema.NAVY,
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=ft.Padding.symmetric(horizontal=22, vertical=14),
                elevation=0,
            ),
        )

        area_entrada = ft.Container(
            padding=ft.Padding.only(top=28),
            border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Column(
                spacing=0,
                controls=[
                    cmp.eyebrow(_T["tu_respuesta"]),
                    ft.Container(height=12),
                    ft.Container(
                        border=ft.Border.only(bottom=ft.BorderSide(1, tema.NAVY)),
                        padding=ft.Padding.only(bottom=10),
                        content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.END, controls=[self.campo, self.boton_enviar]),
                    ),
                    ft.Container(height=18),
                    self.lbl_sesion,
                ],
            ),
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=760,
                    padding=ft.Padding.symmetric(horizontal=56, vertical=44),
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            cmp.topbar(_T["topbar"], derecha=TEXTOS["comun"]["volver_dashboard"], on_back=lambda e: self.router.navegar_a("/menu_inicio")),
                            ft.Container(height=36),
                            encabezado_agente,
                            ft.Container(height=28),
                            cmp.hairline(width=48),
                            ft.Container(height=28),
                            self.turnos_col,
                            self.panel_botones,
                            ft.Container(height=20),
                            area_entrada,
                        ],
                    ),
                )
            ],
        )
