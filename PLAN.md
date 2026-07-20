# План доработки и рефакторинга AI Brief Decoder Lite

В данном документе зафиксирован пошаговый план из 10 пунктов по улучшению архитектуры, надежности и конфигурации проекта.

## Чек-лист задач

- [x] **1. Проверка директории и структуры проекта**
  - Убедиться, что все изменения вносятся в `/home/wstanley/www/brief_decoder_lite` (`backend/` и `extention/`).

- [x] **2. Замена захардкоженных статусов на модели (`BriefStatus`)**
  - В `backend/app/models/brief.py`: заменить `default="pending"` на `default=BriefStatus.PENDING.value` (или строковое значение Enum).
  - В `backend/app/repositories/brief.py`: заменить `status="pending"` на `status=BriefStatus.PENDING.value`.
  - В `backend/app/services/cleanup_service.py`: заменить `"processing"` и `"failed"` на `BriefStatus.PROCESSING.value` и `BriefStatus.FAILED.value`.

- [ ] **3. Аудит и проверка `BriefAnalysisResponse` на соответствие ТЗ**
  - Проверить структуру схемы ответа `BriefAnalysisResponse` (`project_type`, `budget_info`, `deadline_info`, `key_requirements`, `risks`), системный промпт (`prompts.py`) и типы на фронтенде (`contracts.ts`).
  - Устранить любые несоответствия или расхождения между ТЗ, Pydantic-схемой и моками в `polyfactory`.

- [ ] **4. Логирование и отправка ошибок в Sentry для фоновой задачи**
  - В `backend/app/api/v1/briefs.py` (`run_background_brief_decode`) заменить тихое подавление (`except Exception: pass`) на полноценный перехват и отправку в Sentry:
    ```python
    except Exception as e:
        logger.error(f"Background execution failed for brief {brief_id}: {e}", exc_info=True)
        sentry_sdk.capture_exception(e)
    ```

- [ ] **5. Кеширование `get_llm_provider` через `@lru_cache`**
  - В `backend/app/core/providers/__init__.py` обернуть фабрику `get_llm_provider()` декоратором `@lru_cache()` для предотвращения повторной инициализации клиента и моделей Gemini на каждый запрос.

- [ ] **6. Вынос инициализации `BriefService` из API-роутеров (DI)**
  - Создать фабричную зависимость FastAPI `get_brief_service` для внедрения зависимостей (`BriefRepository` и `LLMProvider`).
  - В роутерах (`app/api/v1/briefs.py`) заменить ручной вызов `service = BriefService(repo, provider)` на внедрение через `Depends(get_brief_service)`.

- [ ] **7. Переработка декоратора ретраев (`RetryingLLMProvider`) с использованием `tenacity`**
  - Установить библиотеку `tenacity` (`poetry add tenacity`).
  - Переписать логику повторных попыток в `RetryingLLMProvider` с использованием `AsyncRetrying`, настроек задержек (`wait_exponential` / `wait_fixed`) и логгера событий.

- [ ] **8. Замена `dynaconf` на `pydantic-settings`**
  - Удалить `dynaconf` (`poetry remove dynaconf`) и добавить `pydantic-settings` (`poetry add pydantic-settings`).
  - Переписать `backend/app/core/config.py` с использованием `BaseSettings`, поддержкой файлов `.env` / `settings.toml` и переопределений из системных переменных окружения.
  - Очистить зависимости и тестовое окружение (`conftest.py`, `alembic/env.py`) от следов Dynaconf.

- [ ] **9. Валидация и фильтрация входного текста брифа**
  - В схеме `BriefRequest` и `BriefService` добавить проверки на наличие бессмысленных символов, спама или отсутствия реальных буквенно-цифровых слов.
  - Отклонять мусорный входной поток на раннем этапе до отправки запроса к ИИ-модели.

- [ ] **10. Механизм самокоррекции LLM при ошибке `ValidationError`**
  - При возникновении ошибки валидации Pydantic-схемы ответа от ИИ отправлять модели повторный запрос с указанием предыдущего ошибочного ответа и описанием ошибки валидации для автоматической корректировки формата JSON.
