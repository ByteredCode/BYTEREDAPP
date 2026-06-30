from pydantic import BaseModel, EmailStr, Field

# ── Schemas de autenticación ──────────────────────────────────────────
# Separamos los schemas de entrada (request) y salida (response) para
# que cada endpoint exponga exactamente los campos que necesita: el
# request solo acepta lo que envía el cliente, el response solo devuelve
# lo que el frontend debe ver (por ej. nunca devolvemos la contraseña).


class RegisterRequest(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=8)
    nombre: str
    codigo_empresa: int


class LoginRequest(BaseModel):
    correo: EmailStr
    # En login no repetimos min_length porque la validación fuerte solo
    # es necesaria en el registro; el backend ya sabe que existe ese usuario.
    contrasena: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    # El esquema OAuth2 exige este campo; lo fijamos con un valor
    # constante porque este backend solo emite tokens tipo "bearer".
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    codigo_usuario: int
    correo: str
    nombre: str
    rol: str
    codigo_empresa: int

    # from_attributes permite construir el schema directamente desde un
    # modelo SQLAlchemy (ej. db_user) sin mapear campo por campo.
    model_config = {"from_attributes": True}
