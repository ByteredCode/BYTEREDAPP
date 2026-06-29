from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fichaje import Fichaje


async def registrar_entrada(db: AsyncSession, codigo_usuario: int, codigo_empresa: int) -> Fichaje:
    # Crear fichaje con hora_salida = NULL (indica que esta abierto)
    fichaje = Fichaje(
        codigo_empresa=codigo_empresa,
        codigo_usuario=codigo_usuario,
        hora_entrada=datetime.now(),
    )
    db.add(fichaje)
    await db.commit()
    await db.refresh(fichaje)
    return fichaje


async def registrar_salida(db: AsyncSession, codigo_usuario: int, codigo_empresa: int) -> Fichaje:
    # Buscar el fichaje abierto mas reciente (hora_salida == NULL)
    resultado = await db.execute(
        select(Fichaje).where(
            Fichaje.codigo_usuario == codigo_usuario,
            Fichaje.codigo_empresa == codigo_empresa,
            Fichaje.hora_salida == None,
        ).order_by(Fichaje.hora_entrada.desc())
    )
    fichaje = resultado.scalar_one_or_none()
    if not fichaje:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay fichaje abierto")
    fichaje.hora_salida = datetime.now()
    await db.commit()
    await db.refresh(fichaje)
    return fichaje


async def listar_fichajes(db: AsyncSession, codigo_usuario: int, codigo_empresa: int) -> list[Fichaje]:
    resultado = await db.execute(
        select(Fichaje).where(
            Fichaje.codigo_usuario == codigo_usuario,
            Fichaje.codigo_empresa == codigo_empresa,
        ).order_by(Fichaje.hora_entrada.desc())
    )
    return resultado.scalars().all()


async def fichaje_abierto(db: AsyncSession, codigo_usuario: int, codigo_empresa: int) -> Fichaje | None:
    # Verificar si hay fichaje sin salida registrada
    resultado = await db.execute(
        select(Fichaje).where(
            Fichaje.codigo_usuario == codigo_usuario,
            Fichaje.codigo_empresa == codigo_empresa,
            Fichaje.hora_salida == None,
        ).order_by(Fichaje.hora_entrada.desc())
    )
    return resultado.scalar_one_or_none()
