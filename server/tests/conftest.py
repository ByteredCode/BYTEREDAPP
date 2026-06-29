import os
import sys

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import Base, get_db
from app.core.config import config
from app.core.security import crear_access_token
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.tarea import Tarea
from app.models.sprint import Sprint
from app.models.ticket import Ticket
from app.models.documento import Documento

USE_MYSQL = os.environ.get("USE_MYSQL_TEST") == "1"

if USE_MYSQL:
    TEST_DATABASE_URL = (
        f"mysql+aiomysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}"
        f"@{config.MYSQL_HOST}:3307/{config.MYSQL_DATABASE}_test"
    )
else:
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session
    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def client(test_session):
    from run import app

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_empresa(test_session):
    empresa = Empresa(nombre="Empresa Test")
    test_session.add(empresa)
    await test_session.flush()
    return empresa


@pytest.fixture
async def test_usuario(test_session, test_empresa):
    from app.core.security import hash_contrasena
    usuario = Usuario(
        correo="usuario@test.com",
        contrasena=hash_contrasena("Test1234"),
        nombre="Usuario Test",
        rol="usuario",
        codigo_empresa=test_empresa.codigo_empresa,
    )
    test_session.add(usuario)
    await test_session.flush()
    return usuario


@pytest.fixture
async def test_admin(test_session, test_empresa):
    from app.core.security import hash_contrasena
    admin = Usuario(
        correo="admin@test.com",
        contrasena=hash_contrasena("Admin1234"),
        nombre="Admin Test",
        rol="admin_empresa",
        codigo_empresa=test_empresa.codigo_empresa,
    )
    test_session.add(admin)
    await test_session.flush()
    return admin


@pytest.fixture
async def test_superadmin(test_session):
    from app.core.security import hash_contrasena
    sa = Usuario(
        correo="super@test.com",
        contrasena=hash_contrasena("Super1234"),
        nombre="Super Admin",
        rol="admin_total",
        codigo_empresa=1,
    )
    test_session.add(sa)
    await test_session.flush()
    return sa


@pytest.fixture
def token_usuario(test_usuario):
    token = crear_access_token({"sub": str(test_usuario.codigo_usuario), "empresa": test_usuario.codigo_empresa})
    return token


@pytest.fixture
def token_admin(test_admin):
    token = crear_access_token({"sub": str(test_admin.codigo_usuario), "empresa": test_admin.codigo_empresa})
    return token


@pytest.fixture
def token_superadmin(test_superadmin):
    token = crear_access_token({"sub": str(test_superadmin.codigo_usuario), "empresa": test_superadmin.codigo_empresa})
    return token


@pytest.fixture
def headers_usuario(token_usuario):
    return {"Authorization": f"Bearer {token_usuario}"}


@pytest.fixture
def headers_admin(token_admin):
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture
def headers_superadmin(token_superadmin):
    return {"Authorization": f"Bearer {token_superadmin}"}


@pytest.fixture
async def test_sprint(test_session, test_empresa):
    sprint = Sprint(
        nombre="Sprint 1",
        estado="Planificado",
        codigo_empresa=test_empresa.codigo_empresa,
    )
    test_session.add(sprint)
    await test_session.flush()
    return sprint


@pytest.fixture
async def test_tarea(test_session, test_empresa, test_usuario, test_sprint):
    tarea = Tarea(
        titulo="Tarea test",
        prioridad="Media",
        columna="Todo",
        codigo_empresa=test_empresa.codigo_empresa,
        asignacion=test_usuario.codigo_usuario,
        codigo_sprint=test_sprint.codigo_sprint,
    )
    test_session.add(tarea)
    await test_session.flush()
    return tarea


@pytest.fixture
async def test_ticket(test_session, test_empresa, test_usuario):
    ticket = Ticket(
        mensaje="Ticket de prueba",
        nivel_importancia="Media",
        codigo_empresa=test_empresa.codigo_empresa,
        codigo_usuario=test_usuario.codigo_usuario,
        estado="Pendiente",
    )
    test_session.add(ticket)
    await test_session.flush()
    return ticket
