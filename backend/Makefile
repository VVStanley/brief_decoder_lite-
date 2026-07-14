.PHONY: run db-up db-down migrate lint format typecheck test

run:
	poetry run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

db-up:
	docker-compose up -d

db-down:
	docker-compose down

migrate:
	poetry run alembic upgrade head

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run pyright

test:
	poetry run pytest
