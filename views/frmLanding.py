"""Pantalla de bienvenida de Climb."""

import flet as ft


class frmLanding:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario

    def construir(self):
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER,
                end=ft.Alignment.BOTTOM_CENTER,
                colors=["#0B1020", "#141C36"],
            ),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=24,
                controls=[
                    ft.Text(
                        "Climb",
                        size=84,
                        weight=ft.FontWeight.BOLD,
                        font_family="Syne",
                        color="#FFFFFF",
                    ),
                    ft.Text(
                        "La mano derecha de tu carrera profesional",
                        size=20,
                        color="#AEB6D0",
                        font_family="Inter",
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Comenzar",
                        on_click=lambda e: self.router.navegar_a("/pre_onboarding"),
                        style=ft.ButtonStyle(
                            bgcolor="#BA7517",
                            color="#FFFFFF",
                            padding=ft.Padding.symmetric(horizontal=44, vertical=22),
                            shape=ft.RoundedRectangleBorder(radius=14),
                        ),
                    ),
                    ft.TextButton(
                        "Ya tengo cuenta — Iniciar sesión",
                        on_click=lambda e: self.router.navegar_a("/login"),
                        style=ft.ButtonStyle(color="#AEB6D0"),
                    ),
                ],
            ),
        )
