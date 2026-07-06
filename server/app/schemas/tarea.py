from datetime import date
from typing import Optional

from pydantic import BaseModel

# ── Schemas del módulo Scrum (tareas + sprints) ───────────────────────
# Separamos los schemas de creación, actualización y respuesta para:
# 1) No exponer campos internos (orden, codigo_empresa) en la creación.
# 2) Permitir actualizaciones parciales sin sobrescritura (todos Optional).
# 3) Tener un schema específico para mover tareas (drag & drop) que solo
#    acepte los campos necesarios, evitando cambios accidentales en otros.


class TareaCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    prioridad: Optional[str] = "Media"
    # 'Todo' es la columna por defecto: en el tablero Kanban toda tarea
    # nueva empieza siempre en "Por hacer", luego se mueve con drag & drop.
    columna: Optional[str] = "Todo"
    fecha_limite: Optional[date] = None
    asignacion: Optional[int] = None
    codigo_sprint: Optional[int] = None


class TareaUpdate(BaseModel):
    # Todos los campos opcionales: así el frontend puede enviar solo lo
    # que cambió (por ej. solo el título) sin tener que reenviar todo.
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    columna: Optional[str] = None
    orden: Optional[int] = None
    fecha_limite: Optional[date] = None
    asignacion: Optional[int] = None
    codigo_sprint: Optional[int] = None


class TareaMover(BaseModel):
    # Schema específico para drag & drop: solo recibimos columna
    # destino + nueva posición. Así el frontend no puede modificar
    # título, prioridad, etc. por accidente al reposicionar.
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
    estado: Optional[str] = "Planificado"


class SprintUpdate(BaseModel):
    nombre: Optional[str] = None
    objetivo: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    # El estado del sprint solo se actualiza desde el backend cuando
    # se inicia (Activo) o se completa (Completado), pero permitimos
    # que el admin lo fuerce manualmente si es necesario.
    estado: Optional[str] = None


class SprintResponse(BaseModel):
    codigo_sprint: int
    nombre: str
    objetivo: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: str
    codigo_empresa: int

    model_config = {"from_attributes": True}
