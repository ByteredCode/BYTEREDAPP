# Explicación de requirements.txt

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
aiomysql==0.2.0
alembic==1.13.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt>=3.1.0,<5.0.0
python-multipart==0.0.9
pydantic[email]==2.9.2
pydantic-settings==2.5.2
```

## Dependencia por dependencia

### fastapi
El framework web. La versión 0.115.0 incluye soporte completo para Pydantic v2, parámetros de Query/Path/Body mejorados y OpenAPI 3.1.

### uvicorn[standard]
Servidor ASGI. El extra `[standard]` incluye dependencias adicionales como `httptools` y `uvloop` para mejor rendimiento en Linux. En Windows, `uvloop` no está disponible, pero el resto funciona igual.

### sqlalchemy 2.0.35
ORM. Esta versión usa el estilo **2.0** con `select()` en lugar del viejo estilo `session.query()`. El cambio principal respecto a 1.x es que ahora todas las operaciones se hacen con `select()`, `where()` y `join()` funcionales.

### aiomysql 0.2.0
Driver asíncrono para MySQL. Permite que SQLAlchemy haga consultas sin bloquear el event loop de Python. Es un wrapper alrededor de `pymysql` que añade soporte async.

**Alternativas consideradas:**
- `asyncmy` — más rápido pero menos maduro
- `pymysql` — síncrono, no sirve con async

### alembic 1.13.2
Sistema de migraciones. Lee los modelos SQLAlchemy, compara con la BD actual y genera scripts SQL para sincronizarlos.

### python-jose[cryptography]
Manejo de JWT. El extra `[cryptography]` instala `cryptography` para algoritmos de cifrado más seguros. Sin él, python-jose solo soporta algoritmos básicos.

### passlib[bcrypt] + bcrypt<5.0.0
Hash de contraseñas. `passlib` es un adaptador que permite cambiar el algoritmo de hash sin modificar el código. El extra `[bcrypt]` instala bcrypt como backend.

**¿Por qué bcrypt<5.0.0?** bcrypt 5.0.0 eliminó el módulo `bcrypt.__about__` que passlib 1.7.4 necesita. Al pinner `<5.0.0`, aseguramos que pip nunca instale una versión incompatible.

### python-multipart
Necesario para que FastAPI procese formularios multipart (subida de archivos). No se usa aún, pero se necesita para los módulos de documentos y tickets.

### pydantic[email] + pydantic-settings
- `pydantic[email]`: Añade `EmailStr` para validar correos electrónicos
- `pydantic-settings`: Integración con `.env` para cargar configuración

## ¿Por qué versiones fijas (==) en lugar de rangos (>=)?

Las dependencias de producción tienen versiones fijas (`==0.115.0`) para garantizar **reproducibilidad**. Si dos desarrolladores instalan en momentos diferentes y una librería saca una versión incompatible, las versiones fijas evitan sorpresas.

La excepción es `bcrypt`, que usa un rango (`>=3.1.0,<5.0.0`) porque su versionado sigue semver y la incompatibilidad está acotada.
