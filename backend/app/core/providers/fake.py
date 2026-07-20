# ruff: noqa: E501
import hashlib
import random

from polyfactory.factories.pydantic_factory import ModelFactory

from app.core.providers.base import LLMProvider
from app.schemas import BriefAnalysisResponse, RiskItem, SeverityEnum


class RiskItemFactory(ModelFactory[RiskItem]):
    __model__ = RiskItem

    @classmethod
    def risk(cls) -> str:
        risks = [
            "Отсутствие технического задания (ТЗ)",
            "Интеграция с внешними платежными шлюзами",
            "Высокая нагрузка на сервер в пиковые часы",
            "Сжатые сроки реализации проекта",
            "Проблемы с интеграцией устаревших (legacy) систем",
            "Сложность синхронизации данных в реальном времени",
        ]
        return random.choice(risks)

    @classmethod
    def severity(cls) -> SeverityEnum:
        return random.choice(list(SeverityEnum))

    @classmethod
    def reason(cls) -> str:
        reasons = [
            "В брифе не описаны детальные требования к архитектуре и интеграциям.",
            "Сторонний платежный шлюз может иметь нестабильный API и задержки в обработке транзакций.",
            "В пиковые часы количество одновременных запросов может превысить базовую емкость сервера.",
            "Установленный дедлайн требует высокой параллелизации задач без права на задержку.",
            "Существующие устаревшие системы не поддерживают современные REST/gRPC протоколы.",
            "Высокий поток событий может приводить к рассинхронизации состояния клиентов.",
        ]
        return random.choice(reasons)


class BriefAnalysisResponseFactory(ModelFactory[BriefAnalysisResponse]):
    __model__ = BriefAnalysisResponse

    @classmethod
    def summary(cls) -> str:
        summaries = [
            "Разработка B2B SaaS аналитической платформы с интерактивным дашбордом и сбором лидов.",
            "Создание мобильного приложения для заказа и доставки еды с интеграцией онлайн-оплаты.",
            "Внедрение корпоративной CRM-системы для автоматизации воронки продаж и отчетности.",
            "Запуск интернет-магазина одежды с фильтрацией каталога и личным кабинетом.",
        ]
        return random.choice(summaries)

    @classmethod
    def goals(cls) -> list[str]:
        goals_pool = [
            "Повысить конверсию посетителей в зарегистрированных пользователей",
            "Сократить время обработки клиентских заявок",
            "Увеличить средний чек за счет умных рекомендаций",
            "Обеспечить прозрачную аналитику по всем маркетинговым каналам",
            "Автоматизировать рутинные операции менеджеров по продажам",
        ]
        return random.sample(goals_pool, k=random.randint(2, 4))

    @classmethod
    def deliverables(cls) -> list[str]:
        deliverables_pool = [
            "Адаптивный Landing Page с тизером тарифов",
            "Модуль сбора e-mail адресов и интеграция с CRM",
            "Панель администрирования для управления контентом",
            "Интерактивный дашборд с графиками активности",
            "Базовая SEO-оптимизация и разметка микроданных",
        ]
        return random.sample(deliverables_pool, k=random.randint(2, 4))

    @classmethod
    def constraints(cls) -> list[str]:
        constraints_pool = [
            "Жесткий дедлайн: готовность через 2 недели",
            "Ограниченный фиксированный бюджет на разработку",
            "Обязательное использование React и TypeScript",
            "Интеграция с существующей legacy-базой данных",
        ]
        return random.sample(constraints_pool, k=random.randint(1, 3))

    @classmethod
    def risks(cls) -> list[RiskItem]:
        return [RiskItemFactory.build() for _ in range(random.randint(1, 3))]

    @classmethod
    def clarifying_questions(cls) -> list[str]:
        questions_pool = [
            "Какой сервис рассылок или CRM планируется использовать для сбора e-mail?",
            "У вас уже есть готовый брендбук, логотип и тексты для страниц?",
            "Потребуется ли мультиязычность в первой версии продукта?",
            "Какие ключевые метрики вы планируете отслеживать в аналитике?",
        ]
        return random.sample(questions_pool, k=random.randint(2, 3))

    @classmethod
    def recommended_next_action(cls) -> str:
        actions = [
            "Согласовать структуру Landing Page и провести встречу с дизайнером для создания прототипа.",
            "Утвердить техническое задание на интеграцию с платежными шлюзами и CRM.",
            "Подготовить тестовое окружение и доступы к API сторонних сервисов.",
            "Разработать MVP с минимальным набором функций для проверки гипотезы за 2 недели.",
        ]
        return random.choice(actions)


class FakeLLMProvider(LLMProvider):
    """A fake mock provider that returns a realistic dynamic brief analysis using Pydantic factories."""

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        # Seed random with text hash to ensure that the same input always returns the same result
        seed_val = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        random.seed(seed_val)

        # Build response using factory
        return BriefAnalysisResponseFactory.build()
