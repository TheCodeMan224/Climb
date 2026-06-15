"""Punto de entrada de Climb. Inicializa Flet, la base de datos y el router."""

import flet as ft
from dotenv import load_dotenv

from clsRouter import Router
from data.clsConexionDB import inicializar_db


def main(page: ft.Page):
    load_dotenv()
    inicializar_db()

    page.title = "Climb"
    page.bgcolor = "#0B1020"
    page.fonts = {
        "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
        "Syne": "https://github.com/google/fonts/raw/main/ofl/syne/Syne%5Bwght%5D.ttf",
    }
    page.theme = ft.Theme(font_family="Inter")

    router = Router(page)
    router.navegar_a("/landing")


if __name__ == "__main__":
    ft.app(target=main)
