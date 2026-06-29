import pytest
from httpx import AsyncClient


class TestRegister:
    async def test_register_exito(self, client: AsyncClient, test_empresa):
        data = {
            "correo": "nuevo@test.com",
            "contrasena": "Test1234",
            "nombre": "Nuevo Usuario",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        resp = await client.post("/auth/register", json=data)
        assert resp.status_code == 200
        body = resp.json()
        assert body["correo"] == "nuevo@test.com"
        assert body["nombre"] == "Nuevo Usuario"
        assert "codigo_usuario" in body
        assert body["rol"] == "usuario"
        assert body["codigo_empresa"] == test_empresa.codigo_empresa

    async def test_register_correo_duplicado(self, client: AsyncClient, test_empresa):
        data = {
            "correo": "dup@test.com",
            "contrasena": "Test1234",
            "nombre": "Duplicado",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        resp1 = await client.post("/auth/register", json=data)
        assert resp1.status_code == 200
        resp2 = await client.post("/auth/register", json=data)
        assert resp2.status_code == 400
        assert "ya esta registrado" in resp2.json()["detail"].lower()

    async def test_register_contrasena_corta(self, client: AsyncClient, test_empresa):
        data = {
            "correo": "corto@test.com",
            "contrasena": "Ab1",
            "nombre": "Corto",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        resp = await client.post("/auth/register", json=data)
        assert resp.status_code == 422

    async def test_register_contrasena_sin_mayuscula(self, client: AsyncClient, test_empresa):
        data = {
            "correo": "nomayus@test.com",
            "contrasena": "abcdefg1",
            "nombre": "SinMayuscula",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        resp = await client.post("/auth/register", json=data)
        assert resp.status_code == 400
        assert "mayuscula" in resp.json()["detail"].lower()

    async def test_register_contrasena_sin_numero(self, client: AsyncClient, test_empresa):
        data = {
            "correo": "nonum@test.com",
            "contrasena": "Abcdefgh",
            "nombre": "SinNumero",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        resp = await client.post("/auth/register", json=data)
        assert resp.status_code == 400
        assert "numero" in resp.json()["detail"].lower()


class TestLogin:
    async def test_login_exito(self, client: AsyncClient, test_usuario):
        data = {"correo": "usuario@test.com", "contrasena": "Test1234"}
        resp = await client.post("/auth/login", json=data)
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_credenciales_incorrectas(self, client: AsyncClient, test_usuario):
        data = {"correo": "usuario@test.com", "contrasena": "WrongPass1"}
        resp = await client.post("/auth/login", json=data)
        assert resp.status_code == 401
        assert "credenciales" in resp.json()["detail"].lower()

    async def test_login_correo_inexistente(self, client: AsyncClient):
        data = {"correo": "noexiste@test.com", "contrasena": "Test1234"}
        resp = await client.post("/auth/login", json=data)
        assert resp.status_code == 401
        assert "credenciales" in resp.json()["detail"].lower()


class TestRefresh:
    async def test_refresh_exito(self, client: AsyncClient, test_usuario):
        login_resp = await client.post(
            "/auth/login", json={"correo": "usuario@test.com", "contrasena": "Test1234"}
        )
        refresh_token = login_resp.json()["refresh_token"]
        resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_refresh_token_invalido(self, client: AsyncClient):
        resp = await client.post("/auth/refresh", json={"refresh_token": "token_invalido"})
        assert resp.status_code == 401
        assert "invalido" in resp.json()["detail"].lower()

    async def test_refresh_con_access_token(self, client: AsyncClient, test_usuario):
        login_resp = await client.post(
            "/auth/login", json={"correo": "usuario@test.com", "contrasena": "Test1234"}
        )
        access_token = login_resp.json()["access_token"]
        resp = await client.post("/auth/refresh", json={"refresh_token": access_token})
        assert resp.status_code == 401
        assert "invalido" in resp.json()["detail"].lower()


class TestLogout:
    async def test_logout(self, client: AsyncClient, headers_usuario):
        resp = await client.post("/auth/logout", headers=headers_usuario)
        assert resp.status_code == 204


class TestMe:
    async def test_me_autenticado(self, client: AsyncClient, headers_usuario, test_usuario):
        resp = await client.get("/auth/me", headers=headers_usuario)
        assert resp.status_code == 200
        body = resp.json()
        assert body["correo"] == test_usuario.correo
        assert body["nombre"] == test_usuario.nombre
        assert body["codigo_usuario"] == test_usuario.codigo_usuario

    async def test_me_sin_token(self, client: AsyncClient):
        resp = await client.get("/auth/me")
        assert resp.status_code == 401


class TestRateLimit:
    @pytest.mark.skipif(True, reason="slowapi puede no funcionar en test mode")
    async def test_rate_limit(self, client: AsyncClient, test_usuario):
        data = {"correo": "usuario@test.com", "contrasena": "Test1234"}
        for _ in range(10):
            resp = await client.post("/auth/login", json=data)
            assert resp.status_code == 200
        resp = await client.post("/auth/login", json=data)
        assert resp.status_code == 429
