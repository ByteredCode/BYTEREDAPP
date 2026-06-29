from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.services.email_service import enviar_correo


async def crear_ticket(db: AsyncSession, data: TicketCreate, codigo_usuario: int = None) -> Ticket:
    ticket = Ticket(
        codigo_usuario=codigo_usuario,  # None si es ticket anonimo
        nombre_contacto=data.nombre_contacto,
        correo_contacto=data.correo_contacto,
        asunto=data.asunto,
        nivel_importancia=data.nivel_importancia,
        mensaje=data.mensaje,
        codigo_empresa=data.codigo_empresa,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    # Notificacion por email si el SMTP esta configurado
    asunto_email = f"Nuevo ticket: {ticket.asunto or 'Sin asunto'} ({ticket.nivel_importancia})"
    cuerpo = (
        f"Ticket #{ticket.id_reporte}\n\n"
        f"De: {ticket.nombre_contacto or 'Anonimo'} <{ticket.correo_contacto or 'sin correo'}>\n"
        f"Importancia: {ticket.nivel_importancia}\n"
        f"Mensaje:\n{ticket.mensaje}\n"
    )
    if config.TICKETS_EMAIL:
        await enviar_correo(config.TICKETS_EMAIL, asunto_email, cuerpo)

    return ticket


async def listar_tickets(db: AsyncSession, codigo_empresa: int) -> list[Ticket]:
    resultado = await db.execute(
        select(Ticket).where(Ticket.codigo_empresa == codigo_empresa).order_by(Ticket.fecha_reporte.desc())
    )
    return resultado.scalars().all()


async def obtener_ticket(db: AsyncSession, id_reporte: int, codigo_empresa: int) -> Ticket:
    resultado = await db.execute(
        select(Ticket).where(Ticket.id_reporte == id_reporte, Ticket.codigo_empresa == codigo_empresa)
    )
    ticket = resultado.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
    return ticket


async def actualizar_estado_ticket(
    db: AsyncSession, id_reporte: int, estado: str, codigo_empresa: int, respuesta: str | None = None
) -> Ticket:
    ticket = await obtener_ticket(db, id_reporte, codigo_empresa)
    ticket.estado = estado
    if respuesta:
        ticket.respuesta = respuesta
        ticket.fecha_respuesta = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ticket)
    return ticket
