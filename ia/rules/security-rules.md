# Reglas de Ciberseguridad (OWASP Top 10)

## Control de acceso (A01)
- Todo endpoint protegido debe usar `get_current_user` o `get_current_company`
- Validar que el recurso solicitado pertenece al usuario/empresa autenticado
- Rutas de admin deben verificar rol `admin_total` o `admin_empresa`

## Criptografía (A02)
- Contraseñas con bcrypt (passlib), nunca en texto plano
- JWT con algoritmo HS256 y expiración corta (access: 30 min, refresh: 7 días)
- `SECRET_KEY` en `.env`, mínimo 32 caracteres, nunca hardcodeada

## Inyección (A03)
- SQL: solo SQLAlchemy ORM, nunca SQL raw concatenado
- No usar `dangerouslySetInnerHTML` en React
- Toda entrada validada con esquemas Pydantic

## Diseño seguro (A04)
- Rate limiting en login
- No exponer stack traces ni versiones en errores
- Validar todo input con Pydantic antes de procesar

## Configuración (A05)
- CORS con orígenes específicos en producción
- Headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`
- DEBUG = False en producción
- */docs y /redoc* deshabilitados o con auth en producción

## Autenticación (A07)
- Contraseñas ≥ 8 caracteres con complejidad
- Email único por usuario
- Refresh token de un solo uso (rotación)
- Cierre de sesión invalida tokens

## Logging (A09)
- Loguear intentos de login (éxito y fallo)
- No loguear contraseñas, tokens ni datos personales
- Todos los logs con timestamp
