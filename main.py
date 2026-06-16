"""Punto de entrada de Climb. Inicializa Flet, la base de datos y el router."""

import os

import flet as ft
from dotenv import load_dotenv

import tema
from clsRouter import Router
from data.clsConexionDB import inicializar_db


def main(page: ft.Page):
    load_dotenv()
    inicializar_db()

    page.title = "Climb"
    page.bgcolor = tema.OFF_WHITE
    page.fonts = {
        "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
        "Syne": "https://github.com/google/fonts/raw/main/ofl/syne/Syne%5Bwght%5D.ttf",
        "DM Sans": "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz,wght%5D.ttf",
    }
    page.theme = ft.Theme(font_family=tema.FUENTE_BODY)

    router = Router(page)
    router.navegar_a("/landing")


if __name__ == "__main__":
    # En un host como Render existe la variable PORT: corremos como servidor web.
    # En local (sin PORT) abrimos la app de escritorio como siempre.
    port = os.getenv("PORT")
    if port:
        ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=int(port))
    else:
        ft.run(main)
