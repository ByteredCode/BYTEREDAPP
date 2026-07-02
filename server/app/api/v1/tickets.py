import os
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.dependencies import get_db, get_tenant_filter, get_usuario_actual
from app.core.limiter import limiter
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.admin import Paginacion
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdateEstado
from app.services.email_service import enviar_correo
from app.services.ticket_service import (
    actualizar_estado_ticket,
    crear_ticket,
    listar_tickets,
    obtener_ticket,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])
# auto_error=False permite que el endpoint de creación sea accesible sin token
seguridad_ticket = HTTPBearer(auto_error=False)


class EmpresaSimple(BaseModel):
    codigo_empresa: int
    nombre: str

    model_config = {"from_attributes": True}


async def get_usuario_opcional(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(seguridad_ticket),
    db: AsyncSession = Depends(get_db),
) -> Optional[Usuario]:
    # Si no hay credenciales, devolvemos None en vez de rechazar la petición
    if credenciales is None:
        return None
    try:
        return await get_usuario_actual(credenciales, db)
    except Exception:
        # Token inválido no debe bloquear; el usuario anónimo aún puede crear tickets
        return None


@router.get("/empresas", response_model=list[EmpresaSimple])
async def listar_empresas_publico(db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Empresa.codigo_empresa, Empresa.nombre))
    return [{"codigo_empresa": r[0], "nombre": r[1]} for r in resultado.all()]


@router.post("", response_model=TicketResponse, status_code=201)
@limiter.limit("10/minute")
async def post_ticket(
    request: Request,
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Optional[Usuario] = Depends(get_usuario_opcional),
):
    # Endpoint público: cualquier persona (autenticada o no) puede reportar un problema
    codigo_usuario = usuario.codigo_usuario if usuario else None
    return await crear_ticket(db, data, codigo_usuario)


@router.get("")
async def get_tickets(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    pag: Paginacion = Depends(),
):
    items, total = await listar_tickets(db, codigo_empresa, pag.skip, pag.limit)
    return {"items": items, "total": total}


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
    # Se permite incluir una respuesta (texto) al cambiar el estado para que
    # el admin pueda comunicarse con el reportante sin usar otro canal
    return await actualizar_estado_ticket(db, id_reporte, data.estado, codigo_empresa, data.respuesta)


@router.get("/debug-smtp")
async def debug_smtp():
    """Endpoint temporal para diagnosticar SMTP en Render. ELIMINAR despues."""
    env_host = os.environ.get("SMTP_HOST", "<NO EXISTE>")
    env_port = os.environ.get("SMTP_PORT", "<NO EXISTE>")
    env_user = os.environ.get("SMTP_USER", "<NO EXISTE>")
    env_pass_len = len(os.environ.get("SMTP_PASSWORD", ""))
    env_tickets = os.environ.get("TICKETS_EMAIL", "<NO EXISTE>")
    return {
        "config_py_host": config.SMTP_HOST,
        "config_py_port": config.SMTP_PORT,
        "config_py_user": config.SMTP_USER,
        "config_py_pass_len": len(config.SMTP_PASSWORD),
        "config_py_tickets": config.TICKETS_EMAIL,
        "env_host": env_host,
        "env_port": env_port,
        "env_user": env_user,
        "env_pass_len": env_pass_len,
        "env_tickets": env_tickets,
    }
