from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession


def crear_mock_session() -> AsyncMock:
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
