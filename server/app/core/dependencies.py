from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decodificar_token
from app.models.usuario import Usuario

seguridad = HTTPBearer()


async def get_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(seguridad),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    payload = decodificar_token(credenciales.credentials)
    if payload is None or payload.get("tipo") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )
    resultado = await db.execute(
        select(Usuario).where(Usuario.codigo_usuario == int(sub))
    )
    usuario = resultado.scalar_one_or_none()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    return usuario


def get_tenant_filter(usuario: Usuario = Depends(get_usuario_actual)) -> int:
    return usuario.codigo_empresa
