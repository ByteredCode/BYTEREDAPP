from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decodificar_token
from app.models.usuario import Usuario

# HTTPBearer extrae el token del header "Authorization: Bearer <token>"
seguridad = HTTPBearer(auto_error=False)


async def get_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(seguridad),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    if credenciales is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido"
        )
    payload = await decodificar_token(credenciales.credentials)
    if payload is None or payload.get("tipo") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        )
    # "sub" (subject) es el claim estandar JWT que contiene el ID del usuario
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


# Dependencia que extrae el company_id del usuario autenticado
# Se usa en endpoints para filtrar datos por empresa (multi-tenant)
def get_tenant_filter(usuario: Usuario = Depends(get_usuario_actual)) -> int:
    return usuario.codigo_empresa
