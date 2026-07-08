"""Operaciones CRUD sobre la base de datos de Climb.

Ninguna vista ni el motor de agentes ejecuta SQL directamente: todo pasa por aqui.
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import unicodedata
from datetime import datetime, timedelta, timezone

from core.textos import TEXTOS
from data.clsConexionDB import obtener_conexion

# Parametros de hashing de claves (pbkdf2_hmac, solo libreria estandar).
_ITERACIONES_PBKDF2 = 100_000


def _hash_clave(clave, salt=None):
    """Devuelve (salt_hex, hash_hex) para una clave. Genera salt si no se provee."""
    if salt is None:
        salt = os.urandom(16)
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), salt, _ITERACIONES_PBKDF2)
    return salt.hex(), derivada.hex()


# ----------------------------------------------------------------------------
# Usuarios
# ----------------------------------------------------------------------------
# Reglas de identidad de cuenta.
# username: 3-20 caracteres, empieza con letra, solo a-z 0-9 . y _ (case-insensitive).
_USERNAME_RE = re.compile(r"^[a-z][a-z0-9._]{2,19}$")
_CORREO_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalizar_username(username):
    """El username es case-insensitive: se guarda y compara en minusculas."""
    return (username or "").strip().lower()


def normalizar_correo(correo):
    return (correo or "").strip().lower()


def username_valido(username):
    return bool(_USERNAME_RE.match(normalizar_username(username)))


def correo_valido(correo):
    return bool(_CORREO_RE.match(normalizar_correo(correo)))


def username_existe(username):
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT 1 FROM Usuarios WHERE username = ?", (normalizar_username(username),)
    ).fetchone()
    conexion.close()
    return fila is not None


def correo_existe(correo):
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT 1 FROM Usuarios WHERE correo = ?", (normalizar_correo(correo),)
    ).fetchone()
    conexion.close()
    return fila is not None


def sugerir_username(nombre):
    """Propone un username libre derivado del nombre ('Daniel Beltran' -> 'danielbeltran')."""
    # Quitar acentos y dejar solo a-z 0-9.
    base = unicodedata.normalize("NFKD", nombre or "")
    base = "".join(c for c in base if not unicodedata.combining(c)).lower()
    base = re.sub(r"[^a-z0-9]", "", base)
    if len(base) < 3 or not base[:1].isalpha():
        base = ("user" + base)
    base = base[:20]
    if not username_existe(base):
        return base
    # Sufijo numerico incremental hasta encontrar uno libre.
    n = 2
    while True:
        candidato = f"{base[:20 - len(str(n))]}{n}"
        if not username_existe(candidato):
            return candidato
        n += 1


def crear_usuario(nombre, username, correo, clave, idioma="en"):
    """Crea un usuario con username unico, correo, clave hasheada e idioma.

    Devuelve un dict con id_usuario y username. Lanza ValueError si el username o
    el correo ya estan registrados (colision detectada por el indice unico).
    """
    username = normalizar_username(username)
    correo = normalizar_correo(correo)
    idioma = idioma if idioma in ("en", "es") else "en"
    salt_hex, hash_hex = _hash_clave(clave)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO Usuarios (nombre, username, correo, password_hash, password_salt, idioma) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (nombre.strip(), username, correo, hash_hex, salt_hex, idioma),
        )
    except sqlite3.IntegrityError as exc:
        conexion.close()
        raise ValueError("username o correo ya registrado") from exc
    id_usuario = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return {"id_usuario": id_usuario, "username": username}


def obtener_idioma(id_usuario):
    """Devuelve el idioma preferido del usuario ('en' | 'es'), 'en' por defecto."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT idioma FROM Usuarios WHERE id_usuario = ?", (id_usuario,)
    ).fetchone()
    conexion.close()
    if not fila or fila["idioma"] not in ("en", "es"):
        return "en"
    return fila["idioma"]


def guardar_idioma(id_usuario, idioma):
    """Persiste el idioma preferido del usuario."""
    if idioma not in ("en", "es"):
        return
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Usuarios SET idioma = ? WHERE id_usuario = ?", (idioma, id_usuario)
    )
    conexion.commit()
    conexion.close()


