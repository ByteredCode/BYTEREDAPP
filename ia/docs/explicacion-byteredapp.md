# CLASE: Arquitectura y Funcionamiento Completo de BYTEREDAPP

## Tema 1: Arquitectura General

### 1.1 Visión Macro

BYTEREDAPP es una **aplicación monolítica modular** con separación clara frontend/backend. Imagina un edificio de oficinas: el edificio es el monolito, pero cada piso (módulo) funciona de forma independiente.

```
┌─────────────────────────────────────────────────────────┐
│                      USUARIO                            │
│                  (navegador web)                        │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (HTTPS en producción)
                       ▼
┌─────────────────────────────────────────────────────────┐
│              FRONTEND — React + Vite                    │
│         JavaScript puro (sin TypeScript)                │
│         CSS plano (sin Tailwind)                        │
│         Desplegado en Hostinger                         │
│                                                         │
│  AuthContext ──► Axios (interceptores JWT) ──► API      │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API (JSON)
                       ▼
┌─────────────────────────────────────────────────────────┐
│              BACKEND — FastAPI (Python 3.11+)           │
│                                                         │
│  Router ──► Dependency Injection ──► Service ──► Model   │
│       │            │                      │             │
│   Rate Limit   JWT Auth            SQLAlchemy ORM       │
│   CORS/HTTPS   Tenant Filter       Async/Await         │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
        ┌──────────┐     ┌──────────┐
        │  MySQL 8 │     │  Redis   │
        │  (datos) │     │(blocklist│
        │          │     │  JWT)    │
        └──────────┘     └──────────┘
```

### 1.2 Stack Tecnológico y Por Qué

| Capa | Tecnología | Por qué |
|---|---|---|
| Frontend | React + JavaScript | Facilidad de adopción, ecosistema enorme |
| HTTP Client | Axios con interceptores | Manejo automático de JWT y refresh token |
| Backend | FastAPI | Asíncrono nativo, alto rendimiento, auto-docs |
| ORM | SQLAlchemy (async con aiomysql) | Mapeo objeto-relacional, tipado, seguridad contra SQL injection |
| BD | MySQL 8 | ACID, soporte multi-tenant por fila, maduro |
| Cache/Bloqueo | Redis (fallback a memoria) | Persistencia distribuida para blocklist JWT |
| Email | Resend API (HTTPS) | Servicio gestionado, no bloquea el event loop |
| Auth | JWT (HS256) | Stateless, escalable, estándar de la industria |

### 1.3 El Punto de Entrada: `run.py`

```python
# run.py — El corazón de la aplicación
app = FastAPI(title="BYTEREDAPP API", lifespan=lifespan)

# 1. CORS: permite peticiones desde el frontend
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, ...)

# 2. Rate limiting: previene abusos
app.add_middleware(SlowAPIMiddleware)

# 3. Headers de seguridad: CSP, HSTS, X-Frame-Options
app.add_middleware(BaseHTTPMiddleware, dispatch=seguridad_headers_middleware)

# 4. Rutas agrupadas bajo /api/v1
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth_router)      # /api/v1/auth/*
api_v1.include_router(admin_router)     # /api/v1/admin/*
api_v1.include_router(scrum_router)     # /api/v1/scrum/*
api_v1.include_router(tickets_router)   # /api/v1/tickets/*
api_v1.include_router(documentos_router)# /api/v1/documentos/*
```

**Concepto clave:** El `lifespan` es un context manager asíncrono que se ejecuta al arrancar y apagar la app. Aquí se cierra la conexión a Redis gracefully.

---

## Tema 2: La Autenticación JWT (El Sistema de Seguridad)

### 2.1 Qué es JWT y Por Qué

Un **JSON Web Token** es como un pasaporte digital. En vez de enviar usuario y contraseña en cada petición, el servidor entrega un "pasaporte firmado" que el cliente muestra en cada request.

Estructura de un JWT:
```
HEADER.PAYLOAD.SIGNATURE
eyJhbGci...    .eyJzdWIi...    .HMAC-SHA256...
   │               │                │
 Algoritmo     Datos del usuario   Firma digital
 (HS256)       (ID, empresa,       (verifica que
                expiración,         nadie lo
                jti único)          modificó)
```

### 2.2 Flujo Completo de Login

