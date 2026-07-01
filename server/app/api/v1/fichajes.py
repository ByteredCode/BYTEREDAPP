from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.dependencies import get_usuario_actual
from app.models.empresa import Empresa
from app.models.fichaje import Fichaje
from app.models.usuario import Usuario
from app.schemas.fichaje import GrupoFichajes, FichajeConUsuario
from app.services.fichaje_service import generar_csv, listar_fichajes_admin

router = APIRouter(prefix="/fichajes", tags=["Fichajes"])


def solo_admin_total(usuario: Usuario):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador principal puede acceder a fichajes",
        )


@router.get("/por-empresa", response_model=list[GrupoFichajes])
async def get_fichajes_por_empresa(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    solo_admin_total(usuario)

    resultado = await db.execute(
        select(Fichaje)
        .options(
            joinedload(Fichaje.empresa),
            joinedload(Fichaje.usuario),
        )
        .order_by(Fichaje.codigo_empresa, Fichaje.hora_entrada.desc())
    )
    todos = resultado.unique().scalars().all()

    from collections import defaultdict

    agrupados = defaultdict(list)
    for f in todos:
        agrupados[f.codigo_empresa].append(f)

    codigos = list(agrupados.keys())
    if codigos:
        res_empresas = await db.execute(
            select(Empresa).where(Empresa.codigo_empresa.in_(codigos))
        )
        mapa_empresas = {e.codigo_empresa: e.nombre for e in res_empresas.scalars().all()}
    else:
        mapa_empresas = {}

    resultado_final = []
    for codigo, fichajes in sorted(agrupados.items()):
        resultado_final.append(
            GrupoFichajes(
                codigo_empresa=codigo,
                nombre_empresa=mapa_empresas.get(codigo, f"Empresa #{codigo}"),
                fichajes=[
                    FichajeConUsuario(
                        id_fichaje=f.id_fichaje,
                        codigo_empresa=f.codigo_empresa,
                        codigo_usuario=f.codigo_usuario,
                        hora_entrada=f.hora_entrada,
                        hora_salida=f.hora_salida,
                        usuario_nombre=f.usuario.nombre if f.usuario else None,
                        nombre_empresa=mapa_empresas.get(f.codigo_empresa, f"Empresa #{f.codigo_empresa}"),
                    )
                    for f in fichajes
                ],
            )
        )
    return resultado_final


@router.get("")
async def get_fichajes(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    solo_admin_total(usuario)
    items, _ = await listar_fichajes_admin(db, None)
    return {"items": items}


@router.get("/exportar")
async def get_exportar(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    solo_admin_total(usuario)
    fichajes, _ = await listar_fichajes_admin(db, None)
    csv = generar_csv(fichajes)
    return PlainTextResponse(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fichajes.csv"},
    )
