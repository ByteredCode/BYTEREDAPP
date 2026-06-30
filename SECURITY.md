# Seguridad

## Reportar vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, abre un issue en el repositorio
con el label `security` o contacta al mantenedor directamente.

## Medidas implementadas

- JWT con access + refresh tokens (rotación y blocklist)
- Contraseñas hasheadas con bcrypt
- Rate limiting en login, register y tickets públicos
- CORS configurado por orígenes permitidos
- Headers de seguridad: X-Content-Type-Options, X-Frame-Options,
  Strict-Transport-Security, Content-Security-Policy
- Validación de tipo, extensión y tamaño en subida de documentos
- Multi-tenant por company_id (aislamiento de datos por fila)
- SQL parametrizado via SQLAlchemy (protección contra inyección)

## Buenas prácticas en producción

1. Generar JWT_SECRET seguro: `python scripts/generate_secret.py`
2. Cambiar MYSQL_PASSWORD por defecto
3. Configurar CORS_ORIGINS con el dominio real
4. Configurar SMTP para envío de emails
5. Usar Redis para blocklist persistente (REDIS_HOST)
6. No exponer puertos de MySQL/Redis al host