def obtener_handle(id_usuario):
    """Devuelve el handle publico del usuario ('@username'), o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT username FROM Usuarios WHERE id_usuario = ?", (id_usuario,)
    ).fetchone()
    conexion.close()
    if not fila or not fila["username"]:
        return None
    return f"@{fila['username']}"


def verificar_credenciales(identificador, clave):
    """Verifica login por correo o username + clave. Devuelve id_usuario o None."""
    ident = (identificador or "").strip().lower()
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT id_usuario, password_hash, password_salt FROM Usuarios "
        "WHERE username = ? OR correo = ?",
        (ident, ident),
    ).fetchone()
    conexion.close()

    if not fila or not fila["password_hash"] or not fila["password_salt"]:
        return None

    salt = bytes.fromhex(fila["password_salt"])
    _, hash_hex = _hash_clave(clave, salt)
    if hmac.compare_digest(hash_hex, fila["password_hash"]):
        return fila["id_usuario"]
    return None


def obtener_nombre_usuario(id_usuario):
    """Devuelve el nombre del usuario o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT nombre FROM Usuarios WHERE id_usuario = ?", (id_usuario,)
    ).fetchone()
    conexion.close()
    return fila["nombre"] if fila else None


def obtener_usuario_por_correo(correo):
    """Devuelve {id_usuario, nombre, correo} para un correo, o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT id_usuario, nombre, correo FROM Usuarios WHERE correo = ?",
        (normalizar_correo(correo),),
    ).fetchone()
    conexion.close()
    return dict(fila) if fila else None


# ----------------------------------------------------------------------------
# Recuperacion de contrasena (codigo de 6 digitos por correo)
# ----------------------------------------------------------------------------
_RESET_EXPIRA_MIN = 20      # el codigo caduca a los 20 minutos
_RESET_COOLDOWN_SEG = 60    # minimo entre solicitudes para el mismo correo


def _hash_code(code):
    """Hash del codigo de reset (sha256). No se guarda en texto plano."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _parse_utc(texto):
    """Parsea un ISO a datetime aware en UTC; asume UTC si viene sin zona."""
    dt = datetime.fromisoformat(texto)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def crear_codigo_reset(correo):
    """Genera un codigo de reset para un correo y lo deja listo para enviar.

    Devuelve {id_usuario, nombre, correo, code} si se genero uno, o None si el
    correo no existe o si se pidio otro hace muy poco (rate limit). El caller solo
    envia el correo cuando el resultado no es None; en todos los casos debe mostrar
    el mismo mensaje generico para no revelar si la cuenta existe.
    """
    usuario = obtener_usuario_por_correo(correo)
    if not usuario:
        return None

    ahora = datetime.now(timezone.utc)
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Rate limit: si hay un codigo reciente sin usar, no generamos otro.
    fila = cursor.execute(
        "SELECT fecha_creacion FROM Password_Resets "
        "WHERE id_usuario = ? AND usado = 0 ORDER BY id_reset DESC LIMIT 1",
        (usuario["id_usuario"],),
    ).fetchone()
    if fila:
        try:
            creado = _parse_utc(fila["fecha_creacion"])
            if (ahora - creado).total_seconds() < _RESET_COOLDOWN_SEG:
                conexion.close()
                return None
        except (ValueError, TypeError):
            pass

    # Invalidar codigos anteriores (single-use estricto) y crear el nuevo.
    cursor.execute(
        "UPDATE Password_Resets SET usado = 1 WHERE id_usuario = ? AND usado = 0",
        (usuario["id_usuario"],),
    )
    code = f"{secrets.randbelow(1_000_000):06d}"
    expira = (ahora + timedelta(minutes=_RESET_EXPIRA_MIN)).isoformat()
    cursor.execute(
        "INSERT INTO Password_Resets (id_usuario, code_hash, expira, usado, fecha_creacion) "
        "VALUES (?, ?, ?, 0, ?)",
        (usuario["id_usuario"], _hash_code(code), expira, ahora.isoformat()),
    )
    conexion.commit()
    conexion.close()
    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
        "code": code,
    }


