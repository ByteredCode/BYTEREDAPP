from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_contrasena
from app.models.empresa import Empresa
from app.models.empresa_servicio import EmpresaServicio
from app.models.usuario import Usuario
from app.schemas.admin import EmpresaCreate, EmpresaUpdate, ServicioToggle, UsuarioCreate, UsuarioUpdate

# Al crear empresa se activan todos los modulos por defecto
SERVICIOS_POR_DEFECTO = ["scrum", "tickets", "documentacion", "fichaje", "redireccion"]


async def listar_empresas(db: AsyncSession) -> list[Empresa]:
    resultado = await db.execute(select(Empresa).order_by(Empresa.nombre))
    return list(resultado.scalars().all())


async def crear_empresa(db: AsyncSession, data: EmpresaCreate) -> Empresa:
    empresa = Empresa(nombre=data.nombre, web=data.web)
    db.add(empresa)
    await db.flush()  # Flush para obtener el ID sin commit todavia

    # Crear todos los servicios activos para la nueva empresa
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


async def listar_usuarios(db: AsyncSession, codigo_empresa: int | None = None) -> list[Usuario]:
    query = select(Usuario).order_by(Usuario.nombre)
    if codigo_empresa is not None:
        query = query.where(Usuario.codigo_empresa == codigo_empresa)
    resultado = await db.execute(query)
    return list(resultado.scalars().all())


async def crear_usuario_admin(db: AsyncSession, data: UsuarioCreate) -> Usuario:
    existe = await db.execute(select(Usuario).where(Usuario.correo == data.correo))
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )

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
        # Si no existe, crear nuevo registro (upsert)
        servicio = EmpresaServicio(
            codigo_empresa=codigo_empresa,
            servicio=data.servicio,
            activo=data.activo,
        )
        db.add(servicio)

    await db.commit()
    await db.refresh(servicio)
    return servicio
