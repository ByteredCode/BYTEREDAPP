import smtplib
import logging
from email.mime.text import MIMEText

from app.core.config import config

logger = logging.getLogger(__name__)


async def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    # Si SMTP no esta configurado, fallo silencioso (no rompe el flujo)
    if not config.SMTP_HOST or not config.SMTP_PORT:
        logger.warning("SMTP no configurado, correo no enviado")
        return False

    try:
        msg = MIMEText(cuerpo, "plain", "utf-8")
        msg["Subject"] = asunto
        msg["From"] = config.SMTP_USER
        msg["To"] = destinatario

        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            if config.SMTP_USER and config.SMTP_PASSWORD:
                server.starttls()  # Cifrar conexion antes de autenticar
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Correo enviado a {destinatario}")
        return True
    except Exception as e:
        # Nunca propagar excepcion de email al usuario
        logger.error(f"Error al enviar correo: {e}")
        return False
