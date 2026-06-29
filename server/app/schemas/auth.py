from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    correo: EmailStr
    contrasena: str = Field(min_length=8)
    nombre: str
    codigo_empresa: int


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    codigo_usuario: int
    correo: str
    nombre: str
    rol: str
    codigo_empresa: int

    model_config = {"from_attributes": True}
