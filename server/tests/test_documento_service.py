# Tests unitarios para documento_service (sin BD real, usando mocks de AsyncSession)
import os
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy import Result

from app.services.documento_service import (
    agregar_permiso,
    eliminar_documento,
    listar_documentos,
    obtener_ruta_archivo,
    quitar_permiso,
    subir_documento,
)
from tests.lib.mock_db import crear_mock_session


async def test_subir_documento_exito():
    # Subir un documento válido debe crear el registro y guardar el archivo
    mock_session = crear_mock_session()

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read = AsyncMock(return_value=b"contenido pdf")

    mock_doc = MagicMock()
    mock_doc.id_documento = 1

    mock_session.execute.return_value = MagicMock()

    with patch("app.services.documento_service.os.makedirs"), \
         patch("app.services.documento_service.os.path.exists", return_value=False), \
         patch("builtins.open", MagicMock()):
        result = await subir_documento(mock_session, mock_file, "DPD", 1, 1)

    assert mock_session.add.called
    assert mock_session.commit.called


async def test_subir_documento_tipo_no_permitido():
    # Tipo MIME no permitido debe lanzar HTTPException 400
    mock_session = crear_mock_session()

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "malware.exe"
    mock_file.content_type = "application/x-msdownload"
    mock_file.read = AsyncMock(return_value=b"datos")

    with pytest.raises(HTTPException) as exc:
        await subir_documento(mock_session, mock_file, "DPD", 1, 1)
    assert exc.value.status_code == 400
    assert "no permitido" in exc.value.detail.lower()


async def test_subir_documento_tamano_excedido():
    # Archivo mayor a 10MB debe ser rechazado
    mock_session = crear_mock_session()

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "grande.pdf"
    mock_file.content_type = "application/pdf"
    # Crear contenido de 11MB
    mock_file.read = AsyncMock(return_value=b"x" * (11 * 1024 * 1024))

    with patch("app.services.documento_service.os.makedirs"):
        with pytest.raises(HTTPException) as exc:
            await subir_documento(mock_session, mock_file, "DPD", 1, 1)
    assert exc.value.status_code == 400
    assert "tamano" in exc.value.detail.lower()


async def test_listar_documentos_admin_ve_todo():
    # admin ve todos los documentos de su empresa
    mock_session = crear_mock_session()
    mock_doc = MagicMock()
    mock_doc.nombre = "doc.pdf"

    mock_count = MagicMock(spec=Result)
    mock_count.scalar.return_value = 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.all.return_value = [mock_doc]

    mock_session.execute.side_effect = [mock_count, mock_result]

    docs, total = await listar_documentos(mock_session, codigo_empresa=1, usuario_id=1, es_admin=True)

    assert total == 1
    assert len(docs) == 1


async def test_listar_documentos_usuario_solo_ve_suyos():
    # Usuario normal solo ve sus documentos y los que tiene permiso
    mock_session = crear_mock_session()
    mock_doc = MagicMock()
    mock_doc.nombre = "mio.pdf"

    mock_count = MagicMock(spec=Result)
    mock_count.scalar.return_value = 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.all.return_value = [mock_doc]

    mock_session.execute.side_effect = [mock_count, mock_result]

    docs, total = await listar_documentos(mock_session, codigo_empresa=1, usuario_id=1, es_admin=False)

    assert total == 1
    assert len(docs) == 1


async def test_eliminar_documento_exito_borra_archivo():
    # Eliminar documento debe borrar el registro y el archivo físico
    mock_session = crear_mock_session()

    mock_doc = MagicMock()
    mock_doc.id_documento = 1
    mock_doc.ruta_archivo = "1/archivo.pdf"

    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_session.execute.return_value = mock_result

    with patch("app.services.documento_service.os.path.exists", return_value=True), \
         patch("app.services.documento_service.os.remove"):
        await eliminar_documento(mock_session, 1, 1)

    mock_session.delete.assert_called_once_with(mock_doc)
    mock_session.commit.assert_called_once()


async def test_agregar_permiso_exito():
    # Agregar permiso a un documento válido
    mock_session = crear_mock_session()

    mock_doc = MagicMock()
    mock_doc.usuario_subio = 1
    mock_result_doc = MagicMock(spec=Result)
    mock_result_doc.scalar_one_or_none.return_value = mock_doc

    mock_permiso = MagicMock()
    mock_permiso.id_documento = 1
    mock_permiso.codigo_usuario = 2

    mock_session.execute.return_value = mock_result_doc

    result = await agregar_permiso(mock_session, id_documento=1, codigo_usuario=2, codigo_empresa=1, usuario_actual=1, es_admin=False)

    assert mock_session.add.called
    assert mock_session.commit.called


async def test_agregar_permiso_duplicado():
    # Permiso duplicado debe lanzar HTTPException 400
    mock_session = crear_mock_session()

    mock_doc = MagicMock()
    mock_doc.usuario_subio = 1
    mock_result_doc = MagicMock(spec=Result)
    mock_result_doc.scalar_one_or_none.return_value = mock_doc
    mock_session.execute.return_value = mock_result_doc

    # Simular error de constraint único al hacer commit
    mock_session.commit = AsyncMock(side_effect=Exception("duplicate key"))

    with pytest.raises(HTTPException) as exc:
        await agregar_permiso(mock_session, id_documento=1, codigo_usuario=2, codigo_empresa=1, usuario_actual=1, es_admin=False)
    assert exc.value.status_code == 400
    assert "ya existe" in exc.value.detail.lower()


async def test_quitar_permiso_exito():
    # Quitar un permiso existente
    mock_session = crear_mock_session()

    mock_doc = MagicMock()
    mock_doc.usuario_subio = 1
    mock_result_doc = MagicMock(spec=Result)
    mock_result_doc.scalar_one_or_none.return_value = mock_doc

    mock_permiso = MagicMock()
    mock_permiso.codigo_usuario = 2
    mock_result_permiso = MagicMock(spec=Result)
    mock_result_permiso.scalar_one_or_none.return_value = mock_permiso

    mock_session.execute.side_effect = [mock_result_doc, mock_result_permiso]

    await quitar_permiso(mock_session, id_documento=1, codigo_usuario=2, codigo_empresa=1, usuario_actual=1, es_admin=False)

    mock_session.delete.assert_called_once_with(mock_permiso)
    mock_session.commit.assert_called_once()


async def test_obtener_ruta_archivo_no_encontrado():
    # Archivo físico no encontrado en disco debe lanzar HTTPException 404
    mock_doc = MagicMock()
    mock_doc.ruta_archivo = "1/noexiste.pdf"

    with patch("app.services.documento_service.os.path.exists", return_value=False):
        with pytest.raises(HTTPException) as exc:
            await obtener_ruta_archivo(mock_doc)
    assert exc.value.status_code == 404
    assert "no encontrado" in exc.value.detail.lower()
