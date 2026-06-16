# Reglas Backend (FastAPI + Python)

- Nombres de archivos en snake_case: `auth_service.py`
- Clases en PascalCase, funciones/variables en snake_case
- Usar SQLAlchemy 2.0 async para modelos
- Schemas Pydantic para validación de entrada/salida
- Endpoints RESTful en `app/api/v1/`
- Lógica de negocio en `app/services/` (nunca en los endpoints)
- Modelos en `app/models/`
- Dependencias de autenticación y tenant en `app/core/`
- Usar Alembic para migraciones de BD
- Pruebas en `server/tests/`
