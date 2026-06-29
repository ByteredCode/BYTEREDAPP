from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_filter, get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.fichaje import FichajeResumenResponse, FichajeResponse
from app.services.fichaje_service import (
    fichaje_abierto,
    generar_csv,
    listar_fichajes,
    obtener_resumen,
    registrar_entrada,
    registrar_salida,
)

router = APIRouter(prefix="/fichajes", tags=["Fichajes"])


@router.get("", response_model=list[FichajeResponse])
async def get_fichajes(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return await listar_fichajes(db, usuario.codigo_usuario, codigo_empresa)


@router.get("/actual", response_model=FichajeResponse)
async def get_actual(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    fichaje = await fichaje_abierto(db, usuario.codigo_usuario, codigo_empresa)
    if not fichaje:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay fichaje abierto")
    return fichaje


@router.get("/resumen", response_model=FichajeResumenResponse)
async def get_resumen(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return await obtener_resumen(db, usuario.codigo_usuario, codigo_empresa)


@router.get("/exportar")
async def get_exportar(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    fichajes = await listar_fichajes(db, usuario.codigo_usuario, codigo_empresa)
    csv = generar_csv(fichajes)
    return PlainTextResponse(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fichajes.csv"},
    )


@router.post("/entrada", response_model=FichajeResponse, status_code=201)
async def post_entrada(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    existe = await fichaje_abierto(db, usuario.codigo_usuario, codigo_empresa)
    if existe:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya tienes un fichaje abierto")
    return await registrar_entrada(db, usuario.codigo_usuario, codigo_empresa)


@router.post("/salida", response_model=FichajeResponse)
async def post_salida(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return await registrar_salida(db, usuario.codigo_usuario, codigo_empresa)
