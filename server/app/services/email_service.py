import asyncio
import smtplib
import logging
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from app.core.config import config

logger = logging.getLogger(__name__)

SMTP_TIMEOUT = 15


def _enviar_correo_sync(destinatario: str, asunto: str, cuerpo: str) -> bool:
    logger.info(f"SMTP config: host={config.SMTP_HOST!r} port={config.SMTP_PORT!r} user={config.SMTP_USER!r} pass_len={len(config.SMTP_PASSWORD)} tickets_email={config.TICKETS_EMAIL!r}")

    if not config.SMTP_HOST or not config.SMTP_PORT:
        logger.warning("SMTP no configurado, correo no enviado")
        return False

    msg = MIMEText(cuerpo, "plain", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = config.SMTP_USER
    msg["To"] = destinatario

    # Intento 1: SSL directo (puerto 465) — funciona mejor desde IPs de cloud
    try:
        with SMTP_SSL(config.SMTP_HOST, 465, timeout=SMTP_TIMEOUT) as server:
            server.ehlo()
            if config.SMTP_USER and config.SMTP_PASSWORD:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Correo enviado (SSL/465) a {destinatario}")
        return True
    except Exception as e_ssl:
        logger.warning(f"SSL/465 fallo ({e_ssl}), intentando STARTTLS/{config.SMTP_PORT}")

    # Intento 2: STARTTLS (puerto configurado, normalmente 587)
    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            server.ehlo()
            if config.SMTP_USER and config.SMTP_PASSWORD:
                server.starttls()
                server.ehlo()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Correo enviado (STARTTLS/{config.SMTP_PORT}) a {destinatario}")
        return True
    except Exception as e_stls:
        logger.error(f"STARTTLS/{config.SMTP_PORT} fallo ({e_stls}). No se pudo enviar correo a {destinatario}")
        return False


async def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    return await asyncio.to_thread(_enviar_correo_sync, destinatario, asunto, cuerpo)
