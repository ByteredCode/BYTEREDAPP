import pytest
from httpx import AsyncClient


class TestTickets:

    async def test_crear_ticket_anonimo(self, client: AsyncClient, test_empresa):
        payload = {
            "nombre_contacto": "Anonimo",
            "correo_contacto": "anonimo@test.com",
            "asunto": "Problema anonimo",
            "nivel_importancia": "Alta",
            "mensaje": "Esto es un problema grave",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        response = await client.post("/tickets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["mensaje"] == "Esto es un problema grave"
        assert data["codigo_usuario"] is None
        assert data["codigo_empresa"] == test_empresa.codigo_empresa
        assert data["estado"] == "Pendiente"

    async def test_crear_ticket_autenticado(self, client: AsyncClient, headers_usuario, test_empresa):
        payload = {
            "asunto": "Ticket autenticado",
            "mensaje": "Soy usuario registrado",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        response = await client.post("/tickets", json=payload, headers=headers_usuario)
        assert response.status_code == 201
        data = response.json()
        assert data["asunto"] == "Ticket autenticado"
        assert data["codigo_usuario"] is not None

    async def test_listar_tickets(self, client: AsyncClient, headers_usuario, test_ticket):
        response = await client.get("/tickets", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_obtener_ticket(self, client: AsyncClient, headers_usuario, test_ticket):
        response = await client.get(f"/tickets/{test_ticket.id_reporte}", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert data["id_reporte"] == test_ticket.id_reporte
        assert data["mensaje"] == "Ticket de prueba"

    async def test_cambiar_estado_ticket(self, client: AsyncClient, headers_admin, test_ticket):
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
        payload = {
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        response = await client.post("/tickets", json=payload)
        assert response.status_code == 422