```
USUARIO                    FRONTEND                     BACKEND                    BD
   │                          │                            │                        │
   │  1. Escribe email + pass │                            │                        │
   │─────────────────────────►│                            │                        │
   │                          │                            │                        │
   │  2. Click "Entrar"       │                            │                        │
   │─────────────────────────►│  POST /auth/login          │                        │
   │                          │  {correo, contrasena}      │                        │
   │                          │───────────────────────────►│                        │
   │                          │                            │  3. SELECT usuario     │
   │                          │                            │     WHERE correo=?     │
   │                          │                            │───────────────────────►│
   │                          │                            │  4. Devuelve usuario   │
   │                          │                            │◄───────────────────────│
   │                          │                            │                        │
   │                          │                            │  5. bcrypt.verify()    │
   │                          │                            │     (compara hash)     │
   │                          │                            │                        │
   │                          │  6. TokenResponse:         │                        │
   │                          │  {access_token,            │                        │
   │                          │   refresh_token,           │                        │
   │                          │   usuario}                 │                        │
   │                          │◄───────────────────────────│                        │
   │                          │                            │                        │
   │  7. Guarda tokens en     │                            │                        │
   │     localStorage         │                            │                        │
   │  8. setUsuario()         │                            │                        │
   │◄─────────────────────────│                            │                        │
   │  9. navigate("/dashboard")│                           │                        │
```

### 2.3 Código Explicado: El Interceptor de Axios

Este es el componente **más inteligente** del frontend:

```javascript
// client/src/api/axios.js

// 1. INTERCEPTOR DE PETICIONES: adjunta el token automáticamente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 2. INTERCEPTOR DE RESPUESTAS: maneja el refresh token
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401 && !peticionOriginal._retry) {
      if (refrescando) {
        return new Promise((resolve, reject) => {
          colaPeticiones.push({ resolve, reject })
        }).then((token) => {
          peticionOriginal.headers.Authorization = `Bearer ${token}`
          return api(peticionOriginal)
        })
      }
      refrescando = true
      const refreshToken = localStorage.getItem("refresh_token")
      const res = await api.post("/auth/refresh", { refresh_token: refreshToken })
      const nuevoAccess = res.data.access_token
      localStorage.setItem("access_token", nuevoAccess)
      procesarCola(null, nuevoAccess)
      peticionOriginal.headers.Authorization = `Bearer ${nuevoAccess}`
      return api(peticionOriginal)
    }
  }
)
```

**Analogía:** Es como un traductor automático. Si el embassy (backend) dice "tu pasaporte expiró", el traductor (interceptor) va silenciosamente a renovarlo y reintenta la conversación sin que te des cuenta.

### 2.4 Código Explicado: Creación de Tokens

```python
# server/app/core/security.py

def crear_access_token(data: dict) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({
        "jti": uuid.uuid4().hex,
        "exp": exp,
        "tipo": "access"
    })
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")

# Payload del access token:
# {
#   "sub": "42",           ← ID del usuario (subject)
#   "empresa": 7,          ← company_id para multi-tenant
#   "jti": "a1b2c3...",    ← ID único del token
#   "exp": 1720000000,     ← Timestamp de expiración
#   "tipo": "access"       ← Tipo de token
# }
```

**¿Por qué dos tokens?**
- **Access token** (30 min): Se usa en cada petición. Corta duración = menor ventana de ataque.
- **Refresh token** (7 días): Solo se usa cuando el access token expira. Mayor duración = mejor UX.

### 2.5 La Blocklist de Redis

```
¿Qué pasa si un usuario cierra sesión o un token es comprometido?

Sin blocklist: El token sigue siendo válido hasta que expire.
Con blocklist: Invalidamos el token inmediatamente.

Flujo:
1. Usuario hace logout → POST /auth/logout
2. Backend extrae el JTI (ID único) del token
3. Agrega el JTI a Redis: SET bl:{jti} "1" EX 604800  (7 días)
4. Cada petición futura verifica: ¿está mi JTI en la blocklist?
   → Si sí: rechazar (token invalidado)
   → Si no: aceptar
```

