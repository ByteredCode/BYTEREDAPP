from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TicketCreate(BaseModel):
    # Campos opcionales para tickets anonimos (sin autenticacion)
    nombre_contacto: Optional[str] = None
    correo_contacto: Optional[str] = None
    asunto: Optional[str] = None
    nivel_importancia: str = "Media"
    mensaje: str  # Unico campo obligatorio
    codigo_empresa: int


class TicketUpdateEstado(BaseModel):
    estado: str
    respuesta: Optional[str] = None


class TicketResponse(BaseModel):
    id_reporte: int
    codigo_usuario: Optional[int] = None
    nombre_contacto: Optional[str] = None
    correo_contacto: Optional[str] = None
    asunto: Optional[str] = None
    nivel_importancia: str
    mensaje: str
    codigo_empresa: int
    estado: str
    fecha_reporte: Optional[datetime] = None
    respuesta: Optional[str] = None
    fecha_respuesta: Optional[datetime] = None

    model_config = {"from_attributes": True}
