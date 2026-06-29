import logging
import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    crear_access_token,
    crear_refresh_token,
    hash_contrasena,
    verificar_contrasena,
)
from app.models.usuario import Usuario

logger = logging.getLogger("byteredapp.auth")


async def registrar_usuario(db: AsyncSession, correo: str, contrasena: str, nombre: str, codigo_empresa: int) -> Usuario:
    if not re.search(r"[A-Z]", contrasena) or not re.search(r"[0-9]", contrasena):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contrasena debe tener al menos una mayuscula y un numero",
        )
    existe = await db.execute(select(Usuario).where(Usuario.correo == correo))
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )
    usuario = Usuario(
        correo=correo,
        contrasena=hash_contrasena(contrasena),
        nombre=nombre,
        codigo_empresa=codigo_empresa,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario


async def iniciar_sesion(db: AsyncSession, correo: str, contrasena: str) -> dict:
    resultado = await db.execute(select(Usuario).where(Usuario.correo == correo))
    usuario = resultado.scalar_one_or_none()
    if not usuario or not verificar_contrasena(contrasena, usuario.contrasena):
        logger.warning("Login fallido: correo %s", correo)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    logger.info("Login exitoso: usuario %s, empresa %s", usuario.codigo_usuario, usuario.codigo_empresa)
    access_token = crear_access_token({"sub": str(usuario.codigo_usuario), "empresa": usuario.codigo_empresa})
    refresh_token = crear_refresh_token({"sub": str(usuario.codigo_usuario)})
    return {
        "usuario": usuario,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
    }
