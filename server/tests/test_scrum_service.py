# Tests unitarios para scrum_service (sin BD real, usando mocks de AsyncSession)
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import Result

from app.schemas.tarea import TareaCreate
from app.services.scrum_service import (
    crear_tarea,
    eliminar_tarea,
    listar_sprints,
    listar_tareas,
    mover_tarea,
    obtener_tablero,
)
from tests.lib.mock_db import crear_mock_session


async def test_obtener_tablero_agrupacion_4_columnas():
    # El tablero debe devolver exactamente 4 columnas Kanban
    mock_session = crear_mock_session()

    mock_tarea1 = MagicMock()
    mock_tarea1.columna = "Todo"
    mock_tarea2 = MagicMock()
    mock_tarea2.columna = "Haciendose"
    mock_tarea3 = MagicMock()
    mock_tarea3.columna = "Done"

    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.all.return_value = [mock_tarea1, mock_tarea2, mock_tarea3]
    mock_session.execute.return_value = mock_result

    tablero = await obtener_tablero(mock_session, codigo_empresa=1)

    assert "Todo" in tablero
    assert "Haciendose" in tablero
    assert "En revision" in tablero
    assert "Done" in tablero
    assert len(tablero["Todo"]) == 1
    assert len(tablero["Haciendose"]) == 1
    assert len(tablero["Done"]) == 1
    assert len(tablero["En revision"]) == 0


async def test_obtener_tablero_con_filtro_sprint():
    # Filtrar por sprint debe pasar el filtro a listar_tareas
    mock_session = crear_mock_session()

    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    tablero = await obtener_tablero(mock_session, codigo_empresa=1, codigo_sprint=5)

    assert "Todo" in tablero
    assert "Done" in tablero
    # Verificar que se ejecutó la query con filtro de sprint
    assert mock_session.execute.called


async def test_mover_tarea_exito():
    # Mover una tarea a otra columna y orden debe actualizar los campos
    mock_session = crear_mock_session()

    mock_tarea = MagicMock()
    mock_tarea.codigo_tarea = 1
    mock_tarea.columna = "Todo"
    mock_tarea.orden = 0

    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = mock_tarea
    mock_session.execute.return_value = mock_result

    result = await mover_tarea(mock_session, codigo_tarea=1, columna="Done", orden=3, codigo_empresa=1)

    assert mock_tarea.columna == "Done"
    assert mock_tarea.orden == 3
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


async def test_eliminar_tarea_exito():
    # Eliminar una tarea existente debe llamar a delete y commit
    mock_session = crear_mock_session()

    mock_tarea = MagicMock()
    mock_tarea.codigo_tarea = 1
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = mock_tarea
    mock_session.execute.return_value = mock_result

    await eliminar_tarea(mock_session, 1, 1)

    mock_session.delete.assert_called_once_with(mock_tarea)
    mock_session.commit.assert_called_once()


async def test_eliminar_tarea_404():
    # Eliminar una tarea inexistente debe lanzar HTTPException 404
    mock_session = crear_mock_session()
    mock_result = MagicMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await eliminar_tarea(mock_session, 999, 1)
    assert exc.value.status_code == 404


async def test_listar_tareas_con_paginacion():
    # Listar tareas con parámetros de paginación
    mock_session = crear_mock_session()

    mock_tarea = MagicMock()
    mock_tarea.titulo = "Tarea paginada"
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.all.return_value = [mock_tarea]
    mock_session.execute.return_value = mock_result

    tareas = await listar_tareas(mock_session, codigo_empresa=1, codigo_sprint=None)

    assert len(tareas) == 1
    assert tareas[0].titulo == "Tarea paginada"


async def test_listar_sprints_con_paginacion():
    # Listar sprints con paginación debe devolver tupla (items, total)
    mock_session = crear_mock_session()

    mock_sprint = MagicMock()
    mock_sprint.nombre = "Sprint 1"
    mock_result = MagicMock(spec=Result)
    mock_result.scalars.return_value.all.return_value = [mock_sprint]
    mock_count = MagicMock(spec=Result)
    mock_count.scalar.return_value = 1

    mock_session.execute.side_effect = [mock_count, mock_result]

    items, total = await listar_sprints(mock_session, codigo_empresa=1, skip=0, limit=10)

    assert total == 1
    assert len(items) == 1


async def test_crear_tarea_exito():
    # Crear una tarea nueva con datos válidos
    mock_session = crear_mock_session()

    data = TareaCreate(titulo="Nueva tarea", prioridad="Alta")
    tarea = await crear_tarea(mock_session, data, codigo_empresa=1)

    assert mock_session.add.called
    assert mock_session.commit.called
    assert mock_session.refresh.called
