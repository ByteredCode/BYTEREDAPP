import logging

import resend

from app.core.config import config

logger = logging.getLogger(__name__)

if config.RESEND_API_KEY:
    resend.api_key = config.RESEND_API_KEY


async def enviar_correo_async(destinatario: str, asunto: str, cuerpo: str) -> bool:
    if not config.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY no configurada, correo no enviado")
        return False

    try:
        await resend.Emails.send_async({
            "from": config.RESEND_FROM,
            "to": [destinatario],
            "subject": asunto,
            "text": cuerpo,
        })
        logger.info(f"Correo enviado via Resend a {destinatario}")
        return True
    except Exception as e:
        logger.error(f"Error enviando correo via Resend: {e}")
        return False
