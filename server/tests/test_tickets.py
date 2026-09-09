# Tests de integración para el módulo de tickets (creación, listado, cambio de estado, aislamiento)
import pytest
from httpx import AsyncClient


class TestTickets:

    async def test_crear_ticket_anonimo(self, client: AsyncClient, test_empresa):
        data = {
            "nombre_contacto": "Anonimo",
            "correo_contacto": "anonimo@test.com",
            "asunto": "Problema anonimo",
            "nivel_importancia": "Alta",
            "mensaje": "Esto es un problema grave",
            "codigo_empresa": str(test_empresa.codigo_empresa),
        }
        response = await client.post("/tickets", data=data)
        assert response.status_code == 201
        body = response.json()
        assert body["mensaje"] == "Esto es un problema grave"
        assert body["codigo_usuario"] is None
        assert body["codigo_empresa"] == test_empresa.codigo_empresa
        assert body["estado"] == "Pendiente"

    async def test_crear_ticket_autenticado(self, client: AsyncClient, headers_usuario, test_empresa):
        data = {
            "correo_contacto": "usuario@test.com",
            "asunto": "Ticket autenticado",
            "mensaje": "Soy usuario registrado",
            "codigo_empresa": str(test_empresa.codigo_empresa),
        }
        response = await client.post("/tickets", data=data, headers=headers_usuario)
        assert response.status_code == 201
        body = response.json()
        assert body["asunto"] == "Ticket autenticado"
        assert body["codigo_usuario"] is not None

    async def test_listar_tickets(self, client: AsyncClient, headers_usuario, test_ticket):
        # El listado de tickets debe devolver los tickets de la empresa del usuario autenticado
        response = await client.get("/tickets", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 1

    async def test_obtener_ticket(self, client: AsyncClient, headers_usuario, test_ticket):
        # Obtener un ticket específico por su ID
        response = await client.get(f"/tickets/{test_ticket.id_reporte}", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert data["id_reporte"] == test_ticket.id_reporte
        assert data["mensaje"] == "Ticket de prueba"

    async def test_cambiar_estado_ticket(self, client: AsyncClient, headers_admin, test_ticket):
        # Un admin puede cambiar el estado del ticket (ej. de "Pendiente" a "Leido")
        payload = {"estado": "Leido"}
        response = await client.put(
            f"/tickets/{test_ticket.id_reporte}/estado",
            json=payload,
            headers=headers_admin,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "Leido"

    async def test_ticket_otra_empresa(self, client: AsyncClient, test_session, headers_usuario):
        # Un usuario no debe poder ver tickets de otras empresas (aislamiento multi-tenant)
        from app.models.empresa import Empresa
        from app.models.ticket import Ticket

        otra_empresa = Empresa(nombre="Otra Empresa")
        test_session.add(otra_empresa)
        await test_session.flush()

        ticket_otra = Ticket(
            mensaje="Ticket de otra empresa",
            nivel_importancia="Media",
            codigo_empresa=otra_empresa.codigo_empresa,
            codigo_usuario=None,
            estado="Pendiente",
        )
        test_session.add(ticket_otra)
        await test_session.flush()

        response = await client.get(
            f"/tickets/{ticket_otra.id_reporte}",
            headers=headers_usuario,
        )
        assert response.status_code == 404

    async def test_crear_ticket_sin_mensaje(self, client: AsyncClient, test_empresa):
        # El endpoint debe rechazar tickets sin mensaje (campo requerido)
        data = {
            "correo_contacto": "test@test.com",
            "codigo_empresa": str(test_empresa.codigo_empresa),
        }
        response = await client.post("/tickets", data=data)
        assert response.status_code == 422


class TestEliminarTicket:

    async def test_eliminar_ticket_exito(
        self, client: AsyncClient, headers_superadmin, test_ticket
    ):
        # Un admin_total puede eliminar tickets
        response = await client.delete(
            f"/tickets/{test_ticket.id_reporte}",
            headers=headers_superadmin,
        )
        assert response.status_code == 204

    async def test_eliminar_ticket_no_admin(
        self, client: AsyncClient, headers_usuario, test_ticket
    ):
        # Un usuario normal NO puede eliminar tickets (solo admin_total)
        response = await client.delete(
            f"/tickets/{test_ticket.id_reporte}",
            headers=headers_usuario,
        )
        assert response.status_code == 403


class TestListarEmpresasPublico:

    async def test_listar_empresas_publico(self, client: AsyncClient, test_empresa):
        # El endpoint público de empresas debe devolver la lista sin autenticación
        response = await client.get("/tickets/empresas")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "codigo_empresa" in data[0]
        assert "nombre" in data[0]
