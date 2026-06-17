"""Modelo de datos y lógica del espejo del agente Clarity.

Clarity no produce artefactos: primero DEVUELVE perspectiva (un "espejo" de lo
que la persona ha construido con los otros agentes) y luego abre una
conversación para pensar antes de decidir.

La construcción del espejo es DETERMINÍSTICA: lee datos reales de la base
(Archive, Mirror, Editor, Scout, Pacer) y los convierte en frases narrativas
con el dato embebido. No llama a Claude.
"""

from dataclasses import dataclass, field
from datetime import datetime

from core import clsMirror
from data import clsInteraccionDB

_MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _fecha_corta(dt):
    return f"{dt.day:02d} {_MESES[dt.month - 1]}"


@dataclass
class Referencia:
    """Una pieza real que Clarity puede citar en la conversación (reference-quote)."""
    agente: str
    fecha: str
    cita: str


@dataclass
class EspejoBloque:
    numero: str
    agente: str
    # segmentos: lista de (texto, es_dato). es_dato=True se pinta en gold (Syne).
    segmentos: list
    tiene_datos: bool
    cta_texto: str = ""
    cta_ruta: str = ""
    cta_patron: tuple = None  # (nombre, descripcion) para mandar un patrón de Scout a Mirror


@dataclass
class PacerSnapshot:
    nombre: str
    hechas: int
    total: int


@dataclass
class EspejoResumen:
    nombre: str
    bloques: list
    pacer: PacerSnapshot
    counters: dict = field(default_factory=dict)


def _plural(n, palabra):
    return f"{palabra}{'s' if n != 1 else ''}"


def _patrones_scout_no_procesados(id_usuario):
    """Patrones de Scout (del resumen) que aún no se han llevado a Mirror."""
    pendientes, _ = clsMirror.cargar_hub(id_usuario)
    return [(p.scout_ref or p.quote, p.quote) for p in pendientes if p.source == "scout"]


def cargar_espejo(id_usuario):
    """Arma el EspejoResumen completo a partir de datos reales de la base."""
    nombre = clsInteraccionDB.obtener_nombre_usuario(id_usuario) or ""
    bloques = []

    # --- Archive (03) ---
    logros = clsInteraccionDB.obtener_logros_completos(id_usuario)
    if logros:
        titulos = ", ".join(l["titulo"] for l in logros[:3])
        segs = [
            ("You've rescued ", False), (str(len(logros)), True),
            (f" {_plural(len(logros), 'win')} that had been forgotten — {titulos}.", False),
        ]
        bloques.append(EspejoBloque("03", "Archive", segs, True))
    else:
        bloques.append(EspejoBloque(
            "03", "Archive",
            [("You haven't documented your wins yet. When you close something that matters, Archive saves it for when you need it.", False)],
            False, cta_texto="Open Archive  →", cta_ruta="/archive"))

    # --- Mirror (01) ---
    pendientes, observando = clsMirror.cargar_hub(id_usuario)
    if observando:
        p = observando[0]
        cita = p.reframe.old_quote if p.reframe else p.quote
        dias = (datetime.now() - p.detected_at).days
        segs = [
            ("You worked on the pattern ", False),
            (f'"{cita}"', False),
            (f" {clsMirror._hace(dias)}, and it's already starting to sound different.", False),
        ]
        bloques.append(EspejoBloque("01", "Mirror", segs, True))
    elif pendientes:
        segs = [("You have ", False), (str(len(pendientes)), True),
                (f" {_plural(len(pendientes), 'pattern')} to work on. Mirror takes them apart with questions.", False)]
        bloques.append(EspejoBloque("01", "Mirror", segs, True, cta_texto="Open Mirror  →", cta_ruta="/mirror"))
    else:
        bloques.append(EspejoBloque(
            "01", "Mirror",
            [("You haven't worked on any pattern with Mirror yet.", False)],
            False, cta_texto="Open Mirror  →", cta_ruta="/mirror"))

    # --- Editor (02) ---
    completos = clsInteraccionDB.obtener_borradores_editor(id_usuario, "completado")
    if completos:
        segs = [("You've polished ", False), (str(len(completos)), True),
                (f" {_plural(len(completos), 'piece')} of content ready to show the world.", False)]
        bloques.append(EspejoBloque("02", "Editor", segs, True))
    else:
        bloques.append(EspejoBloque(
            "02", "Editor",
            [("You haven't finished any piece with Editor yet.", False)],
            False, cta_texto="Open Editor  →", cta_ruta="/editor"))

    # --- Scout (00) ---
    scout_pendientes = _patrones_scout_no_procesados(id_usuario)
    if scout_pendientes:
        bloques.append(EspejoBloque(
            "00", "Scout",
            [("Your diagnosis keeps feeding the system. I detected a new pattern worth seeing.", False)],
            True, cta_texto="See detected pattern  →", cta_patron=scout_pendientes[0]))
    else:
        bloques.append(EspejoBloque(
            "00", "Scout",
            [("Your initial diagnosis is still active in the background, watching how you evolve.", False)],
            False))

    # --- Pacer snapshot ---
    estado = clsInteraccionDB.obtener_ultima_mision(id_usuario)
    camino = clsInteraccionDB.obtener_camino_elegido(id_usuario)
    pacer = None
    hechas = total = 0
    if estado:
        acciones = estado["mision"].get("acciones", [])
        total = len(acciones)
        hechas = sum(1 for x in estado["progreso"] if x)
        nombre_pacer = estado["mision"].get("nombre_mision", "") or (camino.get("nombre_camino", "") if camino else "")
        pacer = PacerSnapshot(nombre_pacer, hechas, total)

    counters = {
        "logros": len(logros),
        "patrones": len(observando),
        "piezas": len(completos),
        "mision": (f"{hechas:02d}/{total:02d}" if estado else None),
    }
    return EspejoResumen(nombre, bloques, pacer, counters)


def referencias_disponibles(id_usuario):
    """Material real que Clarity puede citar en la conversación (Mirror + Archive)."""
    refs = []
    _, observando = clsMirror.cargar_hub(id_usuario)
    for p in observando:
        cita = p.reframe.old_quote if p.reframe else p.quote
        refs.append(Referencia("Mirror", _fecha_corta(p.detected_at), cita))
    for l in clsInteraccionDB.obtener_logros_completos(id_usuario)[:5]:
        refs.append(Referencia("Archive", l.get("fecha_corta", ""), l["titulo"]))
    return refs


def resumen_counters_texto(counters):
    """Texto de una línea para el espejo colapsado (pantallas 2 y 3)."""
    w = counters.get('logros', 0)
    pt = counters.get('patrones', 0)
    pz = counters.get('piezas', 0)
    partes = [
        f"{w} {'win' if w == 1 else 'wins'}",
        f"{pt} pattern worked" if pt == 1 else f"{pt} patterns worked",
        f"{pz} {'piece' if pz == 1 else 'pieces'} polished",
    ]
    if counters.get("mision"):
        partes.append(f"mission {counters['mision']}")
    return "  ·  ".join(partes)
