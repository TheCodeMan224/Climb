"""Operaciones CRUD sobre la base de datos de Climb.

Ninguna vista ni el motor de agentes ejecuta SQL directamente: todo pasa por aqui.
"""

import hashlib
import hmac
import json
import os
import random
from datetime import datetime

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


def obtener_handle(id_usuario):
    """Devuelve el handle del usuario ('Nombre#numero'), o solo el nombre, o None."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT nombre, discriminador FROM Usuarios WHERE id_usuario = ?", (id_usuario,)
    ).fetchone()
    conexion.close()
    if not fila:
        return None
    if fila["discriminador"]:
        return f"{fila['nombre']}#{fila['discriminador']}"
    return fila["nombre"]


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
    """Marca un patrón existente como observing con su reframe."""
    conexion = obtener_conexion()
    conexion.execute(
        "UPDATE Mirror_Patrones SET status='observing', reframe_json=?, last_observed=CURRENT_TIMESTAMP WHERE idPatron=?",
        (reframe_json, id_patron),
    )
    conexion.commit()
    conexion.close()


def obtener_patrones_mirror(id_usuario):
    """Devuelve todas las filas de patrones de Mirror del usuario como dicts."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        """
        SELECT idPatron, quote, source, status, scout_ref, reframe_json, detected_at, last_observed
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


# --- Modelo enriquecido para Archive (3 pantallas) -------------------------
# Tipos del archivo de referencia de Archive.
LOGRO_TYPES = [
    "Deal cerrado", "Proyecto", "Certificación", "Aprendizaje",
    "Activación", "Liderazgo", "Presentación", "Otro",
]

_MESES_CORTO = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
_MESES_LARGO = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


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
        "fecha_corta": f"{fecha.day:02d} {_MESES_CORTO[fecha.month - 1]}",
        "mes_anio": f"{_MESES_LARGO[fecha.month - 1]} {fecha.year}",
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
