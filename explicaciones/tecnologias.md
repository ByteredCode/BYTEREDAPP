# Tecnologías utilizadas en BYTEREDAPP

## Stack completo

```
Frontend:  React + Vite + JavaScript (plain CSS)
Backend:   FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2
BD:        MySQL 8.0
Auth:      JWT + bcrypt
Infra:     Docker (MySQL)
```

---

## Frontend

### React
**¿Qué es?** Una librería para construir interfaces de usuario basadas en componentes reutilizables.

**¿Por qué React y no Vue o Angular?**
- React es la librería más popular del ecosistema JavaScript. Esto significa más tutoriales, más componentes de terceros, más soluciones en StackOverflow.
- Es más ligero que Angular (que es un framework completo). React es solo la capa de vista.
- El modelo de componentes de React encaja bien con un sistema modular (cada módulo del backend tiene su sección en el frontend).

### Vite
**¿Qué es?** Un bundler (empaquetador) que reemplaza a Webpack o Create React App.

**¿Por qué Vite y no CRA?**
- **Velocidad:** Vite usa ES modules nativos en desarrollo. El servidor de desarrollo arranca en milisegundos (CRA tardaba 20-30 segundos).
- **HMR (Hot Module Replacement):** Los cambios en el código se reflejan al instante, sin recargar la página.
- **Build rápido:** Usa Rollup para producción, genera bundles optimizados.

### JavaScript (no TypeScript)
**Decisión deliberada.** TypeScript añade una capa de complejidad (configuración, tipos, curva de aprendizaje) que no es necesaria para este proyecto. JavaScript moderno (ES2020+) con React ya proporciona suficiente seguridad. Si el proyecto crece y se vuelve difícil de mantener, se puede migrar a TypeScript gradualmente.

### React Router DOM
Para navegación SPA (Single Page Application). Sin recargar la página, el usuario navega entre Login, Register, Dashboard, etc.

### Axios
Cliente HTTP con soporte para interceptores. Se usa para:
- Adjuntar automáticamente el JWT a cada petición
- Renovar automáticamente el token cuando expira (refresh silencioso)
- Manejar errores de red de forma centralizada

---

## Backend

### FastAPI
**¿Qué es?** Un framework web moderno para Python (similar a Flask pero más rápido y con más características).

**¿Por qué FastAPI y no Flask o Django?**
| Característica | FastAPI | Flask | Django |
|---|---|---|---|
| Async nativo | ✅ Sí | ❌ No (parcial) | ❌ No (parcial) |
| Validación automática | ✅ Sí (Pydantic) | ❌ Manual | ✅ Sí (DRF) |
| Documentación Swagger | ✅ Automática | ❌ Manual | ❌ Manual |
| Rendimiento | Alto | Medio | Bajo |
| Curva de aprendizaje | Baja | Muy baja | Alta |
| ORM incluido | ❌ No | ❌ No | ✅ Sí |

FastAPI es ideal para APIs REST porque:
1. **Async nativo** — soporta `async/await` sin configuración extra
2. **Pydantic integrado** — validación automática con tipos Python
3. **Swagger automático** — nada que configurar, solo escribir el endpoint
4. **Rendimiento** — comparable a Node.js o Go

### SQLAlchemy 2.0 (async)
**¿Qué es?** El ORM (Object-Relational Mapper) más maduro de Python. La versión 2.0 introduce un estilo más moderno y limpio.

**¿Por qué async?** Cuando el backend hace una consulta a la BD, tarda milisegundos. Sin async, el servidor espera bloqueado durante ese tiempo. Con async, el servidor puede atender otras peticiones mientras espera la respuesta de la BD.

**¿Por qué aiomysql?** Es el driver asíncrono para MySQL. Alternativas:
- `pymysql` — síncrono, no sirve para async
- `mysqlclient` — síncrono, más rápido pero más complejo
- `asyncmy` — asíncrono, pero menos maduro que aiomysql
- `aiomysql` — asíncrono, maduro, basado en pymysql

### Pydantic v2
**¿Qué es?** Una librería para validación de datos basada en tipos Python.

**Versión 2** es significativamente más rápida que la v1 porque está escrita en Rust (pydantic-core). Las validaciones de datos se ejecutan en código nativo, no en Python.

### python-jose
**¿Qué es?** Librería para codificar y decodificar JWT en Python.

**¿Por qué no PyJWT?** python-jose soporta más algoritmos de cifrado y tiene una API más limpia. Es la librería recomendada en los tutoriales de FastAPI.

### bcrypt
**¿Qué es?** Algoritmo de hash para contraseñas. Es lento deliberadamente (para dificultar ataques de fuerza bruta).

**¿Por qué bcrypt y no SHA256?** SHA256 es rápido de calcular. Si alguien roba la BD, puede probar millones de contraseñas por segundo. bcrypt es lento (hace 2^salt rounds iteraciones), lo que hace que cada intento lleve tiempo.

