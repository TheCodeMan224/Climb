"""Superficie propia de Pacer: la mision semanal y su progreso."""

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes
from data import clsInteraccionDB


class frmPacer:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.estado = None  # {"id_mision", "mision", "progreso"}
        self.cuerpo = ft.Column(spacing=14)
        self.boton_generar = None

    # --- Render de la mision -----------------------------------------------
    def _render_mision(self):
        self.cuerpo.controls.clear()

        if not self.estado:
            self.cuerpo.controls.append(
                ft.Text("Aún no hay una misión generada.", size=16, font_family=tema.FUENTE_BODY, color=tema.MUTED)
            )
            return

        mision = self.estado["mision"]
        progreso = self.estado["progreso"]
        acciones = mision.get("acciones", [])[:5]
        completadas = sum(1 for p in progreso if p)

        self.cuerpo.controls.extend([
            cmp.eyebrow(f"{completadas} de {len(acciones)} acciones completadas", color=tema.AMBAR),
            ft.Container(height=8),
            ft.Text(mision.get("nombre_mision", ""), size=26, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
            ft.Text(mision.get("descripcion", ""), size=15, font_family=tema.FUENTE_BODY, color=tema.TEXTO),
            ft.Container(height=10),
            cmp.eyebrow("Acciones concretas"),
            ft.Container(height=4),
        ])

        for i, accion in enumerate(acciones):
            hecha = bool(progreso[i]) if i < len(progreso) else False
            self.cuerpo.controls.append(self._fila_accion(i, accion, hecha))

        self.cuerpo.controls.append(ft.Container(height=10))
        self.cuerpo.controls.append(
            ft.Container(
                padding=18,
                bgcolor=tema.NAVY,
                border_radius=12,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        cmp.eyebrow("Conexión con tu camino", color=tema.TEXTO_SUAVE_SOBRE_NAVY),
                        ft.Text(mision.get("conexion_camino", ""), size=14, font_family=tema.FUENTE_BODY, color=tema.TEXTO_SOBRE_NAVY),
                    ],
                ),
            )
        )

        # Cuando todas las acciones están hechas, se puede cerrar la misión.
        if acciones and completadas >= len(acciones):
            self.cuerpo.controls.append(ft.Container(height=16))
            self.cuerpo.controls.append(
                ft.Row(controls=[cmp.boton_primario("Completar misión  →", on_click=self._completar)])
            )

    def _fila_accion(self, indice, accion, hecha):
        # Fila completa clickeable; el texto envuelve y ocupa todo el ancho.
        return ft.Container(
            on_click=lambda e, idx=indice, v=not hecha: self._toggle_accion(idx, v),
            ink=True,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=8, vertical=8),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=12,
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_BOX_ROUNDED if hecha else ft.Icons.CHECK_BOX_OUTLINE_BLANK_ROUNDED,
                        color=tema.NAVY if hecha else tema.MUTED,
                        size=22,
                    ),
                    ft.Text(
                        accion,
                        size=14,
                        font_family=tema.FUENTE_BODY,
                        color=tema.MUTED if hecha else tema.TEXTO,
                        italic=hecha,
                        expand=True,
                    ),
                ],
            ),
        )

    # --- Eventos ------------------------------------------------------------
    def _toggle_accion(self, indice, valor):
        if not self.estado:
            return
        self.estado["progreso"][indice] = bool(valor)
        clsInteraccionDB.guardar_progreso_mision(self.estado["id_mision"], self.estado["progreso"])
        self._render_mision()
        self.router.page.update()

    def _completar(self, e=None):
        if not self.estado:
            return
        clsInteraccionDB.completar_mision(self.estado["id_mision"])
        self.router.pacer_completada = self.estado["mision"]
        self.router.navegar_a("/pacer/completada")

    async def al_cargar(self):
        # La mision ya se carga en construir(); aqui solo generamos si no existe.
        if self.estado is None:
            await self._generar()

    async def _generar(self, e=None):
        self.router.mostrar_carga("Generando tu misión…")
        if self.boton_generar:
            self.boton_generar.disabled = True
        try:
            await clsAgentes.generar_mision_pacer(self.id_usuario)
        except Exception:
            pass
        self.estado = clsInteraccionDB.obtener_ultima_mision(self.id_usuario)
        self._render_mision()
        if self.boton_generar:
            self.boton_generar.disabled = False
            self.boton_generar.content = "Generar nueva misión"
        self.router.ocultar_carga()
        self.router.page.update()

    # --- Construccion -------------------------------------------------------
    def construir(self):
        self.estado = clsInteraccionDB.obtener_ultima_mision(self.id_usuario)
        self._render_mision()

        self.boton_generar = cmp.boton_primario("Generar nueva misión", on_click=lambda e: self.router.page.run_task(self._generar))
        boton_menu = cmp.enlace("‹ Regresar al menú", on_click=lambda e: self.router.navegar_a("/menu_inicio"))

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=720,
                    padding=ft.Padding.symmetric(horizontal=40, vertical=40),
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            cmp.eyebrow("Pacer · Tu semana"),
                            ft.Container(height=12),
                            cmp.hairline(width=40),
                            ft.Container(height=20),
                            ft.Text("Tu misión de esta semana", size=40, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                            ft.Container(height=24),
                            ft.Container(
                                padding=30,
                                bgcolor=tema.SUPERFICIE,
                                border=ft.Border.all(1, tema.BORDER_LIGHT),
                                border_radius=12,
                                content=self.cuerpo,
                            ),
                            ft.Container(height=24),
                            ft.Row(spacing=24, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[self.boton_generar, boton_menu]),
                            ft.Container(height=40),
                        ],
                    ),
                )
            ],
        )
