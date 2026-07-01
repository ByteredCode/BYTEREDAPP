import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.blocklist import agregar_a_blocklist
from app.core.dependencies import get_usuario_actual
from app.core.limiter import limiter
from app.core.security import (
    crear_access_token,
    crear_refresh_token,
    decodificar_token,
)
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, LogoutRequest, TokenResponse, UsuarioResponse
from app.services.auth_service import cerrar_sesion, iniciar_sesion
from app.services.fichaje_service import registrar_entrada

logger = logging.getLogger("byteredapp.auth")
router = APIRouter(tags=["Auth"])


@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    resultado = await iniciar_sesion(db, correo=body.correo, contrasena=body.contrasena)
    usuario = resultado["usuario"]
    logger.info("Login exitoso: usuario %s, empresa %s", usuario.codigo_usuario, usuario.codigo_empresa)
    return TokenResponse(
        access_token=resultado["tokens"]["access_token"],
        refresh_token=resultado["tokens"]["refresh_token"],
        token_type="bearer",
        usuario=UsuarioResponse(
            codigo_usuario=usuario.codigo_usuario,
            correo=usuario.correo,
            nombre=usuario.nombre,
            rol=usuario.rol,
            codigo_empresa=usuario.codigo_empresa,
        ),
    )


@router.post("/auth/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh(request: Request, refresh_token: str = Body(..., embed=True), db: AsyncSession = Depends(get_db)):
    payload = await decodificar_token(refresh_token)
    if payload is None or payload.get("tipo") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    jti_anterior = payload.get("jti")
    if jti_anterior:
        # Invalidamos el refresh anterior para que no pueda reutilizarse (rotation)
        await agregar_a_blocklist(jti_anterior)
    access_token = crear_access_token({"sub": str(payload["sub"]), "empresa": payload.get("empresa")})
    nuevo_refresh = crear_refresh_token({"sub": str(payload["sub"])})
    return TokenResponse(access_token=access_token, refresh_token=nuevo_refresh)


@router.post("/auth/logout", status_code=204)
@limiter.limit("10/minute")
async def logout(
    request: Request,
    body: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual),
):
    logger.info("Logout: usuario %s", usuario.codigo_usuario)
    auth_header = request.headers.get("Authorization", "")
    access_token = auth_header.removeprefix("Bearer ")
    await cerrar_sesion(db, body.refresh_token, access_token)


@router.get("/auth/me", response_model=UsuarioResponse)
# Endpoint para que el frontend obtenga los datos del usuario autenticado sin enviar credenciales
async def me(usuario: Usuario = Depends(get_usuario_actual)):
    return usuario
