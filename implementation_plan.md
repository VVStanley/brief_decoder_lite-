# Стартовый план реализации: AI Brief Decoder Lite (Обновленный)

Этот план описывает проектирование и пошаговую реализацию прототипа **AI Brief Decoder Lite**. Проект будет организован как самостоятельный монорепозиторий внутри папки `brief_decoder_lite/` для удобства отправки в архиве или отдельной Git-репозиторием.

---

## Требуется подтверждение пользователя

> [!IMPORTANT]
> **Конфигурация провайдера ИИ и локальный запуск:**
> Чтобы выполнить требование о возможности локального запуска проекта без платных API-ключей, мы реализуем класс `FakeLLMProvider`, который будет возвращать готовый мок-ответ JSON, соответствующий ожидаемой Pydantic-схеме.
>
> Переключение между режимами работы `fake` (заглушка) и `gemini` (реальный ИИ через PydanticAI) будет осуществляться через переменную окружения `LLM_PROVIDER` в настройках Dynaconф (`settings.yaml`).

> [!IMPORTANT]
> **База данных и DevOps:**
> Мы добавим `docker-compose.yml` для локального запуска PostgreSQL. Мы также настроим **Alembic** для управления миграциями внутри бэкенда.

---

## Предлагаемые изменения

Мы создадим чистую модульную структуру папок внутри директории `brief_decoder_lite/`.

### Структура монорепозитория

```
brief_decoder_lite/
├── backend/            # Сервис на FastAPI
│   ├── app/
│   │   ├── api/        # Эндпоинты (/health, /v1/briefs/decode, /v1/briefs/runs/{run_id})
│   │   ├── core/       # Настройки (Dynaconf), абстракция провайдера ИИ
│   │   ├── db/         # Настройка подключения к БД, получение сессии (session.py)
│   │   ├── models/     # Модели SQLAlchemy (brief_decode.py)
│   │   ├── schemas/    # Схемы Pydantic (запросы, ответы, структуры анализа)
│   │   ├── services/   # Сервисный слой бизнес-логики (brief_service.py)
│   │   └── main.py     # Точка входа в приложение FastAPI
│   ├── config/         # Файлы конфигурации Dynaconф (settings.toml)
│   ├── tests/          # Тесты (pytest)
│   ├── pyproject.toml  # Зависимости Poetry
│   ├── alembic.ini     # Конфигурация миграций Alembic
│   ├── Makefile        # Быстрые команды (запуск, тесты, линтинг)
│   └── docker-compose.yml # Запуск локальной БД PostgreSQL
│
├── extension/          # Chrome-расширение на WXT + React + TS
│   ├── entrypoints/
│   │   └── sidepanel/  # Точка входа боковой панели
│   ├── src/
│   │   ├── api/        # Axios-клиент (client.ts), контракты (contracts.ts)
│   │   ├── components/ # Модульные React-компоненты
│   │   │   ├── BriefDecoder/ # Компонент декодера (BriefDecoder.tsx, BriefDecoder.css)
│   │   │   └── RiskCard/     # Карточка отображения рисков (RiskCard.tsx, RiskCard.css)
│   │   └── constants/  # Глобальные константы
│   ├── package.json    # Скрипты (dev, build, generate-types)
│   └── wxt.config.ts
│
├── README.md           # Инструкция по сборке, запуску и тестированию всей системы
├── AI_USAGE.md         # Отчет об использовании ИИ-ассистентов
├── provider_usage.md   # Инструкция по использованию фейкового и реального провайдеров
└── notes.md            # Заметки о принятых допущениях и компромиссах (assumptions & tradeoffs)
```

---

### Бэкенд (Backend)

#### [schemas/decode.py](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/backend/app/schemas/decode.py)
Определяет модели Pydantic для валидации структурированного вывода LLM:
* `SeverityEnum` (Python `str, Enum`): содержит `low`, `medium`, `high`.
* `RiskItem`: `risk: str`, `severity: SeverityEnum`, `reason: str`.
* `BriefAnalysisResponse`: `summary: str`, `goals: list[str]`, `deliverables: list[str]`, `constraints: list[str]`, `risks: list[RiskItem]`, `clarifying_questions: list[str]`, `recommended_next_action: str`.
* `BriefDecodeRequest`: `text: str` (минимальная длина 10 символов).
* `BriefDecodeRunResponse`: Единый формат ответа API, возвращающий статус запуска, входные данные, результат и безопасные ошибки.