def verificar_codigo_reset(correo, code):
    """Valida un codigo (vigente, sin usar, correcto). Devuelve id_usuario o None.

    Si es valido, lo marca como usado en el acto para que no se pueda reutilizar.
    """
    usuario = obtener_usuario_por_correo(correo)
    if not usuario:
        return None

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    fila = cursor.execute(
        "SELECT id_reset, expira FROM Password_Resets "
        "WHERE id_usuario = ? AND code_hash = ? AND usado = 0 "
        "ORDER BY id_reset DESC LIMIT 1",
        (usuario["id_usuario"], _hash_code((code or "").strip())),
    ).fetchone()
    if not fila:
        conexion.close()
        return None

    try:
        expira = _parse_utc(fila["expira"])
    except (ValueError, TypeError):
        conexion.close()
        return None
    if datetime.now(timezone.utc) > expira:
        conexion.close()
        return None

    cursor.execute("UPDATE Password_Resets SET usado = 1 WHERE id_reset = ?", (fila["id_reset"],))
    conexion.commit()
    conexion.close()
    return usuario["id_usuario"]


def cambiar_password(id_usuario, nueva_clave):
    """Reemplaza la clave del usuario (nuevo salt + hash)."""
    salt_hex, hash_hex = _hash_clave(nueva_clave)
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Usuarios SET password_hash = ?, password_salt = ? WHERE id_usuario = ?",
        (hash_hex, salt_hex, id_usuario),
    )
    conexion.commit()
    conexion.close()


# ----------------------------------------------------------------------------
# Usuario_Perfil
# ----------------------------------------------------------------------------
def guardar_perfil(
    id_usuario,
    apertura_emocional,
    contexto_profesional,
    logro_principal,
    reaccion_presion_visibilidad,
    intentos_previos,
    vision_futuro,
    desahogo_libre,
):
    """Guarda las 9 respuestas del onboarding en Usuario_Perfil."""
    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO Usuario_Perfil (
            id_usuario, apertura_emocional, contexto_profesional, logro_principal,
            reaccion_presion_visibilidad, intentos_previos, vision_futuro, desahogo_libre
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_usuario,
            apertura_emocional,
            contexto_profesional,
            logro_principal,
            reaccion_presion_visibilidad,
            intentos_previos,
            vision_futuro,
            desahogo_libre,
        ),
    )
    conexion.commit()
    conexion.close()


def obtener_perfil(id_usuario):
    """Devuelve el perfil mas reciente del usuario como dict, o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        """
        SELECT apertura_emocional, contexto_profesional, logro_principal,
               reaccion_presion_visibilidad, intentos_previos, vision_futuro, desahogo_libre
        FROM Usuario_Perfil
        WHERE id_usuario = ?
        ORDER BY id_perfil DESC
        LIMIT 1
        """,
        (id_usuario,),
    ).fetchone()
    conexion.close()
    return dict(fila) if fila else None


# ----------------------------------------------------------------------------
# Chats
# ----------------------------------------------------------------------------
def obtener_chat(id_usuario, tipo_agente):
    """Devuelve el id_chat existente mas reciente para ese tipo de agente, o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        """
        SELECT id_chat FROM Chats
        WHERE id_usuario = ? AND tipo_agente = ?
        ORDER BY id_chat DESC
        LIMIT 1
        """,
        (id_usuario, tipo_agente),
    ).fetchone()
    conexion.close()
    return fila["id_chat"] if fila else None


def crear_chat(id_usuario, tipo_agente):
    """Crea una fila nueva en Chats y devuelve el id_chat."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO Chats (id_usuario, tipo_agente) VALUES (?, ?)",
        (id_usuario, tipo_agente),
    )
    id_chat = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_chat


def obtener_o_crear_chat(id_usuario, tipo_agente):
    """Reusa el chat existente del tipo de agente o crea uno nuevo."""
    id_chat = obtener_chat(id_usuario, tipo_agente)
    if id_chat is None:
        id_chat = crear_chat(id_usuario, tipo_agente)
    return id_chat


# ----------------------------------------------------------------------------
# Mensajes_Chat
# ----------------------------------------------------------------------------
def insertar_mensaje(id_chat, rol, contenido):
    """Inserta un mensaje del usuario o del agente."""
    conexion = obtener_conexion()
    conexion.execute(
        "INSERT INTO Mensajes_Chat (id_chat, rol, contenido) VALUES (?, ?, ?)",
        (id_chat, rol, contenido),
    )
    conexion.commit()
    conexion.close()


def obtener_mensajes(id_chat):
    """Devuelve el historial completo del chat en orden cronologico."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT rol, contenido FROM Mensajes_Chat
        WHERE id_chat = ?
        ORDER BY fecha_envio ASC, id_mensaje ASC
        """,
        (id_chat,),
    ).fetchall()
    conexion.close()
    return [dict(f) for f in filas]


def obtener_ultimos_mensajes(id_chat, limite=10):
    """Devuelve los ultimos N mensajes en orden cronologico para contexto."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT rol, contenido FROM Mensajes_Chat
        WHERE id_chat = ?
        ORDER BY fecha_envio DESC, id_mensaje DESC
        LIMIT ?
        """,
        (id_chat, limite),
    ).fetchall()
    conexion.close()
    # Invertir para devolver en orden cronologico ascendente.
    return [dict(f) for f in reversed(filas)]


# ----------------------------------------------------------------------------
# Hallazgos_Perfil
# ----------------------------------------------------------------------------
def insertar_hallazgo(id_usuario, origen, tipo, descripcion):
    """Inserta un hallazgo individual."""
    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO Hallazgos_Perfil (id_usuario, origen, tipo, descripcion)
        VALUES (?, ?, ?, ?)
        """,
        (id_usuario, origen, tipo, descripcion),
    )
    conexion.commit()
    conexion.close()


