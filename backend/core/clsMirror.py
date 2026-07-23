"""Modelo de datos del agente Mirror (dataclasses).

- Patron: un patrón limitante (detectado por Scout o descrito por el usuario).
- MirrorTurn: un turno de la sesión socrática.
- MirrorReframe: el reencuadre final de un patrón procesado.

La persistencia (tablas SQLite) se conecta al construir el Hub; aquí viven solo
las estructuras de datos y sus textos derivados (metadatos legibles).
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

from core.textos import TEXTOS
from data import clsInteraccionDB


def _hace(dias):
    """Texto relativo en el idioma activo a partir de un número de días."""
    _F = TEXTOS["fechas"]
    if dias <= 0:
        return _F["hoy"]
    if dias == 1:
        return _F["ayer"]
    if dias < 7:
        return _F["hace_dias"].format(n=dias)
    if dias < 14:
        return _F["hace_semana"]
    if dias < 30:
        return _F["hace_semanas"].format(n=dias // 7)
    meses = dias // 30
    return (_F["hace_mes"] if meses == 1 else _F["hace_meses"]).format(n=meses)


@dataclass
class MirrorReframe:
    old_quote: str
    new_quote: str
    lo_que_vimos: str
    manifestacion: str
    recomendaciones: list = field(default_factory=list)


def reframe_de_dict(d):
    """Construye un MirrorReframe tolerando datos viejos (campo 'pregunta')."""
    recs = d.get("recomendaciones")
    if not recs and d.get("pregunta"):
        recs = [d["pregunta"]]
    return MirrorReframe(
        old_quote=d.get("old_quote", ""),
        new_quote=d.get("new_quote", ""),
        lo_que_vimos=d.get("lo_que_vimos", ""),
        manifestacion=d.get("manifestacion", ""),
        recomendaciones=recs or [],
    )


@dataclass
class MirrorTurn:
    speaker: str  # "mirror" | "user"
    text: str


@dataclass
class Patron:
    id: str
    quote: str
    source: str            # "scout" | "user"
    detected_at: datetime
    status: str            # "pending" | "processing" | "observing"
    reframe: Optional[MirrorReframe] = None
    last_observed: Optional[datetime] = None
    scout_ref: Optional[str] = None  # nombre del patron de Scout (para dedupe)
    turns_json: Optional[str] = None  # conversacion en progreso (sesion a medias)

    @property
    def sesion(self):
        """Sesión en progreso como dict {turns, current_question, question_number}, o None."""
        if not self.turns_json:
            return None
        try:
            return json.loads(self.turns_json)
        except (ValueError, TypeError):
            return None

    @property
    def en_progreso(self) -> bool:
        """True si el patrón tiene una conversación a medias para retomar."""
        return self.status != "observing" and self.sesion is not None

    @property
    def respuestas_en_progreso(self) -> int:
        s = self.sesion or {}
        return sum(1 for t in s.get("turns", []) if t and t[0] == "user")

    @property
    def detected_meta(self) -> str:
        origen = "Described by you" if self.source == "user" else "Detected by Scout"
        return f"{origen}  ·  {_hace((datetime.now() - self.detected_at).days)}"

    @property
    def observed_meta(self) -> str:
        if not self.last_observed:
            return "No recent observations"
        return f"Last observed: {_hace((datetime.now() - self.last_observed).days)}"


# ----------------------------------------------------------------------------
# Carga del Hub: patrones de Scout (del resumen) + patrones de la tabla
# ----------------------------------------------------------------------------
def _parse_ts(ts):
    # PostgreSQL devuelve datetime (tz-aware); lo dejamos naive para comparar con
    # datetime.now() (naive) en el resto de este módulo.
    if isinstance(ts, datetime):
        return ts.replace(tzinfo=None)
    s = str(ts) if ts else ""
    for fmt, corte in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d", 10)):
        try:
            return datetime.strptime(s[:corte], fmt)
        except ValueError:
            continue
    return datetime.now()


def reframe_a_json(reframe: MirrorReframe) -> str:
    return json.dumps(asdict(reframe), ensure_ascii=False)


def _patron_de_fila(f):
    reframe = None
    if f.get("reframe_json"):
        try:
            reframe = reframe_de_dict(json.loads(f["reframe_json"]))
        except (ValueError, TypeError):
            reframe = None
    return Patron(
        id=f"db:{f['id_patron']}",
        quote=f["quote"],
        source=f.get("source") or "user",
        detected_at=_parse_ts(f.get("detected_at")),
        status=f.get("status") or "pending",
        reframe=reframe,
        last_observed=_parse_ts(f["last_observed"]) if f.get("last_observed") else None,
        scout_ref=f.get("scout_ref"),
        turns_json=f.get("turns_json"),
    )


def _patrones_scout(id_usuario):
    raw = clsInteraccionDB.obtener_ultimo_resumen(id_usuario)
    if not raw:
        return []
    try:
        return json.loads(raw).get("patrones_consolidados", [])
    except (ValueError, TypeError):
        return []


def cargar_hub(id_usuario):
    """Devuelve (pendientes, observando) como listas de Patron, combinando los
    patrones de Scout (resumen) con los de la tabla Mirror_Patrones."""
    filas = clsInteraccionDB.obtener_patrones_mirror(id_usuario)
    pendientes, observando = [], []
    procesados_scout = set()
    for f in filas:
        p = _patron_de_fila(f)
        # Cualquier patrón de Scout ya presente en la tabla (en progreso o procesado)
        # no debe volver a aparecer desde el resumen.
        if f.get("scout_ref"):
            procesados_scout.add(f["scout_ref"])
        if p.status == "observing":
            observando.append(p)
        else:
            pendientes.append(p)

    # Patrones de Scout que aún no se han procesado.
    for i, sp in enumerate(_patrones_scout(id_usuario)):
        nombre = sp.get("nombre", "")
        if nombre in procesados_scout:
            continue
        pendientes.append(Patron(
            id=f"scout:{i}",
            quote=sp.get("descripcion") or nombre,
            source="scout",
            detected_at=datetime.now(),
            status="pending",
            scout_ref=nombre,
        ))

    pendientes.sort(key=lambda p: p.detected_at, reverse=True)
    observando.sort(key=lambda p: p.detected_at, reverse=True)
    return pendientes, observando

