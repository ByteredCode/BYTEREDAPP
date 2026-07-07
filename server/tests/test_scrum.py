# Tests de integración para el módulo Scrum (tareas, tablero kanban, sprints)
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.empresa import Empresa
from app.models.empresa_servicio import EmpresaServicio
from app.models.tarea import Tarea


class TestTareas:

    async def test_crear_tarea(
        self, client: AsyncClient, headers_usuario
    ):
        # Una tarea nueva se crea con columna "Todo" por defecto
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
        # El listado de tareas debe incluir las tareas existentes del usuario
        response = await client.get("/scrum/tareas", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_obtener_tarea(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        # Obtener una tarea por su ID debe devolver sus datos completos
        response = await client.get(
            f"/scrum/tareas/{test_tarea.codigo_tarea}",
            headers=headers_usuario,
        )
        assert response.status_code == 200
        assert response.json()["titulo"] == "Tarea test"

    async def test_actualizar_tarea(
        self, client: AsyncClient, headers_usuario, test_tarea
    ):
        # PUT debe actualizar los campos de la tarea existente
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
        # Mover una tarea a otra columna (drag & drop) debe actualizar columna y orden
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
        # Eliminar una tarea debe devolver 204 sin contenido
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
        # Un usuario no debe poder acceder a tareas de otra empresa (aislamiento multi-tenant)
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
        # El tablero kanban debe devolver las 4 columnas con sus tareas agrupadas
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
        # El tablero puede filtrarse por sprint para ver solo tareas de ese sprint
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
        # Un sprint nuevo se crea con estado "Planificado" por defecto
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
        # El listado debe incluir los sprints existentes
        response = await client.get("/scrum/sprints", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1

    async def test_actualizar_sprint(
        self, client: AsyncClient, headers_usuario, test_sprint
    ):
        # Actualizar el estado de un sprint (ej. a "Activo")
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
        # Eliminar un sprint debe devolver 204
        response = await client.delete(
            f"/scrum/sprints/{test_sprint.codigo_sprint}",
            headers=headers_usuario,
        )
        assert response.status_code == 204


class TestFeatureFlags:

    async def test_servicio_desactivado_bloquea_acceso(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        # Desactivar el servicio scrum y verificar que se bloquea el acceso
        from sqlalchemy import update
        await test_session.execute(
            update(EmpresaServicio)
            .where(
                EmpresaServicio.codigo_empresa == test_empresa.codigo_empresa,
                EmpresaServicio.servicio == "scrum",
            )
            .values(activo=False)
        )
        await test_session.flush()

        response = await client.get("/scrum/tablero", headers=headers_usuario)
        assert response.status_code == 403
        assert "no esta activo" in response.json()["detail"].lower()

    async def test_admin_total_no_bloqueado_por_servicio(
        self, client: AsyncClient, headers_superadmin, test_session, test_empresa
    ):
        # admin_total siempre puede acceder, incluso si el servicio esta desactivado
        from sqlalchemy import update
        await test_session.execute(
            update(EmpresaServicio)
            .where(
                EmpresaServicio.codigo_empresa == test_empresa.codigo_empresa,
                EmpresaServicio.servicio == "scrum",
            )
            .values(activo=False)
        )
        await test_session.flush()

        response = await client.get("/scrum/tablero", headers=headers_superadmin)
        assert response.status_code == 200