```python
# server/app/core/blocklist.py
async def esta_en_blocklist(jti: str) -> bool:
    r = await get_conexion()
    if r:
        return await r.exists(f"bl:{jti}")
    return jti in _token_blocklist

async def agregar_a_blocklist(jti: str, ttl: int = 604800) -> None:
    r = await get_conexion()
    if r:
        await r.set(f"bl:{jti}", "1", ex=ttl)
    else:
        _token_blocklist.add(jti)
```

**Patrón de diseño:** Fallback pattern. Si Redis no está disponible, degradamos gracefully a memoria en vez de romper la app.

---

## Tema 3: El Sistema Multi-Tenant

### 3.1 Concepto

**Multi-tenant** significa que una sola instancia de la aplicación sirve a múltiples empresas, pero cada empresa solo ve SUS datos. Es como un edificio de departamentos: todos comparten la misma estructura, pero cada departamento tiene sus propias habitaciones.

### 3.2 Cómo Funciona en BYTEREDAPP

```
JWT contiene: {"sub": "42", "empresa": 7}

Cada tabla tiene: codigo_empresa (FK → empresa.codigo_empresa)

Middleware: Extrae "empresa" del JWT → inyecta en cada query

Resultado: SELECT * FROM tareas WHERE codigo_empresa = 7
           (Nunca ves tareas de otra empresa)
```

### 3.3 Código: La Dependencia de Tenant

```python
# server/app/core/dependencies.py

def get_tenant_filter(usuario: Usuario = Depends(get_usuario_actual)) -> int:
    return usuario.codigo_empresa

# En cualquier endpoint:
@router.get("/tablero")
async def get_tablero(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await obtener_tablero(db, codigo_empresa)
```

### 3.4 Código: Cada Query Filtra Automáticamente

```python
# server/app/services/scrum_service.py

async def listar_tareas(db: AsyncSession, codigo_empresa: int) -> list[Tarea]:
    query = select(Tarea).where(Tarea.codigo_empresa == codigo_empresa)
    query = query.order_by(Tarea.columna, Tarea.orden)
    resultado = await db.execute(query)
    return resultado.scalars().all()
```

### 3.5 El Modelo de Base de Datos

```sql
CREATE TABLE empresa (
    codigo_empresa INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL
);

CREATE TABLE usuario (
    codigo_usuario INT PRIMARY KEY AUTO_INCREMENT,
    correo VARCHAR(150) UNIQUE NOT NULL,
    codigo_empresa INT NOT NULL,
    FOREIGN KEY (codigo_empresa) REFERENCES empresa(codigo_empresa) ON DELETE CASCADE
);

CREATE TABLE tareas (
    codigo_tarea INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    columna ENUM('Todo', 'Haciendose', 'En revision', 'Done'),
    codigo_empresa INT NOT NULL,
    FOREIGN KEY (codigo_empresa) REFERENCES empresa(codigo_empresa) ON DELETE CASCADE
);

CREATE TABLE tickets (
    id_reporte INT PRIMARY KEY AUTO_INCREMENT,
    mensaje TEXT NOT NULL,
    codigo_empresa INT NOT NULL,
    FOREIGN KEY (codigo_empresa) REFERENCES empresa(codigo_empresa) ON DELETE CASCADE
);
```

**CASCADE:** Al eliminar una empresa, TODAS sus filas se borran automáticamente.

---

## Tema 4: Sistema de Feature Flags

### 4.1 Concepto

Las **feature flags** permiten activar/desactivar módulos por empresa sin modificar código.

### 4.2 Tabla de Feature Flags

```sql
CREATE TABLE empresa_servicios (
    codigo_empresa INT,
    servicio VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (codigo_empresa, servicio)
);
```

### 4.3 Código: La Dependencia `require_servicio`

```python
# server/app/core/dependencies.py

def require_servicio(nombre_servicio: str):
    async def _check(
        usuario: Usuario = Depends(get_usuario_actual),
        db: AsyncSession = Depends(get_db)
    ):
        if usuario.rol in ("admin_total", "admin_empresa"):
            return
        resultado = await db.execute(
            select(EmpresaServicio).where(
                EmpresaServicio.codigo_empresa == usuario.codigo_empresa,
                EmpresaServicio.servicio == nombre_servicio,
                EmpresaServicio.activo == True,
            ).limit(1)
        )
        if not resultado.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail=f"El servicio {nombre_servicio} no está activo para tu empresa"
            )
    return _check
```