def obtener_hallazgos(id_usuario):
    """Devuelve todos los hallazgos del usuario."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT origen, tipo, descripcion, fecha_registro
        FROM Hallazgos_Perfil
        WHERE id_usuario = ?
        ORDER BY id_hallazgo ASC
        """,
        (id_usuario,),
    ).fetchall()
    conexion.close()
    return [dict(f) for f in filas]


# ----------------------------------------------------------------------------
# Historico_Resumenes
# ----------------------------------------------------------------------------
def insertar_resumen(id_usuario, contenido_json):
    """Inserta una fila de resumen consolidado (JSON ya serializado)."""
    conexion = obtener_conexion()
    conexion.execute(
        "INSERT INTO Historico_Resumenes (id_usuario, contenido_json) VALUES (?, ?)",
        (id_usuario, contenido_json),
    )
    conexion.commit()
    conexion.close()


def obtener_ultimo_resumen(id_usuario):
    """Devuelve el contenido_json del resumen mas reciente, o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        """
        SELECT contenido_json FROM Historico_Resumenes
        WHERE id_usuario = ?
        ORDER BY id_resumen DESC
        LIMIT 1
        """,
        (id_usuario,),
    ).fetchone()
    conexion.close()
    return fila["contenido_json"] if fila else None


# ----------------------------------------------------------------------------
# Camino_Elegido
# ----------------------------------------------------------------------------
def insertar_camino_elegido(
    id_usuario,
    nombre_camino,
    descripcion_camino,
    tradeoff_principal,
    riesgo_principal,
    tiempo_estimado_semanal,
    patron_que_rompe,
    caminos_alternativos_json,
):
    """Inserta el camino elegido por el usuario (una sola fila por usuario en el MVP)."""
    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO Camino_Elegido (
            id_usuario, nombre_camino, descripcion_camino, tradeoff_principal,
            riesgo_principal, tiempo_estimado_semanal, patron_que_rompe,
            caminos_alternativos_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_usuario,
            nombre_camino,
            descripcion_camino,
            tradeoff_principal,
            riesgo_principal,
            tiempo_estimado_semanal,
            patron_que_rompe,
            caminos_alternativos_json,
        ),
    )
    conexion.commit()
    conexion.close()


# ----------------------------------------------------------------------------
# Voice Profile: captura de textos del usuario y perfil de voz
# ----------------------------------------------------------------------------
def registrar_texto_usuario(id_usuario, fuente, texto):
    """Registra un texto escrito por el usuario (para construir su voice profile)."""
    if not texto or not texto.strip():
        return
    conexion = obtener_conexion()
    conexion.execute(
        "INSERT INTO Textos_Usuario (id_usuario, fuente, texto) VALUES (?, ?, ?)",
        (id_usuario, fuente, texto.strip()),
    )
    conexion.commit()
    conexion.close()


def obtener_textos_usuario(id_usuario, desde_id=0):
    """Devuelve los textos del usuario con idTexto > desde_id (orden cronológico)."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT idTexto, fuente, texto FROM Textos_Usuario
        WHERE id_usuario = ? AND idTexto > ?
        ORDER BY idTexto ASC
        """,
        (id_usuario, desde_id),
    ).fetchall()
    conexion.close()
    return [dict(f) for f in filas]


def obtener_voice_profile(id_usuario):
    """Devuelve el voice profile del usuario como dict, o None.

    Estructura: {"contenido" (dict|None), "n_muestras", "ultimo_texto_id"}.
    """
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT contenido_json, n_muestras, ultimo_texto_id FROM Voice_Profile WHERE id_usuario = ?",
        (id_usuario,),
    ).fetchone()
    conexion.close()
    if not fila:
        return None
    return {
        "contenido": json.loads(fila["contenido_json"]) if fila["contenido_json"] else None,
        "n_muestras": fila["n_muestras"] or 0,
        "ultimo_texto_id": fila["ultimo_texto_id"] or 0,
    }


def guardar_voice_profile(id_usuario, contenido, n_muestras, ultimo_texto_id):
    """Inserta o reemplaza el voice profile del usuario (contenido = dict)."""
    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT OR REPLACE INTO Voice_Profile (id_usuario, contenido_json, n_muestras, ultimo_texto_id, fecha)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (id_usuario, json.dumps(contenido, ensure_ascii=False), n_muestras, ultimo_texto_id),
    )
    conexion.commit()
    conexion.close()


# ----------------------------------------------------------------------------
# Mirror_Patrones
# ----------------------------------------------------------------------------
def insertar_patron_usuario(id_usuario, quote):
    """Registra un patrón descrito por el usuario (pending). Devuelve idPatron."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO Mirror_Patrones (id_usuario, quote, source, status) VALUES (?, ?, 'user', 'pending')",
        (id_usuario, quote),
    )
    id_patron = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_patron


