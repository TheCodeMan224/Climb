"""Editor · Home: borradores activos, completados y crear uno nuevo.

Es la primera pantalla de Editor. Desde aquí se retoma un borrador existente o
se entra al estudio (/editor/estudio) para crear uno nuevo.
"""

import flet as ft

import componentes as cmp
import tema
from core.textos import TEXTOS
from data import clsInteraccionDB

_T = TEXTOS["editor_home"]


class frmEditorHome:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario

    # --- Navegación ---------------------------------------------------------
    def _nuevo(self, e=None):
        self.router.editor_borrador_id = None
        self.router.editor_contexto = None
        self.router.navegar_a("/editor/estudio")

    def _abrir(self, id_borrador):
        self.router.editor_borrador_id = id_borrador
        self.router.editor_contexto = None
        self.router.navegar_a("/editor/estudio")

    # --- Helpers de presentación -------------------------------------------
    def _etiqueta(self, d):
        f = (d.get("formato") or "").strip().lower()
        if f == "linkedin":
            return _T["lbl_linkedin"]
        if d.get("es_correo"):
            return _T["lbl_correo"]
        return (d.get("formato") or _T["lbl_fallback"]).upper()[:30]

    def _pill(self, d):
        f = (d.get("formato") or "").strip().lower()
        if f == "linkedin":
            corto = _T["pill_linkedin"]
        elif d.get("es_correo"):
            corto = _T["pill_correo"]
        else:
            corto = (d.get("formato") or _T["pill_texto"]).split()[0].capitalize()[:10]
        return ft.Container(
            width=78, height=58, border_radius=4, bgcolor=tema.AMBAR_LIGHT,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(corto, size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.AMBAR),
        )

    def _card(self, d, completado=False):
        info = ft.Column(spacing=8, expand=True, controls=[
            ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                cmp.eyebrow(self._etiqueta(d), color=tema.AMBAR, size=11),
                cmp.eyebrow(_T["editado"].format(hace=d.get('hace', '')), color=tema.HINT, size=10),
            ]),
            ft.Text(f'"{d.get("preview","")}"' if d.get("preview") else _T["sin_contenido"],
                    size=15, color=tema.NAVY, font_family=tema.FUENTE_BODY),
        ])
        accion = cmp.enlace_cta(_T["ver"] if completado else _T["continuar"],
                                on_click=lambda e, i=d["id"]: self._abrir(i))
        return ft.Container(
            border=ft.Border.all(1, tema.BORDER_LIGHT), border_radius=6,
            padding=ft.Padding.symmetric(horizontal=22, vertical=20),
            margin=ft.Margin.only(bottom=14),
            content=ft.Row(spacing=22, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                           controls=[self._pill(d), info, accion]),
        )

    def _vacio(self, texto):
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=24),
            content=ft.Text(texto, size=15, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
        )

    # --- Construcción -------------------------------------------------------
    def construir(self):
        activos = clsInteraccionDB.obtener_borradores_editor(self.id_usuario, "activo")
        completos = clsInteraccionDB.obtener_borradores_editor(self.id_usuario, "completado")

        encabezado = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("02", size=64, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.AMBAR),
                ft.Container(width=24),
                ft.Column(spacing=8, expand=True, controls=[
                    ft.Text(_T["titulo"], size=46, weight=ft.FontWeight.W_700, font_family=tema.FUENTE_DISPLAY, color=tema.NAVY),
                    ft.Container(width=520, content=ft.Text(
                        _T["subtitulo"],
                        size=15, font_family=tema.FUENTE_BODY, color=tema.MUTED)),
                ]),
                cmp.boton_primario(_T["nuevo"], on_click=self._nuevo),
            ],
        )

        contenido = [
            cmp.topbar(_T["topbar"], derecha=TEXTOS["comun"]["volver_dashboard"], on_back=lambda e: self.router.navegar_a("/menu_inicio")),
            ft.Container(height=36),
            encabezado,
            cmp.section_divider(),
            cmp.section_header(_T["h_activos"], _T["activos_contador"].format(n=len(activos))),
            ft.Container(height=16),
        ]
        if activos:
            contenido.extend(self._card(d) for d in activos)
        else:
            contenido.append(self._vacio(_T["vacio"]))

        if completos:
            contenido.append(cmp.section_divider())
            contenido.append(cmp.section_header(_T["h_completados"], str(len(completos))))
            contenido.append(ft.Container(height=16))
            contenido.extend(self._card(d, completado=True) for d in completos)

        contenido.append(ft.Container(height=48))

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=1040,
                    padding=ft.Padding.symmetric(horizontal=56, vertical=44),
                    content=ft.Column(spacing=0, controls=contenido),
                )
            ],
        )
