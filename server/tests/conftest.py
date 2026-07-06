# Configuración global de pytest: aquí se definen todos los "fixtures" compartidos
# entre los distintos archivos de test. Separarlos en conftest.py evita duplicar
# la lógica de conexión a BD, creación de empresas/usuarios y obtención de tokens.
import os
import sys

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Añadimos server/ al path para poder importar la app sin instalar el paquete
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from app.core.database import Base, get_db
from app.core.config import config
from app.core.security import crear_access_token
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.tarea import Tarea
from app.models.sprint import Sprint
from app.models.ticket import Ticket
from app.models.documento import Documento

# Importamos los routers para montarlos sin prefijo en tests
from app.api.v1.admin import router as test_admin_router
from app.api.v1.auth import router as test_auth_router
from app.api.v1.empresa import router as test_empresa_router
from app.api.v1.scrum import router as test_scrum_router
from app.api.v1.tickets import router as test_tickets_router
from app.api.v1.documentos import router as test_documentos_router
from app.api.v1.redireccion import router as test_redireccion_router

# Variable de entorno para decidir si usar MySQL real o SQLite en memoria
# (por defecto SQLite, que es más rápido y no requiere servidor)
USE_MYSQL = os.environ.get("USE_MYSQL_TEST") == "1"

if USE_MYSQL:
    TEST_DATABASE_URL = (
        f"mysql+aiomysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}"
        f"@{config.MYSQL_HOST}:3307/{config.MYSQL_DATABASE}_test"
    )
else:
    # SQLite en memoria: se crea y destruye cada sesión de test; no hay efectos colaterales entre tests
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def test_engine():
    # Un solo engine para toda la sesión: creamos las tablas al inicio y las borramos al final.
    # El engine se comparte entre todos los tests, pero cada uno obtiene una transacción propia.
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    # Cada test obtiene su propia conexión y transacción; al terminar hacemos rollback
    # para que ningún test deje suciedad en la BD (aislamiento total entre tests).
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    yield session
    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def client(test_session):
    # Creamos un cliente HTTP asíncrono que apunta a la app FastAPI, y sobrescribimos
    # la dependencia get_db para que use la sesión de test en lugar de la real.
    from run import app

    # Montamos los routers sin prefijo /api/v1 para que los tests
    # sigan funcionando con las rutas cortas (ej. /auth/login)
    test_router = APIRouter()
    test_router.include_router(test_auth_router)
    test_router.include_router(test_admin_router)
    test_router.include_router(test_empresa_router)
    test_router.include_router(test_scrum_router)
    test_router.include_router(test_tickets_router)
    test_router.include_router(test_documentos_router)
    test_router.include_router(test_redireccion_router)
    app.include_router(test_router)

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    # Limpiamos las sobreescrituras para no contaminar otros tests
    app.dependency_overrides.clear()


@pytest.fixture
async def test_empresa(test_session):
    # Empresa mínima para los tests que necesitan un tenant multi-empresa
    empresa = Empresa(nombre="Empresa Test")
    test_session.add(empresa)
    await test_session.flush()
    return empresa


@pytest.fixture
async def test_usuario(test_session, test_empresa):
    # Usuario regular (rol "usuario") asociado a la empresa de test
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
    # Usuario con rol admin_empresa para probar endpoints que requieren permisos de administración
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
    # Superadmin (admin_total) sin empresa fija, para probar endpoints globales
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
    # Generamos un JWT para el usuario de test; estos tokens son síncronos (no requieren DB)
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
    # Encabezado HTTP listo para usar en las peticiones de test
    return {"Authorization": f"Bearer {token_usuario}"}


@pytest.fixture
def headers_admin(token_admin):
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture
def headers_superadmin(token_superadmin):
    return {"Authorization": f"Bearer {token_superadmin}"}


@pytest.fixture
async def test_sprint(test_session, test_empresa):
    # Sprint por defecto para los tests del módulo Scrum
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
    # Tarea asignada al usuario de test dentro de un sprint, listo para probar CRUD y movimientos
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
    # Ticket de soporte asociado al usuario de test para probar el ciclo de vida de tickets
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
