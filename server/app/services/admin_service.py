import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_contrasena
from app.models.empresa import Empresa
from app.models.empresa_servicio import EmpresaServicio
from app.models.fichaje import Fichaje
from app.models.tarea import Tarea
from app.models.ticket import Ticket
from app.models.usuario import Usuario
from app.schemas.admin import (
    AdminStatsResponse,
    ConteoPorClave,
    EmpresaCreate,
    EmpresaUpdate,
    ServicioToggle,
    UsuarioCreate,
    UsuarioUpdate,
)

# Al crear empresa se activan todos los modulos por defecto
SERVICIOS_POR_DEFECTO = ["scrum", "tickets", "documentacion", "fichaje", "redireccion"]

# Los servicios de admin reciben codigo_empresa como opcional (int | None):
# - admin_total lo omite (None) y ve datos de todo el sistema sin filtro de tenant
# - admin_empresa pasa su codigo_empresa y solo ve los datos de su compañía


async def listar_empresas(db: AsyncSession, skip: int = 0, limit: int = 50) -> tuple[list[Empresa], int]:
    total = (await db.execute(select(func.count(Empresa.codigo_empresa)))).scalar()
    resultado = await db.execute(select(Empresa).order_by(Empresa.nombre).offset(skip).limit(limit))
    return list(resultado.scalars().all()), total


async def crear_empresa(db: AsyncSession, data: EmpresaCreate) -> Empresa:
    empresa = Empresa(nombre=data.nombre, web=data.web)
    db.add(empresa)
    await db.flush()  # Flush para obtener el ID sin commit todavia

    # Tras crear la empresa, activamos todos los módulos por defecto para que
    # el nuevo tenant empiece operativo sin necesidad de configuración manual
    for servicio in SERVICIOS_POR_DEFECTO:
        es = EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio=servicio, activo=True)
        db.add(es)

    await db.commit()
    await db.refresh(empresa)
    return empresa


async def obtener_empresa(db: AsyncSession, codigo_empresa: int) -> Empresa | None:
    resultado = await db.execute(select(Empresa).where(Empresa.codigo_empresa == codigo_empresa))
    return resultado.scalar_one_or_none()


async def actualizar_empresa(db: AsyncSession, codigo_empresa: int, data: EmpresaUpdate) -> Empresa:
    empresa = await obtener_empresa(db, codigo_empresa)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )
    # exclude_unset=True: solo actualiza campos enviados explicitamente
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(empresa, key, value)
    await db.commit()
    await db.refresh(empresa)
    return empresa


async def eliminar_empresa(db: AsyncSession, codigo_empresa: int) -> None:
    empresa = await obtener_empresa(db, codigo_empresa)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )
    await db.delete(empresa)
    await db.commit()


async def listar_usuarios(db: AsyncSession, codigo_empresa: int | None = None, skip: int = 0, limit: int = 50) -> tuple[list[Usuario], int]:
    count_query = select(func.count(Usuario.codigo_usuario))
    query = select(Usuario).order_by(Usuario.nombre)
    if codigo_empresa is not None:
        count_query = count_query.where(Usuario.codigo_empresa == codigo_empresa)
        query = query.where(Usuario.codigo_empresa == codigo_empresa)
    total = (await db.execute(count_query)).scalar()
    resultado = await db.execute(query.offset(skip).limit(limit))
    return list(resultado.scalars().all()), total


async def crear_usuario_admin(db: AsyncSession, data: UsuarioCreate) -> Usuario:
    if len(data.contrasena) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contrasena debe tener al menos 8 caracteres",
        )
    if not re.search(r"[A-Z]", data.contrasena) or not re.search(r"[0-9]", data.contrasena):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contrasena debe tener al menos una mayuscula y un numero",
        )
    existe = await db.execute(select(Usuario).where(Usuario.correo == data.correo))
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )

    # Verificamos que la empresa destino exista antes de crear el usuario
    # para evitar huérfanos (usuarios sin empresa válida) en el sistema
    empresa = await db.execute(select(Empresa).where(Empresa.codigo_empresa == data.codigo_empresa))
    if not empresa.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    usuario = Usuario(
        correo=data.correo,
        contrasena=hash_contrasena(data.contrasena),
        nombre=data.nombre,
        codigo_empresa=data.codigo_empresa,
        rol=data.rol,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario


async def actualizar_usuario(db: AsyncSession, codigo_usuario: int, data: UsuarioUpdate) -> Usuario:
    resultado = await db.execute(select(Usuario).where(Usuario.codigo_usuario == codigo_usuario))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)
    await db.commit()
    await db.refresh(usuario)
    return usuario


async def obtener_usuario_por_id(db: AsyncSession, codigo_usuario: int) -> Usuario | None:
    resultado = await db.execute(select(Usuario).where(Usuario.codigo_usuario == codigo_usuario))
    return resultado.scalar_one_or_none()


