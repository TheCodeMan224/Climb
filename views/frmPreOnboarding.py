"""Registro: captura del nombre y la clave del usuario."""

import flet as ft
import tema

from data import clsInteraccionDB


class frmPreOnboarding:
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
        self.campo_clave = ft.TextField(
            label="Crea una clave",
            password=True,
            can_reveal_password=True,
            border_color=tema.BORDER_LIGHT,
            focused_border_color=tema.BLUE,
            color=tema.TEXTO,
            cursor_color=tema.BLUE,
        )
        self.campo_clave2 = ft.TextField(
            label="Confirma tu clave",
            password=True,
            can_reveal_password=True,
            border_color=tema.BORDER_LIGHT,
            focused_border_color=tema.BLUE,
            color=tema.TEXTO,
            cursor_color=tema.BLUE,
            on_submit=self._continuar,
        )
        self.error = ft.Text("", color=tema.CORAL, size=13)

    def _continuar(self, e):
        nombre = (self.campo_nombre.value or "").strip()
        clave = self.campo_clave.value or ""
        clave2 = self.campo_clave2.value or ""

        if not nombre:
            self.error.value = "Por favor escribe tu nombre para continuar."
            self.router.page.update()
            return
        if len(clave) < 4:
            self.error.value = "La clave debe tener al menos 4 caracteres."
            self.router.page.update()
            return
        if clave != clave2:
            self.error.value = "Las claves no coinciden."
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
            title=ft.Text("Tu cuenta está lista", color=tema.TEXTO, font_family=tema.FUENTE_DISPLAY),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Text(
                        "Este es tu usuario para iniciar sesión la próxima vez. "
                        "Guárdalo bien:",
                        color=tema.TEXTO_SUAVE,
                    ),
                    ft.Text(handle, size=26, weight=ft.FontWeight.BOLD, color=tema.AMBAR, selectable=True),
                ],
            ),
            actions=[
                ft.ElevatedButton(
                    "Continuar",
                    on_click=ir_onboarding,
                    style=ft.ButtonStyle(bgcolor=tema.NAVY, color=tema.TEXTO_SOBRE_NAVY),
                ),
            ],
        )
        self.router.page.show_dialog(dialog)

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
                            "Crea tu cuenta",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            font_family=tema.FUENTE_DISPLAY,
                            color=tema.TEXTO,
                        ),
                        ft.Text(
                            "Elige tu nombre y una clave. Te daremos un usuario único "
                            "para volver a entrar.",
                            size=14,
                            color=tema.TEXTO_SUAVE,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        self.campo_nombre,
                        self.campo_clave,
                        self.campo_clave2,
                        self.error,
                        ft.ElevatedButton(
                            "Crear cuenta",
                            on_click=self._continuar,
                            style=ft.ButtonStyle(
                                bgcolor=tema.NAVY,
                                color=tema.TEXTO_SOBRE_NAVY,
                                padding=ft.Padding.symmetric(horizontal=36, vertical=20),
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                        ft.TextButton(
                            "¿Ya tienes cuenta? Inicia sesión",
                            on_click=lambda e: self.router.navegar_a("/login"),
                            style=ft.ButtonStyle(color=tema.BLUE),
                        ),
                    ],
                ),
            ),
        )
