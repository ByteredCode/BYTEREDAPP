# Tests de integración para el módulo de empresa (/empresa/mi-empresa)
import pytest
from httpx import AsyncClient


class TestMiEmpresa:

    async def test_obtener_mi_empresa(self, client: AsyncClient, headers_admin, test_empresa):
        # Un admin autenticado puede obtener los datos de su empresa
        resp = await client.get("/empresa/mi-empresa", headers=headers_admin)
        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "Empresa Test"
        assert "codigo_empresa" in data

    async def test_obtener_mi_empresa_sin_auth(self, client: AsyncClient):
        # Sin token JWT, debe devolver 401
        resp = await client.get("/empresa/mi-empresa")
        assert resp.status_code == 401

    async def test_actualizar_mi_empresa(self, client: AsyncClient, headers_admin):
        # Un admin de empresa puede modificar el nombre y la web
        resp = await client.patch(
            "/empresa/mi-empresa",
            json={"nombre": "Nuevo Nombre", "web": "https://nueva-web.com"},
            headers=headers_admin,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "Nuevo Nombre"
        assert data["web"] == "https://nueva-web.com"

    async def test_actualizar_solo_nombre(self, client: AsyncClient, headers_admin):
        # Enviar solo un campo (PATCH) no debe afectar los demÃ¡s
        resp = await client.patch(
            "/empresa/mi-empresa",
            json={"nombre": "Solo Nombre"},
            headers=headers_admin,
        )
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Solo Nombre"

    async def test_usuario_normal_no_puede_actualizar(self, client: AsyncClient, headers_usuario):
        # Un usuario con rol 'usuario' no tiene permisos para modificar la empresa (403)
        resp = await client.patch(
            "/empresa/mi-empresa",
            json={"nombre": "Hack"},
            headers=headers_usuario,
        )
        assert resp.status_code == 403
