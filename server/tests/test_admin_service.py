# Tests unitarios para admin_service (sin BD real, usando mocks de AsyncSession)
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy import Result

from app.schemas.admin import EmpresaCreate, ServicioToggle, UsuarioCreate, UsuarioUpdate
from app.services.admin_service import (
    crear_empresa,
    crear_usuario_admin,
    eliminar_empresa,
    eliminar_usuario,
    listar_servicios,
    obtener_stats,
    toggle_servicio,
    actualizar_usuario,
)
from tests.lib.mock_db import crear_mock_session


async def test_crear_empresa_exito():
    # Crear una empresa con datos válidos debe llamar a add, flush, commit y refresh
    mock_session = crear_mock_session()
    # Mock para que obtener_empresa devuelva None (empresa no existe previamente)
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    data = EmpresaCreate(nombre="Nueva Empresa", web="https://nueva.com")
    empresa = await crear_empresa(mock_session, data)

    assert mock_session.add.called
    assert mock_session.commit.called
    # Se deben haber añadido 4 servicios por defecto (scrum, tickets, documentacion, redireccion)
    assert mock_session.add.call_count >= 5  # 1 empresa + 4 servicios


async def test_crear_empresa_nombre_vacio():
    # Empresa con nombre vacío: el servicio lo permite (validación en BD/endpoint)
    # pero verificamos que se crea correctamente con nombre vacío
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    data = EmpresaCreate(nombre="", web=None)
    empresa = await crear_empresa(mock_session, data)

    # El servicio no valida nombre vacío; eso es responsabilidad del endpoint/schema
    assert mock_session.add.called
    assert mock_session.commit.called


async def test_eliminar_empresa_exito():
    # Eliminar una empresa existente debe llamar a delete y commit
    mock_session = crear_mock_session()

    mock_empresa = MagicMock()
    mock_empresa.codigo_empresa = 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = mock_empresa
    mock_session.execute.return_value = mock_result

    await eliminar_empresa(mock_session, 1)

    mock_session.delete.assert_called_once_with(mock_empresa)
    mock_session.commit.assert_called_once()


async def test_eliminar_empresa_404():
    # Eliminar una empresa inexistente debe lanzar HTTPException 404
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await eliminar_empresa(mock_session, 99999)
    assert exc.value.status_code == 404


async def test_crear_usuario_admin_exito():
    # Crear usuario con datos válidos debe hashear la contraseña y persistir
    mock_session = crear_mock_session()

    # Mock para verificar correo duplicado: devuelve None (no existe)
    mock_resultcorreo = MagicMock(spec=Result)
    mock_resultcorreo.scalar_one_or_none.return_value = None

    # Mock para verificar que la empresa existe
    mock_resultempresa = MagicMock(spec=Result)
    mock_resultempresa.scalar_one_or_none.return_value = MagicMock()

    mock_session.execute.side_effect = [mock_resultcorreo, mock_resultempresa]

    data = UsuarioCreate(
        correo="nuevo@test.com",
        contrasena="Password1",
        nombre="Nuevo",
        codigo_empresa=1,
        rol="usuario",
    )
    usuario = await crear_usuario_admin(mock_session, data)

    assert mock_session.add.called
    assert mock_session.commit.called
    assert usuario.correo == "nuevo@test.com"


async def test_crear_usuario_admin_contrasena_sin_mayuscula():
    # Contraseña sin mayúscula debe ser rechazada
    mock_session = crear_mock_session()

    data = UsuarioCreate(
        correo="test@test.com",
        contrasena="password1",
        nombre="Test",
        codigo_empresa=1,
        rol="usuario",
    )
    with pytest.raises(HTTPException) as exc:
        await crear_usuario_admin(mock_session, data)
    assert exc.value.status_code == 400
    assert "mayuscula" in exc.value.detail.lower()


async def test_crear_usuario_admin_contrasena_sin_numero():
    # Contraseña sin número debe ser rechazada
    mock_session = crear_mock_session()

    data = UsuarioCreate(
        correo="test@test.com",
        contrasena="Password",
        nombre="Test",
        codigo_empresa=1,
        rol="usuario",
    )
    with pytest.raises(HTTPException) as exc:
        await crear_usuario_admin(mock_session, data)
    assert exc.value.status_code == 400
    assert "numero" in exc.value.detail.lower()


async def test_crear_usuario_admin_correo_duplicado():
    # Si el correo ya existe, debe lanzar HTTPException 400
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = MagicMock()  # Usuario existente
    mock_session.execute.return_value = mock_result

    data = UsuarioCreate(
        correo="duplicado@test.com",
        contrasena="Password1",
        nombre="Duplicado",
        codigo_empresa=1,
        rol="usuario",
    )
    with pytest.raises(HTTPException) as exc:
        await crear_usuario_admin(mock_session, data)
    assert exc.value.status_code == 400
    assert "correo ya esta registrado" in exc.value.detail.lower()


async def test_actualizar_usuario_exito():
    # Actualizar nombre de usuario existente
    mock_session = crear_mock_session()
    mock_usuario = MagicMock()
    mock_usuario.codigo_usuario = 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = mock_usuario
    mock_session.execute.return_value = mock_result

    data = UsuarioUpdate(nombre="Nuevo Nombre")
    result = await actualizar_usuario(mock_session, 1, data)

    assert mock_session.commit.called
    assert mock_session.refresh.called
    assert mock_usuario.nombre == "Nuevo Nombre"


