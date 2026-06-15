"""Inicio de sesión: handle (Nombre#número) + clave."""

import flet as ft
import tema

from data import clsInteraccionDB


class frmLogin:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario
        self.campo_nombre = ft.TextField(
            label="Tu nombre",
            autofocus=True,
            border_color=tema.BORDER_LIGHT,
            focused_border_color=tema.BLUE,
            color=tema.TEXTO,
            cursor_color=tema.BLUE,
        )
        self.campo_numero = ft.TextField(
            label="Número (ej. 4821)",
            border_color=tema.BORDER_LIGHT,
            focused_border_color=tema.BLUE,
            color=tema.TEXTO,
            cursor_color=tema.BLUE,
        )
        self.campo_clave = ft.TextField(
            label="Tu clave",
            password=True,
            can_reveal_password=True,
            border_color=tema.BORDER_LIGHT,
            focused_border_color=tema.BLUE,
            color=tema.TEXTO,
            cursor_color=tema.BLUE,
            on_submit=self._entrar,
        )
        self.error = ft.Text("", color=tema.CORAL, size=13)

    def _entrar(self, e):
        nombre = (self.campo_nombre.value or "").strip()
        numero = (self.campo_numero.value or "").strip().lstrip("#")
        clave = self.campo_clave.value or ""

        if not (nombre and numero and clave):
            self.error.value = "Completa nombre, número y clave."
            self.router.page.update()
            return

        # El discriminador se guarda con 4 dígitos; normalizamos lo tecleado.
        if numero.isdigit():
            numero = numero.zfill(4)

        id_usuario = clsInteraccionDB.verificar_credenciales(nombre, numero, clave)
        if id_usuario is None:
            self.error.value = "Usuario o clave incorrectos."
            self.router.page.update()
            return

        self.router.id_usuario = id_usuario
        self.router.nombre = nombre

        # Si ya completó el onboarding, va directo al dashboard; si no, lo reanuda.
        if clsInteraccionDB.obtener_perfil(id_usuario):
            self.router.navegar_a("/menu_inicio")
        else:
            self.router.navegar_a("/onboarding")

    def construir(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                width=480,
                padding=40,
                bgcolor=tema.SUPERFICIE,
                border_radius=20,
                shadow=ft.BoxShadow(blur_radius=40, color="#00000066"),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Text(
                            "Inicia sesión",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            font_family=tema.FUENTE_DISPLAY,
                            color=tema.TEXTO,
                        ),
                        ft.Text(
                            "Entra con el usuario que te dimos al crear tu cuenta.",
                            size=14,
                            color=tema.TEXTO_SUAVE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(expand=2, content=self.campo_nombre),
                                ft.Container(expand=1, content=self.campo_numero),
                            ],
                        ),
                        self.campo_clave,
                        self.error,
                        ft.ElevatedButton(
                            "Entrar",
                            on_click=self._entrar,
                            style=ft.ButtonStyle(
                                bgcolor=tema.NAVY,
                                color=tema.TEXTO_SOBRE_NAVY,
                                padding=ft.Padding.symmetric(horizontal=36, vertical=20),
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                        ft.TextButton(
                            "¿No tienes cuenta? Créala",
                            on_click=lambda e: self.router.navegar_a("/pre_onboarding"),
                            style=ft.ButtonStyle(color=tema.BLUE),
                        ),
                    ],
                ),
            ),
        )
