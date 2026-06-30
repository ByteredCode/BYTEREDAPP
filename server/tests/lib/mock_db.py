# Factoría de sesiones mock para tests unitarios de servicios
# Crea un AsyncSession simulado donde todos los métodos son MagicMock/AsyncMock,
# permitiendo probar la lógica de negocio sin necesidad de una base de datos real.
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession


def crear_mock_session() -> AsyncMock:
    # Cada llamada devuelve una sesión independiente, evitando efectos colaterales
    # entre tests unitarios que se ejecuten en el mismo proceso.
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    return session
