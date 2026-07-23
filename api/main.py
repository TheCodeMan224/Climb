"""API REST de Climb (Fase 2 — esqueleto).

Expone el data layer / Core sobre HTTP para que el futuro frontend (Next.js, Fase 3)
lo consuma. Corre como servicio propio (uvicorn) junto al backend Flet, compartiendo
el mismo data layer y la misma base PostgreSQL. Flet sigue llamando al Core directo;
esta API NO reemplaza esas llamadas todavía.

Arranque: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data import clsInteraccionDB as db

app = FastAPI(title="Climb API", version="0.1.0")

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
