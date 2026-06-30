# Contribuir

## Requisitos

- Python 3.11+
- Node.js 20+
- pnpm
- MySQL 8 (o Docker)

## Entorno local

```bash
cp .env.example .env
# Ajusta variables en .env si es necesario
pip install -r server/requirements.txt
cd client && pnpm install
```

## Base de datos

```bash
# Con Docker:
docker compose up -d db

# Sin Docker: crear base de datos 'gestion_empresas' en MySQL

# Migraciones:
cd server && alembic upgrade head

# Datos de prueba:
python scripts/seed.py
```

## Ejecutar en desarrollo

```bash
# Terminal 1 — backend
cd server && uvicorn run:app --reload --port 8000

# Terminal 2 — frontend
cd client && pnpm dev
```

## Tests

```bash
# Backend
cd server && python -m pytest tests/ -q

# Frontend
cd client && pnpm test -- --run
```

## Convenciones

- Código en español (mensajes, comentarios, nombres de tablas)
- React con JavaScript (no TypeScript), CSS plano (no Tailwind)
- pnpm para frontend, pip para backend
- Commits descriptivos en español o inglés