### 4.4 Cómo se Usa en los Endpoints

```python
router = APIRouter(
    prefix="/scrum",
    dependencies=[Depends(require_servicio("scrum"))],
)
```

### 4.5 Flujo Completo

```
Empresa crea cuenta → Se activan TODOS los módulos por defecto
Admin desactiva "tickets"
Usuario intenta ver tickets → 403 Forbidden
```

---

## Tema 5: Módulo Scrum (Tablero Kanban)

### 5.1 Modelos de Datos

```python
class Sprint(Base):
    codigo_sprint = Column(Integer, primary_key=True)
    nombre = Column(String(150))
    estado = Column(Enum("Planificado", "Activo", "Completado"))
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa"))

class Tarea(Base):
    codigo_tarea = Column(Integer, primary_key=True)
    titulo = Column(String(200))
    columna = Column(Enum("Todo", "Haciendose", "En revision", "Done"))
    orden = Column(Integer)
    prioridad = Column(Enum("Baja", "Media", "Alta", "Critica"))
    asignacion = Column(Integer, ForeignKey("usuario.codigo_usuario"))
    codigo_sprint = Column(Integer, ForeignKey("sprints.codigo_sprint"))
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa"))
```

### 5.2 Flujo de Drag and Drop

```
USUARIO arrastra tarea "Fix login" de "Haciendose" a "Done"
   │
   ▼
BOARD.jsx calcula la nueva posición
   │
   ▼
PUT /api/v1/scrum/tareas/42/mover
Body: { "columna": "Done", "orden": 3 }
   │
   ▼
scrum_service.mover_tarea(db, 42, "Done", 3, empresa_id)
   │  - SELECT * FROM tareas WHERE codigo_tarea=42 AND codigo_empresa=?
   │  - UPDATE tareas SET columna='Done', orden=3
   │  - await db.commit()
   │
   ▼
BOARD.jsx actualiza el estado local (optimistic update)
   │  - La tarea aparece en "Done" instantáneamente
   │  - Si falla el PUT, se revierte con fetchTablero()
```

### 5.3 Código del Drag & Drop (Board.jsx)

```javascript
async function handleDragEnd(event) {
  const { active, over } = event

  // 1. Determinar columna destino y posición
  if (COLUMNAS.some((c) => c.id === over.id)) {
    columnaDestino = over.id
    nuevoOrden = columnas[over.id]?.length || 0
  } else {
    const tareaOver = todasLasTareas.find((t) => t.codigo_tarea === over.id)
    columnaDestino = tareaOver.columna
    nuevoOrden = columnas[columnaDestino]?.findIndex((t) => t.codigo_tarea === over.id)
  }

  // 2. Actualización optimista (instantánea)
  const nuevas = { ...columnas }
  for (const col of Object.keys(nuevas)) {
    nuevas[col] = nuevas[col].filter((t) => t.codigo_tarea !== tareaId)
  }
  const itemActualizado = { ...tareaMovida, columna: columnaDestino, orden: nuevoOrden }
  nuevas[columnaDestino].splice(nuevoOrden, 0, itemActualizado)
  setColumnas(nuevas)

  // 3. Persistir en el backend
  try {
    await api.put(`/scrum/tareas/${tareaId}/mover`, {
      columna: columnaDestino,
      orden: itemActualizado.orden
    })
  } catch {
    fetchTablero()
  }
}
```

**Patrón de diseño:** Optimistic Update. Actualizas la UI primero y si el backend falla, reviertes.

---

## Tema 6: Módulo de Tickets

### 6.1 Flujo Completo

```
USUARIO (autenticado o anónimo)                  BACKEND                      EMAIL
   │                                               │                            │
   │ 1. Rellena formulario                         │                            │
   │ 2. Click "Enviar ticket"                      │                            │
   │──────────────────────────────────────────────►│                            │
   │                                               │ 3. Si anónimo: validar empresa
   │                                               │ 4. INSERT INTO tickets     │
   │                                               │ 5. COMMIT                  │
   │                                               │ 6. enviar_correo() ───────►│
   │                                               │                            │ 7. Resend API
   │  ◄────────────────────────────────────────────│                            │
   │  TicketResponse { id, estado, fecha }         │                            │
```

### 6.2 Código del Endpoint

