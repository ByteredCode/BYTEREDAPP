from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fichaje import Fichaje
from app.schemas.fichaje import FichajeResumenResponse


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


def _calcular_horas(fichajes: list[Fichaje], desde: datetime) -> float:
    total = 0.0
    for f in fichajes:
        if f.hora_entrada >= desde and f.hora_salida:
            diff = f.hora_salida - f.hora_entrada
            total += diff.total_seconds() / 3600
    return round(total, 2)


async def obtener_resumen(db: AsyncSession, codigo_usuario: int, codigo_empresa: int) -> FichajeResumenResponse:
    resultado = await db.execute(
        select(Fichaje).where(
            Fichaje.codigo_usuario == codigo_usuario,
            Fichaje.codigo_empresa == codigo_empresa,
        )
    )
    todos = resultado.scalars().all()
    ahora = datetime.now()
    inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_semana = inicio_hoy - timedelta(days=ahora.weekday())
    inicio_mes = inicio_hoy.replace(day=1)

    return FichajeResumenResponse(
        horas_hoy=_calcular_horas(todos, inicio_hoy),
        horas_semana=_calcular_horas(todos, inicio_semana),
        horas_mes=_calcular_horas(todos, inicio_mes),
        total_fichajes=len(todos),
    )


def generar_csv(fichajes: list[Fichaje]) -> str:
    lineas = ["id,usuario,empresa,entrada,salida,duracion_min"]
    for f in fichajes:
        entrada = f.hora_entrada.isoformat()
        salida = f.hora_salida.isoformat() if f.hora_salida else ""
        duracion = ""
        if f.hora_salida:
            duracion = str(int((f.hora_salida - f.hora_entrada).total_seconds() / 60))
        lineas.append(f"{f.id_fichaje},{f.codigo_usuario},{f.codigo_empresa},{entrada},{salida},{duracion}")
    return "\n".join(lineas)