def insertar_patron_procesado(id_usuario, quote, source, reframe_json, scout_ref=None):
    """Registra un patrón ya procesado (observing) con su reframe. Devuelve idPatron."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO Mirror_Patrones (id_usuario, quote, source, status, scout_ref, reframe_json, last_observed)
        VALUES (?, ?, ?, 'observing', ?, ?, CURRENT_TIMESTAMP)
        """,
        (id_usuario, quote, source, scout_ref, reframe_json),
    )
    id_patron = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_patron


def marcar_patron_procesado(id_patron, reframe_json):
    """Marca un patrón existente como observing con su reframe (y limpia la sesión en progreso)."""
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Mirror_Patrones SET status='observing', reframe_json=?, turns_json=NULL, last_observed=CURRENT_TIMESTAMP WHERE idPatron=?",
        (reframe_json, id_patron),
    )
    conexion.commit()
    conexion.close()


def guardar_sesion_mirror(id_patron, turns_json):
    """Guarda la conversación en progreso de un patrón existente (para retomarla)."""
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Mirror_Patrones SET turns_json=? WHERE idPatron=?",
        (turns_json, id_patron),
    )
    conexion.commit()
    conexion.close()


def insertar_patron_en_progreso(id_usuario, quote, source, turns_json, scout_ref=None):
    """Inserta un patrón aún 'pending' con su conversación en progreso. Devuelve idPatron.

    Se usa cuando el usuario deja a medias un patrón que aún no estaba en la tabla
    (p. ej. uno detectado por Scout)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO Mirror_Patrones (id_usuario, quote, source, status, scout_ref, turns_json) "
        "VALUES (?, ?, ?, 'pending', ?, ?)",
        (id_usuario, quote, source, scout_ref, turns_json),
    )
    id_patron = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_patron


def obtener_patrones_mirror(id_usuario):
    """Devuelve todas las filas de patrones de Mirror del usuario como dicts."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT idPatron, quote, source, status, scout_ref, reframe_json, turns_json, detected_at, last_observed
        FROM Mirror_Patrones WHERE id_usuario = ? ORDER BY idPatron DESC
        """,
        (id_usuario,),
    ).fetchall()
    conexion.close()
    return [dict(f) for f in filas]


# ----------------------------------------------------------------------------
# Misiones
# ----------------------------------------------------------------------------
def insertar_mision(id_usuario, mision):
    """Guarda una mision (dict) como JSON, con su progreso inicializado en falso.

    Devuelve el id_mision recien creado.
    """
    progreso = [False] * len(mision.get("acciones", []))
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO Misiones (id_usuario, contenido_json, progreso_json) VALUES (?, ?, ?)",
        (
            id_usuario,
            json.dumps(mision, ensure_ascii=False),
            json.dumps(progreso),
        ),
    )
    id_mision = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_mision


def obtener_ultima_mision(id_usuario):
    """Devuelve el estado de la mision ACTIVA mas reciente, o None.

    Estructura: {"id_mision", "mision" (dict), "progreso" (list[bool])}.
    Las misiones ya completadas no se consideran activas.
    """
    conexion = obtener_conexion()
    fila = conexion.execute(
        """
        SELECT id_mision, contenido_json, progreso_json FROM Misiones
        WHERE id_usuario = ? AND (estado = 'activa' OR estado IS NULL)
        ORDER BY id_mision DESC
        LIMIT 1
        """,
        (id_usuario,),
    ).fetchone()
    conexion.close()
    if not fila:
        return None

    mision = json.loads(fila["contenido_json"])
    progreso = json.loads(fila["progreso_json"]) if fila["progreso_json"] else []
    # Alinear el progreso con el numero de acciones (por si falta).
    n = len(mision.get("acciones", []))
    if len(progreso) != n:
        progreso = (progreso + [False] * n)[:n]
    return {"id_mision": fila["id_mision"], "mision": mision, "progreso": progreso}


# ----------------------------------------------------------------------------
# Logros_Personales (registrados por Archive)
# ----------------------------------------------------------------------------
TIPOS_LOGRO = ["Project", "Impact", "Recognition", "Leadership", "Skill"]


def insertar_logro(id_usuario, tipo, logro, descripcion):
    """Registra un logro personal del usuario (lo guarda Archive)."""
    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO Logros_Personales (usuarioLogro, tipoLogro, logro, descripcionLogro)
        VALUES (?, ?, ?, ?)
        """,
        (id_usuario, tipo, logro, descripcion),
    )
    conexion.commit()
    conexion.close()


