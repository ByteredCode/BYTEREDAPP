from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fichaje import Fichaje
from app.models.usuario import Usuario
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


async def listar_fichajes(db: AsyncSession, codigo_usuario: int, codigo_empresa: int, skip: int = 0, limit: int = 50) -> tuple[list[Fichaje], int]:
    where = [
        Fichaje.codigo_usuario == codigo_usuario,
        Fichaje.codigo_empresa == codigo_empresa,
    ]
    total = (await db.execute(select(func.count(Fichaje.id_fichaje)).where(*where))).scalar()
    resultado = await db.execute(
        select(Fichaje).where(*where).order_by(Fichaje.hora_entrada.desc()).offset(skip).limit(limit)
    )
    return resultado.scalars().all(), total


async def listar_fichajes_admin(db: AsyncSession, codigo_empresa: int | None = None, skip: int = 0, limit: int = 50) -> tuple[list, int]:
    # Vista para administradores: devuelve fichajes de toda la empresa (o global
    # si codigo_empresa es None) con el nombre del usuario mediante JOIN.
    # Esto permite a admin_total ver fichajes de cualquier empresa y a
    # admin_empresa ver los de su propia compañia.
    where = []
    if codigo_empresa is not None:
        where.append(Fichaje.codigo_empresa == codigo_empresa)

    count_query = (
        select(func.count(Fichaje.id_fichaje))
        .select_from(Fichaje)
        .join(Usuario, Fichaje.codigo_usuario == Usuario.codigo_usuario)
    )
    if where:
        count_query = count_query.where(*where)
    total = (await db.execute(count_query)).scalar()

    query = (
        select(Fichaje, Usuario.nombre)
        .join(Usuario, Fichaje.codigo_usuario == Usuario.codigo_usuario)
        .order_by(Fichaje.hora_entrada.desc())
        .offset(skip)
        .limit(limit)
    )
    if where:
        query = query.where(*where)

    resultado = await db.execute(query)
    rows = resultado.all()

    items = [
        {
            "id_fichaje": fichaje.id_fichaje,
            "codigo_empresa": fichaje.codigo_empresa,
            "codigo_usuario": fichaje.codigo_usuario,
            "usuario_nombre": nombre,
            "hora_entrada": fichaje.hora_entrada,
            "hora_salida": fichaje.hora_salida,
        }
        for fichaje, nombre in rows
    ]
    return items, total


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


# Filtra fichajes completados (con salida) dentro de un rango de fecha y suma las horas.
# Solo se cuentan fichajes cerrados para no contabilizar fichajes aun en curso.
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
    # Calendario: hoy desde las 00:00:00
    inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    # La semana empieza el lunes (weekday() devuelve 0 para lunes)
    inicio_semana = inicio_hoy - timedelta(days=ahora.weekday())
    # El mes empieza el dia 1 a las 00:00:00
    inicio_mes = inicio_hoy.replace(day=1)

    return FichajeResumenResponse(
        horas_hoy=_calcular_horas(todos, inicio_hoy),
        horas_semana=_calcular_horas(todos, inicio_semana),
        horas_mes=_calcular_horas(todos, inicio_mes),
        total_fichajes=len(todos),
    )


def generar_csv(fichajes: list) -> str:
    lineas = ["id,usuario,empresa,entrada,salida,duracion_min"]
    for f in fichajes:
        if isinstance(f, dict):
            fid = f["id_fichaje"]
            uid = f["codigo_usuario"]
            eid = f["codigo_empresa"]
            entrada = f["hora_entrada"].isoformat()
            salida = f["hora_salida"].isoformat() if f.get("hora_salida") else ""
            duracion = str(int((f["hora_salida"] - f["hora_entrada"]).total_seconds() / 60)) if f.get("hora_salida") else ""
        else:
            fid = f.id_fichaje
            uid = f.codigo_usuario
            eid = f.codigo_empresa
            entrada = f.hora_entrada.isoformat()
            salida = f.hora_salida.isoformat() if f.hora_salida else ""
            duracion = str(int((f.hora_salida - f.hora_entrada).total_seconds() / 60)) if f.hora_salida else ""
        lineas.append(f"{fid},{uid},{eid},{entrada},{salida},{duracion}")
    return "\n".join(lineas)
