.PHONY: dev dev-client dev-server test test-client test-server migrate seed lint

dev:
	docker compose up -d --wait server

dev-client:
	cd client && pnpm dev

dev-server:
	cd server && uvicorn run:app --reload --port 8000

test:
	cd server && python -m pytest tests/ -q
	cd client && pnpm test -- --run

test-server:
	cd server && python -m pytest tests/ -q

test-client:
	cd client && pnpm test -- --run

migrate:
	cd server && alembic upgrade head

seed:
	python scripts/seed.py

lint:
	cd server && ruff check .
	cd client && pnpm lint