#### [core/providers.py](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/backend/app/core/providers.py)
Реализует абстракцию провайдера ИИ:
* `BaseLLMProvider`: Абстрактный класс с сигнатурой `async def decode_brief(self, text: str) -> tuple[BriefAnalysisResponse | None, str, str | None]`.
* `FakeLLMProvider`: Фейковый провайдер, возвращающий валидный объект `BriefAnalysisResponse` без выполнения сетевых запросов.
* `GeminiLLMProvider`: Реальный провайдер, работающий на базе **PydanticAI** и Gemini Flash.

#### [models/brief_decode.py](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/backend/app/models/brief_decode.py)
Модель SQLAlchemy `BriefDecode` (вместо `Run`) для таблицы `brief_decodes`:
* `id` (первичный ключ, UUID);
* `status` (строка: `pending`, `completed`, `failed`);
* `input_text` (исходный текст брифа);
* `structured_result` (JSONB, может быть null);
* `raw_provider_output` (текст, может быть null);
* `error_code` (строка, может быть null);
* `error_message` (текст, может быть null);
* `created_at` (timestamp);
* `updated_at` (timestamp).

#### [db/session.py](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/backend/app/db/session.py)
Инициализирует асинхронный движок SQLAlchemy на базе настроек Dynaconf и предоставляет генератор сессий `get_db`.

#### [services/brief_service.py](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/backend/app/services/brief_service.py)
Сервисный слой (бизнес-логика):
* Отвечает за вызовы провайдера ИИ.
* Управляет транзакциями сохранения запусков `BriefDecode` в БД.
* Обрабатывает ошибки валидации и сбоев сети.

#### [api/v1/briefs.py](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/backend/app/api/v1/briefs.py)
Реализует эндпоинты API:
* `POST /v1/briefs/decode`:
  1. Вызывает метод сервиса `BriefService.create_run`.
  2. Возвращает данные запуска.
* `GET /v1/briefs/runs/{run_id}`:
  1. Вызывает метод сервиса `BriefService.get_run`.
  2. Если запись не найдена, возвращает 404.

---

### Расширение Chrome (Chrome Extension)

#### Слой API и Контрактов
* [src/api/client.ts](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/extension/src/api/client.ts): Экземпляр Axios с централизованными настройками и возможностью легкой замены библиотеки.
* [src/api/contracts.ts](file:///home/wstanley/www/unirec_tz/brief_decoder_lite/extension/src/api/contracts.ts): Сгенерированные типы на основе бэкенд-схемы OpenAPI.

#### Модульные Компоненты (Каждый со своими стилями рядом):
* `BriefDecoder/`:
  * `BriefDecoder.tsx`: Логика отправки текста, состояние загрузки, отображение результатов, кнопка копирования.
  * `BriefDecoder.css`: Стили, специфичные для этого контейнера.
* `RiskCard/`:
  * `RiskCard.tsx`: Рендеринг рисков с цветовыми тегами в зависимости от `severity` (Enum).
  * `RiskCard.css`: Стили карточки риска.

---

## План проверки (Verification Plan)

### Автоматические тесты
Мы добавим интеграционные и юнит-тесты в папку `backend/tests/`:
1. **Тесты валидации схемы:**
   * Проверка корректного разбора валидных ответов.
   * Проверка падения валидации при неверном значении `severity`.
   * Проверка падения валидации при отсутствии обязательных полей.
2. **Happy-path тест API:**
   * Отправка запроса на `POST /v1/briefs/decode` с использованием конфигурации `FakeLLMProvider`. Проверка создания записи в БД и успешного статуса ответа.
3. **Failure-path тест API:**
   * Имитация сбоя провайдера ИИ или ошибки валидации. Проверка перевода статуса в `failed` и возврата безопасной ошибки.
4. **Команда для запуска тестов:**
   ```bash
   pytest backend/tests/
   ```

### Ручное тестирование
1. Сборка расширения командой `npm run build` в папке `extension/`.
2. Загрузка расширения в Chrome и проверка функционала.
