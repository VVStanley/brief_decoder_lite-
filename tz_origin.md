# Тестовое задание: Senior Fullstack Engineer, Platform + Chrome Extensions

## Контекст

AnytoolAI строит платформенное ядро для запуска AI-сценариев из декларативных конфигов: input -> workflow/action -> LLM provider -> structured output -> artifact/result -> Chrome Extension UI.

Нам нужен инженер, который может провести небольшую фичу через backend, LLM structured output, typed API, Chrome Extension, тесты и документацию.

## Задача

Сделать прототип **AI Brief Decoder Lite**.

Пользователь вставляет текст клиентского брифа или задачи в Chrome Extension. Backend вызывает LLM, получает структурированный результат, валидирует его через Pydantic и возвращает результат в extension UI.

Ограничение по времени: **2 рабочих дня**.

Если не успеваете реализовать всё, сдайте рабочий end-to-end slice и опишите, что осталось бы сделать дальше.

## Основной сценарий

Input example:

```text
We need a landing page for a B2B SaaS analytics product.
The page should explain the product, include pricing teaser,
capture emails, and be ready in 2 weeks.
Budget is limited. We also need copy suggestions and basic SEO.
```

Expected structured result:

```json
{
  "summary": "Short normalized summary of the client request",
  "goals": ["..."],
  "deliverables": ["..."],
  "constraints": ["..."],
  "risks": [
    {
      "risk": "...",
      "severity": "low|medium|high",
      "reason": "..."
    }
  ],
  "clarifying_questions": ["..."],
  "recommended_next_action": "..."
}
```

## Requirements

### Backend

Implement a FastAPI service.

Required endpoints:

- `POST /v1/briefs/decode`
- `GET /v1/briefs/runs/{run_id}`
- `GET /health`

The backend must:

- accept raw brief text;
- call an LLM through a provider abstraction;
- support fake/mock provider for local review without API keys;
- validate structured output with **Pydantic**;
- optionally use **PydanticAI**;
- store decode runs in PostgreSQL;
- return safe errors for provider or validation failures.

Minimum stored fields:

- run id;
- status;
- input text;
- structured result;
- raw provider output;
- safe error code/message;
- timestamps.

### LLM Structured Output

The implementation must handle:

- valid structured output;
- malformed JSON or invalid structured response;
- missing required fields;
- invalid `severity` value;
- provider failure.

### Chrome Extension

Frontend must be a **Chrome Extension**.

The extension must include:

- text input for brief/task text;
- run button;
- loading state;
- result rendering;
- error state;
- copy result action.

Use React + TypeScript. WXT is preferred but not required.

### AI-assisted Coding

Use a coding agent during the task: Codex, Cursor, Claude Code, Copilot Chat or similar.

Add `AI_USAGE.md` with:

- which agent/tools you used;
- which parts you delegated;
- examples of 3-5 prompts or task briefs;
- what you accepted, changed or rejected;
- how you verified generated code;
- one or more mistakes or limitations you found in agent output.

### Tests

Required:

- backend tests for structured output validation;
- backend API happy-path test with fake provider;
- at least one backend failure-path test;
- frontend/extension typecheck or build command.

## Submission

Submit a Git repository or archive with:

- source code;
- README with setup, run and test commands;
- instructions for fake provider and real LLM provider if implemented;
- `AI_USAGE.md`;
- notes on assumptions and tradeoffs.

The project must be runnable locally without a paid API key.

## Evaluation

We will evaluate:

- backend architecture and API boundaries;
- quality of Pydantic structured output validation;
- provider abstraction and fake provider support;
- Chrome Extension implementation;
- tests and local reproducibility;
- clarity of README;
- quality of AI-assisted coding workflow and review discipline.