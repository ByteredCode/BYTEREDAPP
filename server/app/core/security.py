import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_token_blocklist: set[str] = set()


def esta_en_blocklist(jti: str) -> bool:
    return jti in _token_blocklist


def agregar_a_blocklist(jti: str) -> None:
    _token_blocklist.add(jti)


def hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)


def verificar_contrasena(contrasena: str, hash: str) -> bool:
    return pwd_context.verify(contrasena, hash)


def crear_access_token(data: dict) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"jti": uuid.uuid4().hex, "exp": exp, "tipo": "access"})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")


def crear_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(
        days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"jti": uuid.uuid4().hex, "exp": exp, "tipo": "refresh"})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")


def decodificar_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        jti = payload.get("jti")
        if jti and esta_en_blocklist(jti):
            return None
        return payload
    except JWTError:
        return None