def obtener_logros(id_usuario):
    """Devuelve los logros del usuario (mas recientes primero)."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT idRegistro, tipoLogro, logro, descripcionLogro, fechaRegistroLogro
        FROM Logros_Personales
        WHERE usuarioLogro = ?
        ORDER BY idRegistro DESC
        """,
        (id_usuario,),
    ).fetchall()
    conexion.close()
    return [dict(f) for f in filas]


# --- Modelo enriquecido para Archive (3 pantallas) -------------------------
# Tipos del archivo de referencia de Archive.
LOGRO_TYPES = [
    "Deal closed", "Project", "Certification", "Learning",
    "Activation", "Leadership", "Presentation", "Other",
]

def _parse_fecha(ts):
    """Convierte el timestamp de SQLite en datetime (con respaldo a hoy)."""
    s = str(ts) if ts else ""
    for fmt, corte in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d", 10)):
        try:
            return datetime.strptime(s[:corte], fmt)
        except ValueError:
            continue
    return datetime.now()


def insertar_logro_completo(id_usuario, tipo, titulo, contexto, mi_rol="", aprendizaje="", tags=None, metrics=None, conversacion=None):
    """Registra un logro completo (modelo Archive). Devuelve idRegistro.

    tags: list[str].  metrics: list[{"value", "label"}].
    conversacion: lista de turnos de Archive que originó la ficha (opcional).
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO Logros_Personales
            (usuarioLogro, tipoLogro, logro, descripcionLogro, mi_rol, aprendizaje,
             tags_json, metrics_json, conversacion_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_usuario, tipo, titulo, contexto, mi_rol, aprendizaje,
            json.dumps(tags or [], ensure_ascii=False),
            json.dumps(metrics or [], ensure_ascii=False),
            json.dumps(conversacion, ensure_ascii=False) if conversacion is not None else None,
        ),
    )
    id_logro = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_logro


def _logro_dict(fila):
    """Construye el dict enriquecido (con campos calculados) desde una fila."""
    fecha = _parse_fecha(fila["fechaRegistroLogro"])
    tags = json.loads(fila["tags_json"]) if fila["tags_json"] else []
    metrics = json.loads(fila["metrics_json"]) if fila["metrics_json"] else []
    return {
        "id": fila["idRegistro"],
        "tipo": fila["tipoLogro"] or "",
        "titulo": fila["logro"] or "",
        "contexto": fila["descripcionLogro"] or "",
        "mi_rol": fila["mi_rol"] or "",
        "aprendizaje": fila["aprendizaje"] or "",
        "tags": tags,
        "metrics": metrics,
        "fecha": fecha,
        "fecha_corta": f"{fecha.day:02d} {TEXTOS['comun']['meses'][fecha.month - 1]}",
        "mes_anio": f"{TEXTOS['comun']['meses_largo'][fecha.month - 1]} {fecha.year}",
        "metric_destacada": metrics[0] if metrics else None,
    }


def obtener_logros_completos(id_usuario):
    """Devuelve los logros enriquecidos del usuario, mas recientes primero."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT idRegistro, tipoLogro, logro, descripcionLogro, mi_rol, aprendizaje,
               tags_json, metrics_json, fechaRegistroLogro
        FROM Logros_Personales
        WHERE usuarioLogro = ?
        ORDER BY fechaRegistroLogro DESC, idRegistro DESC
        """,
        (id_usuario,),
    ).fetchall()
    conexion.close()
    return [_logro_dict(f) for f in filas]


def archivo_agrupado_por_mes(id_usuario):
    """Agrupa los logros por 'Mes Año', preservando orden (mas reciente primero)."""
    agrupado = {}
    for logro in obtener_logros_completos(id_usuario):
        agrupado.setdefault(logro["mes_anio"], []).append(logro)
    return agrupado


def _agregar_impacto(logros):
    """Suma simple de metricas tipo '$240K' / '$1.2M'. Devuelve string '$X K/M'."""
    total_k = 0.0
    for logro in logros:
        for m in logro["metrics"]:
            v = str(m.get("value", "")).replace("$", "").replace(",", "").strip()
            try:
                if v.endswith("K"):
                    total_k += float(v[:-1])
                elif v.endswith("M"):
                    total_k += float(v[:-1]) * 1000
            except ValueError:
                pass
    if total_k >= 1000:
        return f"${total_k / 1000:.1f}M"
    return f"${int(total_k)}K"


def archivo_stats(id_usuario):
    """Estadisticas para el encabezado del timeline de Archive."""
    logros = obtener_logros_completos(id_usuario)
    ahora = datetime.now()
    trimestre = (ahora.month - 1) // 3
    este_trim = sum(
        1 for l in logros
        if l["fecha"].year == ahora.year and (l["fecha"].month - 1) // 3 == trimestre
    )
    tags = {t for l in logros for t in l["tags"]}
    return {
        "total": len(logros),
        "este_trimestre": este_trim,
        "impacto": _agregar_impacto(logros),
        "tags": len(tags),
    }


def guardar_progreso_mision(id_mision, progreso):
    """Actualiza la lista de acciones completadas (list[bool]) de una mision."""
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Misiones SET progreso_json = ? WHERE id_mision = ?",
        (json.dumps(progreso), id_mision),
    )
    conexion.commit()
    conexion.close()


def completar_mision(id_mision):
    """Marca una mision como completada con su fecha de cierre."""
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Misiones SET estado = 'completada', fecha_completada = CURRENT_TIMESTAMP WHERE id_mision = ?",
        (id_mision,),
    )
    conexion.commit()
    conexion.close()


def obtener_misiones_completadas(id_usuario):
    """Devuelve las misiones completadas (mas recientes primero) como dicts:
    {"nombre", "fecha"}. Útil para el historial y para alimentar a Pacer."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT contenido_json, fecha_completada FROM Misiones
        WHERE id_usuario = ? AND estado = 'completada'
        ORDER BY fecha_completada DESC, id_mision DESC
        """,
        (id_usuario,),
    ).fetchall()
    conexion.close()
    resultado = []
    for f in filas:
        try:
            mision = json.loads(f["contenido_json"])
        except (ValueError, TypeError):
            mision = {}
        resultado.append({"nombre": mision.get("nombre_mision", ""), "fecha": f["fecha_completada"]})
    return resultado


# ----------------------------------------------------------------------------
# Editor_Borradores (estudio de redacción)
# ----------------------------------------------------------------------------
def _hace(ts):
    """Texto relativo en el idioma activo ('5 min ago' / 'hace 5 min', etc.)."""
    _F = TEXTOS["fechas"]
    fecha = _parse_fecha(ts)
    seg = (datetime.now() - fecha).total_seconds()
    if seg < 60:
        return _F["ahora"]
    if seg < 3600:
        return _F["hace_min"].format(n=int(seg // 60))
    if seg < 86400:
        return _F["hace_horas"].format(n=int(seg // 3600))
    dias = int(seg // 86400)
    return _F["ayer"] if dias == 1 else _F["hace_dias"].format(n=dias)


def _preview_borrador(texto):
    """Primera línea/recorte del borrador para la lista del home."""
    t = " ".join((texto or "").split())
    return (t[:90] + "…") if len(t) > 90 else t


def crear_borrador_editor(id_usuario, formato, es_correo, asunto, borrador,
                          contexto_json=None, turns_json=None, estado="activo"):
    """Crea un borrador del estudio de Editor. Devuelve idBorrador."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO Editor_Borradores
            (id_usuario, formato, es_correo, asunto, borrador, estado, contexto_json, turns_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id_usuario, formato, int(bool(es_correo)), asunto, borrador, estado, contexto_json, turns_json),
    )
    id_borrador = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return id_borrador


