# Explicación del núcleo del backend

## run.py — Punto de entrada

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="BYTEREDAPP API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### ¿Qué hace este archivo?

Es el **arranque de la aplicación**. Crea la instancia de FastAPI, configura CORS, monta los routers y define un endpoint de salud.

### lifespan

FastAPI tiene un **contexto de ciclo de vida** (`lifespan`). El bloque `yield` separa el código que se ejecuta al iniciar (antes de `yield`) del que se ejecuta al parar (después de `yield`). De momento no hay nada porque no necesitamos conexiones previas, pero aquí se añadirían tareas como conectar a Redis o inicializar pools de conexiones.

### CORS

```python
allow_origins=["http://localhost:5173"]
```

CORS (Cross-Origin Resource Sharing) es un mecanismo de seguridad del navegador. Cuando el frontend corre en `localhost:5173` (Vite) y hace peticiones a `localhost:8000` (FastAPI), el navegador bloquea la petición porque son orígenes diferentes. CORS le dice al navegador: "esta API confía en ese origen".

### include_router

Monta las rutas de `auth.py` bajo la aplicación principal. Cuando añadamos más módulos (scrum, tickets...), cada uno tendrá su propio router y se montará aquí.

### /health

Endpoint mínimo para verificar que el servidor responde. Útil para monitors de disponibilidad (health checks).

---

## config.py — Configuración centralizada

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "byteredapp"

    JWT_SECRET: str = "changeme"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMTP_HOST: str = ""
    SMTP_PORT: Optional[int] = None
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    TICKETS_EMAIL: str = "admin@byteredapp.com"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    model_config = {"env_file": "../.env", "case_sensitive": True, "extra": "ignore"}

config = Config()
```

### ¿Cómo funciona BaseSettings?

`BaseSettings` de `pydantic-settings` busca valores en este orden:
1. Variables de entorno del sistema
2. Archivo `.env` (especificado en `model_config`)
3. Valores por defecto en la clase

### El decorador @property (database_url)

Es una **propiedad calculada**. No se almacena en la BD ni en el .env. Cada vez que alguien accede a `config.database_url`, construye la URL de conexión completo a partir de las partes. Esto evita tener que mantener la URL de conexión como una variable separada.

### ¿Por qué `extra: "ignore"`?

El archivo `.env` está en la raíz del proyecto (`../.env` desde `server/`). Ese mismo `.env` contiene variables del frontend como `VITE_API_URL`. Sin `extra: "ignore"`, Pydantic lanzaría un error porque no reconoce esa variable.

### Instancia global `config = Config()`

Se crea **una única instancia** al importar el módulo. Cualquier archivo que haga `from app.core.config import config` obtiene la misma instancia (patrón singleton).

---

## database.py — Conexión a MySQL

```python
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import config

engine = create_async_engine(config.database_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
```

### create_async_engine

Crea el **motor de base de datos asíncrono**. La URL `mysql+aiomysql://user:pass@host:port/db` le dice a SQLAlchemy que use el driver `aiomysql` para conectar a MySQL.

`echo=False` — no imprime las consultas SQL en consola. En desarrollo se puede poner `True` para depurar.

### async_sessionmaker

Es una **fábrica de sesiones**. Cada vez que necesitas una sesión para hacer consultas, llamas a `async_session()` y te devuelve una nueva. `expire_on_commit=False` evita que SQLAlchemy invalide los objetos después de hacer commit (útil para devolver objetos en respuestas API).

### Clase Base

Es la clase base de la que heredan **todos los modelos**. `DeclarativeBase` es el nuevo estilo de SQLAlchemy 2.0 (antes se usaba `declarative_base()`). `AsyncAttrs` permite acceder a relaciones lazy de forma asíncrona.

### get_db() — Generador asíncrono

```python
async def get_db():
    async with async_session() as session:
        yield session
```

Usa `yield` en lugar de `return`. FastAPI lo trata como una **dependencia**: abre la sesión, la inyecta en el endpoint, y cuando el endpoint termina, cierra la sesión automáticamente. Es un patrón de **inyección de dependencias**.

---

## security.py — Autenticación (bcrypt + JWT)

```python
from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)

def verificar_contrasena(contrasena: str, hash: str) -> bool:
    return pwd_context.verify(contrasena, hash)

def crear_access_token(data: dict) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": exp, "tipo": "access"})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")

def crear_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(days=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": exp, "tipo": "refresh"})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")

def decodificar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        return None
```

### bcrypt — Hash de contraseñas

`CryptContext` de passlib es un **adaptador** que permite cambiar de algoritmo de hash sin modificar el código. Ahora usa bcrypt, pero si mañana queremos argon2, solo cambiamos `schemes=["argon2"]`.

**¿Por qué bcrypt?** Es un algoritmo **lento deliberadamente**. Mientras SHA256 puede calcular millones de hashes por segundo, bcrypt hace ~100 hashes/segundo. Esto hace que un ataque de fuerza bruta sea inviable incluso si roban la base de datos.

### JWT — Tokens

`crear_access_token` y `crear_refresh_token` hacen lo mismo pero con diferente tiempo de expiración y tipo. Ambos:
1. Copian los datos que se quieren incluir en el token
2. Añaden la expiración (`exp`) y el tipo (`tipo`)
3. Firman el token con el secreto usando HMAC-SHA256 (HS256)

`decodificar_token` hace lo contrario: verifica la firma y devuelve los datos. Si el token expiró o la firma no coincide, captura `JWTError` y devuelve `None`.

### ¿Por qué dos tokens?

El **access token** tiene corta duración (60 min) y viaja en cada petición. Si alguien lo intercepta, tiene una ventana de ataque limitada. El **refresh token** dura más (7 días) pero solo se usa para renovar el access token.

---

## dependencies.py — Dependencias de FastAPI

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decodificar_token
from app.models.usuario import Usuario

seguridad = HTTPBearer()

async def get_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(seguridad),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    payload = decodificar_token(credenciales.credentials)
    if payload is None or payload.get("tipo") != "access":
        raise HTTPException(status_code=401, detail="Token invalido")
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Token invalido")
    resultado = await db.execute(select(Usuario).where(Usuario.codigo_usuario == int(sub)))
    usuario = resultado.scalar_one_or_none()
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario

def get_tenant_filter(usuario: Usuario = Depends(get_usuario_actual)) -> int:
    return usuario.codigo_empresa
```

### HTTPBearer

FastAPI Security espera que el cliente envíe el token en el header `Authorization: Bearer <token>`. Si no lo envía, FastAPI devuelve 403 automáticamente.

### get_usuario_actual

Es un **guard** (protector) de endpoints. Cuando un endpoint tiene `usuario: Usuario = Depends(get_usuario_actual)`, antes de ejecutar el endpoint:
1. Extrae el token del header
2. Lo decodifica
3. Verifica que sea un access token
4. Busca el usuario en la BD
5. Si algo falla, lanza 401

**Observación:** `int(sub)` — el claim `sub` en JWT debe ser string (estándar), pero en la BD es un entero. Se convierte al vuelo.

### get_tenant_filter

Prepara el filtro multi-tenant. Cuando construyamos consultas para otras tablas, inyectaremos `codigo_empresa = get_tenant_filter()` para asegurar que cada empresa solo ve sus datos.
