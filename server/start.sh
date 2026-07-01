#!/bin/bash
set -e
alembic upgrade head
python scripts/auto_seed.py
python scripts/seed_test_data.py
uvicorn run:app --host 0.0.0.0 --port "$PORT" --forwarded-allow-ips '*'
