"""Paleta de colores y tipografias centralizadas de Climb.

Toda la UI importa de aqui. Para cambiar el look de la app, edita este archivo.
"""

# ----------------------------------------------------------------------------
# Colores primarios
# ----------------------------------------------------------------------------
NAVY = "#0A1F44"        # texto principal, headers display, CTAs primarios, cards destacadas, borde de patrones
OFF_WHITE = "#FAFAF7"   # background general de la app (nunca blanco puro)
BLUE = "#2244DD"        # links activos, CTAs secundarios, borde de citas, focus de inputs, hover

# ----------------------------------------------------------------------------
# Soporte
# ----------------------------------------------------------------------------
MUTED = "#5F5E5A"       # subtexto, labels secundarios, descripciones bajo titulos
SECTION_BG = "#F5F5F2"  # diferenciar secciones, loading states, cards inactivas

# ----------------------------------------------------------------------------
# Funcionales (semaforo de visibilidad)
# ----------------------------------------------------------------------------
VERDE = "#1A6B3F"       # estados positivos ("Solida", "Establecida")
AMBAR = "#BA7517"       # estados intermedios, highlight de mision activa, CTAs sobre navy
AMBAR_LIGHT = "#FAEEDA" # relleno/acento suave ambar (fichas, metricas de Archive)
CORAL = "#712B13"       # estados criticos ("Invisible"), borde de patrones limitantes, alertas

# ----------------------------------------------------------------------------
# Bordes y superficies
# ----------------------------------------------------------------------------
BORDER_LIGHT = "#E5E5E0"  # bordes de cards normales, separadores, divisores sutiles
SUPERFICIE = "#FFFFFF"    # superficie de cards normales sobre el fondo off-white
HINT = "#B4B2A9"          # color de placeholders / texto fantasma en inputs
GRIS_TACHADO = "#D3D1C7"  # citas/patrones "viejos" atenuados (reframes de Mirror)

# ----------------------------------------------------------------------------
# Texto
# ----------------------------------------------------------------------------
TEXTO = NAVY             # texto principal sobre fondos claros
TEXTO_SUAVE = MUTED      # texto secundario / captions
TEXTO_SOBRE_NAVY = OFF_WHITE  # texto sobre cards/fondos navy oscuros
TEXTO_SUAVE_SOBRE_NAVY = "#B3FAFAF7"  # off-white al ~70% para labels sobre navy

# ----------------------------------------------------------------------------
# Tipografias (cargadas desde Google Fonts en main.py)
# ----------------------------------------------------------------------------
FUENTE_DISPLAY = "Syne"       # 700 - heroes, frase pivote, titulos de pantalla
FUENTE_SUBHEADER = "DM Sans"  # 600 - subtitulos, headers de seccion, labels, titulos de caminos
FUENTE_BODY = "Inter"         # 400 - cuerpo de texto (line-height 1.7)
FUENTE_SERIF = "Georgia"      # italic - citas (creencia limitante)

# ----------------------------------------------------------------------------
# Semaforo: mapea el valor que devuelve Claude a su color funcional.
# ----------------------------------------------------------------------------
COLOR_SEMAFORO = {
    "verde": VERDE,
    "ambar": AMBAR,
    "rojo": CORAL,
}
