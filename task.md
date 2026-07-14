# Чек-лист реализации: AI Brief Decoder Lite

## Часть 1: Инфраструктура бэкенда и настройки (Backend Infra & Config)
- [x] **1.1. Инициализация и зависимости:**
  - Настроить Poetry-окружение в `backend/pyproject.toml`.
  - Добавить зависимости: `fastapi`, `uvicorn`, `pydantic`, `pydantic-ai`, `sqlalchemy`, `asyncpg`, `alembic`, `dynaconf`, `python-dotenv`.
  - Добавить dev-зависимости: `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `pyright`.
  - Настроить `ruff` на максимальную длину строки в 99 символов и таргет Python 3.12.
- [x] **1.2. База данных и Docker-compose:**
  - Создать `backend/docker-compose.yml` для локального запуска PostgreSQL.
  - Настроить порты, имя базы данных (`brief_decoder`), логин и пароль.
- [x] **1.3. Инициализация FastAPI и Healthcheck:**
  - Создать `backend/app/main.py`.
  - Описать запуск приложения через фабричную функцию `create_app()`.
  - Добавить базовый роутер и эндпоинт `/health`.
  - Создать схему для проверки здоровья в доменной области `backend/app/schemas/health.py`.
- [x] **1.4. Настройка конфигурации сред (Dynaconf):**
  - Инициализировать конфигурацию в `backend/app/core/config.py`.
  - Создать файлы настроек `backend/config/settings.toml` и `backend/config/.secrets.toml`.
  - Настроить окружения `local`, `testing` и `production`.

## Часть 2: База данных, Модели и Миграции (Database & Models)
- [x] **2.1. Настройка подключения к БД (db/session):**
  - Создать `backend/app/db/session.py`.
  - Настроить асинхронный движок `create_async_engine` и `async_sessionmaker`.
  - Написать зависимость-генератор `get_db` для внедрения сессий в FastAPI эндпоинты.
- [x] **2.2. Создание модели БД (models/brief_decode):**
  - Создать модель SQLAlchemy `BriefDecode` в `backend/app/models/brief_decode.py` (таблица `brief_decodes`).
  - Описать поля: `id` (UUID), `status`, `input_text`, `structured_result` (JSONB), `raw_provider_output`, `error_code`, `error_message`, `created_at`, `updated_at`.
- [x] **2.3. Инициализация миграций Alembic:**
  - Выполнить инициализацию alembic в папке `backend/`.
  - Настроить асинхронный запуск в `backend/alembic/env.py`.
  - Сгенерировать и применить первую миграцию для создания таблицы `brief_decodes`.

## Часть 3: Валидация вывода и Провайдеры LLM (Schemas & LLM Providers)
- [ ] **3.1. Описание схем Pydantic:**
  - Создать файл `backend/app/schemas/api.py` (схемы контрактов API).
  - Описать `SeverityEnum` (Python Enum: `low`, `medium`, `high`).
  - Описать схемы `RiskItem`, `BriefAnalysisResponse`, `BriefDecodeRequest` и `BriefDecodeRunResponse`.
- [x] **3.2. Абстракция провайдеров:**
  - Создать `backend/app/core/providers.py`.
  - Описать абстрактный класс `BaseLLMProvider`.
- [x] **3.3. Реализация FakeLLMProvider (заглушка):**
  - Добавить класс `FakeLLMProvider` в `providers.py`.
  - Реализовать генерацию валидного ответа `BriefAnalysisResponse` на основе мок-данных.
- [x] **3.4. Реализация GeminiLLMProvider (реальный ИИ):**
  - Добавить класс `GeminiLLMProvider` в `providers.py`.
  - Реализовать запрос к Gemini Flash с использованием PydanticAI и валидацией в модель.

## Часть 4: Бизнес-логика и API Эндпоинты (Services & Endpoints)
- [x] **4.1. Сервис декодирования (services/brief_service):**
  - Создать `backend/app/services/brief_service.py`.
  - Реализовать метод создания запуска (сохранение в БД в статусе `pending`).
  - Реализовать логику вызова провайдера, валидацию ответа, перехват ошибок и сохранение результатов (`completed` / `failed`).
- [x] **4.2. Создание API эндпоинтов:**
  - Создать `backend/app/api/v1/briefs.py`.
  - Добавить `POST /v1/briefs/decode` (вызывает сервис декодирования).
  - Добавить `GET /v1/briefs/runs/{run_id}` (возвращает статус и детали запуска).
- [x] **4.3. Регистрация API в приложении:**
  - Подключить роутер `/v1` к FastAPI приложению в `main.py`.

## Часть 5: Тестирование бэкенда (Backend Tests)
- [x] **5.1. Настройка тестового окружения:**
  - Создать `backend/tests/conftest.py`.
  - Настроить создание временной тестовой базы данных PostgreSQL.
  - Написать фикстуру асинхронного клиента `AsyncClient` и фикстуру подмены провайдеров.
- [x] **5.2. Написание тестов валидации схемы:**
  - Написать тесты на валидацию Pydantic модели (тестирование некорректного JSON, отсутствия полей, неверного `severity`).
- [x] **5.3. Happy-path интеграционный тест API:**
  - Написать тест эндпоинта `POST /v1/briefs/decode` с `FakeLLMProvider`. Проверить создание записи в БД и успешный ответ 200.
- [x] **5.4. Failure-path интеграционный тест API:**
  - Написать тест на сбой провайдера ИИ. Убедиться, что статус записи переходит в `failed`, а API возвращает корректную безопасную ошибку.

## Часть 6: Хром Расширение (Chrome Extension)
- [ ] **6.1. Настройка окружения WXT:**
  - Создать скелет расширения в папке `extension/`.
  - Настроить манифест с разрешениями (`sidePanel`, `storage`, `activeTab`) в `wxt.config.ts`.
  - Настроить Axios-клиент в `extension/src/api/client.ts`.
- [ ] **6.2. Автогенерация типов из OpenAPI:**
  - Выгрузить спецификацию бэкенда `openapi.json`.
  - Сгенерировать контракты в `extension/src/api/contracts.ts` с помощью `openapi-typescript`.
- [ ] **6.3. Модульные компоненты:**
  - Создать компонент `BriefDecoder/BriefDecoder.tsx` и `BriefDecoder.css` (поле ввода, кнопка, лоадер, копирование).
  - Создать компонент `RiskCard/RiskCard.tsx` и `RiskCard.css` (вывод рисков с бейджами в зависимости от `SeverityEnum`).
- [ ] **6.4. Сборка Sidepanel:**
  - Подключить `BriefDecoder` в `sidepanel/App.tsx`.

## Часть 7: Документация и финальная сборка (Documentation & Packaging)
- [ ] **7.1. Заполнение документации:**
  - Оформить `README.md` (настройка, команды запуска и тестирования).
  - Оформить `AI_USAGE.md` (отчет о промптах и исправлениях).
  - Оформить `provider_usage.md` (инструкция по переключению провайдеров).
  - Оформить `notes.md` (компромиссы и принятые допущения).
- [ ] **7.2. Финальная сборка и проверка:**
  - Написать `backend/Makefile` для быстрой проверки всего бэкенда.
  - Проверить линтинг (`ruff check`) и типы (`pyright`) на бэкенде.
  - Проверить сборку расширения (`npm run build`).
