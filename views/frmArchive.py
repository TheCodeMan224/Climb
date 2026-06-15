"""Archive: chat que documenta logros y los registra, con la lista en vivo."""

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes
from data import clsInteraccionDB


class frmArchive:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.tipo_agente = "coach_archive"
        self.id_chat = clsInteraccionDB.obtener_o_crear_chat(self.id_usuario, self.tipo_agente)
        self.logro_propuesto = None

        self.lista_mensajes = ft.ListView(expand=True, spacing=12, padding=20, auto_scroll=True)
        self.campo = ft.TextField(
            hint_text="Cuéntale a Archive un logro...",
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=4,
            border_color=tema.BORDER_LIGHT,
            focused_border_color=tema.BLUE,
            color=tema.TEXTO,
            cursor_color=tema.BLUE,
            on_submit=self._enviar,
        )
        self.boton_enviar = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=tema.NAVY, on_click=self._enviar)
        self.panel_logros = ft.ListView(expand=True, spacing=0, padding=0)
        self.tarjeta_confirmar = ft.Container(visible=False)

    # --- Burbujas / historial ----------------------------------------------
    def _burbuja(self, rol, contenido):
        es_usuario = rol == "user"
        return ft.Row(
            alignment=ft.MainAxisAlignment.END if es_usuario else ft.MainAxisAlignment.START,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    bgcolor=tema.NAVY if es_usuario else tema.SECTION_BG,
                    border_radius=14,
                    width=460,
                    content=ft.Text(
                        contenido,
                        size=14,
                        font_family=tema.FUENTE_BODY,
                        color=tema.TEXTO_SOBRE_NAVY if es_usuario else tema.TEXTO,
                        selectable=True,
                    ),
                )
            ],
        )

    def _cargar_historial(self):
        for mensaje in clsInteraccionDB.obtener_mensajes(self.id_chat):
            self.lista_mensajes.controls.append(self._burbuja(mensaje["rol"], mensaje["contenido"]))

    def _fila_logro(self, logro):
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=14),
            border=ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Column(
                spacing=4,
                controls=[
                    cmp.eyebrow(logro.get("tipoLogro") or "", color=tema.AMBAR),
                    ft.Text(logro.get("logro", ""), size=14, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY),
                    ft.Text(logro.get("descripcionLogro", ""), size=12, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                ],
            ),
        )

    def _refrescar_panel(self):
        logros = clsInteraccionDB.obtener_logros(self.id_usuario)
        self.panel_logros.controls.clear()
        if not logros:
            self.panel_logros.controls.append(
                ft.Text("Aún no has registrado logros.", size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED)
            )
        else:
            for l in logros:
                self.panel_logros.controls.append(self._fila_logro(l))

    # --- Confirmacion de guardado ------------------------------------------
    def _mostrar_confirmar(self, logro):
        self.logro_propuesto = logro
        self.tarjeta_confirmar.visible = True
        self.tarjeta_confirmar.content = ft.Column(
            spacing=8,
            controls=[
                cmp.eyebrow(f"¿Registrar este logro?  ·  {logro.get('tipo','')}", color=tema.AMBAR),
                ft.Text(logro.get("logro", ""), size=15, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY),
                ft.Text(logro.get("descripcion", ""), size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                ft.Row(
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        cmp.boton_primario("Guardar logro", on_click=self._guardar_logro),
                        cmp.enlace("Ahora no", on_click=self._descartar),
                    ],
                ),
            ],
        )

    def _ocultar_confirmar(self):
        self.logro_propuesto = None
        self.tarjeta_confirmar.visible = False
        self.tarjeta_confirmar.content = None

    def _guardar_logro(self, e):
        if not self.logro_propuesto:
            return
        clsInteraccionDB.insertar_logro(
            self.id_usuario,
            self.logro_propuesto.get("tipo"),
            self.logro_propuesto.get("logro"),
            self.logro_propuesto.get("descripcion"),
        )
        self._ocultar_confirmar()
        self._refrescar_panel()
        self.router.page.update()

    def _descartar(self, e):
        self._ocultar_confirmar()
        self.router.page.update()

    # --- Envio de mensaje ---------------------------------------------------
    async def _enviar(self, e):
        texto = (self.campo.value or "").strip()
        if not texto:
            return
        self.campo.value = ""
        self.campo.disabled = True
        self.boton_enviar.disabled = True

        clsInteraccionDB.insertar_mensaje(self.id_chat, "user", texto)
        self.lista_mensajes.controls.append(self._burbuja("user", texto))
        self.router.page.update()

        try:
            respuesta = await clsAgentes.responder_chat_agente(self.id_chat, self.tipo_agente, self.id_usuario)
        except Exception:
            respuesta = "Tuvimos un problema generando la respuesta. Intenta de nuevo."

        clsInteraccionDB.insertar_mensaje(self.id_chat, "assistant", respuesta)
        self.lista_mensajes.controls.append(self._burbuja("assistant", respuesta))

        self.campo.disabled = False
        self.boton_enviar.disabled = False
        self.router.page.update()

        # ¿Archive ya tiene un logro listo para registrar? Si es asi, lo ofrecemos.
        try:
            logro = await clsAgentes.extraer_logro_archive(self.id_chat)
        except Exception:
            logro = None
        if logro:
            self._mostrar_confirmar(logro)
            self.router.page.update()

    # --- Construccion -------------------------------------------------------
    def construir(self):
        self._cargar_historial()
        self._refrescar_panel()

        header = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.only(bottom=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=tema.NAVY, on_click=lambda e: self.router.navegar_a("/menu_inicio")),
                    ft.Text("Archive", size=22, weight=ft.FontWeight.W_700, color=tema.NAVY, font_family=tema.FUENTE_DISPLAY),
                ],
            ),
        )

        self.tarjeta_confirmar.padding = ft.Padding.symmetric(horizontal=20, vertical=16)
        self.tarjeta_confirmar.bgcolor = tema.SECTION_BG
        self.tarjeta_confirmar.border = ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT))

        entrada = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
            content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[self.campo, self.boton_enviar]),
        )

        columna_chat = ft.Container(
            expand=True,
            content=ft.Column(expand=True, spacing=0, controls=[header, self.lista_mensajes, self.tarjeta_confirmar, entrada]),
        )

        panel = ft.Container(
            width=340,
            bgcolor=tema.OFF_WHITE,
            border=ft.Border.only(left=ft.BorderSide(1, tema.BORDER_LIGHT)),
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    cmp.eyebrow("Logros registrados"),
                    ft.Container(height=12),
                    cmp.hairline(width=36),
                    ft.Container(height=12),
                    self.panel_logros,
                ],
            ),
        )

        return ft.Container(
            expand=True,
            content=ft.Row(spacing=0, controls=[columna_chat, panel]),
        )
