import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import Response
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
    guardar_fotos,
    leer_foto_bytes,
    listar_tickets,
    obtener_ticket,
    obtener_fotos_adjuntos,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])
seguridad_ticket = HTTPBearer(auto_error=False)


class EmpresaSimple(BaseModel):
    codigo_empresa: int
    nombre: str

    model_config = {"from_attributes": True}


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


@router.get("/empresas", response_model=list[EmpresaSimple])
async def listar_empresas_publico(db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Empresa.codigo_empresa, Empresa.nombre))
    return [{"codigo_empresa": r[0], "nombre": r[1]} for r in resultado.all()]


@router.post("", response_model=TicketResponse, status_code=201)
@limiter.limit("10/minute")
async def post_ticket(
    request: Request,
    correo_contacto: str = Form(...),
    mensaje: str = Form(...),
    nombre_contacto: Optional[str] = Form(None),
    asunto: Optional[str] = Form(None),
    nivel_importancia: str = Form("Media"),
    codigo_empresa: Optional[int] = Form(None),
    fotos: Optional[list[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
    usuario: Optional[Usuario] = Depends(get_usuario_opcional),
):
    if not usuario:
        existe_empresa = await db.execute(
            select(Empresa).where(Empresa.codigo_empresa == codigo_empresa).limit(1)
        )
        if not existe_empresa.scalar_one_or_none():
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Empresa no válida")
    else:
        codigo_empresa = usuario.codigo_empresa

    import re
    if not re.match(r"^(Baja|Media|Alta|Critica)$", nivel_importancia):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Nivel de importancia no válido")

    data = TicketCreate(
        correo_contacto=correo_contacto,
        mensaje=mensaje,
        nombre_contacto=nombre_contacto,
        asunto=asunto,
        nivel_importancia=nivel_importancia,
        codigo_empresa=codigo_empresa,
    )

    codigo_usuario = usuario.codigo_usuario if usuario else None
    ticket = await crear_ticket(db, data, codigo_usuario)

    fotos_validas = [f for f in (fotos or []) if f.filename]
    if fotos_validas and usuario:
        await guardar_fotos(ticket, fotos_validas, codigo_empresa, db)

    if config.TICKETS_EMAIL:
        resultado_empresa = await db.execute(
            select(Empresa.nombre).where(Empresa.codigo_empresa == codigo_empresa)
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
        adjuntos = obtener_fotos_adjuntos(ticket) if ticket.fotos else None
        await enviar_correo(config.TICKETS_EMAIL, asunto_email, cuerpo, adjuntos)

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


@router.get("/{id_reporte}/fotos/{filename}")
async def descargar_foto_ticket(
    id_reporte: int,
    filename: str,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    _servicio: None = Depends(require_servicio("tickets")),
):
    ticket = await obtener_ticket(db, id_reporte, codigo_empresa)
    if not ticket.fotos:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Ticket sin fotos")

    try:
        rutas = json.loads(ticket.fotos)
    except (json.JSONDecodeError, TypeError):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Fotos no válidas")

    for ruta in rutas:
        if os.path.basename(ruta) == filename:
            contenido = leer_foto_bytes(ruta)
            ext = os.path.splitext(filename)[1].lower()
            content_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }.get(ext, "application/octet-stream")
            return Response(content=contenido, media_type=content_type)

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Foto no encontrada")


@router.put("/{id_reporte}/estado", response_model=TicketResponse)
async def put_estado_ticket(
    id_reporte: int,
    data: TicketUpdateEstado,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    _servicio: None = Depends(require_servicio("tickets")),
):
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
