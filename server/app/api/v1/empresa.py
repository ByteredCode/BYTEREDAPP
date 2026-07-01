from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_usuario_actual
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.admin import EmpresaResponse, ServicioResponse
from app.services import admin_service

router = APIRouter(prefix="/empresa", tags=["Empresa"])


class MiEmpresaUpdate(BaseModel):
    # Modelo separado para que PATCH solo acepte los campos actualizables
    # y no exponga campos internos como codigo_empresa o fecha_creacion
    nombre: Optional[str] = None
    web: Optional[str] = None


@router.get("/mi-empresa", response_model=EmpresaResponse)
async def obtener_mi_empresa(
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    # No usamos tenant_filter porque la empresa se obtiene a partir del
    # codigo_empresa del usuario autenticado, no de un parámetro externo
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
    # Solo los administradores pueden modificar los datos de la empresa;
    # un usuario normal puede verlos (GET) pero no editarlos (PATCH)
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
    # exclude_unset=True para que solo se actualicen los campos enviados
    # y no se sobrescriban con None los que el cliente omitió
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(empresa, key, value)
    await db.commit()
    await db.refresh(empresa)
    return empresa


@router.get("/mi-empresa/servicios", response_model=list[ServicioResponse])
async def obtener_servicios_mi_empresa(
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    servicios_db = await admin_service.listar_servicios(db, usuario.codigo_empresa)
    servicios = [
        {"codigo_empresa": s.codigo_empresa, "servicio": s.servicio, "activo": s.activo}
        for s in servicios_db
    ]
    if usuario.rol == "admin_total":
        servicios.append(
            {"codigo_empresa": usuario.codigo_empresa, "servicio": "gestion_usuarios", "activo": True}
        )
    return servicios
