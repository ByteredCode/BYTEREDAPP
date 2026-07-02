import asyncio
import smtplib
import logging
from email.mime.text import MIMEText

from app.core.config import config

logger = logging.getLogger(__name__)

SMTP_TIMEOUT = 15  # segundos maximos para conexion/envio SMTP


def _enviar_correo_sync(destinatario: str, asunto: str, cuerpo: str) -> bool:
    """Funcion sincrona que envia el correo. Se ejecuta en un thread separado
    para no bloquear el event loop de asyncio."""
    if not config.SMTP_HOST or not config.SMTP_PORT:
        logger.warning("SMTP no configurado, correo no enviado")
        return False

    try:
        msg = MIMEText(cuerpo, "plain", "utf-8")
        msg["Subject"] = asunto
        msg["From"] = config.SMTP_USER
        msg["To"] = destinatario

        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            server.ehlo()
            if config.SMTP_USER and config.SMTP_PASSWORD:
                server.starttls()
                server.ehlo()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Correo enviado a {destinatario}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo: {e}")
        return False


async def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    """Wrapper async: ejecuta el envio sincrono en un thread del pool
    para no bloquear el event loop de FastAPI."""
    return await asyncio.to_thread(_enviar_correo_sync, destinatario, asunto, cuerpo)
