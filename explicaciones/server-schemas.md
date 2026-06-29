# Schemas Pydantic — Explicación Didáctica

## ¿Qué son los schemas Pydantic?

Pydantic es una librería de Python que permite definir **modelos de validación de datos**. Cada schema define:
1. La **estructura** de los datos que esperamos recibir (request) o devolver (response)
2. Las **validaciones** automáticas (tipos, formatos, valores requeridos)
3. La **serialización/deserialización** entre JSON y objetos Python

En FastAPI, los schemas se usan en tres lugares:
- **RequestBody**: validan la entrada del usuario
- **ResponseModel**: garantizan que la salida tenga la forma correcta
- **Documentación**: Swagger genera automáticamente la documentación a partir de ellos

---

## 1. `auth.py` — Autenticación

Cuatro schemas simples y fundamentales:

### `RegisterRequest`
```python
correo: EmailStr    # Valida formato de email automáticamente
contrasena: str      # Sin validación de complejidad (debilidad)
nombre: str
codigo_empresa: int
```
`EmailStr` es un validador especial de Pydantic que rechaza strings sin formato de email válido.

### `LoginRequest`
```python
correo: EmailStr
contrasena: str
```

### `TokenResponse`
```python
access_token: str
refresh_token: str
token_type: str = "bearer"   # Valor fijo, como dicta OAuth2
```

### `UsuarioResponse`
```python
model_config = {"from_attributes": True}  # Permite crear desde ORM
```
La clave es `from_attributes = True`: permite construir este schema directamente desde un objeto SQLAlchemy (`Usuario`). Sin esto, Pydantic no sabe cómo leer atributos de un modelo ORM.

---

## 2. `admin.py` — Administración

Schemas para el panel de administración (CRUD de empresas, usuarios y servicios).

### Empresa
- `EmpresaCreate`: nombre obligatorio, web opcional.
- `EmpresaUpdate`: todos los campos opcionales. El servicio usa `exclude_unset=True` para solo actualizar los campos enviados.
- `EmpresaResponse`: incluye `codigo_empresa` y `from_attributes`.

### Usuario (admin)
- `UsuarioCreate`: incluye `contrasena` (solo en creación).
- `UsuarioUpdate`: sin contraseña (no se puede cambiar desde el panel).
- `UsuarioAdminResponse`: igual que `UsuarioResponse` de auth pero para el contexto admin.

### Servicios
- `ServicioToggle`: dos campos: `servicio` (string con el nombre del módulo) y `activo` (bool).
- `ServicioResponse`: refleja el estado actual.

---

## 3. `tarea.py` — Tareas y Sprints (Scrum)

### Tarea
- **`TareaCreate`**: `titulo` obligatorio, el resto opcional con defaults. `columna` por defecto es "Todo" (primera columna del Kanban).
- **`TareaUpdate`**: todos los campos opcionales. El frontend envía solo lo que cambió.
- **`TareaMover`**: schema mínimo para drag & drop: solo `columna` y `orden`.
- **`TareaResponse`**: incluye todos los campos de la tarea más `codigo_empresa`.

### Sprint
- **`SprintCreate`**: nombre obligatorio, objetivo, fechas y estado opcionales.
- **`SprintUpdate`**: incluye `estado` (para cambiar entre Planificado/Activo/Completado).
- **`SprintResponse`**: devuelve el estado actual del sprint.

---

## 4. `ticket.py` — Tickets de soporte

- **`TicketCreate`**: El único campo obligatorio es `mensaje`. El resto son opcionales para permitir tickets anónimos sin autenticación. `codigo_empresa` es obligatorio para saber a qué empresa dirigir el ticket.
- **`TicketUpdateEstado`**: solo permite cambiar el `estado`.
- **`TicketResponse`**: incluye `fecha_reporte` (generada por la BD con `server_default`).

---

## 5. `fichaje.py` — Control horario

Schema mínimo: solo `FichajeResponse` con los campos del modelo. `hora_salida` es opcional (`None` = fichaje abierto).

---

## 6. `documento.py` — Documentos y permisos

- **`DocumentoResponse`**: metadatos del documento (nombre, tipo, fecha, ruta). No incluye el contenido binario.
- **`PermisoAgregar`**: solo el `codigo_usuario` a quien se le da permiso.
- **`PermisoResponse`**: refleja la relación documento-usuario.

---

## Buenas prácticas aplicadas

| Práctica | Ejemplo |
|---|---|
| **Validación de tipos** | `EmailStr`, `int`, `date`, `datetime` |
| **Campos opcionales** | `Optional[str] = None` para permitir valores nulos |
| **Valores por defecto** | `columna: str = "Todo"` en TareaCreate |
| **from_attributes** | Permite convertir ORM → schema automáticamente |
| **Schemas separados** | Create ≠ Update ≠ Response (principio de responsabilidad única) |
| **Exclude unset** | El servicio usa `exclude_unset=True` para parches parciales |

Cada schema es una **contrato** entre el frontend y el backend: define exactamente qué datos se esperan y qué forma tendrá la respuesta. FastAPI lo usa para generar automáticamente la validación y la documentación Swagger.
