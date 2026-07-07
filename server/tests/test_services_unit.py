# Tests unitarios para los servicios (sin BD real, usando mocks de AsyncSession)
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import Result

from app.schemas.ticket import TicketCreate
from app.services.auth_service import iniciar_sesion, registrar_usuario
from app.services.ticket_service import crear_ticket
from tests.lib.mock_db import crear_mock_session


async def test_registrar_usuario_exito():
    # Registrar un usuario con datos válidos debe llamar a session.add, commit y refresh
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    usuario = await registrar_usuario(
        db=mock_session,
        correo="nuevo@test.com",
        contrasena="Test1234",
        nombre="Nuevo",
        codigo_empresa=1,
    )

    assert mock_session.add.called
    assert mock_session.commit.called
    assert mock_session.refresh.called
    assert usuario.correo == "nuevo@test.com"


async def test_registrar_usuario_correo_duplicado():
    # Si el correo ya existe, debe lanzar HTTPException 400
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = MagicMock()
    mock_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await registrar_usuario(
            db=mock_session,
            correo="duplicado@test.com",
            contrasena="Test1234",
            nombre="Duplicado",
            codigo_empresa=1,
        )
    assert exc.value.status_code == 400


async def test_registrar_usuario_contrasena_sin_mayuscula():
    # Validación de seguridad: contraseña sin mayúscula debe ser rechazada
    mock_session = crear_mock_session()

    with pytest.raises(HTTPException) as exc:
        await registrar_usuario(
            db=mock_session,
            correo="test@test.com",
            contrasena="test1234",
            nombre="Test",
            codigo_empresa=1,
        )
    assert exc.value.status_code == 400


async def test_registrar_usuario_contrasena_sin_numero():
    # Validación de seguridad: contraseña sin número debe ser rechazada
    mock_session = crear_mock_session()

    with pytest.raises(HTTPException) as exc:
        await registrar_usuario(
            db=mock_session,
            correo="test@test.com",
            contrasena="Testabcd",
            nombre="Test",
            codigo_empresa=1,
        )
    assert exc.value.status_code == 400


async def test_iniciar_sesion_exito():
    # Login exitoso debe devolver usuario + tokens
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_usuario = MagicMock()
    mock_usuario.codigo_usuario = 1
    mock_usuario.codigo_empresa = 1
    mock_usuario.correo = "test@test.com"
    mock_usuario.contrasena = "hashed"
    mock_result.scalar_one_or_none.return_value = mock_usuario
    mock_session.execute.return_value = mock_result

    with patch("app.services.auth_service.verificar_contrasena", return_value=True):
        resultado = await iniciar_sesion(
            db=mock_session,
            correo="test@test.com",
            contrasena="Test1234",
        )

    assert "usuario" in resultado
    assert "tokens" in resultado
    assert resultado["tokens"]["token_type"] == "bearer"


async def test_iniciar_sesion_fallido():
    # Login con usuario inexistente debe lanzar HTTPException 401
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await iniciar_sesion(
            db=mock_session,
            correo="noexiste@test.com",
            contrasena="Test1234",
        )
    assert exc.value.status_code == 401


async def test_crear_ticket_exito():
    # Crear un ticket debe llamar a session.add y session.commit
    mock_session = crear_mock_session()

    data = TicketCreate(
        nombre_contacto="Test",
        correo_contacto="test@test.com",
        asunto="Problema",
        mensaje="Ayuda",
        codigo_empresa=1,
    )

    ticket = await crear_ticket(
        db=mock_session,
        data=data,
        codigo_usuario=1,
    )

    assert mock_session.add.called
    assert mock_session.commit.called


async def test_crear_ticket_anonimo():
    # Un ticket creado sin usuario autenticado debe tener codigo_usuario=None
    mock_session = crear_mock_session()

    data = TicketCreate(
        nombre_contacto="Anonimo",
        correo_contacto="anonimo@test.com",
        mensaje="Sin cuenta",
        codigo_empresa=1,
    )

    await crear_ticket(
        db=mock_session,
        data=data,
        codigo_usuario=None,
    )

    ticket_creado = mock_session.add.call_args[0][0]
    assert ticket_creado.codigo_usuario is None
