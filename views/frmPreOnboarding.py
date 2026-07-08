"""Registro: nombre, correo, nombre de usuario único y clave."""

import flet as ft

import componentes as cmp
import tema
from core.textos import TEXTOS
from data import clsInteraccionDB

_T = TEXTOS["registro"]


class frmPreOnboarding:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario
        # Si el usuario edita el username a mano, dejamos de autosugerirlo.
        self.username_editado = False
        self.campo_nombre = cmp.textfield_subrayado(
            _T["ph_nombre"], autofocus=True, on_blur=self._sugerir_si_vacio
        )
        self.campo_correo = cmp.textfield_subrayado(_T["ph_correo"])
        self.campo_username = cmp.textfield_subrayado(
            _T["ph_username"], on_change=self._marcar_username_editado
        )
        self.campo_clave = cmp.textfield_subrayado(_T["ph_clave"], password=True, can_reveal=True)
        self.campo_clave2 = cmp.textfield_subrayado(
            _T["ph_clave2"], password=True, can_reveal=True, on_submit=self._continuar
        )
        self.check_disclaimer = ft.Checkbox(
            label=_T["disclaimer_check"],
            value=False,
            fill_color=tema.NAVY,
            check_color=tema.OFF_WHITE,
            label_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=13, color=tema.NAVY),
        )
        self.error = ft.Text("", color=tema.CORAL, size=13)

    # --- Sugerencia de username -------------------------------------------
    def _marcar_username_editado(self, e):
        self.username_editado = True

    def _sugerir_si_vacio(self, e):
        """Al salir del campo de nombre, propone un username si aún no hay uno propio."""
        nombre = (self.campo_nombre.value or "").strip()
        if nombre and not self.username_editado and not (self.campo_username.value or "").strip():
            self.campo_username.value = clsInteraccionDB.sugerir_username(nombre)
            self.router.page.update()

    def _forzar_sugerencia(self, e):
        """Enlace 'sugerir uno': regenera desde el nombre, aunque haya algo escrito."""
        nombre = (self.campo_nombre.value or "").strip()
        if not nombre:
            self.error.value = _T["err_sin_nombre"]
            self.router.page.update()
            return
        self.campo_username.value = clsInteraccionDB.sugerir_username(nombre)
        self.username_editado = False
        self.error.value = ""
        self.router.page.update()

    # --- Creación de cuenta -----------------------------------------------
    def _continuar(self, e):
        nombre = (self.campo_nombre.value or "").strip()
        correo = (self.campo_correo.value or "").strip()
        username = (self.campo_username.value or "").strip()
        clave = self.campo_clave.value or ""
        clave2 = self.campo_clave2.value or ""

        def fallar(msg):
            self.error.value = msg
            self.router.page.update()

        if not nombre:
            return fallar(_T["err_sin_nombre"])
        if not clsInteraccionDB.correo_valido(correo):
            return fallar(_T["err_correo_invalido"])
        if not clsInteraccionDB.username_valido(username):
            return fallar(_T["err_username_invalido"])
        if len(clave) < 4:
            return fallar(_T["err_clave_corta"])
        if clave != clave2:
            return fallar(_T["err_no_coinciden"])
        if not self.check_disclaimer.value:
            return fallar(_T["err_disclaimer"])
        if clsInteraccionDB.correo_existe(correo):
            return fallar(_T["err_correo_existe"])
        if clsInteraccionDB.username_existe(username):
            return fallar(_T["err_username_existe"])

        try:
            datos = clsInteraccionDB.crear_usuario(nombre, username, correo, clave, self.router.idioma)
        except ValueError:
            # Colisión detectada por el índice único (carrera contra otro registro).
            return fallar(_T["err_username_existe"])

        self.router.id_usuario = datos["id_usuario"]
        self.router.nombre = nombre
        self.router.navegar_a("/onboarding")

    def _abrir_acuerdo(self, e):
        """Ventana emergente con el disclaimer; el usuario lo lee y luego marca el checkbox."""
        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=tema.SUPERFICIE,
            title=ft.Text(_T["disclaimer_titulo"], color=tema.NAVY, font_family=tema.FUENTE_DISPLAY, size=22, weight=ft.FontWeight.W_700),
            content=ft.Container(
                width=460,
                content=ft.Text(_T["disclaimer_cuerpo"], size=15, color=tema.NAVY, font_family=tema.FUENTE_BODY),
            ),
            actions=[cmp.boton_primario(_T["disclaimer_cerrar"], on_click=lambda e: self.router.page.pop_dialog())],
        )
        self.router.page.show_dialog(dialog)

    def construir(self):
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=480,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=44),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=0,
                        controls=[
                        cmp.eyebrow(_T["eyebrow"]),
                        ft.Container(height=16),
                        cmp.hairline(width=40),
                        ft.Container(height=28),
                        ft.Text(
                            _T["titulo"],
                            size=44,
                            weight=ft.FontWeight.W_700,
                            font_family=tema.FUENTE_DISPLAY,
                            color=tema.NAVY,
                        ),
                        ft.Container(height=12),
                        ft.Text(
                            _T["subtitulo"],
                            size=14,
                            font_family=tema.FUENTE_BODY,
                            color=tema.MUTED,
                        ),
                        ft.Container(height=44),
                        cmp.campo_etiquetado(_T["lbl_nombre"], self.campo_nombre),
                        ft.Container(height=32),
                        cmp.campo_etiquetado(_T["lbl_correo"], self.campo_correo),
                        ft.Container(height=32),
                        cmp.campo_etiquetado(_T["lbl_username"], self.campo_username),
                        ft.Container(height=8),
                        cmp.enlace(_T["sugerir_username"], on_click=self._forzar_sugerencia),
                        ft.Container(height=32),
                        cmp.campo_etiquetado(_T["lbl_clave"], self.campo_clave),
                        ft.Container(height=32),
                        cmp.campo_etiquetado(_T["lbl_clave2"], self.campo_clave2),
                        ft.Container(height=24),
                        cmp.enlace(_T["leer_acuerdo"], on_click=self._abrir_acuerdo),
                        ft.Container(height=4),
                        self.check_disclaimer,
                        ft.Container(height=14),
                        self.error,
                        ft.Container(height=24),
                        ft.Row(
                            spacing=28,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                cmp.boton_primario(_T["crear"], on_click=self._continuar),
                                cmp.enlace(_T["ir_login"], on_click=lambda e: self.router.navegar_a("/login")),
                            ],
                        ),
                    ],
                ),
                ),
            ],
        )
