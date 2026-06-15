"""Interfaz de chat con Mirror, Editor, Archive o Clarity."""

import flet as ft

from core import clsAgentes
from data import clsInteraccionDB

AMBAR = "#BA7517"

NOMBRES_AGENTE = {
    "coach_mirror": "Mirror",
    "coach_editor": "Editor",
    "coach_archive": "Archive",
    "clarity_session": "Clarity",
}


class frmAgenteChat:
    def __init__(self, router, id_usuario=None, tipo_agente="coach_mirror"):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.tipo_agente = tipo_agente
        self.nombre_agente = NOMBRES_AGENTE.get(tipo_agente, "Agente")

        # Reusa el chat existente o crea uno nuevo (seccion 7.9 / 9.1).
        self.id_chat = clsInteraccionDB.obtener_o_crear_chat(self.id_usuario, tipo_agente)

        self.lista_mensajes = ft.ListView(expand=True, spacing=12, padding=20, auto_scroll=True)
        self.campo = ft.TextField(
            hint_text="Escribe tu mensaje...",
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=4,
            border_color="#39406A",
            focused_border_color=AMBAR,
            color="#FFFFFF",
            cursor_color=AMBAR,
            on_submit=self._enviar,
        )
        self.boton_enviar = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=AMBAR,
            on_click=self._enviar,
        )

    # --- Burbujas -----------------------------------------------------------
    def _burbuja(self, rol, contenido):
        es_usuario = rol == "user"
        return ft.Row(
            alignment=ft.MainAxisAlignment.END if es_usuario else ft.MainAxisAlignment.START,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    bgcolor=AMBAR if es_usuario else "#1B2342",
                    border_radius=14,
                    width=520,
                    content=ft.Text(
                        contenido,
                        size=14,
                        color="#FFFFFF" if es_usuario else "#DDE2F2",
                        selectable=True,
                    ),
                )
            ],
        )

    def _cargar_historial(self):
        for mensaje in clsInteraccionDB.obtener_mensajes(self.id_chat):
            self.lista_mensajes.controls.append(self._burbuja(mensaje["rol"], mensaje["contenido"]))

    # --- Eventos ------------------------------------------------------------
    async def _enviar(self, e):
        texto = (self.campo.value or "").strip()
        if not texto:
            return

        self.campo.value = ""
        self.campo.disabled = True
        self.boton_enviar.disabled = True

        # Insertar y renderizar el mensaje del usuario.
        clsInteraccionDB.insertar_mensaje(self.id_chat, "user", texto)
        self.lista_mensajes.controls.append(self._burbuja("user", texto))
        self.router.page.update()

        try:
            respuesta = await clsAgentes.responder_chat_agente(
                self.id_chat, self.tipo_agente, self.id_usuario
            )
        except Exception:
            respuesta = "Tuvimos un problema generando la respuesta. Intenta de nuevo."

        clsInteraccionDB.insertar_mensaje(self.id_chat, "assistant", respuesta)
        self.lista_mensajes.controls.append(self._burbuja("assistant", respuesta))

        self.campo.disabled = False
        self.boton_enviar.disabled = False
        self.router.page.update()

    def _regresar(self, e):
        # Al cerrar una Clarity Session se dispara la extraccion de hallazgos
        # en background, sin esperar a que termine (seccion 7.9).
        if self.tipo_agente == "clarity_session":
            self.router.page.run_task(
                clsAgentes.procesar_cierre_clarity_async, self.id_chat, self.id_usuario
            )
        self.router.navegar_a("/menu_inicio")

    # --- Construccion -------------------------------------------------------
    def construir(self):
        self._cargar_historial()

        header = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            bgcolor="#141C36",
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color="#FFFFFF", on_click=self._regresar),
                    ft.Text(self.nombre_agente, size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="Syne"),
                ],
            ),
        )

        entrada = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            bgcolor="#141C36",
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.campo, self.boton_enviar],
            ),
        )

        return ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[header, self.lista_mensajes, entrada],
            ),
        )
