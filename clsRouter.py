"""Enrutador central tipo SPA para Climb.

Mantiene el estado global minimo de la sesion (id y nombre del usuario activo, y
los artefactos JSON que viajan entre pantallas) y cambia la vista actual.
"""

import flet as ft

import tema
from views.frmLanding import frmLanding
from views.frmLogin import frmLogin
from views.frmPreOnboarding import frmPreOnboarding
from views.frmOnboarding import frmOnboarding
from views.frmScoutReflection import frmScoutReflection
from views.frmProgreso import frmProgreso
from views.frmDiagnostico import frmDiagnostico
from views.frmCaminos import frmCaminos
from views.frmMenuInicio import frmMenuInicio
from views.frmAgenteChat import frmAgenteChat
from views.frmPacer import frmPacer


class Router:
    def __init__(self, page: ft.Page):
        self.page = page

        # Estado global minimo de la sesion.
        self.id_usuario = None
        self.nombre = None

        # Artefactos que viajan entre pantallas.
        self.diagnostico_actual = None
        self.caminos_actual = None
        self.mision_actual = None

    def navegar_a(self, ruta):
        """Cambia la vista actual segun la ruta indicada."""
        vista = self._resolver_vista(ruta)

        # Reset de propiedades de pagina a un estado base; cada vista las ajusta.
        # La pagina NO debe hacer scroll: cada vista usa un Container(expand=True)
        # con su propio Column(scroll=AUTO). Si la pagina hace scroll, el expand
        # no resuelve una altura acotada y el scroll interno colapsa (la vista
        # desaparece al desplazarse).
        self.page.controls.clear()
        self.page.scroll = None
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = tema.OFF_WHITE
        self.page.padding = 0

        self.page.add(vista.construir())
        self.page.update()

        # Hook opcional que se ejecuta cuando la vista termina de montarse.
        if hasattr(vista, "al_cargar"):
            self.page.run_task(vista.al_cargar)

    def _resolver_vista(self, ruta):
        if ruta.startswith("/chat/"):
            tipo_agente = ruta.split("/chat/", 1)[1]
            return frmAgenteChat(self, self.id_usuario, tipo_agente)

        vistas = {
            "/landing": frmLanding,
            "/login": frmLogin,
            "/pre_onboarding": frmPreOnboarding,
            "/onboarding": frmOnboarding,
            "/scout_reflection": frmScoutReflection,
            "/progreso": frmProgreso,
            "/diagnostico": frmDiagnostico,
            "/caminos": frmCaminos,
            "/menu_inicio": frmMenuInicio,
            "/pacer": frmPacer,
        }
        clase = vistas.get(ruta, frmLanding)
        return clase(self, self.id_usuario)
