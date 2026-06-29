from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_usuario_actual
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.admin import EmpresaResponse

router = APIRouter(prefix="/empresa", tags=["Empresa"])


class MiEmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    web: Optional[str] = None


@router.get("/mi-empresa", response_model=EmpresaResponse)
async def obtener_mi_empresa(
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(Empresa).where(Empresa.codigo_empresa == usuario.codigo_empresa)
    )
    empresa = resultado.scalar_one_or_none()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )
    return empresa


@router.patch("/mi-empresa", response_model=EmpresaResponse)
async def actualizar_mi_empresa(
    body: MiEmpresaUpdate,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol not in ("admin_total", "admin_empresa"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar la empresa",
        )
    resultado = await db.execute(
        select(Empresa).where(Empresa.codigo_empresa == usuario.codigo_empresa)
    )
    empresa = resultado.scalar_one_or_none()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(empresa, key, value)
    await db.commit()
    await db.refresh(empresa)
    return empresa
