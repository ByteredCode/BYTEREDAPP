# Tests de seguridad: blocklist, tokens expirados, CORS, SQL injection, headers de seguridad
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from jose import jwt

from app.core.config import config
from app.core.security import decodificar_token


class TestBlocklist:

    async def test_blocklist_refresh_rotacion(self, client: AsyncClient, test_usuario):
        # Al refrescar un token, el refresh anterior debe quedar invalidado (rotación de tokens)
        login_resp = await client.post(
            "/auth/login", json={"correo": "usuario@test.com", "contrasena": "Test1234"}
        )
        refresh_token = login_resp.json()["refresh_token"]
        assert await decodificar_token(refresh_token) is not None
        resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        # Tras refrescar, el viejo refresh_token debe estar en la blocklist
        assert await decodificar_token(refresh_token) is None


class TestTokenExpirado:

    async def test_token_expirado(self, client: AsyncClient):
        # Un token JWT expirado debe ser rechazado (401) por el middleware de autenticación
        payload = {
            "sub": "1",
            "tipo": "access",
            "jti": uuid.uuid4().hex,
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")
        headers = {"Authorization": f"Bearer {expired}"}
        resp = await client.get("/auth/me", headers=headers)
        assert resp.status_code == 401


class TestAccesoSinAuth:

    async def test_acceso_sin_auth(self, client: AsyncClient):
        # Endpoints protegidos deben rechazar peticiones sin token JWT
        resp = await client.get("/scrum/tablero")
        assert resp.status_code == 401


class TestSQLInjection:

    async def test_sql_injection_email(self, client: AsyncClient, test_empresa):
        # Inyección SQL en el campo email debe ser neutralizada por SQLAlchemy (consultas parametrizadas)
        data = {
            "correo": "' OR '1'='1",
            "contrasena": "Test1234",
            "nombre": "Hacker",
            "codigo_empresa": test_empresa.codigo_empresa,
        }
        resp = await client.post("/auth/register", json=data)
        assert resp.status_code in (400, 422)


class TestCORS:

    async def test_cors_headers(self, client: AsyncClient):
        # La API debe responder con CORS permitiendo el origen del frontend (localhost:5173)
        resp = await client.options(
            "/auth/login",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


class TestSecurityHeaders:

    async def test_security_headers(self, client: AsyncClient):
        # La API debe incluir cabeceras de seguridad estándar (OWASP)
        resp = await client.get("/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"
        assert "content-security-policy" in resp.headers
