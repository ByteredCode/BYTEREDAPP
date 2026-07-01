#!/bin/bash
set -e
# Forzar re-ejecución de migraciones pendientes (start.sh anterior
# tenía stamp head antes de upgrade head, lo que saltaba migraciones)
alembic stamp 3e03f2cf94fe 2>/dev/null || true
alembic upgrade head
python scripts/auto_seed.py
python scripts/seed_test_data.py
uvicorn run:app --host 0.0.0.0 --port "$PORT" --forwarded-allow-ips '*'
