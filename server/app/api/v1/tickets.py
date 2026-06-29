from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_filter, get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdateEstado
from app.services.ticket_service import (
    actualizar_estado_ticket,
    crear_ticket,
    listar_tickets,
    obtener_ticket,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])
seguridad_ticket = HTTPBearer(auto_error=False)


async def get_usuario_opcional(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(seguridad_ticket),
    db: AsyncSession = Depends(get_db),
) -> Optional[Usuario]:
    if credenciales is None:
        return None
    try:
        return await get_usuario_actual(credenciales, db)
    except Exception:
        return None


@router.post("", response_model=TicketResponse, status_code=201)
async def post_ticket(
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Optional[Usuario] = Depends(get_usuario_opcional),
):
    codigo_usuario = usuario.codigo_usuario if usuario else None
    return await crear_ticket(db, data, codigo_usuario)


@router.get("", response_model=list[TicketResponse])
async def get_tickets(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await listar_tickets(db, codigo_empresa)


@router.get("/{id_reporte}", response_model=TicketResponse)
async def get_ticket(
    id_reporte: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await obtener_ticket(db, id_reporte, codigo_empresa)


@router.put("/{id_reporte}/estado", response_model=TicketResponse)
async def put_estado_ticket(
    id_reporte: int,
    data: TicketUpdateEstado,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await actualizar_estado_ticket(db, id_reporte, data.estado, codigo_empresa, data.respuesta)
