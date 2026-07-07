import asyncio
import logging
from functools import partial

import resend

from app.core.config import config

logger = logging.getLogger(__name__)

if config.RESEND_API_KEY:
    resend.api_key = config.RESEND_API_KEY


def _enviar_correo_sync(destinatario: str, asunto: str, cuerpo: str) -> bool:
    if not config.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY no configurada, correo no enviado")
        return False

    try:
        resend.Emails.send({
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


async def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_enviar_correo_sync, destinatario, asunto, cuerpo))