async def eliminar_usuario(db: AsyncSession, codigo_usuario: int) -> None:
    resultado = await db.execute(select(Usuario).where(Usuario.codigo_usuario == codigo_usuario))
    usuario = resultado.scalar_one_or_none()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    await db.delete(usuario)
    await db.commit()


async def listar_servicios(db: AsyncSession, codigo_empresa: int) -> list[EmpresaServicio]:
    resultado = await db.execute(
        select(EmpresaServicio).where(EmpresaServicio.codigo_empresa == codigo_empresa)
    )
    return list(resultado.scalars().all())


async def toggle_servicio(db: AsyncSession, codigo_empresa: int, data: ServicioToggle) -> EmpresaServicio:
    empresa = await obtener_empresa(db, codigo_empresa)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    resultado = await db.execute(
        select(EmpresaServicio).where(
            EmpresaServicio.codigo_empresa == codigo_empresa,
            EmpresaServicio.servicio == data.servicio,
        )
    )
    servicio = resultado.scalar_one_or_none()

    if servicio:
        # Si ya existe, actualizar estado
        servicio.activo = data.activo
    else:
        # Upsert: si no existe el registro de servicio, lo creamos.
        # Esto permite activar módulos que no estaban en SERVICIOS_POR_DEFECTO
        # sin depender de una migración ni lanzar error por registro faltante
        servicio = EmpresaServicio(
            codigo_empresa=codigo_empresa,
            servicio=data.servicio,
            activo=data.activo,
        )
        db.add(servicio)

    await db.commit()
    await db.refresh(servicio)
    return servicio


async def obtener_stats(db: AsyncSession, codigo_empresa: int | None = None) -> AdminStatsResponse:
    # 'filtrar' es una función auxiliar que devuelve la condición WHERE apropiada:
    # - codigo_empresa=None (admin_total) -> no filtra (devuelve la columna tal cual)
    # - codigo_empresa=valor (admin_empresa) -> filtra por ese tenant
    # Así evitamos repetir if/else en cada una de las queries siguientes
    def filtrar(col):
        return col if codigo_empresa is None else col == codigo_empresa

    total_empresas = (await db.execute(select(func.count(Empresa.codigo_empresa)))).scalar()

    uq = select(Usuario.rol, func.count().label("total")).group_by(Usuario.rol)
    if codigo_empresa:
        uq = uq.where(Usuario.codigo_empresa == codigo_empresa)
    filas_rol = await db.execute(uq)
    usuarios_por_rol = [ConteoPorClave(clave=r.rol, total=r.total) for r in filas_rol]

    total_usuarios = sum(c.total for c in usuarios_por_rol)

    tq = select(Ticket.estado, func.count().label("total")).group_by(Ticket.estado)
    if codigo_empresa:
        tq = tq.where(Ticket.codigo_empresa == codigo_empresa)
    filas_ticket = await db.execute(tq)
    tickets_por_estado = [ConteoPorClave(clave=r.estado, total=r.total) for r in filas_ticket]

    fq = select(func.count(Fichaje.id_fichaje)).where(Fichaje.hora_salida.is_(None))
    if codigo_empresa:
        fq = fq.where(Fichaje.codigo_empresa == codigo_empresa)
    fichajes_abiertos = (await db.execute(fq)).scalar()

    eq = select(func.count(Empresa.codigo_empresa)).where(Empresa.web.is_(None))
    empresas_sin_web = (await db.execute(eq)).scalar()

    taq = select(Tarea.columna, func.count().label("total")).group_by(Tarea.columna)
    if codigo_empresa:
        taq = taq.where(Tarea.codigo_empresa == codigo_empresa)
    filas_tarea = await db.execute(taq)
    tareas_por_columna = [ConteoPorClave(clave=r.columna, total=r.total) for r in filas_tarea]

    hace_un_mes = datetime.now(timezone.utc) - timedelta(days=30)
    ttmq = select(func.count(Ticket.id_reporte)).where(Ticket.fecha_reporte >= hace_un_mes)
    if codigo_empresa:
        ttmq = ttmq.where(Ticket.codigo_empresa == codigo_empresa)
    tickets_ultimo_mes = (await db.execute(ttmq)).scalar()

    return AdminStatsResponse(
        total_empresas=total_empresas,
        total_usuarios=total_usuarios,
        usuarios_por_rol=usuarios_por_rol,
        tickets_por_estado=tickets_por_estado,
        fichajes_abiertos=fichajes_abiertos,
        empresas_sin_web=empresas_sin_web,
        tareas_por_columna=tareas_por_columna,
        tickets_ultimo_mes=tickets_ultimo_mes,
    )
