# Reglas Base de Datos (MySQL + SQLAlchemy + Alembic)

- Nombres de tablas y columnas en español y snake_case
- Primary key: `codigo_<tabla>` (ej: `codigo_empresa`, `codigo_usuario`) o `id_<tabla>`
- Foreign keys: `codigo_<tabla_referenciada>`
- Timestamps con `DEFAULT CURRENT_TIMESTAMP`
- Índices para todas las foreign keys
- Usar ENUM para columnas con valores fijos (rol, estado, columna, tipo)
- Aislamiento multi-tenant: todas las tablas operativas tienen `codigo_empresa`
- Migraciones con Alembic: `alembic revision --autogenerate -m "mensaje"`
- Revisar siempre el SQL generado por autogenerate antes de aplicarlo
