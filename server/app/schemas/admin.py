from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# ── Schemas de administración ─────────────────────────────────────────
# Todos los responses usan from_attributes para convertir modelos
# SQLAlchemy directamente sin serialización manual.


class EmpresaCreate(BaseModel):
    nombre: str
    # web es opcional porque una empresa puede no tener sitio externo;
    # el None se almacenará como NULL en la BD.
    web: Optional[str] = None


class EmpresaUpdate(BaseModel):
    # Todos los campos opcionales para actualización parcial (PATCH).
    # Si usáramos campos obligatorios obligaríamos al cliente a enviar
    # datos que quizá no quiere modificar (sobrescritura indeseada).
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
    contrasena: str = Field(min_length=8)
    nombre: str
    codigo_empresa: int
    # El rol por defecto es "usuario" para que, si el admin no lo
    # especifica, el nuevo usuario no herede privilegios no deseados.
    # Validación explícita de enum para evitar inyección de valores inválidos
    rol: str = Field(default="usuario", pattern=r"^(admin_total|admin_empresa|usuario)$")


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    contrasena: Optional[str] = None
    rol: Optional[str] = Field(default=None, pattern=r"^(admin_total|admin_empresa|usuario)$")


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
    # Schema auxiliar para las estadísticas: representa una fila genérica
    # del tipo {clave: "admin", total: 5}. Reutilizable para roles,
    # estados de tickets, columnas de tareas, etc.
    clave: str
    total: int


from fastapi import Query


class Paginacion:
    def __init__(self, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
        self.skip = skip
        self.limit = limit


class AdminStatsResponse(BaseModel):
    total_empresas: int
    total_usuarios: int
    # Las listas de ConteoPorClave permiten que el endpoint decida
    # qué agrupaciones devolver sin tener que crear un schema distinto
    # para cada tipo de conteo (DRY).
    usuarios_por_rol: list[ConteoPorClave]
    tickets_por_estado: list[ConteoPorClave]
    empresas_sin_web: int
    tareas_por_columna: list[ConteoPorClave]
    tickets_ultimo_mes: int
