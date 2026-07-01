#!/bin/bash
set -e
alembic upgrade head
python scripts/auto_seed.py || echo "WARNING: auto_seed fallo (no critico)"
python scripts/seed_test_data.py || echo "WARNING: seed_test_data fallo (no critico)"
uvicorn run:app --host 0.0.0.0 --port "$PORT" --forwarded-allow-ips '*'
