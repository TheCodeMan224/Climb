"""Recuperación de contraseña: pide el correo, envía un código y lo canjea.

Una sola vista con dos fases internas ('correo' -> 'codigo'), para no pasar el
correo entre rutas. Por seguridad, tras pedir el código siempre se muestra el
mismo mensaje genérico (no revela si la cuenta existe).
"""

import flet as ft

import componentes as cmp
import tema
from core import clsCorreo
from core.textos import TEXTOS
from data import clsInteraccionDB

_T = TEXTOS["recuperar"]


class frmRecuperarPassword:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.fase = "correo"
        self.correo = ""

        self.campo_correo = cmp.textfield_subrayado(_T["ph_correo"], autofocus=True, on_submit=self._enviar_codigo)
        self.campo_codigo = cmp.textfield_subrayado(_T["ph_codigo"])
        self.campo_clave = cmp.textfield_subrayado(_T["ph_clave"], password=True, can_reveal=True)
        self.campo_clave2 = cmp.textfield_subrayado(
            _T["ph_clave2"], password=True, can_reveal=True, on_submit=self._restablecer
        )
        self.status = ft.Text("", size=13, color=tema.CORAL)
        self.contenedor = ft.Container(width=480)

    # --- Helpers ----------------------------------------------------------
    def _mostrar(self, texto, error=True):
        self.status.value = texto
        self.status.color = tema.CORAL if error else tema.MUTED
        self.router.page.update()

    def _refrescar(self):
        self.status.value = ""
        self.contenedor.content = self._panel()
        self.router.page.update()

    # --- Fase 1: pedir el correo ------------------------------------------
    def _enviar_codigo(self, e):
        correo = (self.campo_correo.value or "").strip()
        if not clsInteraccionDB.correo_valido(correo):
            self._mostrar(_T["err_correo"])
            return
        self.correo = correo
        # Genera y envía en segundo plano; pasamos a la fase 2 con mensaje genérico.
        self.router.page.run_task(self._procesar_envio, correo)
        self.fase = "codigo"
        self._refrescar()
        self._mostrar(_T["enviado"], error=False)

    async def _procesar_envio(self, correo):
        datos = clsInteraccionDB.crear_codigo_reset(correo)
        if datos:
            await clsCorreo.enviar_codigo_reset_async(datos["correo"], datos["nombre"], datos["code"])

    def _reenviar(self, e):
        self.router.page.run_task(self._procesar_envio, self.correo)
        self._mostrar(_T["enviado"], error=False)

    # --- Fase 2: canjear el código ----------------------------------------
    def _restablecer(self, e):
        code = (self.campo_codigo.value or "").strip()
        clave = self.campo_clave.value or ""
        clave2 = self.campo_clave2.value or ""

        if len(clave) < 4:
            self._mostrar(_T["err_clave_corta"])
            return
        if clave != clave2:
            self._mostrar(_T["err_no_coinciden"])
            return

        id_usuario = clsInteraccionDB.verificar_codigo_reset(self.correo, code)
        if id_usuario is None:
            self._mostrar(_T["err_codigo"])
            return

        clsInteraccionDB.cambiar_password(id_usuario, clave)
        self._exito()

    def _exito(self):
        def ir_login(e):
            self.router.page.pop_dialog()
            self.router.navegar_a("/login")

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=tema.SUPERFICIE,
            title=ft.Text(_T["listo"], color=tema.NAVY, font_family=tema.FUENTE_DISPLAY, size=22, weight=ft.FontWeight.W_700),
            actions=[cmp.boton_primario(_T["volver_login"], on_click=ir_login)],
        )
        self.router.page.show_dialog(dialog)

    # --- Render -----------------------------------------------------------
    def _panel(self):
        if self.fase == "correo":
            campos = [
                cmp.campo_etiquetado(_T["lbl_correo"], self.campo_correo),
                ft.Container(height=20),
                self.status,
                ft.Container(height=24),
                ft.Row(
                    spacing=28,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        cmp.boton_primario(_T["enviar"], on_click=self._enviar_codigo),
                        cmp.enlace(_T["volver_login"], on_click=lambda e: self.router.navegar_a("/login")),
                    ],
                ),
            ]
            titulo, subtitulo = _T["titulo"], _T["subtitulo"]
        else:
            campos = [
                cmp.campo_etiquetado(_T["lbl_codigo"], self.campo_codigo),
                ft.Container(height=32),
                cmp.campo_etiquetado(_T["lbl_clave"], self.campo_clave),
                ft.Container(height=32),
                cmp.campo_etiquetado(_T["lbl_clave2"], self.campo_clave2),
                ft.Container(height=20),
                self.status,
                ft.Container(height=24),
                ft.Row(
                    spacing=28,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        cmp.boton_primario(_T["restablecer"], on_click=self._restablecer),
                        cmp.enlace(_T["reenviar"], on_click=self._reenviar),
                    ],
                ),
                ft.Container(height=12),
                cmp.enlace(_T["volver_login"], on_click=lambda e: self.router.navegar_a("/login")),
            ]
            titulo, subtitulo = _T["titulo2"], _T["subtitulo2"]

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=0,
            controls=[
                cmp.eyebrow(_T["eyebrow"]),
                ft.Container(height=16),
                cmp.hairline(width=40),
                ft.Container(height=28),
                ft.Text(titulo, size=44, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                ft.Container(height=12),
                ft.Text(subtitulo, size=14, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                ft.Container(height=44),
                *campos,
            ],
        )

    def construir(self):
        self.contenedor.content = self._panel()
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=40, vertical=44),
                    content=self.contenedor,
                ),
            ],
        )
