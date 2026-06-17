"""Registro: captura del nombre y la clave del usuario."""

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
        self.campo_nombre = cmp.textfield_subrayado(_T["ph_nombre"], autofocus=True)
        self.campo_clave = cmp.textfield_subrayado(_T["ph_clave"], password=True, can_reveal=True)
        self.campo_clave2 = cmp.textfield_subrayado(
            _T["ph_clave2"], password=True, can_reveal=True, on_submit=self._continuar
        )
        self.error = ft.Text("", color=tema.CORAL, size=13)

    def _continuar(self, e):
        nombre = (self.campo_nombre.value or "").strip()
        clave = self.campo_clave.value or ""
        clave2 = self.campo_clave2.value or ""

        if not nombre:
            self.error.value = _T["err_sin_nombre"]
            self.router.page.update()
            return
        if len(clave) < 4:
            self.error.value = _T["err_clave_corta"]
            self.router.page.update()
            return
        if clave != clave2:
            self.error.value = _T["err_no_coinciden"]
            self.router.page.update()
            return

        datos = clsInteraccionDB.crear_usuario(nombre, clave)
        self.router.id_usuario = datos["id_usuario"]
        self.router.nombre = nombre
        self._mostrar_handle(datos["handle"])

    def _mostrar_handle(self, handle):
        """Muestra el handle generado y, al confirmar, avanza al onboarding."""
        def ir_onboarding(e):
            self.router.page.pop_dialog()
            self.router.navegar_a("/onboarding")

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=tema.SUPERFICIE,
            title=ft.Text(_T["dlg_titulo"], color=tema.NAVY, font_family=tema.FUENTE_DISPLAY),
            content=ft.Column(
                tight=True,
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    cmp.eyebrow(_T["dlg_eyebrow"]),
                    ft.Text(handle, size=26, weight=ft.FontWeight.BOLD, color=tema.AMBAR, selectable=True),
                    cmp.hairline(width=40),
                    ft.Text(
                        _T["dlg_aviso"],
                        color=tema.MUTED,
                        font_family=tema.FUENTE_BODY,
                    ),
                ],
            ),
            actions=[cmp.boton_primario(_T["dlg_continuar"], on_click=ir_onboarding)],
        )
        self.router.page.show_dialog(dialog)

    def construir(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=40,
            content=ft.Container(
                width=480,
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
                        cmp.campo_etiquetado(_T["lbl_clave"], self.campo_clave),
                        ft.Container(height=32),
                        cmp.campo_etiquetado(_T["lbl_clave2"], self.campo_clave2),
                        ft.Container(height=20),
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
        )
