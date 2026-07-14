# ruff: noqa: E501
import hashlib
import random

from polyfactory.factories.pydantic_factory import ModelFactory

from app.core.providers.base import LLMProvider
from app.schemas import BriefAnalysisResponse, RiskItem, SeverityEnum


class RiskItemFactory(ModelFactory[RiskItem]):
    __model__ = RiskItem

    @classmethod
    def description(cls) -> str:
        descriptions = [
            "Отсутствие технического задания (ТЗ)",
            "Интеграция с внешними платежными шлюзами",
            "Высокая нагрузка на сервер в пиковые часы",
            "Сжатые сроки реализации проекта",
            "Проблемы с интеграцией устаревших (legacy) систем",
            "Сложность синхронизации данных в реальном времени",
        ]
        return random.choice(descriptions)

    @classmethod
    def severity(cls) -> SeverityEnum:
        return random.choice(list(SeverityEnum))

    @classmethod
    def mitigation(cls) -> str:
        mitigations = [
            "Провести серию встреч и составить подробное ТЗ перед написанием кода.",
            "Использовать проверенные готовые SDK (ЮKassa, Сбербанк) и заложить время на тесты.",
            "Настроить горизонтальное масштабирование и кэширование запросов.",
            "Разработать MVP с минимальным набором функций для быстрого запуска.",
            "Спроектировать сбалансированный слой адаптеров и провести нагрузочные тесты интеграции.",
            "Использовать брокеры сообщений (Redis/RabbitMQ) для надежной очереди задач.",
        ]
        return random.choice(mitigations)


class BriefAnalysisResponseFactory(ModelFactory[BriefAnalysisResponse]):
    __model__ = BriefAnalysisResponse

    @classmethod
    def project_type(cls) -> str:
        project_types = [
            "Интернет-магазин одежды",
            "Мобильное приложение доставки еды",
            "CRM-система для управления продажами",
            "Социальная сеть для совместных поездок",
            "ERP-система автоматизации логистики",
            "Платформа онлайн-обучения",
        ]
        return random.choice(project_types)

    @classmethod
    def budget_info(cls) -> str:
        return f"{random.randint(150, 950)} тыс. рублей"

    @classmethod
    def deadline_info(cls) -> str:
        return f"{random.randint(2, 6)} месяца"

    @classmethod
    def key_requirements(cls) -> list[str]:
        requirements_pool = [
            "Каталог товаров с умной фильтрацией и поиском",
            "Корзина товаров и интеграция онлайн-оплаты (СБП/карты)",
            "Личный кабинет пользователя с историей и избранным",
            "Интерактивная карта для выбора адреса доставки",
            "Система push-уведомлений о статусе заказа",
            "Панель администратора для управления товарами и заказами",
            "Интеграция с 1С для синхронизации остатков на складе",
            "Канбан-доска для сделок и воронки продаж",
            "Генерация PDF-отчетов об активности пользователей",
        ]
        # Choose 3 to 5 random requirements
        return random.sample(requirements_pool, k=random.randint(3, 5))

    @classmethod
    def risks(cls) -> list[RiskItem]:
        # Generate 1 to 3 risks using RiskItemFactory
        return [RiskItemFactory.build() for _ in range(random.randint(1, 3))]


class FakeLLMProvider(LLMProvider):
    """A fake mock provider that returns a realistic dynamic brief analysis using Pydantic factories."""

    async def analyze_brief(self, text: str) -> BriefAnalysisResponse:
        # Seed random with text hash to ensure that the same input always returns the same result
        seed_val = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        random.seed(seed_val)

        # Build response using factory
        return BriefAnalysisResponseFactory.build()
