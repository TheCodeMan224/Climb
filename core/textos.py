"""Capa de internacionalización (i18n) de Climb.

Los textos viven en dos árboles paralelos con las MISMAS claves:
    core/textos_en.py  ->  EN
    core/textos_es.py  ->  ES

Las vistas siguen usando `TEXTOS["seccion"]["clave"]` igual que antes, pero aquí
`TEXTOS` es un objeto "vivo": resuelve el idioma actual en el momento de leer cada
texto. Cambiar el idioma con `set_idioma(...)` y volver a renderizar la vista basta
para que todo aparezca en el nuevo idioma (las vistas se reconstruyen al navegar).

Idioma por defecto: inglés.
"""

from core.textos_en import EN
from core.textos_es import ES

_TREES = {"en": EN, "es": ES}
IDIOMA_DEFAULT = "en"

# Estado global del idioma activo en la sesión en curso.
_idioma_actual = IDIOMA_DEFAULT


def set_idioma(idioma):
    """Fija el idioma activo. Ignora valores desconocidos (deja el actual)."""
    global _idioma_actual
    if idioma in _TREES:
        _idioma_actual = idioma
    return _idioma_actual


def get_idioma():
    return _idioma_actual


def idiomas_disponibles():
    return list(_TREES.keys())


class _Seccion:
    """Proxy de una sección (p. ej. 'login') que resuelve el idioma al leer.

    `TEXTOS["login"]["titulo"]` -> _Seccion('login')['titulo'] -> texto en el
    idioma actual, con respaldo en inglés si una clave falta en el idioma activo.
    """

    __slots__ = ("_nombre",)

    def __init__(self, nombre):
        self._nombre = nombre

    def _resolver(self, key):
        seccion = _TREES.get(_idioma_actual, EN).get(self._nombre, {})
        if key in seccion:
            return seccion[key]
        # Respaldo: inglés (evita KeyError si una clave falta en el otro idioma).
        return EN.get(self._nombre, {})[key]

    def __getitem__(self, key):
        return self._resolver(key)

    def get(self, key, default=None):
        try:
            return self._resolver(key)
        except KeyError:
            return default

    def __contains__(self, key):
        seccion = _TREES.get(_idioma_actual, EN).get(self._nombre, {})
        return key in seccion or key in EN.get(self._nombre, {})


class _Textos:
    """Objeto público `TEXTOS`: indexar por sección devuelve un proxy vivo."""

    def __getitem__(self, nombre):
        return _Seccion(nombre)

    def __contains__(self, nombre):
        return nombre in EN


TEXTOS = _Textos()
