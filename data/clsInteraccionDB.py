"""Operaciones CRUD sobre la base de datos de Climb.

Ninguna vista ni el motor de agentes ejecuta SQL directamente: todo pasa por aqui.
"""

import hashlib
import hmac
import json
import os
import random

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
def crear_usuario(nombre, clave):
    """Crea un usuario con handle Nombre#numero y clave hasheada.

    Genera un discriminador de 4 digitos unico para ese nombre. Devuelve un dict
    con id_usuario, discriminador y handle completo (ej. 'Daniel#4821').
    """
    salt_hex, hash_hex = _hash_clave(clave)
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Generar un discriminador unico para este nombre (reintenta ante colision).
    while True:
        discriminador = f"{random.randint(0, 9999):04d}"
        existe = cursor.execute(
            "SELECT 1 FROM Usuarios WHERE nombre = ? AND discriminador = ?",
            (nombre, discriminador),
        ).fetchone()
        if not existe:
            break

    cursor.execute(
        "INSERT INTO Usuarios (nombre, discriminador, password_hash, password_salt) "
        "VALUES (?, ?, ?, ?)",
        (nombre, discriminador, hash_hex, salt_hex),
    )
    id_usuario = cursor.lastrowid
    conexion.commit()
    conexion.close()
    return {
        "id_usuario": id_usuario,
        "discriminador": discriminador,
        "handle": f"{nombre}#{discriminador}",
    }


def verificar_credenciales(nombre, discriminador, clave):
    """Verifica el handle (Nombre#numero) y la clave. Devuelve id_usuario o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT id_usuario, password_hash, password_salt FROM Usuarios "
        "WHERE nombre = ? AND discriminador = ?",
        (nombre, discriminador),
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
    """Devuelve el estado de la mision mas reciente, o None.

    Estructura: {"id_mision", "mision" (dict), "progreso" (list[bool])}.
    """
    conexion = obtener_conexion()
    fila = conexion.execute(
        """
        SELECT id_mision, contenido_json, progreso_json FROM Misiones
        WHERE id_usuario = ?
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
TIPOS_LOGRO = ["Proyecto", "Impacto", "Reconocimiento", "Liderazgo", "Habilidad"]


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


def guardar_progreso_mision(id_mision, progreso):
    """Actualiza la lista de acciones completadas (list[bool]) de una mision."""
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Misiones SET progreso_json = ? WHERE id_mision = ?",
        (json.dumps(progreso), id_mision),
    )
    conexion.commit()
    conexion.close()


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
