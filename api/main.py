"""API REST de Climb (Fase 2 — esqueleto).

Expone el data layer / Core sobre HTTP para que el futuro frontend (Next.js, Fase 3)
lo consuma. Corre como servicio propio (uvicorn) junto al backend Flet, compartiendo
el mismo data layer y la misma base PostgreSQL. Flet sigue llamando al Core directo;
esta API NO reemplaza esas llamadas todavía.

Arranque: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
"""

import json
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import clsAgentes, clsCorreo
from core.clsAgentes import orquestar_interaccion_agente, seed_agentes
from data import clsInteraccionDB as db


@asynccontextmanager
async def lifespan(app):
    # Siembra el catalogo de Agentes desde el codigo al arrancar (idempotente).
    try:
        seed_agentes()
        print("[api] catalogo de Agentes sembrado")
    except Exception as exc:  # noqa: BLE001 - no impedir el arranque por el seed
        print(f"[api] seed_agentes fallo: {exc}")
    yield


app = FastAPI(title="Climb API", version="0.1.0", lifespan=lifespan)

# CORS para el futuro frontend Next.js (orígenes configurables por env).
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Liveness simple del servicio."""
    return {"status": "ok", "service": "climb-api", "version": app.version}


# ============================================================================
# Auth (escritura)
# ============================================================================
class RegistroIn(BaseModel):
    nombre: str
    correo: str
    username: str
    clave: str
    idioma: str = "en"


class LoginIn(BaseModel):
    identificador: str   # correo o username
    clave: str


class RecuperarIn(BaseModel):
    correo: str


class RestablecerIn(BaseModel):
    correo: str
    codigo: str
    nueva_clave: str


@app.get("/api/auth/sugerir-username")
def api_sugerir_username(nombre: str):
    """Propone un username libre derivado del nombre."""
    return {"username": db.sugerir_username(nombre)}


@app.get("/api/auth/username-disponible")
def api_username_disponible(username: str):
    """Valida el formato del username y si está libre."""
    return {"valido": db.username_valido(username), "disponible": not db.username_existe(username)}


@app.get("/api/auth/correo-disponible")
def api_correo_disponible(correo: str):
    """Valida el formato del correo y si está libre."""
    return {"valido": db.correo_valido(correo), "disponible": not db.correo_existe(correo)}


@app.post("/api/auth/registro", status_code=201)
def api_registro(payload: RegistroIn):
    """Crea una cuenta. 400 si algo no valida, 409 si username/correo ya existen."""
    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre es obligatorio.")
    if not db.correo_valido(payload.correo):
        raise HTTPException(status_code=400, detail="Correo inválido.")
    if not db.username_valido(payload.username):
        raise HTTPException(status_code=400, detail="Username inválido.")
    if len(payload.clave) < 4:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 4 caracteres.")
    if db.correo_existe(payload.correo):
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado.")
    if db.username_existe(payload.username):
        raise HTTPException(status_code=409, detail="Ese usuario ya está tomado.")
    try:
        datos = db.crear_usuario(nombre, payload.username, payload.correo, payload.clave, payload.idioma)
    except ValueError:
        raise HTTPException(status_code=409, detail="Username o correo ya registrado.")
    return {"id_usuario": datos["id_usuario"], "username": datos["username"]}


@app.post("/api/auth/login")
def api_login(payload: LoginIn):
    """Inicia sesión con correo o username. 401 si las credenciales fallan."""
    id_usuario = db.verificar_credenciales(payload.identificador, payload.clave)
    if id_usuario is None:
        raise HTTPException(status_code=401, detail="Correo/usuario o contraseña incorrectos.")
    return {
        "id_usuario": id_usuario,
        "nombre": db.obtener_nombre_usuario(id_usuario),
        "handle": db.obtener_handle(id_usuario),
        "idioma": db.obtener_idioma(id_usuario),
    }


@app.post("/api/auth/recuperar")
async def api_recuperar(payload: RecuperarIn):
    """Envía un código de recuperación. Respuesta genérica (no revela si la cuenta existe)."""
    if not db.correo_valido(payload.correo):
        raise HTTPException(status_code=400, detail="Correo inválido.")
    datos = db.crear_codigo_reset(payload.correo)
    if datos:
        await clsCorreo.enviar_codigo_reset_async(datos["correo"], datos["nombre"], datos["code"])
    return {"enviado": True}


@app.post("/api/auth/restablecer")
def api_restablecer(payload: RestablecerIn):
    """Canjea el código y cambia la contraseña."""
    if len(payload.nueva_clave) < 4:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 4 caracteres.")
    id_usuario = db.verificar_codigo_reset(payload.correo, payload.codigo)
    if id_usuario is None:
        raise HTTPException(status_code=400, detail="Código incorrecto o vencido.")
    db.cambiar_password(id_usuario, payload.nueva_clave)
    return {"ok": True}


# ============================================================================
# Onboarding (escritura)
# ============================================================================
class PerfilIn(BaseModel):
    apertura_emocional: str = ""
    contexto_profesional: str = ""
    logro_principal: str = ""
    reaccion_presion_visibilidad: str = ""
    intentos_previos: str = ""
    vision_futuro: str = ""
    desahogo_libre: str = ""


@app.post("/api/usuarios/{id_usuario}/perfil", status_code=201)
def api_guardar_perfil(id_usuario: int, payload: PerfilIn):
    """Guarda las respuestas del onboarding para el usuario."""
    if db.obtener_nombre_usuario(id_usuario) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.guardar_perfil(
        id_usuario,
        payload.apertura_emocional,
        payload.contexto_profesional,
        payload.logro_principal,
        payload.reaccion_presion_visibilidad,
        payload.intentos_previos,
        payload.vision_futuro,
        payload.desahogo_libre,
    )
    return {"ok": True}


# ============================================================================
# Generación (LLM) — Scout y Pacer
# ============================================================================
class CaminosIn(BaseModel):
    diagnostico: Optional[dict] = None   # el diagnóstico que devolvió /diagnostico


class CaminoElegidoIn(BaseModel):
    nombre_camino: str
    descripcion_camino: str = ""
    tradeoff_principal: str = ""
    riesgo_principal: str = ""
    tiempo_estimado_semanal: str = ""
    patron_que_rompe: str = ""
    caminos_alternativos: list = []


def _requiere_perfil(id_usuario):
    if db.obtener_perfil(id_usuario) is None:
        raise HTTPException(status_code=400, detail="El usuario aún no completó el onboarding.")


@app.post("/api/usuarios/{id_usuario}/diagnostico")
async def api_diagnostico(id_usuario: int):
    """Corre Scout: genera y persiste el diagnóstico cualitativo. Devuelve el JSON."""
    _requiere_perfil(id_usuario)
    return await clsAgentes.generar_diagnostico_cualitativo(id_usuario)


@app.post("/api/usuarios/{id_usuario}/caminos")
async def api_caminos(id_usuario: int, payload: CaminosIn):
    """Corre Scout: genera los 3 caminos a partir del diagnóstico (o lo regenera)."""
    _requiere_perfil(id_usuario)
    return await clsAgentes.generar_tres_caminos(id_usuario, payload.diagnostico)


@app.post("/api/usuarios/{id_usuario}/camino-elegido", status_code=201)
def api_camino_elegido(id_usuario: int, payload: CaminoElegidoIn):
    """Guarda el camino elegido por el usuario."""
    if db.obtener_nombre_usuario(id_usuario) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.insertar_camino_elegido(
        id_usuario,
        payload.nombre_camino,
        payload.descripcion_camino,
        payload.tradeoff_principal,
        payload.riesgo_principal,
        payload.tiempo_estimado_semanal,
        payload.patron_que_rompe,
        json.dumps(payload.caminos_alternativos, ensure_ascii=False),
    )
    return {"ok": True}


@app.post("/api/usuarios/{id_usuario}/mision")
async def api_mision(id_usuario: int):
    """Corre Pacer: genera y persiste la misión semanal desde el camino elegido."""
    _requiere_perfil(id_usuario)
    return await clsAgentes.generar_mision_pacer(id_usuario)


# --- Pacer: progreso / completar / sugerencias ---
class ProgresoIn(BaseModel):
    progreso: list   # list[bool] alineada con las acciones


class MisionIn(BaseModel):
    mision: dict


@app.patch("/api/misiones/{id_mision}/progreso")
def api_progreso_mision(id_mision: int, payload: ProgresoIn):
    """Actualiza las acciones completadas de una misión."""
    db.guardar_progreso_mision(id_mision, payload.progreso)
    return {"ok": True}


@app.post("/api/misiones/{id_mision}/completar")
def api_completar_mision(id_mision: int):
    """Marca la misión como completada."""
    db.completar_mision(id_mision)
    return {"ok": True}


@app.get("/api/usuarios/{id_usuario}/misiones/sugerencias")
async def api_sugerencias_mision(id_usuario: int):
    """Pacer sugiere 2-3 misiones nuevas (tras completar una)."""
    return {"sugerencias": await clsAgentes.sugerir_misiones_pacer(id_usuario)}


@app.post("/api/usuarios/{id_usuario}/misiones", status_code=201)
def api_aceptar_mision(id_usuario: int, payload: MisionIn):
    """Acepta una misión sugerida (la inserta como activa)."""
    return {"id_mision": db.insertar_mision(id_usuario, payload.mision)}


# ============================================================================
# Archive (chat -> ficha -> timeline)
# ============================================================================
class TurnosIn(BaseModel):
    turns: list = []   # [[speaker, texto], ...]


_ARCHIVE_TRIGGER = "document the win this way"


@app.post("/api/usuarios/{id_usuario}/archive/mensaje")
async def api_archive_mensaje(id_usuario: int, payload: TurnosIn):
    """Responde en la conversación de Archive. Indica si ya se puede generar la ficha."""
    turns = payload.turns
    if turns and turns[-1][0] == "user":
        db.registrar_texto_usuario(id_usuario, "archive", turns[-1][1])
    respuesta = await clsAgentes.responder_archive(turns, id_usuario)
    try:
        await clsAgentes.actualizar_voice_profile_si_toca(id_usuario)
    except Exception:
        pass
    return {"respuesta": respuesta, "ofrecer_ficha": _ARCHIVE_TRIGGER in (respuesta or "").lower()}


@app.post("/api/usuarios/{id_usuario}/archive/ficha", status_code=201)
async def api_archive_ficha(id_usuario: int, payload: TurnosIn):
    """Genera la ficha de logro desde la conversación y la persiste."""
    ficha = await clsAgentes.generar_ficha_logro(payload.turns, id_usuario)
    id_registro = db.insertar_logro_completo(
        id_usuario, ficha["tipo"], ficha["titulo"], ficha["contexto"],
        ficha.get("mi_rol", ""), ficha.get("aprendizaje", ""),
        ficha.get("tags", []), ficha.get("metrics", []), conversacion=payload.turns,
    )
    return {**ficha, "id": id_registro}


@app.get("/api/usuarios/{id_usuario}/archive/timeline")
def api_archive_timeline(id_usuario: int):
    """Stats + logros agrupados por mes para la línea de tiempo de Archive."""
    return {"stats": db.archivo_stats(id_usuario), "meses": db.archivo_agrupado_por_mes(id_usuario)}


@app.get("/api/usuarios/{id_usuario}")
def get_usuario(id_usuario: int):
    """Datos básicos de un usuario (nombre, handle, idioma)."""
    nombre = db.obtener_nombre_usuario(id_usuario)
    if nombre is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id_usuario": id_usuario,
        "nombre": nombre,
        "handle": db.obtener_handle(id_usuario),
        "idioma": db.obtener_idioma(id_usuario),
    }


@app.get("/api/usuarios/{id_usuario}/perfil")
def get_perfil(id_usuario: int):
    """Las 9 respuestas del onboarding (perfil más reciente)."""
    perfil = db.obtener_perfil(id_usuario)
    if perfil is None:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return perfil


@app.get("/api/usuarios/{id_usuario}/mision")
def get_mision(id_usuario: int):
    """Misión activa más reciente del usuario, con su progreso."""
    mision = db.obtener_ultima_mision(id_usuario)
    if mision is None:
        raise HTTPException(status_code=404, detail="Sin misión activa")
    return mision


@app.get("/api/usuarios/{id_usuario}/logros")
def get_logros(id_usuario: int):
    """Logros documentados con Archive (enriquecidos), más recientes primero."""
    return db.obtener_logros_completos(id_usuario)


@app.get("/api/agentes")
def get_agentes():
    """Catálogo de agentes (nombre + descripción)."""
    return db.listar_agentes()


@app.get("/api/agentes/{nombre}")
def get_agente(nombre: str):
    """Configuración completa de un agente (identidad + reglas base)."""
    agente = db.obtener_agente(nombre)
    if agente is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")
    return agente


class InteraccionIn(BaseModel):
    id_usuario: int
    mensaje: str


@app.post("/api/agentes/{nombre}/interactuar")
async def interactuar(nombre: str, payload: InteraccionIn):
    """Interacción conversacional con un agente vía el orquestador único.

    El orquestador arma el prompt desde la config del agente en la BD (identidad
    + reglas) y responde. Cubre los agentes conversacionales.
    """
    try:
        respuesta = await orquestar_interaccion_agente(nombre, payload.id_usuario, payload.mensaje)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"agente": nombre, "respuesta": respuesta}
