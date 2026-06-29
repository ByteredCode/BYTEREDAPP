from typing import Optional

from pydantic import BaseModel, EmailStr


class EmpresaCreate(BaseModel):
    nombre: str
    web: Optional[str] = None


class EmpresaUpdate(BaseModel):
    # Todos los campos opcionales para actualizacion parcial (PATCH)
    nombre: Optional[str] = None
    codigo_scrum: Optional[str] = None
    usuario_admin_dpd: Optional[int] = None
    web: Optional[str] = None


class EmpresaResponse(BaseModel):
    codigo_empresa: int
    nombre: str
    codigo_scrum: Optional[str] = None
    usuario_admin_dpd: Optional[int] = None
    web: Optional[str] = None

    model_config = {"from_attributes": True}


class UsuarioCreate(BaseModel):
    correo: EmailStr
    contrasena: str
    nombre: str
    codigo_empresa: int
    rol: str = "usuario"


class UsuarioUpdate(BaseModel):
    # Sin contrasena: en edicion se deja vacia para no sobrescribir
    nombre: Optional[str] = None
    rol: Optional[str] = None


class UsuarioAdminResponse(BaseModel):
    codigo_usuario: int
    correo: str
    nombre: str
    rol: str
    codigo_empresa: int

    model_config = {"from_attributes": True}


class ServicioToggle(BaseModel):
    servicio: str
    activo: bool


class ServicioResponse(BaseModel):
    codigo_empresa: int
    servicio: str
    activo: bool

    model_config = {"from_attributes": True}


class ConteoPorClave(BaseModel):
    clave: str
    total: int


class AdminStatsResponse(BaseModel):
    total_empresas: int
    total_usuarios: int
    usuarios_por_rol: list[ConteoPorClave]
    tickets_por_estado: list[ConteoPorClave]
    fichajes_abiertos: int
    empresas_sin_web: int
    tareas_por_columna: list[ConteoPorClave]
    tickets_ultimo_mes: int
