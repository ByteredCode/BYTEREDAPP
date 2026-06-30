import logging
import re

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.blocklist import agregar_a_blocklist
from app.core.config import config
from app.core.security import (
    crear_access_token,
    crear_refresh_token,
    hash_contrasena,
    verificar_contrasena,
)
from app.models.usuario import Usuario

logger = logging.getLogger("byteredapp.auth")

# Separamos la lógica de auth de los endpoints HTTP para poder testearla
# de forma unitaria y reutilizarla desde otros servicios (ej. registro desde admin)


async def registrar_usuario(db: AsyncSession, correo: str, contrasena: str, nombre: str, codigo_empresa: int) -> Usuario:
    # Validamos aquí la complejidad de la contraseña para tener la regla de negocio
    # centralizada en el servicio, no dispersa entre el endpoint y otras posibles llamadas
    if len(contrasena) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contrasena debe tener al menos 8 caracteres",
        )
    if not re.search(r"[A-Z]", contrasena) or not re.search(r"[0-9]", contrasena):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contrasena debe tener al menos una mayuscula y un numero",
        )
    # Verificamos unicidad de correo antes de insertar para evitar la violación de
    # la constraint única y poder devolver un mensaje claro al usuario
    existe = await db.execute(select(Usuario).where(Usuario.correo == correo))
    if existe.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado",
        )
    usuario = Usuario(
        correo=correo,
        contrasena=hash_contrasena(contrasena),  # Hash antes de persistir: nunca almacenamos texto plano
        nombre=nombre,
        codigo_empresa=codigo_empresa,  # codigo_empresa como tenant: aísla los datos de cada empresa por fila
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario


async def iniciar_sesion(db: AsyncSession, correo: str, contrasena: str) -> dict:
    resultado = await db.execute(select(Usuario).where(Usuario.correo == correo))
    usuario = resultado.scalar_one_or_none()
    # Comprobamos existencia Y contraseña en un solo paso para no revelar
    # si el correo existe o no (protección contra enumeración de usuarios)
    if not usuario or not verificar_contrasena(contrasena, usuario.contrasena):
        logger.warning("Login fallido: correo %s", correo)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    logger.info("Login exitoso: usuario %s, empresa %s", usuario.codigo_usuario, usuario.codigo_empresa)
    # Incluimos 'empresa' en el access_token para que el middleware de tenant
    # pueda filtrar cada query sin consultar la BD en cada request
    access_token = crear_access_token({"sub": str(usuario.codigo_usuario), "empresa": usuario.codigo_empresa})
    # El refresh_token solo lleva 'sub' porque su única función es renovar
    # tokens; no necesita datos de tenant, ya que al refrescar se genera
    # un nuevo access_token con la empresa extraída del usuario en BD
    refresh_token = crear_refresh_token({"sub": str(usuario.codigo_usuario)})
    return {
        "usuario": usuario,
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
    }


async def cerrar_sesion(db: AsyncSession, refresh_token: str, access_token: str) -> None:
    for token_str in (refresh_token, access_token):
        if not token_str:
            continue
        try:
            payload = jwt.decode(token_str, config.JWT_SECRET, algorithms=["HS256"], options={"verify_exp": False})
            jti = payload.get("jti")
            if jti:
                await agregar_a_blocklist(jti)
        except JWTError:
            logger.warning("Token invalido ignorado durante logout")
    logger.info("Sesion cerrada: tokens invalidados")
