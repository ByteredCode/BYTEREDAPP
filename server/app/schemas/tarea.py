from datetime import date
from typing import Optional

from pydantic import BaseModel


class TareaCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    prioridad: Optional[str] = "Media"
    columna: Optional[str] = "Todo"  # Columna inicial en el Kanban
    fecha_limite: Optional[date] = None
    asignacion: Optional[int] = None
    codigo_sprint: Optional[int] = None


class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    columna: Optional[str] = None
    orden: Optional[int] = None
    fecha_limite: Optional[date] = None
    asignacion: Optional[int] = None
    codigo_sprint: Optional[int] = None


class TareaMover(BaseModel):
    # Schema especifico para drag & drop: solo columna destino + posicion
    columna: str
    orden: int


class TareaResponse(BaseModel):
    codigo_tarea: int
    titulo: str
    descripcion: Optional[str] = None
    prioridad: str
    columna: str
    orden: int
    fecha_limite: Optional[date] = None
    asignacion: Optional[int] = None
    codigo_sprint: Optional[int] = None
    codigo_empresa: int

    model_config = {"from_attributes": True}


class SprintCreate(BaseModel):
    nombre: str
    objetivo: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class SprintUpdate(BaseModel):
    nombre: Optional[str] = None
    objetivo: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None  # Planificado, Activo, Completado


class SprintResponse(BaseModel):
    codigo_sprint: int
    nombre: str
    objetivo: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: str
    codigo_empresa: int

    model_config = {"from_attributes": True}
