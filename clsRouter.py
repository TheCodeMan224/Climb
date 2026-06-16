"""Enrutador central tipo SPA para Climb.

Mantiene el estado global minimo de la sesion (id y nombre del usuario activo, y
los artefactos JSON que viajan entre pantallas) y cambia la vista actual.
"""

import flet as ft

import tema
from data import clsInteraccionDB
from views.frmLanding import frmLanding
from views.frmLogin import frmLogin
from views.frmPreOnboarding import frmPreOnboarding
from views.frmOnboarding import frmOnboarding
from views.frmScoutReflection import frmScoutReflection
from views.frmProgreso import frmProgreso
from views.frmDiagnostico import frmDiagnostico
from views.frmCaminos import frmCaminos
from views.frmMenuInicio import frmMenuInicio
from views.frmPacer import frmPacer
from views.frmPacerCompletada import frmPacerCompletada
from views.frmArchiveChat import frmArchiveChat
from views.frmArchiveFicha import frmArchiveFicha
from views.frmArchiveTimeline import frmArchiveTimeline
from views.frmMirrorHub import frmMirrorHub
from views.frmMirrorEntry import frmMirrorEntry
from views.frmMirrorSession import frmMirrorSession
from views.frmMirrorEspejo import frmMirrorEspejo
from views.frmEditor import frmEditor
from views.frmEditorHome import frmEditorHome
from views.frmClarityEspejo import frmClarityEspejo
from views.frmClarityConversacion import frmClarityConversacion
from views.frmClarityPuertas import frmClarityPuertas


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
        self.logro_ficha = None  # ficha de logro propuesta por Archive (Pantalla 2)
        self.mirror_patron = None  # patrón seleccionado para una sesión de Mirror
        self.mirror_reframe = None  # reframe generado al cerrar la sesión
        self.mirror_minutos = 0
        self.editor_contexto = None  # logro que viaja de Archive a Editor
        self.editor_borrador_id = None  # borrador a retomar en el estudio (None = nuevo)
        self.clarity_inicial = None  # primer mensaje que arranca la conversación de Clarity
        self.clarity_turns = None  # turnos de la sesión de Clarity (para las puertas)
        self.clarity_cierre = None  # síntesis + clasificación de puertas de Clarity
        self.pacer_completada = None  # misión recién completada (para su pantalla de cierre)

        # Chip fijo (esquina superior derecha) con el handle del usuario, para
        # que tenga su codigo de acceso siempre presente. Vive en el overlay, asi
        # que persiste entre vistas (page.controls.clear() no lo borra).
        self._chip_texto = ft.Text("", size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY)
        self.chip_handle = ft.Container(
            visible=False,
            right=18,
            top=14,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.all(1, tema.BORDER_LIGHT),
            border_radius=20,
            content=ft.Row(
                spacing=8,
                tight=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, size=15, color=tema.AMBAR), self._chip_texto],
            ),
        )
        self.page.overlay.append(self.chip_handle)

        # Overlay de carga: cubre la pantalla y bloquea clics durante operaciones
        # pesadas (generación con Claude antes de navegar). Vive en el overlay.
        self._carga_texto = ft.Text("Cargando…", size=14, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.NAVY)
        self.overlay_carga = ft.Container(
            visible=False,
            left=0, top=0, right=0, bottom=0,
            bgcolor=ft.Colors.with_opacity(0.78, tema.OFF_WHITE),
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=18,
                controls=[
                    ft.ProgressRing(width=44, height=44, color=tema.AMBAR, stroke_width=4),
                    self._carga_texto,
                ],
            ),
        )
        self.page.overlay.append(self.overlay_carga)

    def mostrar_carga(self, mensaje="Cargando…"):
        self._carga_texto.value = mensaje
        self.overlay_carga.visible = True
        self.page.update()

    def ocultar_carga(self):
        self.overlay_carga.visible = False
        self.page.update()

    # Rutas sin sesion donde el chip no debe mostrarse.
    _RUTAS_SIN_CHIP = {"/landing", "/login", "/pre_onboarding"}

    def _actualizar_chip(self, ruta):
        if self.id_usuario and ruta not in self._RUTAS_SIN_CHIP:
            handle = clsInteraccionDB.obtener_handle(self.id_usuario)
            self._chip_texto.value = handle or ""
            self.chip_handle.visible = bool(handle)
        else:
            self.chip_handle.visible = False

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
        self._actualizar_chip(ruta)
        self.overlay_carga.visible = False  # toda navegación limpia el cargando
        self.page.update()

        # Hook opcional que se ejecuta cuando la vista termina de montarse.
        if hasattr(vista, "al_cargar"):
            self.page.run_task(vista.al_cargar)

    def _resolver_vista(self, ruta):
        if ruta.startswith("/chat/"):
            tipo_agente = ruta.split("/chat/", 1)[1]
            # Archive usa su propio flujo editorial (chat → ficha → timeline).
            if tipo_agente == "coach_archive":
                return frmArchiveChat(self, self.id_usuario)
            # El resto de los agentes ya no usan el chat genérico.
            return frmMenuInicio(self, self.id_usuario)

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
            "/pacer/completada": frmPacerCompletada,
            "/archive": frmArchiveTimeline,
            "/archive/ficha": frmArchiveFicha,
            "/mirror": frmMirrorHub,
            "/mirror/entry": frmMirrorEntry,
            "/mirror/session": frmMirrorSession,
            "/mirror/espejo": frmMirrorEspejo,
            "/editor": frmEditorHome,
            "/editor/estudio": frmEditor,
            "/clarity": frmClarityEspejo,
            "/clarity/conversacion": frmClarityConversacion,
            "/clarity/puertas": frmClarityPuertas,
        }
        clase = vistas.get(ruta, frmLanding)
        return clase(self, self.id_usuario)
