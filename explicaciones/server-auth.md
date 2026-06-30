# Explicación del módulo de autenticación

## Arquitectura en 3 capas

El módulo de autenticación sigue una separación estricta en 3 capas:

```
Endpoint (api/v1/auth.py)  →  recibe la petición HTTP
    ↓
Service (services/auth_service.py)  →  lógica de negocio
    ↓
Model (models/usuario.py)  →  acceso a datos
```

**Principio:** Los endpoints NO contienen lógica de negocio. Solo reciben, validan y responden. Las reglas están en services/.

---

## schemas/auth.py — Validación de datos

```python
class RegisterRequest(BaseModel):
    correo: EmailStr
    contrasena: str
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
```

### ¿Qué hacen los schemas?

Definen la **forma de los datos** que entran y salen de la API.

- **RegisterRequest**: Al registrarse, el cliente debe enviar correo (validado como email), contraseña, nombre y código de empresa.
- **LoginRequest**: Solo correo y contraseña.
- **TokenResponse**: Lo que devuelve login y refresh.
- **UsuarioResponse**: Lo que devuelve /me.

### EmailStr

`EmailStr` de Pydantic valida que el string tenga formato de email (con @ y dominio). Si no, devuelve error 422 automáticamente.

### from_attributes

```python
model_config = {"from_attributes": True}
```

Permite construir el schema a partir de un objeto SQLAlchemy: `UsuarioResponse.model_validate(usuario_obj)`. Sin esto, habría que mapear campo por campo.

---

## services/auth_service.py — Lógica de autenticación

### registrar_usuario

```python
async def registrar_usuario(db, correo, contrasena, nombre, codigo_empresa) -> Usuario:
    existe = await db.execute(select(Usuario).where(Usuario.correo == correo))
    if existe.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")

    usuario = Usuario(
        correo=correo,
        contrasena=hash_contrasena(contrasena),
        nombre=nombre,
        codigo_empresa=codigo_empresa,
    )
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario
```

**Flujo:**

1. **Verificar duplicados**: Busca un usuario con ese correo. Si existe, error 400.
2. **Hash de contraseña**: `hash_contrasena` de security.py aplica bcrypt. **Nunca** se guarda la contraseña en texto plano.
3. **Guardar en BD**: `db.add(usuario)` pone el objeto en la sesión, `db.commit()` lo persiste en MySQL.
4. **Refresh**: Después de commit, el objeto tiene los valores por defecto de la BD (como `codigo_usuario` autoincrementado). `db.refresh(usuario)` recarga esos valores.

### iniciar_sesion

```python
async def iniciar_sesion(db, correo, contrasena) -> dict:
    resultado = await db.execute(select(Usuario).where(Usuario.correo == correo))
    usuario = resultado.scalar_one_or_none()
    if not usuario or not verificar_contrasena(contrasena, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token = crear_access_token({"sub": str(usuario.codigo_usuario), "empresa": usuario.codigo_empresa})
    refresh_token = crear_refresh_token({"sub": str(usuario.codigo_usuario)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
```

**Punto clave de seguridad:** `verificar_contrasena(contrasena, usuario.contrasena)` compara la contraseña enviada con el hash almacenado. **Nunca se desencripta el hash.** bcrypt aplica el mismo proceso al texto plano y compara el resultado con el hash almacenado.

**Por qué `str(codigo_usuario)`:** El estándar JWT (RFC 7519) exige que el claim `sub` (subject) sea de tipo string. Si pasas un entero, python-jose lanza un error.

---

## api/v1/auth.py — Endpoints REST

```python
router = APIRouter(tags=["Auth"])

@router.post("/auth/register", response_model=UsuarioResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    usuario = await registrar_usuario(db, ...)
    return usuario

@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await iniciar_sesion(db, ...)

@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str = Body(...), db: AsyncSession = Depends(get_db)):
    payload = decodificar_token(refresh_token)
    if payload is None or payload.get("tipo") != "refresh":
        raise HTTPException(status_code=401, detail="Token invalido")
    access_token = crear_access_token({"sub": str(payload["sub"]), "empresa": payload.get("empresa")})
    nuevo_refresh = crear_refresh_token({"sub": str(payload["sub"])})
    return TokenResponse(access_token=access_token, refresh_token=nuevo_refresh)

@router.get("/auth/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_usuario_actual)):
    return usuario
```

### POST /auth/register

**Entrada:** correo, contraseña, nombre, codigo_empresa
**Salida:** datos del usuario creado (sin contraseña)
**Validaciones:** correo único, contraseña hasheada con bcrypt

### POST /auth/login

**Entrada:** correo, contraseña
**Salida:** access_token, refresh_token, token_type
**Validaciones:** el correo existe y la contraseña coincide

### POST /auth/refresh

**Entrada:** refresh_token (en el body, no en el header)
**Salida:** nuevo access_token + nuevo refresh_token
**Validaciones:** el refresh token es válido y no ha expirado

### GET /auth/me

**Entrada:** access_token en el header Authorization
**Salida:** datos del usuario autenticado
**Validaciones:** el token es válido, el usuario existe en BD

### Uso de Depends

- `Depends(get_db)`: Inyecta la sesión de BD
- `Depends(get_usuario_actual)`: Protege el endpoint, extrae el usuario del token

Ambos son ejemplos de **inyección de dependencias**: las dependencias se declaran en los parámetros, FastAPI las resuelve automáticamente.

---

## Flujo completo de autenticación

```
CLIENTE                          SERVIDOR
  │                                  │
  │  1. POST /auth/register          │
  │  {correo, contrasena, ...}       │
  │ ────────────────────────────────→│
  │                                  │─ ¿Correo ya existe? → error 400
  │                                  │─ Hash bcrypt(contrasena)
  │                                  │─ INSERT en BD
  │  2. ← {codigo_usuario, nombre}   │
  │                                  │
  │  3. POST /auth/login             │
  │  {correo, contrasena}            │
  │ ────────────────────────────────→│
  │                                  │─ ¿Usuario existe? → error 401
  │                                  │─ ¿bcrypt coincide? → error 401
  │                                  │─ Crear JWT (sub=str(id), empresa)
  │  4. ← {access_token, refresh}    │
  │                                  │
  │  5. GET /auth/me                 │
  │  Authorization: Bearer <token>   │
  │ ────────────────────────────────→│
  │                                  │─ Decodificar JWT
  │                                  │─ ¿tipo=access? → error 401
  │                                  │─ Buscar usuario por sub → error 401
  │  6. ← {codigo_usuario, nombre,   │
  │         rol, codigo_empresa}      │
```
