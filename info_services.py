"""Реализации справочных сервисов (информация и новости)."""

from interfaces import InfoService
from typing import List


class YandexInfoService(InfoService):
    """Имитация получения информации и новостей через Яндекс."""

    def get_info(self, query: str) -> str:
        """Возвращает текстовый ответ по запросу (заглушка)."""
        return f"Yandex: информация по '{query}'"

    def get_news(self, topic: str, count: int = 5) -> List[str]:
        """Возвращает список новостей по теме (заглушка)."""
        return [f"Yandex news {i+1} about {topic}" for i in range(count)]


class GoogleInfoService(InfoService):
    """Имитация получения информации и новостей через Google."""

    def get_info(self, query: str) -> str:
        """Возвращает текстовый ответ по запросу (заглушка)."""
        return f"Google: информация по '{query}'"

    def get_news(self, topic: str, count: int = 5) -> List[str]:
        """Возвращает список новостей по теме (заглушка)."""
        return [f"Google news {i+1} about {topic}" for i in range(count)]


class WikipediaInfoService(InfoService):
    """Имитация получения справки из Wikipedia; новости не поддерживаются."""

    def get_info(self, query: str) -> str:
        """Возвращает краткое описание по запросу (заглушка)."""
        return f"Wikipedia summary for {query}"

    def get_news(self, topic: str, count: int = 5) -> List[str]:
        """Wikipedia не предоставляет новости — пустой список."""
        return []
