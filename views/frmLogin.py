"""Inicio de sesión: handle (Nombre#número) + clave."""

import flet as ft

import componentes as cmp
import tema
from data import clsInteraccionDB


class frmLogin:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario
        self.campo_nombre = cmp.textfield_subrayado("Mike Prueba", autofocus=True)
        self.campo_numero = cmp.textfield_subrayado("4821")
        self.campo_clave = cmp.textfield_subrayado(
            "••••••••", password=True, can_reveal=True, on_submit=self._entrar
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
            padding=40,
            content=ft.Container(
                width=480,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=0,
                    controls=[
                        cmp.eyebrow("Acceso"),
                        ft.Container(height=16),
                        cmp.hairline(width=40),
                        ft.Container(height=28),
                        ft.Text(
                            "Inicia sesión",
                            size=44,
                            weight=ft.FontWeight.W_700,
                            font_family=tema.FUENTE_DISPLAY,
                            color=tema.NAVY,
                        ),
                        ft.Container(height=12),
                        ft.Text(
                            "Entra con el usuario que te dimos al crear tu cuenta.",
                            size=14,
                            font_family=tema.FUENTE_BODY,
                            color=tema.MUTED,
                        ),
                        ft.Container(height=44),
                        ft.Row(
                            spacing=28,
                            controls=[
                                ft.Container(expand=2, content=cmp.campo_etiquetado("Tu nombre", self.campo_nombre)),
                                ft.Container(expand=1, content=cmp.campo_etiquetado("Número", self.campo_numero)),
                            ],
                        ),
                        ft.Container(height=32),
                        cmp.campo_etiquetado("Tu clave", self.campo_clave),
                        ft.Container(height=20),
                        self.error,
                        ft.Container(height=24),
                        ft.Row(
                            spacing=28,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                cmp.boton_primario("Entrar", on_click=self._entrar),
                                cmp.enlace("¿No tienes cuenta? Créala", on_click=lambda e: self.router.navegar_a("/pre_onboarding")),
                            ],
                        ),
                    ],
                ),
            ),
        )
