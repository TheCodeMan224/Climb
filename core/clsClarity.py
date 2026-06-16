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
            ("Has rescatado ", False), (str(len(logros)), True),
            (f" {_plural(len(logros), 'logro')} que estaban olvidados — {titulos}.", False),
        ]
        bloques.append(EspejoBloque("03", "Archive", segs, True))
    else:
        bloques.append(EspejoBloque(
            "03", "Archive",
            [("Aún no documentas tus logros. Cuando cierres algo que importe, Archive lo guarda para cuando lo necesites.", False)],
            False, cta_texto="Abrir Archive  →", cta_ruta="/archive"))

    # --- Mirror (01) ---
    pendientes, observando = clsMirror.cargar_hub(id_usuario)
    if observando:
        p = observando[0]
        cita = p.reframe.old_quote if p.reframe else p.quote
        dias = (datetime.now() - p.detected_at).days
        segs = [
            ("Trabajaste el patrón ", False),
            (f'"{cita}"', False),
            (f" {clsMirror._hace(dias)}, y ya empieza a sonar distinto.", False),
        ]
        bloques.append(EspejoBloque("01", "Mirror", segs, True))
    elif pendientes:
        segs = [("Tienes ", False), (str(len(pendientes)), True),
                (f" {_plural(len(pendientes), 'patrón')} por trabajar. Mirror los desarma con preguntas.", False)]
        bloques.append(EspejoBloque("01", "Mirror", segs, True, cta_texto="Abrir Mirror  →", cta_ruta="/mirror"))
    else:
        bloques.append(EspejoBloque(
            "01", "Mirror",
            [("Todavía no has trabajado ningún patrón con Mirror.", False)],
            False, cta_texto="Abrir Mirror  →", cta_ruta="/mirror"))

    # --- Editor (02) ---
    completos = clsInteraccionDB.obtener_borradores_editor(id_usuario, "completado")
    if completos:
        segs = [("Has pulido ", False), (str(len(completos)), True),
                (f" {_plural(len(completos), 'pieza')} de contenido listas para mostrar afuera.", False)]
        bloques.append(EspejoBloque("02", "Editor", segs, True))
    else:
        bloques.append(EspejoBloque(
            "02", "Editor",
            [("Aún no has terminado ninguna pieza con Editor.", False)],
            False, cta_texto="Abrir Editor  →", cta_ruta="/editor"))

    # --- Scout (00) ---
    scout_pendientes = _patrones_scout_no_procesados(id_usuario)
    if scout_pendientes:
        bloques.append(EspejoBloque(
            "00", "Scout",
            [("Tu diagnóstico sigue alimentando al sistema. Detecté un patrón nuevo que vale la pena ver.", False)],
            True, cta_texto="Ver patrón detectado  →", cta_patron=scout_pendientes[0]))
    else:
        bloques.append(EspejoBloque(
            "00", "Scout",
            [("Tu diagnóstico inicial sigue activo en el fondo, observando cómo evolucionas.", False)],
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
    partes = [
        f"{counters.get('logros', 0)} logros",
        f"{counters.get('patrones', 0)} patrón trabajado" if counters.get('patrones', 0) == 1 else f"{counters.get('patrones', 0)} patrones trabajados",
        f"{counters.get('piezas', 0)} piezas pulidas",
    ]
    if counters.get("mision"):
        partes.append(f"misión {counters['mision']}")
    return "  ·  ".join(partes)
