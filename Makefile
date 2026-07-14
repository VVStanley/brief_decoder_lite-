.PHONY: run-back db-up db-down migrate-back lint-back format-back typecheck-back test-back install-back \
        run-ext build-ext typecheck-ext lint-ext install-ext install-all help

help:
	@echo "Доступные команды из корня проекта:"
	@echo "  Backend:"
	@echo "    make install-back   - Установка зависимостей бэкенда (Poetry)"
	@echo "    make run-back       - Запуск бэкенда FastAPI"
	@echo "    make db-up          - Запуск базы данных в Docker"
	@echo "    make db-down        - Остановка базы данных"
	@echo "    make migrate-back   - Запуск миграций Alembic"
	@echo "    make lint-back      - Проверка линтером Ruff"
	@echo "    make format-back    - Форматирование кода Ruff"
	@echo "    make typecheck-back - Проверка типов Pyright"
	@echo "    make test-back      - Запуск тестов Pytest"
	@echo ""
	@echo "  Extension (Frontend):"
	@echo "    make install-ext    - Установка зависимостей расширения (npm)"
	@echo "    make run-ext        - Запуск расширения в режиме разработки (dev server)"
	@echo "    make build-ext      - Сборка расширения под Chrome MV3"
	@echo "    make typecheck-ext  - Проверка типов расширения (tsc --noEmit)"
	@echo "    make lint-ext       - Проверка линтером расширения (tsc --noEmit)"
	@echo ""
	@echo "  Общие:"
	@echo "    make install-all    - Установка зависимостей для бэкенда и расширения"

# Backend
install-back:
	cd backend && poetry install

run-back:
	cd backend && poetry run uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000

db-up:
	cd backend && docker-compose up -d

db-down:
	cd backend && docker-compose down

migrate-back:
	cd backend && poetry run alembic upgrade head

lint-back:
	cd backend && poetry run ruff check .

format-back:
	cd backend && poetry run ruff format .

typecheck-back:
	cd backend && poetry run pyright

test-back:
	cd backend && poetry run pytest

# Extension (Frontend)
install-ext:
	cd extention && npm install

run-ext:
	cd extention && npm run dev

build-ext:
	cd extention && npm run build

typecheck-ext:
	cd extention && npm run compile

lint-ext:
	cd extention && npx tsc --noEmit

# Общие
install-all: install-back install-ext
