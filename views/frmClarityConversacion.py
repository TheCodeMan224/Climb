"""Clarity · Pantalla 2: conversación activa.

Chat editorial (sin burbujas) con espejo colapsado arriba y reference-quotes
inline cuando Clarity cruza contexto con otros agentes. Al detectar cierre
natural ([listo]), pasa a las puertas de salida.
"""

import traceback

import flet as ft

import componentes as cmp
import tema
from core import clsAgentes, clsClarity
from data import clsInteraccionDB


class frmClarityConversacion:
    def __init__(self, router, id_usuario=None):
        self.router = router
        self.id_usuario = id_usuario if id_usuario is not None else router.id_usuario
        self.id_chat = clsInteraccionDB.obtener_o_crear_chat(self.id_usuario, "clarity_session")
        self.refs = clsClarity.referencias_disponibles(self.id_usuario)
        self.counters = clsClarity.cargar_espejo(self.id_usuario).counters
        self.tema = ""

        # turns: list[{"speaker","text","ref"}] (ref = clsClarity.Referencia | None)
        self.turns = []
        for m in clsInteraccionDB.obtener_mensajes(self.id_chat):
            self.turns.append({
                "speaker": "clarity" if m["rol"] == "assistant" else "user",
                "text": m["contenido"], "ref": None,
            })

        self.inicial = router.clarity_inicial
        router.clarity_inicial = None

        self.chat_list = ft.ListView(expand=True, spacing=0, padding=ft.Padding.symmetric(vertical=8), auto_scroll=True)
        self.anchor_lbl = cmp.eyebrow("Pensando · Tu situación", color=tema.AMBAR, size=11)
        self.campo = ft.TextField(
            hint_text="O dime si ya viste lo que necesitabas...",
            expand=True, multiline=True, min_lines=1, max_lines=4,
            border=ft.InputBorder.NONE, bgcolor="transparent", cursor_color=tema.NAVY,
            text_style=ft.TextStyle(font_family=tema.FUENTE_BODY, size=15, color=tema.NAVY),
            hint_style=ft.TextStyle(font_family=tema.FUENTE_SERIF, italic=True, size=15, color=tema.HINT),
            on_submit=self._enviar_input,
        )

    # --- Hook tras montar ---------------------------------------------------
    async def al_cargar(self):
        if self.inicial:
            texto, self.inicial = self.inicial, None
            await self._procesar_usuario(texto)
        elif not self.turns:
            # Entrada directa sin mensaje inicial: Clarity abre.
            await self._turno_clarity()

    # --- Render -------------------------------------------------------------
    def _turno_control(self, turno):
        es_clarity = turno["speaker"] == "clarity"
        hijos = [
            cmp.eyebrow("Clarity" if es_clarity else "Tú", color=tema.AMBAR if es_clarity else tema.MUTED, size=11),
            ft.Container(height=10),
            ft.Container(width=600, content=ft.Text(
                turno["text"], size=16,
                color=tema.NAVY if es_clarity else tema.MUTED,
                italic=not es_clarity,
                font_family=tema.FUENTE_BODY if es_clarity else tema.FUENTE_SERIF)),
        ]
        if turno.get("ref"):
            hijos.append(ft.Container(height=12))
            hijos.append(self._reference_quote(turno["ref"]))
        return ft.Container(padding=ft.Padding.only(bottom=28), content=ft.Column(spacing=0, controls=hijos))

    def _reference_quote(self, ref):
        return ft.Container(
            width=560,
            bgcolor=tema.SUPERFICIE,
            border=ft.Border.only(left=ft.BorderSide(2, tema.AMBAR)),
            border_radius=4, padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            content=ft.Column(spacing=6, controls=[
                cmp.eyebrow(f"{ref.agente} · {ref.fecha}", color=tema.AMBAR, size=10),
                ft.Text(f'"{ref.cita}"', size=13, italic=True, font_family=tema.FUENTE_SERIF, color=tema.MUTED),
            ]),
        )

    def _rerender(self):
        self.chat_list.controls = [self._turno_control(t) for t in self.turns]

    # --- Lógica de conversación --------------------------------------------
    async def _enviar_input(self, e):
        texto = (self.campo.value or "").strip()
        if texto:
            self.campo.value = ""
            await self._procesar_usuario(texto)

    async def _procesar_usuario(self, texto):
        self.turns.append({"speaker": "user", "text": texto, "ref": None})
        clsInteraccionDB.insertar_mensaje(self.id_chat, "user", texto)
        clsInteraccionDB.registrar_texto_usuario(self.id_usuario, "clarity", texto)
        self.router.page.run_task(clsAgentes.actualizar_voice_profile_si_toca, self.id_usuario)
        self._rerender()
        self.router.page.update()
        await self._turno_clarity()

    async def _turno_clarity(self):
        self.router.mostrar_carga("Clarity está pensando…")
        try:
            pares = [(t["speaker"], t["text"]) for t in self.turns]
            res = await clsAgentes.responder_clarity(pares, self.id_usuario, self.refs, primer_turno=not self.turns)
        except Exception:
            traceback.print_exc()
            self.router.ocultar_carga()
            self.turns.append({"speaker": "clarity", "text": "Tuve un problema. Intentémoslo de nuevo.", "ref": None})
            self._rerender()
            self.router.page.update()
            return

        ref = None
        if res.get("referencia_id") is not None and 0 <= res["referencia_id"] < len(self.refs):
            ref = self.refs[res["referencia_id"]]
        mensaje = res.get("mensaje") or "…"
        self.turns.append({"speaker": "clarity", "text": mensaje, "ref": ref})
        clsInteraccionDB.insertar_mensaje(self.id_chat, "assistant", mensaje)

        if res.get("tema") and not self.tema:
            self.tema = res["tema"]
            self.anchor_lbl.value = f"Pensando · {self.tema}".upper()

        self._rerender()
        self.router.ocultar_carga()

        if res.get("listo"):
            await self._cerrar()

    async def _cerrar(self):
        self.router.mostrar_carga("Cerrando la conversación…")
        try:
            pares = [(t["speaker"], t["text"]) for t in self.turns]
            cierre = await clsAgentes.clarity_cierre(pares, self.id_usuario)
        except Exception:
            traceback.print_exc()
            self.router.ocultar_carga()
            return  # nos quedamos en la conversación si falla
        self.router.clarity_cierre = cierre
        self.router.clarity_turns = [(t["speaker"], t["text"]) for t in self.turns]
        self.router.navegar_a("/clarity/puertas")

    # --- Construcción -------------------------------------------------------
    def construir(self):
        self._rerender()

        colapsado = ft.Container(
            bgcolor=tema.SUPERFICIE, border=ft.Border.all(1, tema.BORDER_LIGHT), border_radius=6,
            padding=ft.Padding.symmetric(horizontal=22, vertical=16), margin=ft.Margin.only(bottom=28),
            on_click=lambda e: self.router.navegar_a("/clarity"), ink=True,
            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    cmp.eyebrow("Tu espejo", color=tema.AMBAR, size=11),
                    ft.Text(clsClarity.resumen_counters_texto(self.counters), size=13, font_family=tema.FUENTE_BODY, color=tema.MUTED),
                ]),
                cmp.eyebrow("Ver completo  →", color=tema.BLUE, size=10),
            ]),
        )

        anchor = ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12, controls=[
            self.anchor_lbl,
            ft.Container(expand=True, height=1, bgcolor=tema.BORDER_LIGHT),
        ])

        entrada = ft.Column(spacing=12, controls=[
            cmp.eyebrow("Sigue pensando en voz alta", color=tema.MUTED, size=11),
            ft.Container(
                border=ft.Border.only(bottom=ft.BorderSide(1, tema.NAVY)),
                padding=ft.Padding.only(bottom=12),
                content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.END, controls=[
                    self.campo,
                    ft.ElevatedButton(
                        content=ft.Text("ENVIAR  →", size=12, weight=ft.FontWeight.W_600, font_family=tema.FUENTE_SUBHEADER, color=tema.TEXTO_SOBRE_NAVY),
                        on_click=self._enviar_input,
                        style=ft.ButtonStyle(bgcolor=tema.NAVY, shape=ft.RoundedRectangleBorder(radius=4), padding=ft.Padding.symmetric(horizontal=22, vertical=14), elevation=0)),
                ]),
            ),
        ])

        cuerpo = ft.Column(expand=True, spacing=0, controls=[
            cmp.topbar("Clarity · Sesión", derecha="← Volver", on_back=lambda e: self.router.navegar_a("/clarity")),
            ft.Container(height=24),
            colapsado,
            anchor,
            ft.Container(height=8),
            self.chat_list,
            ft.Container(
                padding=ft.Padding.only(top=20), margin=ft.Margin.only(top=12),
                border=ft.Border.only(top=ft.BorderSide(1, tema.BORDER_LIGHT)),
                content=entrada),
        ])

        return ft.Row(expand=True, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
            ft.Container(width=760, padding=ft.Padding.symmetric(horizontal=56, vertical=36), expand=True, content=cuerpo),
        ])