```python
@router.post("", response_model=TicketResponse, status_code=201)
@limiter.limit("10/minute")
async def post_ticket(
    request: Request,
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Optional[Usuario] = Depends(get_usuario_opcional),
):
    if not usuario:
        existe_empresa = await db.execute(
            select(Empresa).where(Empresa.codigo_empresa == data.codigo_empresa)
        )
        if not existe_empresa.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Empresa no válida")

    codigo_usuario = usuario.codigo_usuario if usuario else None
    ticket = await crear_ticket(db, data, codigo_usuario)

    if config.TICKETS_EMAIL:
        await enviar_correo(config.TICKETS_EMAIL, f"Nuevo ticket: {ticket.asunto}", ...)

    return ticket
```

### 6.3 El Servicio de Email (Resend)

```python
async def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_enviar_correo_sync, ...))
```

**Concepto clave:** `run_in_executor` es el puente entre el mundo síncrono (Resend SDK) y el asíncrono (FastAPI).

---

## Tema 7: Módulo de Documentos

### 7.1 Flujo Completo de Subida

```
USUARIO                                         BACKEND                     DISCO
   │                                               │                          │
   │ POST /documentos                              │                          │
   │ Content-Type: multipart/form-data             │                          │
   │──────────────────────────────────────────────►│                          │
   │                                               │ 4. Validar tipo MIME     │
   │                                               │ 5. Validar extensión     │
   │                                               │ 6. Validar tamaño ≤10MB  │
   │                                               │ 7. os.makedirs()         │──►
   │                                               │ 8. Generar nombre único  │
   │                                               │ 9. Guardar archivo       │──►
   │                                               │ 10. INSERT documentos    │
   │                                               │ 11. COMMIT               │
   │  ◄────────────────────────────────────────────│                          │
```

### 7.2 Código del Servicio

```python
TIPOS_PERMITIDOS = {"application/pdf", "image/jpeg", "image/png", ...}
MAX_TAMANO = 10 * 1024 * 1024  # 10MB

async def subir_documento(db, archivo, tipo_documento, codigo_empresa, usuario_subio):
    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(400, f"Tipo no permitido: {archivo.content_type}")
    ext = os.path.splitext(archivo.filename)[1].lower()
    os.makedirs(os.path.join(DIRECTORIO_UPLOADS, str(codigo_empresa)), exist_ok=True)
    nombre_unico = f"{uuid.uuid4().hex}{ext}"
    contenido = await archivo.read()
    if len(contenido) > MAX_TAMANO:
        raise HTTPException(400, "El archivo supera el tamaño máximo de 10MB")
    with open(ruta_completa, "wb") as f:
        f.write(contenido)
    doc = Documento(nombre=archivo.filename, ...)
    db.add(doc)
    await db.commit()
    return doc
```

**¿Por qué no guardar el archivo en la BD?** Los binarios crecen la BD enormemente.

### 7.3 Sistema de Permisos de Documentos

```sql
CREATE TABLE documento_permisos (
    id_documento INT,
    codigo_usuario INT,
    PRIMARY KEY (id_documento, codigo_usuario)
);
```

**Lógica de acceso:**
| Rol | Acceso |
|---|---|
| `admin_total` | Todos los documentos de todas las empresas |
| `admin_empresa` | Todos los documentos de su empresa |
| `usuario` | Documentos que subió + documentos con permiso explícito |

---

## Tema 8: Módulo Admin (CRUD Completo)

### 8.1 Estructura de Permisos

```
admin_total: Ve TODAS las empresas, crea/edita/borra empresas y usuarios
admin_empresa: Ve SOLO su empresa, ve usuarios de SU empresa
usuario: Ve SOLO sus tareas, ve documentos con permiso
```

### 8.2 Flujo: Crear Empresa

```
POST /admin/empresas → Verificar rol → INSERT empresa → INSERT servicios por defecto → COMMIT
```

### 8.3 Código: Crear Empresa con Feature Flags

```python
SERVICIOS_POR_DEFECTO = ["scrum", "tickets", "documentacion", "redireccion"]

async def crear_empresa(db, data):
    empresa = Empresa(nombre=data.nombre, web=data.web)
    db.add(empresa)
    await db.flush()
    for servicio in SERVICIOS_POR_DEFECTO:
        db.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio=servicio, activo=True))
    await db.commit()
    return empresa
```

