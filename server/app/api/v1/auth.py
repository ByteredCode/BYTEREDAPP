import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_usuario_actual
from app.core.security import (
    agregar_a_blocklist,
    crear_access_token,
    crear_refresh_token,
    decodificar_token,
)
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UsuarioResponse
from app.services.auth_service import iniciar_sesion, registrar_usuario
from app.services.fichaje_service import registrar_entrada

logger = logging.getLogger("byteredapp.auth")
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["Auth"])


@router.post("/auth/register", response_model=UsuarioResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    usuario = await registrar_usuario(
        db, correo=body.correo, contrasena=body.contrasena, nombre=body.nombre, codigo_empresa=body.codigo_empresa
    )
    logger.info("Usuario registrado: %s (empresa %s)", usuario.codigo_usuario, usuario.codigo_empresa)
    return usuario


@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    resultado = await iniciar_sesion(db, correo=body.correo, contrasena=body.contrasena)
    usuario = resultado["usuario"]
    logger.info("Login exitoso: usuario %s, empresa %s", usuario.codigo_usuario, usuario.codigo_empresa)
    try:
        await registrar_entrada(db, usuario.codigo_usuario, usuario.codigo_empresa)
    except Exception:
        pass
    return resultado["tokens"]


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    payload = decodificar_token(refresh_token)
    if payload is None or payload.get("tipo") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    # Invalidar token anterior (rotacion)
    jti_anterior = payload.get("jti")
    if jti_anterior:
        agregar_a_blocklist(jti_anterior)
    access_token = crear_access_token({"sub": str(payload["sub"]), "empresa": payload.get("empresa")})
    nuevo_refresh = crear_refresh_token({"sub": str(payload["sub"])})
    return TokenResponse(access_token=access_token, refresh_token=nuevo_refresh)


@router.post("/auth/logout", status_code=204)
async def logout(usuario: Usuario = Depends(get_usuario_actual)):
    logger.info("Logout: usuario %s", usuario.codigo_usuario)


@router.get("/auth/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_usuario_actual)):
    return usuario
