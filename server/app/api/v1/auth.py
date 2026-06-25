from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_usuario_actual
from app.core.security import crear_access_token, crear_refresh_token, decodificar_token
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UsuarioResponse
from app.services.auth_service import iniciar_sesion, registrar_usuario

router = APIRouter(tags=["Auth"])


@router.post("/auth/register", response_model=UsuarioResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    usuario = await registrar_usuario(
        db, correo=body.correo, contrasena=body.contrasena, nombre=body.nombre, codigo_empresa=body.codigo_empresa
    )
    return usuario


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await iniciar_sesion(db, correo=body.correo, contrasena=body.contrasena)


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str = Body(...), db: AsyncSession = Depends(get_db)):
    payload = decodificar_token(refresh_token)
    if payload is None or payload.get("tipo") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    access_token = crear_access_token({"sub": str(payload["sub"]), "empresa": payload.get("empresa")})
    nuevo_refresh = crear_refresh_token({"sub": str(payload["sub"])})
    return TokenResponse(access_token=access_token, refresh_token=nuevo_refresh)


@router.get("/auth/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_usuario_actual)):
    return usuario
