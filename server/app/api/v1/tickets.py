from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.dependencies import get_db, get_tenant_filter, get_usuario_actual, require_servicio
from app.core.limiter import limiter
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.admin import Paginacion
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdateEstado
from app.services.email_service import enviar_correo
from app.services.ticket_service import (
    actualizar_estado_ticket,
    crear_ticket,
    eliminar_ticket,
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
    # Para anónimos: validar que la empresa existe y aplicar rate limit más estricto
    if not usuario:
        existe_empresa = await db.execute(
            select(Empresa).where(Empresa.codigo_empresa == data.codigo_empresa).limit(1)
        )
        if not existe_empresa.scalar_one_or_none():
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Empresa no válida")

    codigo_usuario = usuario.codigo_usuario if usuario else None
    ticket = await crear_ticket(db, data, codigo_usuario)

    if config.TICKETS_EMAIL:
        resultado_empresa = await db.execute(
            select(Empresa.nombre).where(Empresa.codigo_empresa == data.codigo_empresa)
        )
        nombre_empresa = resultado_empresa.scalar_one_or_none() or "Desconocida"
        asunto_email = f"Nuevo ticket: {ticket.asunto or 'Sin asunto'} ({ticket.nivel_importancia})"
        cuerpo = (
            f"Nuevo ticket #{ticket.id_reporte}\n\n"
            f"Nombre: {ticket.nombre_contacto or 'Anonimo'}\n"
            f"Correo: {ticket.correo_contacto}\n"
            f"Empresa: {nombre_empresa}\n"
            f"Importancia: {ticket.nivel_importancia}\n\n"
            f"Mensaje:\n{ticket.mensaje}"
        )
        await enviar_correo(config.TICKETS_EMAIL, asunto_email, cuerpo)

    return ticket


@router.get("")
async def get_tickets(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    pag: Paginacion = Depends(),
    _servicio: None = Depends(require_servicio("tickets")),
):
    items, total = await listar_tickets(db, codigo_empresa, pag.skip, pag.limit)
    return {"items": items, "total": total}


@router.get("/{id_reporte}", response_model=TicketResponse)
async def get_ticket(
    id_reporte: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    _servicio: None = Depends(require_servicio("tickets")),
):
    return await obtener_ticket(db, id_reporte, codigo_empresa)


@router.put("/{id_reporte}/estado", response_model=TicketResponse)
async def put_estado_ticket(
    id_reporte: int,
    data: TicketUpdateEstado,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    _servicio: None = Depends(require_servicio("tickets")),
):
    # Se permite incluir una respuesta (texto) al cambiar el estado para que
    # el admin pueda comunicarse con el reportante sin usar otro canal
    return await actualizar_estado_ticket(db, id_reporte, data.estado, codigo_empresa, data.respuesta)


@router.delete("/{id_reporte}", status_code=204)
async def delete_ticket(
    id_reporte: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
    _servicio: None = Depends(require_servicio("tickets")),
):
    if usuario.rol != "admin_total":
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin_total puede eliminar tickets")
    await eliminar_ticket(db, id_reporte, codigo_empresa)
