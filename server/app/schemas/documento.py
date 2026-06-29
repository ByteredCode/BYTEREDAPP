from datetime import date
from typing import Optional

from pydantic import BaseModel


class DocumentoResponse(BaseModel):
    id_documento: int
    nombre: str  # Nombre original del archivo
    codigo_empresa: int
    usuario_subio: int
    fecha: date
    tipo_documento: Optional[str] = None  # DPD o ISO
    ruta_archivo: Optional[str] = None  # Ruta interna en disco

    model_config = {"from_attributes": True}


class PermisoAgregar(BaseModel):
    codigo_usuario: int  # ID del usuario a quien se da permiso


class PermisoResponse(BaseModel):
    id_documento: int
    codigo_usuario: int

    model_config = {"from_attributes": True}
