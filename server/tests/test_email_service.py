# Tests unitarios para email_service (mock de Resend)
from unittest.mock import patch, MagicMock

import pytest

from app.services.email_service import _enviar_correo_sync


async def test_enviar_correo_exito():
    # Enviar correo con API key configurada debe llamar a resend.Emails.send
    mock_resend = MagicMock()

    with patch("app.services.email_service.config") as mock_config, \
         patch("app.services.email_service.resend", mock_resend):
        mock_config.RESEND_API_KEY = "re_test_key"
        mock_config.RESEND_FROM = "test@byteredapp.com"

        resultado = _enviar_correo_sync("dest@test.com", "Asunto", "Cuerpo del correo")

    assert resultado is True
    mock_resend.Emails.send.assert_called_once()


async def test_enviar_correo_api_key_no_configurada():
    # Sin API key configurada, el correo no se envía y devuelve False
    with patch("app.services.email_service.config") as mock_config:
        mock_config.RESEND_API_KEY = None

        resultado = _enviar_correo_sync("dest@test.com", "Asunto", "Cuerpo")

    assert resultado is False