### 8.4 Flujo: Toggle de Servicio

```
PUT /admin/empresas/3/servicios → ¿Existe? → UPDATE o INSERT → COMMIT
```

---

## Tema 9: El Módulo de Redirección

### 9.1 Concepto

Endpoint público (sin auth) que redirige a la web de una empresa. Útil para códigos QR.

```
QR Code → /r/5 → Redirige a https://acme.com
```

### 9.2 Protecciones de Seguridad

```python
@router.get("/r/{codigo_empresa}")
async def redirigir(codigo_empresa: int, db: AsyncSession = Depends(get_db)):
    empresa = await db.execute(select(Empresa).where(Empresa.codigo_empresa == codigo_empresa))
    if not empresa or not empresa.web:
        raise HTTPException(404, "Empresa o enlace no configurado")
    svc = await db.execute(select(EmpresaServicio).where(...))
    if not svc.scalar_one_or_none():
        raise HTTPException(404, "Servicio no disponible")
    parsed = urlparse(empresa.web)
    if parsed.scheme not in ("https", "http"):
        raise HTTPException(400, "URL no válida")
    if not _es_url_segura(empresa.web):
        raise HTTPException(400, "URL no permitida")
    return RedirectResponse(url=empresa.web)
```

**¿Qué es SSRF?** Server-Side Request Forgery. La validación de IP previene que el servidor acceda a IPs internas.

---

## Tema 10: Protección de Rutas en el Frontend

### 10.1 El Sistema de Guards

```javascript
// ProtectedRoute.jsx
export default function ProtectedRoute({ children }) {
  const { usuario, cargando } = useAuth()
  if (cargando) return <p>Cargando...</p>
  if (!usuario) return <Navigate to="/login" replace />
  return children
}

// AdminOnlyRoute.jsx
export default function AdminOnlyRoute({ children }) {
  const { usuario, cargando } = useAuth()
  if (cargando) return <p>Cargando...</p>
  if (!usuario) return <Navigate to="/login" replace />
  if (usuario.rol !== "admin_total" && usuario.rol !== "admin_empresa")
    return <Navigate to="/dashboard" replace />
  return children
}
```

### 10.2 Árbol de Rutas

```
/ (RootRedirect)
├── /login (pública)
├── /register (pública)
├── /tickets/nuevo (pública)
│
└── Layout (navbar)
    ├── /dashboard [ProtectedRoute]
    ├── /mi-empresa [ProtectedRoute]
    ├── /scrum [ProtectedRoute]
    │   ├── /scrum/tablero [Board]
    │   └── /scrum/sprints [Sprints]
    │
    └── /admin [AdminOnlyRoute]
        ├── /admin/empresas [Empresas]
        ├── /admin/usuarios [Usuarios]
        ├── /admin/tickets [TicketsAdmin]
        └── /admin/documentos [DocumentosAdmin]
```

---

## Tema 11: El Patrón de Capas (Resumen)

```
FRONTEND
  Página → Context → Axios (interceptors) → API REST
         │
BACKEND
  Router → Dependencies (auth, tenant, feature flags) → Service → Model
         │
BD
  MySQL 8 (datos) + Redis (blocklist JWT)
```

---

## Tema 12: Buenas Prácticas Aplicadas

| Práctica | Dónde se aplica | Por qué |
|---|---|---|
| **Singleton** | `config.py` | Una sola instancia de configuración |
| **Dependency Injection** | FastAPI `Depends()` | Desacoplamiento, testabilidad |
| **Repository Pattern** | Services separados de routers | Lógica reutilizable y testeable |
| **Optimistic Update** | Board.jsx drag & drop | UI instantánea, se revierte si falla |
| **Fallback Pattern** | Redis blocklist → memoria | Graceful degradation |
| **Rate Limiting** | slowapi en endpoints sensibles | Previene abusos |
| **CORS** | Middleware en run.py | Solo permite peticiones desde el frontend |
| **Security Headers** | Middleware de headers | CSP, HSTS, X-Frame-Options |
| **Cascade Delete** | FK con `ondelete="CASCADE"` | Elimina datos dependientes automáticamente |
| **Soft Delete** | Tickets (estado=Cerrado) | Mantiene histórico sin borrar |