### passlib (no usado finalmente)
Originalmente se contempló passlib, una librería que abstrae múltiples algoritmos de hash. Pero bcrypt 5.0.0 rompió la compatibilidad. Se eliminó la dependencia y se usa bcrypt directamente.

### python-dotenv
Carga variables de entorno desde un archivo `.env`. FastAPI con Pydantic Settings lo usa internamente.

### uvicorn
Servidor ASGI (Asynchronous Server Gateway Interface). FastAPI necesita un servidor ASGI para ejecutarse. uvicorn es el estándar de facto.

---

## Base de datos

### MySQL 8.0
**¿Por qué MySQL y no PostgreSQL?**
- BYTEREDAPP usa funcionalidades básicas de SQL (transacciones, foreign keys, índices). MySQL 8.0 las soporta todas.
- MySQL es más sencillo de configurar (especialmente en Windows) y tiene herramientas de administración más accesibles (Workbench, phpMyAdmin).
- El proyecto no necesita características avanzadas de PostgreSQL (como tipos JSONB avanzados, tablas con herencia, índices GIN).

**¿Por qué MySQL 8.0 y no 5.7?** MySQL 8.0 introduce mejoras importantes: ventanas (window functions), CTE (WITH), índices invisibles, mejor rendimiento general.

### Multi-tenant por fila
**¿Qué es?** Una sola base de datos, mismas tablas, pero cada registro tiene un `codigo_empresa` que identifica a qué empresa pertenece.

**Alternativas:**
| Estrategia | Pros | Contras |
|---|---|---|
| BD por empresa | Aislamiento total | Más coste, mantenimiento complejo |
| Esquema por empresa | Aislamiento medio | Migraciones complejas |
| **Fila por empresa** | Simple, barato | Riesgo de filtrado incorrecto |

Se eligió fila por empresa porque es la más simple y suficiente para el número esperado de clientes (decenas, no miles). El riesgo de filtrado incorrecto se mitiga con un middleware que inyecta automáticamente el filtro.

---

## Autenticación

### JWT (JSON Web Token)
**¿Qué es?** Un estándar (RFC 7519) para transmitir información entre partes como un objeto JSON firmado digitalmente.

**Ventajas sobre sesiones tradicionales:**
- **Stateless:** el servidor no guarda sesiones en memoria/BD. El token contiene toda la información.
- **Escalable:** cualquier instancia del servidor puede validar el token sin compartir sesiones.
- **Mobile-friendly:** los tokens funcionan bien en apps móviles y SPA.

**Estructura de un JWT:**
```
header.payload.signature
```
- **Header:** algoritmo de firma (HS256)
- **Payload:** datos (sub, empresa, exp, tipo)
- **Signature:** firma que verifica que el token no fue modificado

### Access + Refresh token
**¿Por qué dos tokens?** Si un access token es robado, el atacante solo puede usarlo por 60 minutos. El refresh token se usa solo para renovar, reduciendo la exposición. Es una práctica estándar de seguridad.

### bcrypt
**¿Por qué específicamente bcrypt?** Es el estándar de la industria para hash de contraseñas. Alternativas como argon2 son más seguras pero menos compatibles con librerías existentes.

---

## Infraestructura

### Docker
**¿Por qué Docker para MySQL?**
1. **Aislamiento:** la BD no se instala directamente en el sistema operativo
2. **Reproducibilidad:** cualquier desarrollador ejecuta `docker compose up` y tiene la misma versión de MySQL
3. **Limpieza:** `docker compose down` elimina el contenedor y sus datos, sin dejar rastro
4. **Versiones:** se puede cambiar de MySQL 8.0 a 5.7 cambiando una línea en docker-compose.yml

### pip (gestor de dependencias Python)
**¿Por qué no Poetry o pipenv?** Para un proyecto de este tamaño, pip + requirements.txt es suficiente. Poetry añade complejidad (archivo pyproject.toml, lockfile, resolución de dependencias) que no compensa para un equipo pequeño.

### pnpm (gestor de dependencias JavaScript)
**¿Por qué pnpm y no npm?** pnpm es más rápido que npm porque:
1. Usa un almacén global de paquetes (no descarga lo mismo varias veces)
2. Resuelve dependencias de forma más eficiente
3. Genera node_modules más pequeños

---

## Resumen de decisiones

| Decisión | Alternativa descartada | Motivo |
|---|---|---|
| React + JS | TypeScript, Vue, Angular | Simplicidad + popularidad |
| Vite | CRA, Webpack | Velocidad en desarrollo |
| FastAPI | Flask, Django | Async + validación automática |
| SQLAlchemy async | Tortoise ORM, Django ORM | Madurez + flexibilidad |
| MySQL 8.0 | PostgreSQL, MariaDB | Simplicidad en Windows |
| JWT | Sesiones con cookies | Stateless + escalable |
| bcrypt | SHA256, argon2 | Estándar industrial |
| Docker | Instalación directa | Aislamiento + reproducibilidad |
| pip | Poetry, pipenv | Simplicidad |
| pnpm | npm, yarn | Velocidad |
