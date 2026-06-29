import pytest
from httpx import AsyncClient


class TestFichajes:

    async def test_fichar_entrada(self, client: AsyncClient, headers_usuario):
        response = await client.post("/fichajes/entrada", headers=headers_usuario)
        assert response.status_code == 201
        data = response.json()
        assert data["hora_entrada"] is not None
        assert data["hora_salida"] is None
        assert data["codigo_usuario"] is not None

    async def test_fichaje_duplicado(self, client: AsyncClient, headers_usuario):
        await client.post("/fichajes/entrada", headers=headers_usuario)
        response = await client.post("/fichajes/entrada", headers=headers_usuario)
        assert response.status_code == 400

    async def test_fichar_salida(self, client: AsyncClient, headers_usuario):
        await client.post("/fichajes/entrada", headers=headers_usuario)
        response = await client.post("/fichajes/salida", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert data["hora_salida"] is not None

    async def test_fichar_salida_sin_entrada(self, client: AsyncClient, headers_usuario):
        response = await client.post("/fichajes/salida", headers=headers_usuario)
        assert response.status_code == 404

    async def test_obtener_fichaje_actual(self, client: AsyncClient, headers_usuario):
        await client.post("/fichajes/entrada", headers=headers_usuario)
        response = await client.get("/fichajes/actual", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert data["hora_salida"] is None

    async def test_obtener_fichaje_actual_sin_abierto(self, client: AsyncClient, headers_usuario):
        response = await client.get("/fichajes/actual", headers=headers_usuario)
        assert response.status_code == 404

    async def test_listar_fichajes(self, client: AsyncClient, headers_usuario):
        await client.post("/fichajes/entrada", headers=headers_usuario)
        await client.post("/fichajes/salida", headers=headers_usuario)
        await client.post("/fichajes/entrada", headers=headers_usuario)

        response = await client.get("/fichajes", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    async def test_fichaje_otro_usuario(
        self, client: AsyncClient, headers_usuario, test_session, test_empresa
    ):
        from app.core.security import hash_contrasena, crear_access_token
        from app.models.usuario import Usuario

        otro = Usuario(
            correo="otro_fichaje@test.com",
            contrasena=hash_contrasena("Pass1234"),
            nombre="Otro Fichaje",
            rol="usuario",
            codigo_empresa=test_empresa.codigo_empresa,
        )
        test_session.add(otro)
        await test_session.flush()

        token_otro = crear_access_token(
            {"sub": str(otro.codigo_usuario), "empresa": otro.codigo_empresa}
        )
        headers_otro = {"Authorization": f"Bearer {token_otro}"}

        await client.post("/fichajes/entrada", headers=headers_otro)

        response = await client.get("/fichajes", headers=headers_usuario)
        assert response.status_code == 200
        data = response.json()
        for fichaje in data:
            assert fichaje["codigo_usuario"] != otro.codigo_usuario
