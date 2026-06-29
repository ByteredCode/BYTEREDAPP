from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.empresa import Empresa

router = APIRouter(tags=["Redireccion"])


@router.get("/r/{codigo_empresa}")
async def redirigir(codigo_empresa: int, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Empresa).where(Empresa.codigo_empresa == codigo_empresa))
    empresa = resultado.scalar_one_or_none()
    if not empresa or not empresa.web:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa o enlace no configurado")
    parsed = urlparse(empresa.web)
    if parsed.scheme not in ("https", "http"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL no valida")
    return RedirectResponse(url=empresa.web)
