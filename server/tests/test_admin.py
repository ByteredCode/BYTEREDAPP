# Tests de integración para los endpoints de administración (CRUD empresas, usuarios, servicios)
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_contrasena
from app.models.empresa import Empresa
from app.models.empresa_servicio import EmpresaServicio
from app.models.usuario import Usuario


class TestAdminEmpresas:

    async def test_listar_empresas_como_superadmin(
        self, client: AsyncClient, headers_superadmin
    ):
        # El superadmin (admin_total) debe poder ver todas las empresas del sistema
        response = await client.get("/admin/empresas", headers=headers_superadmin)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data and "total" in data
        assert isinstance(data["items"], list)

    async def test_listar_empresas_como_admin_empresa(
        self, client: AsyncClient, headers_admin
    ):
        # Un admin_empresa NO debe poder listar todas las empresas (solo ve la suya)
        response = await client.get("/admin/empresas", headers=headers_admin)
        assert response.status_code == 403

    async def test_crear_empresa(
        self, client: AsyncClient, headers_superadmin
    ):
        # Creación básica de una empresa; el superadmin debería poder hacerlo
        payload = {"nombre": "Nueva Empresa", "web": "https://nueva.com"}
        response = await client.post("/admin/empresas", json=payload, headers=headers_superadmin)
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Nueva Empresa"
        assert data["web"] == "https://nueva.com"

    async def test_obtener_empresa(
        self, client: AsyncClient, headers_superadmin, test_empresa
    ):
        # Obtener una empresa por su ID (codigo_empresa)
        response = await client.get(
            f"/admin/empresas/{test_empresa.codigo_empresa}",
            headers=headers_superadmin,
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Empresa Test"

    async def test_actualizar_empresa(
        self, client: AsyncClient, headers_superadmin, test_empresa
    ):
        # PUT debe actualizar los campos existentes de la empresa
        payload = {"nombre": "Empresa Actualizada"}
        response = await client.put(
            f"/admin/empresas/{test_empresa.codigo_empresa}",
            json=payload,
            headers=headers_superadmin,
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Empresa Actualizada"


class TestAdminUsuarios:

    async def test_listar_usuarios_superadmin(
        self,
        client: AsyncClient,
        headers_superadmin,
        test_usuario,
        test_admin,
        test_superadmin,
    ):
        # El superadmin debe listar TODOS los usuarios del sistema, sin filtro de empresa
        response = await client.get("/admin/usuarios", headers=headers_superadmin)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data and "total" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= 3

    async def test_listar_usuarios_admin_empresa(
        self,
        client: AsyncClient,
        headers_admin,
        test_session: AsyncSession,
        test_admin,
        test_usuario,
    ):
        # El admin_empresa solo debe ver usuarios de su propia empresa (aislamiento multi-tenant)
        otra_empresa = Empresa(nombre="Otra Empresa")
        test_session.add(otra_empresa)
        await test_session.flush()

        otro_usuario = Usuario(
            correo="otro@test.com",
            contrasena=hash_contrasena("Otro1234"),
            nombre="Otro Usuario",
            rol="usuario",
            codigo_empresa=otra_empresa.codigo_empresa,
        )
        test_session.add(otro_usuario)
        await test_session.flush()

        response = await client.get("/admin/usuarios", headers=headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        codigos = [u["codigo_usuario"] for u in data["items"]]
        assert test_usuario.codigo_usuario in codigos
        assert test_admin.codigo_usuario in codigos
        assert otro_usuario.codigo_usuario not in codigos
        for user in data["items"]:
            assert user["codigo_empresa"] == test_admin.codigo_empresa

    async def test_crear_usuario_admin(
        self,
        client: AsyncClient,
        headers_superadmin,
        test_empresa,
    ):
        # El superadmin puede crear usuarios en cualquier empresa
        payload = {
            "correo": "nuevo@test.com",
            "contrasena": "Password1",
            "nombre": "Nuevo Usuario",
            "codigo_empresa": test_empresa.codigo_empresa,
            "rol": "usuario",
        }
        response = await client.post("/admin/usuarios", json=payload, headers=headers_superadmin)
        assert response.status_code == 201
        data = response.json()
        assert data["correo"] == "nuevo@test.com"
        assert data["nombre"] == "Nuevo Usuario"
        assert data["rol"] == "usuario"


class TestAdminServicios:

    async def test_listar_servicios(
        self,
        client: AsyncClient,
        headers_superadmin,
        test_session: AsyncSession,
        test_empresa,
    ):
        # Creamos servicios de prueba y verificamos que se listen correctamente
        for servicio in ["scrum", "tickets"]:
            es = EmpresaServicio(
                codigo_empresa=test_empresa.codigo_empresa,
                servicio=servicio,
                activo=True,
            )
            test_session.add(es)
        await test_session.flush()

        response = await client.get(
            f"/admin/empresas/{test_empresa.codigo_empresa}/servicios",
            headers=headers_superadmin,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        servicios = {s["servicio"] for s in data}
        assert "scrum" in servicios
        assert "tickets" in servicios

    async def test_toggle_servicio(
        self,
        client: AsyncClient,
        headers_superadmin,
        test_session: AsyncSession,
        test_empresa,
    ):
        # Activar/desactivar un servicio (toggle) debe reflejarse en la BD
        es = EmpresaServicio(
            codigo_empresa=test_empresa.codigo_empresa,
            servicio="scrum",
            activo=True,
        )
        test_session.add(es)
        await test_session.flush()

        payload = {"servicio": "scrum", "activo": False}
        response = await client.put(
            f"/admin/empresas/{test_empresa.codigo_empresa}/servicios",
            json=payload,
            headers=headers_superadmin,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["servicio"] == "scrum"
        assert data["activo"] is False
