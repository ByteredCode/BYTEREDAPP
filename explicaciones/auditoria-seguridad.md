# Auditoría de Ciberseguridad — BYTEREDAPP

**Fecha:** 29/06/2026
**Alcance:** Full-stack (FastAPI + React)
**Estándar:** OWASP Top 10 (2021)

---

## Resumen Ejecutivo

Se auditaron 20+ archivos del backend y frontend. Se identificaron **12 hallazgos**: 1 crítico, 3 altos, 5 medios, 3 bajos.

| Severidad | Cantidad |
|-----------|----------|
| Crítico | 1 |
| Alto | 3 |
| Medio | 5 |
| Bajo | 3 |

---

## [CRÍTICO] A07 — Refresh token sin rotación

**Archivo:** `server/app/api/v1/auth.py:36-42`

El endpoint `/auth/refresh` genera un nuevo par de tokens sin invalidar el refresh token anterior. Esto permite que un refresh token robado pueda usarse múltiples veces.

```python
@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str = Body(...), db: AsyncSession = Depends(get_db)):
    payload = decodificar_token(refresh_token)
    # ...
    access_token = crear_access_token(...)
    nuevo_refresh = crear_refresh_token(...)
    return TokenResponse(access_token=access_token, refresh_token=nuevo_refresh)
```

**Solución:** Implementar una lista negra (blocklist) de refresh tokens usados en Redis o BD. Cada vez que se use un refresh token, invalidarlo y generar uno nuevo. Si un token ya usado se reenvía, rechazarlo y forzar cierre de sesión.

---

## [ALTO] A05 — JWT_SECRET débil

**Archivo:** `server/app/core/config.py:16`
**Archivo:** `.env:9`

```python
JWT_SECRET: str = "changeme"  # Default en código
# .env: JWT_SECRET=super-secret-key-change-in-production (36 chars pero predecible)
```

**Riesgo:** Un atacante que obtenga el `.env` o el código fuente puede falsificar JWTs y suplantar cualquier usuario.

**Solución:**
- Generar una clave con `openssl rand -hex 64` (128 caracteres hex).
- Eliminar el valor por defecto del código (`config.py`) para que falle si no está configurada.
- Rotar la clave periódicamente.

---

## [ALTO] A04 — Sin rate limiting en login

**Archivo:** `server/app/api/v1/auth.py:24-32`

El endpoint `/auth/login` no tiene límite de intentos ni bloqueo temporal. Un atacante puede hacer fuerza bruta de contraseñas sin restricción.

**Solución:**
- Implementar `slowapi` o middleware de rate limiting.
- Bloquear IP tras 5 intentos fallidos en 15 minutos.
- Añadir delay progresivo entre intentos.

---

## [ALTO] A07 — Sin validación de complejidad de contraseñas

**Archivo:** `server/app/schemas/auth.py:6`
**Archivo:** `server/app/services/auth_service.py:14`

```python
class RegisterRequest(BaseModel):
    contrasena: str  # Sin mínimo de longitud ni complejidad
```

No hay validación de longitud mínima, caracteres especiales, mayúsculas, etc. El registro acepta `"a"` como contraseña.

**Solución:**
- Añadir validador Pydantic: `Field(min_length=8)`.
- Exigir al menos: 1 mayúscula, 1 minúscula, 1 número.
- Implementar comprobación contra contraseñas comunes (rockyou list).

---

## [MEDIO] A05 — CORS permisivo en producción

**Archivo:** `server/run.py:28`

```python
allow_origins=["http://localhost:5173"]
```

Solo permite localhost — correcto para desarrollo. Pero en producción debería cambiarse al dominio real de Hostinger. No hay manejo de entornos.

**Solución:**
- Leer orígenes desde variable de entorno `CORS_ORIGINS`.
- En producción: `allow_origins=["https://tudominio.com"]`.

---

## [MEDIO] A05 — Documentación Swagger sin protección

**Archivo:** `server/run.py:23`

```python
app = FastAPI(title="BYTEREDAPP API", version="0.1.0", lifespan=lifespan)
```

`/docs` y `/redoc` están habilitados por defecto. Exponen todos los endpoints, schemas y parámetros. En producción, esto revela información valiosa a atacantes.

**Solución:**
```python
app = FastAPI(docs_url=None, redoc_url=None)  # Deshabilitar en producción
# O proteger con dependencia de autenticación
```

---

## [MEDIO] A09 — Sin logging de seguridad

**Archivo:** `server/app/services/auth_service.py` (todo el archivo)

No se registran intentos de login (exitosos ni fallidos). No hay auditoría de cambios de rol ni creación de usuarios.

**Solución:**
- Añadir logger en `iniciar_sesion` y `registrar_usuario`:
```python
logger.info(f"Login exitoso: usuario {usuario.codigo_usuario}, empresa {usuario.codigo_empresa}")
logger.warning(f"Login fallido: correo {correo}")
```