def actualizar_borrador_editor(id_borrador, formato, es_correo, asunto, borrador, turns_json):
    """Actualiza el contenido de un borrador y refresca su marca de tiempo."""
    conexion = obtener_conexion()
    conexion.execute(
        """
        UPDATE Editor_Borradores
        SET formato = ?, es_correo = ?, asunto = ?, borrador = ?, turns_json = ?,
            actualizado = CURRENT_TIMESTAMP
        WHERE idBorrador = ?
        """,
        (formato, int(bool(es_correo)), asunto, borrador, turns_json, id_borrador),
    )
    conexion.commit()
    conexion.close()


def marcar_borrador_estado(id_borrador, estado):
    """Cambia el estado de un borrador ('activo' | 'completado')."""
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Editor_Borradores SET estado = ?, actualizado = CURRENT_TIMESTAMP WHERE idBorrador = ?",
        (estado, id_borrador),
    )
    conexion.commit()
    conexion.close()


def eliminar_borrador_editor(id_borrador):
    """Elimina un borrador definitivamente."""
    conexion = obtener_conexion()
    conexion.execute("DELETE FROM Editor_Borradores WHERE idBorrador = ?", (id_borrador,))
    conexion.commit()
    conexion.close()


def obtener_borrador_editor(id_borrador):
    """Devuelve un borrador completo como dict, o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        """
        SELECT idBorrador, formato, es_correo, asunto, borrador, estado,
               contexto_json, turns_json, actualizado
        FROM Editor_Borradores WHERE idBorrador = ?
        """,
        (id_borrador,),
    ).fetchone()
    conexion.close()
    if not fila:
        return None
    d = dict(fila)
    d["id"] = d["idBorrador"]
    d["es_correo"] = bool(d["es_correo"])
    return d


def obtener_borradores_editor(id_usuario, estado=None):
    """Lista los borradores del usuario (más recientes primero) para el home.

    Cada dict trae: id, formato, es_correo, asunto, estado, preview, hace.
    """
    conexion = obtener_conexion()
    if estado:
        filas = conexion.execute(
            """
            SELECT idBorrador, formato, es_correo, asunto, borrador, estado, actualizado
            FROM Editor_Borradores WHERE id_usuario = ? AND estado = ?
            ORDER BY actualizado DESC, idBorrador DESC
            """,
            (id_usuario, estado),
        ).fetchall()
    else:
        filas = conexion.execute(
            """
            SELECT idBorrador, formato, es_correo, asunto, borrador, estado, actualizado
            FROM Editor_Borradores WHERE id_usuario = ?
            ORDER BY actualizado DESC, idBorrador DESC
            """,
            (id_usuario,),
        ).fetchall()
    conexion.close()
    resultado = []
    for f in filas:
        resultado.append({
            "id": f["idBorrador"],
            "formato": f["formato"] or "",
            "es_correo": bool(f["es_correo"]),
            "asunto": f["asunto"] or "",
            "estado": f["estado"] or "activo",
            "preview": _preview_borrador(f["asunto"] if f["es_correo"] and f["asunto"] else f["borrador"]),
            "hace": _hace(f["actualizado"]),
        })
    return resultado


def obtener_camino_elegido(id_usuario):
    """Devuelve el camino elegido del usuario como dict, o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        """
        SELECT nombre_camino, descripcion_camino, tradeoff_principal, riesgo_principal,
               tiempo_estimado_semanal, patron_que_rompe, caminos_alternativos_json
        FROM Camino_Elegido
        WHERE id_usuario = ?
        ORDER BY id_camino_elegido DESC
        LIMIT 1
        """,
        (id_usuario,),
    ).fetchone()
    conexion.close()
    return dict(fila) if fila else None
