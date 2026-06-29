import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.empresa import Empresa
from app.models.tarea import Tarea


class TestTareas:

    async def test_crear_tarea(
        self, client: AsyncClient, headers_usuario
    ):
        payload = {
            "titulo": "Nueva tarea",
            "prioridad": "Alta",
        }
        response = await client.post("/scrum/tareas", json=payload, headers=headers_usuario)
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == "Nueva tarea"
        assert data["prioridad"] == "Alta"
        assert data["columna"] == "Todo"

    async def test_listar_tareas(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        response = await client.get("/scrum/tareas", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_obtener_tarea(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        response = await client.get(
            f"/scrum/tareas/{test_tarea.codigo_tarea}",
            headers=headers_usuario,
        )
        assert response.status_code == 200
        assert response.json()["titulo"] == "Tarea test"

    async def test_actualizar_tarea(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        payload = {"titulo": "Tarea actualizada"}
        response = await client.put(
            f"/scrum/tareas/{test_tarea.codigo_tarea}",
            json=payload,
            headers=headers_usuario,
        )
        assert response.status_code == 200
        assert response.json()["titulo"] == "Tarea actualizada"

    async def test_mover_tarea(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        payload = {"columna": "Done", "orden": 1}
        response = await client.put(
            f"/scrum/tareas/{test_tarea.codigo_tarea}/mover",
            json=payload,
            headers=headers_usuario,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["columna"] == "Done"
        assert data["orden"] == 1

    async def test_eliminar_tarea(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        response = await client.delete(
            f"/scrum/tareas/{test_tarea.codigo_tarea}",
            headers=headers_usuario,
        )
        assert response.status_code == 204

    async def test_tarea_fuera_del_tenant(
        self,
        client: AsyncClient,
        headers_usuario,
        test_session: AsyncSession,
    ):
        otra_empresa = Empresa(nombre="Otra Empresa")
        test_session.add(otra_empresa)
        await test_session.flush()

        tarea_otra = Tarea(
            titulo="Tarea de otra empresa",
            prioridad="Media",
            columna="Todo",
            codigo_empresa=otra_empresa.codigo_empresa,
        )
        test_session.add(tarea_otra)
        await test_session.flush()

        response = await client.get(
            f"/scrum/tareas/{tarea_otra.codigo_tarea}",
            headers=headers_usuario,
        )
        assert response.status_code == 404


class TestTablero:

    async def test_obtener_tablero(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        response = await client.get("/scrum/tablero", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert "Todo" in data
        assert "Haciendose" in data
        assert "En revision" in data
        assert "Done" in data
        assert len(data["Todo"]) >= 1

    async def test_tablero_filtrado_por_sprint(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        response = await client.get(
            "/scrum/tablero",
            params={"codigo_sprint": test_tarea.codigo_sprint},
            headers=headers_usuario,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Todo" in data


class TestSprints:

    async def test_crear_sprint(
        self, client: AsyncClient, headers_usuario
    ):
        payload = {
            "nombre": "Sprint Nuevo",
            "objetivo": "Objetivo del sprint",
        }
        response = await client.post("/scrum/sprints", json=payload, headers=headers_usuario)
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Sprint Nuevo"
        assert data["objetivo"] == "Objetivo del sprint"
        assert data["estado"] == "Planificado"

    async def test_listar_sprints(
        self, client: AsyncClient, headers_usuario, test_sprint
    ):
        response = await client.get("/scrum/sprints", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_actualizar_sprint(
        self, client: AsyncClient, headers_usuario, test_sprint
    ):
        payload = {"estado": "Activo"}
        response = await client.put(
            f"/scrum/sprints/{test_sprint.codigo_sprint}",
            json=payload,
            headers=headers_usuario,
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "Activo"

    async def test_eliminar_sprint(
        self, client: AsyncClient, headers_usuario, test_sprint
    ):
        response = await client.delete(
            f"/scrum/sprints/{test_sprint.codigo_sprint}",
            headers=headers_usuario,
        )
        assert response.status_code == 204
