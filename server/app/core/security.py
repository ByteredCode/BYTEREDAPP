import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.blocklist import esta_en_blocklist
from app.core.config import config

# passlib con bcrypt: gestiona automaticamente el salt, el hash y la verificacion
# Usar bcrypt directamente requeriria manejar salt, iteraciones y timing attacks manualmente
# deprecated="auto" permite migrar de algoritmo sin romper hashes existentes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)


def verificar_contrasena(contrasena: str, hash: str) -> bool:
    return pwd_context.verify(contrasena, hash)


def crear_access_token(data: dict) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # UUID4 como jti (JWT ID): unico e impredecible, permite invalidar tokens especificos
    # Incluir "tipo" evita usar un refresh token como si fuese un access token
    to_encode.update({"jti": uuid.uuid4().hex, "exp": exp, "tipo": "access"})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")


def crear_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(
        days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    # Misma estructura que el access token pero con tipo "refresh"
    # Esto permite refresh token rotation: al renovar se invalida el anterior via blocklist
    to_encode.update({"jti": uuid.uuid4().hex, "exp": exp, "tipo": "refresh"})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")


async def decodificar_token(token: str) -> dict | None:
    try:
        # jwt.decode verifica firma y expiracion automaticamente
        # Si la firma no coincide o el token expiro, lanza JWTError
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        jti = payload.get("jti")
        # Consulta async a la blocklist (Redis o memoria) antes de aceptar el token
        # Asi los tokens invalidados manualmente no pueden reutilizarse
        if jti and await esta_en_blocklist(jti):
            return None
        return payload
    # JWTError engloba: expiracion, firma invalida, malformado, etc.
    except JWTError:
        return None