---

## [MEDIO] A01 — Documentos sin verificación de propiedad del permiso

**Archivo:** `server/app/services/documento_service.py:91-101`

```python
async def agregar_permiso(db, id_documento, codigo_usuario, codigo_empresa):
    await obtener_documento(db, id_documento, codigo_empresa)
    permiso = DocumentoPermiso(id_documento=id_documento, codigo_usuario=codigo_usuario)
```

Cualquier usuario autenticado puede otorgar permisos sobre cualquier documento de su empresa. No se verifica que quien otorga el permiso sea el propietario del documento o admin.

**Solución:** Verificar que `usuario_subio == usuario_actual` o que el usuario sea admin antes de permitir agregar permisos.

---

## [MEDIO] A10 — Subida de archivos sin validación de tipo/tamaño

**Archivo:** `server/app/services/documento_service.py:16-44`

```python
async def subir_documento(db, archivo: UploadFile, ...):
    contenido = await archivo.read()
    with open(ruta_completa, "wb") as f:
        f.write(contenido)
```

No se valida:
- Tipo MIME del archivo (podrían subir .exe, .php, .html)
- Tamaño máximo (podrían saturar el disco)
- No se escanea el contenido (malware)

**Solución:**
- Validar `archivo.content_type` contra lista blanca (`application/pdf`, `image/*`, `application/msword`, etc.)
- Limitar tamaño: `archivo.size` < 10MB
- Validar extensión contra lista blanca
- Almacenar fuera del webroot (ya se hace con `/uploads/`)

---

## [MEDIO] A07 — Logout no invalida tokens en servidor

**Archivo:** `client/src/context/AuthContext.jsx:39-43`

```javascript
const logout = () => {
  localStorage.removeItem("access_token")
  localStorage.removeItem("refresh_token")
  setUsuario(null)
}
```

El logout solo elimina los tokens del cliente. Los tokens siguen siendo válidos hasta su expiración. Si alguien interceptó un token, puede seguir usándolo.

**Solución:** Implementar endpoint `POST /auth/logout` que añada el token a una blocklist. El frontend debe llamarlo antes de limpiar localStorage.

---

## [BAJO] A02 — Access token con expiración larga (60 min)

**Archivo:** `server/app/core/config.py:17`
**Archivo:** `.env:10`

```python
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
```

60 minutos es excesivo para un access token. Lo recomendado son 15-30 minutos.

**Solución:** Reducir a 15-30 minutos y depender del refresh token para sesiones largas.

---

## [BAJO] A05 — Encabezados de seguridad HTTP ausentes

**Archivo:** `server/run.py` (toda la app)

No se configuran headers de seguridad:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy`
- `Strict-Transport-Security`

**Solución:** Añadir middleware que inyecte estos headers en todas las respuestas.

---

## [BAJO] A10 — Open redirect potencial en redirección

**Archivo:** `server/app/api/v1/redireccion.py:13-20`

```python
@router.get("/r/{codigo_empresa}")
async def redirigir(codigo_empresa: int, db: AsyncSession = Depends(get_db)):
    empresa = await db.execute(...)
    return RedirectResponse(url=empresa.web)
```

Un admin malicioso podría configurar una URL de redirección a un sitio de phishing. Aunque el atacante necesitaría ser admin para cambiar la URL, es un riesgo de SSRF/open redirect.

**Solución:** Validar que `empresa.web` sea una URL HTTPS a un dominio conocido o permitido. Añadir advertencia visual al admin cuando configure la URL.

---

## Resumen de hallazgos por archivo

| Archivo | Hallazgos |
|---|---|
| `server/app/core/config.py` | JWT_SECRET default débil |
| `server/app/api/v1/auth.py` | Sin rate limiting, refresh sin rotación |
| `server/app/services/auth_service.py` | Sin logging, sin complejidad de contraseña |
| `server/app/schemas/auth.py` | Sin validación de contraseña |
| `server/app/services/documento_service.py` | Sin validación de archivos, permisos sin verificación |
| `server/app/api/v1/redireccion.py` | Open redirect potencial |
| `server/run.py` | CORS fijo, sin headers seguridad, Swagger expuesto |
| `client/src/context/AuthContext.jsx` | Logout sin invalidación server-side |

---

## Recomendaciones prioritarias

1. **Crítico**: Implementar rotación de refresh tokens (blocklist)
2. **Alto**: Añadir rate limiting en login
3. **Alto**: Fortalecer JWT_SECRET (128+ chars aleatorios)
4. **Alto**: Validar complejidad de contraseñas (min 8 chars, mayúscula, número)
5. **Medio**: Añadir logging de eventos de seguridad
6. **Medio**: Validar tipo y tamaño de archivos subidos

---

*Auditoría realizada según el OWASP Top 10 2021 y las reglas definidas en `ia/rules/security-rules.md`.*
