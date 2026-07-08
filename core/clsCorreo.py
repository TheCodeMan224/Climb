"""Envío de correo para Climb (SMTP, p. ej. Gmail con App Password).

Aislado a propósito: cualquier función que necesite mandar correo pasa por aquí.
Config por variables de entorno (.env / env vars de Render):

    SMTP_USER           usuario de la cuenta (ej. climb.app@gmail.com)
    SMTP_APP_PASSWORD   App Password de 16 caracteres (NO la clave normal)
    SMTP_FROM           remitente visible (opcional; por defecto = SMTP_USER)
    SMTP_HOST           por defecto smtp.gmail.com
    SMTP_PORT           por defecto 465 (SSL). Usa 587 para STARTTLS.

Si no hay credenciales configuradas, cae a modo desarrollo: imprime el correo en
consola en vez de enviarlo. Así la app y la demo funcionan sin red.
"""

import asyncio
import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def _config():
    """Devuelve la config SMTP si está completa, o None (modo consola)."""
    usuario = os.getenv("SMTP_USER")
    clave = os.getenv("SMTP_APP_PASSWORD")
    if not (usuario and clave):
        return None
    return {
        "usuario": usuario,
        "clave": clave,
        "remitente": os.getenv("SMTP_FROM") or usuario,
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "puerto": int(os.getenv("SMTP_PORT", "465")),
    }


def enviar_correo(destino, asunto, cuerpo):
    """Envía un correo de texto plano. Devuelve True si salió (o se imprimió en dev).

    Nunca lanza: ante un fallo de SMTP devuelve False para que el flujo que llama
    siga mostrando el mismo mensaje genérico al usuario.
    """
    cfg = _config()

    # Modo desarrollo: sin credenciales, se imprime en consola.
    if cfg is None:
        print(
            "\n===== [clsCorreo] MODO DEV (sin SMTP configurado) =====\n"
            f"Para:    {destino}\n"
            f"Asunto:  {asunto}\n"
            f"---\n{cuerpo}\n"
            "=======================================================\n"
        )
        return True

    mensaje = EmailMessage()
    mensaje["From"] = cfg["remitente"]
    mensaje["To"] = destino
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)

    try:
        if cfg["puerto"] == 465:
            contexto = ssl.create_default_context()
            with smtplib.SMTP_SSL(cfg["host"], cfg["puerto"], context=contexto, timeout=20) as servidor:
                servidor.login(cfg["usuario"], cfg["clave"])
                servidor.send_message(mensaje)
        else:
            with smtplib.SMTP(cfg["host"], cfg["puerto"], timeout=20) as servidor:
                servidor.starttls(context=ssl.create_default_context())
                servidor.login(cfg["usuario"], cfg["clave"])
                servidor.send_message(mensaje)
        return True
    except Exception as exc:  # noqa: BLE001 - no romper el flujo por un fallo de envío
        print(f"[clsCorreo] Error al enviar a {destino}: {exc}")
        return False


def enviar_codigo_reset(destino, nombre, code):
    """Compone y envía el correo con el código de recuperación de contraseña."""
    saludo = f"Hi {nombre}," if nombre else "Hi,"
    asunto = "Your Climb password reset code"
    cuerpo = (
        f"{saludo}\n\n"
        f"Your password reset code is:\n\n"
        f"    {code}\n\n"
        "Enter it in the app to set a new password. It expires in 20 minutes.\n"
        "If you didn't request this, you can ignore this email.\n\n"
        "— Climb"
    )
    return enviar_correo(destino, asunto, cuerpo)


async def enviar_codigo_reset_async(destino, nombre, code):
    """Versión no bloqueante: corre el envío SMTP en un hilo aparte."""
    return await asyncio.to_thread(enviar_codigo_reset, destino, nombre, code)