async def test_actualizar_usuario_con_cambio_contrasena():
    # Cambiar contraseña debe hashearla antes de persistir
    mock_session = crear_mock_session()
    mock_usuario = MagicMock()
    mock_usuario.codigo_usuario = 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = mock_usuario
    mock_session.execute.return_value = mock_result

    data = UsuarioUpdate(contrasena="NewPass123")
    result = await actualizar_usuario(mock_session, 1, data)

    assert mock_session.commit.called
    # La contraseña no debe guardarse en texto plano
    assert mock_usuario.contrasena != "NewPass123"


async def test_actualizar_usuario_contrasena_invalida():
    # Contraseña inválida (sin mayúscula ni número) debe ser rechazada
    mock_session = crear_mock_session()
    mock_usuario = MagicMock()
    mock_usuario.codigo_usuario = 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = mock_usuario
    mock_session.execute.return_value = mock_result

    data = UsuarioUpdate(contrasena="invalida")
    with pytest.raises(HTTPException) as exc:
        await actualizar_usuario(mock_session, 1, data)
    assert exc.value.status_code == 400


async def test_toggle_servicio_crear_nuevo():
    # Toggle de un servicio que no existe debe crearlo (upsert)
    mock_session = crear_mock_session()

    # Primera llamada: obtener empresa
    mock_empresa = MagicMock()
    mock_empresa.codigo_empresa = 1
    mock_result_empresa = MagicMock(spec=Result)
    mock_result_empresa.scalar_one_or_none.return_value = mock_empresa

    # Segunda llamada: buscar servicio existente
    mock_result_svc = MagicMock(spec=Result)
    mock_result_svc.scalar_one_or_none.return_value = None  # No existe

    mock_session.execute.side_effect = [mock_result_empresa, mock_result_svc]

    data = ServicioToggle(servicio="nuevo_modulo", activo=True)
    result = await toggle_servicio(mock_session, 1, data)

    assert mock_session.add.called
    assert mock_session.commit.called
    assert result.servicio == "nuevo_modulo"
    assert result.activo is True


async def test_toggle_servicio_actualizar_existente():
    # Toggle de un servicio existente debe actualizar su estado
    mock_session = crear_mock_session()

    mock_empresa = MagicMock()
    mock_empresa.codigo_empresa = 1
    mock_result_empresa = MagicMock(spec=Result)
    mock_result_empresa.scalar_one_or_none.return_value = mock_empresa

    mock_svc = MagicMock()
    mock_svc.activo = True
    mock_svc.servicio = "scrum"
    mock_result_svc = MagicMock(spec=Result)
    mock_result_svc.scalar_one_or_none.return_value = mock_svc

    mock_session.execute.side_effect = [mock_result_empresa, mock_result_svc]

    data = ServicioToggle(servicio="scrum", activo=False)
    result = await toggle_servicio(mock_session, 1, data)

    assert result.activo is False
    mock_session.commit.assert_called_once()


async def test_listar_servicios():
    # Listar servicios de una empresa debe devolver la lista
    mock_session = crear_mock_session()
    mock_svc1 = MagicMock()
    mock_svc1.servicio = "scrum"
    mock_svc2 = MagicMock()
    mock_svc2.servicio = "tickets"
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.all.return_value = [mock_svc1, mock_svc2]
    mock_session.execute.return_value = mock_result

    servicios = await listar_servicios(mock_session, 1)

    assert len(servicios) == 2
    assert servicios[0].servicio == "scrum"


async def test_obtener_stats_basico():
    # Obtener stats debe devolver un AdminStatsResponse con todos los campos
    mock_session = crear_mock_session()

    # Mocks para cada query de stats
    mock_count_empresa = MagicMock(spec=Result)
    mock_count_empresa.scalar.return_value = 5

    mock_rol = MagicMock()
    mock_rol.rol = "usuario"
    mock_rol.total = 10
    mock_result_rol = MagicMock(spec=Result)
    mock_result_rol.__iter__ = lambda self: iter([mock_rol])

    mock_estado = MagicMock()
    mock_estado.estado = "Pendiente"
    mock_estado.total = 3
    mock_result_estado = MagicMock(spec=Result)
    mock_result_estado.__iter__ = lambda self: iter([mock_estado])

    mock_count_noweb = MagicMock(spec=Result)
    mock_count_noweb.scalar.return_value = 2

    mock_columna = MagicMock()
    mock_columna.columna = "Todo"
    mock_columna.total = 7
    mock_result_col = MagicMock(spec=Result)
    mock_result_col.__iter__ = lambda self: iter([mock_columna])

    mock_count_tickets = MagicMock(spec=Result)
    mock_count_tickets.scalar.return_value = 4

    mock_session.execute.side_effect = [
        mock_count_empresa,
        mock_result_rol,
        mock_result_estado,
        mock_count_noweb,
        mock_result_col,
        mock_count_tickets,
    ]

    stats = await obtener_stats(mock_session)

    assert stats.total_empresas == 5
    assert stats.total_usuarios == 10
    assert len(stats.usuarios_por_rol) == 1
    assert len(stats.tickets_por_estado) == 1
    assert stats.empresas_sin_web == 2
    assert stats.tickets_ultimo_mes == 4
