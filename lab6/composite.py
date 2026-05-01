"""Composite: иерархия «ответа» ассистента (листья и контейнеры)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class ResponseComponent(ABC):
    """Общий интерфейс узла дерева ответа."""

    @abstractmethod
    def get_children(self) -> List["ResponseComponent"]:
        """Дочерние узлы (для листа — пустой список)."""


class TextLeaf(ResponseComponent):
    """Лист: один текстовый фрагмент. Детей нет — вложенность только через ResponseGroup."""

    def __init__(self, text: str) -> None:
        self.text = text

    def get_children(self) -> List[ResponseComponent]:
        return []




class ResponseGroup(ResponseComponent):
    """Контейнер: объединяет несколько дочерних компонентов."""

    def __init__(self) -> None:
        self._children: List[ResponseComponent] = []

    def add(self, child: ResponseComponent) -> None:
        self._children.append(child)

    def get_children(self) -> List[ResponseComponent]:
        return list(self._children)


class NewsResponseGroup(ResponseGroup):
    """Специализированный композит для сценария «новости»: заголовок + пункты + хвост."""

    def __init__(self, topic: str) -> None:
        super().__init__()
        self._topic = topic

    def build_from_items(self, items: List[str]) -> None:
        news_group = ResponseGroup()

        news_group.add(TextLeaf(f"Новости по теме «{self._topic.strip() or 'общее'}»."))
        option_group = ResponseGroup()
        for i, item in enumerate(items, start=1):
            option_group.add(TextLeaf(f"Пункт {i}. {item}"))
        news_group.add(option_group)
        news_group.add(TextLeaf("Это были главные заголовки."))
        news_group.add(TextLeaf(""))

        self.add(news_group)



class ResponseBuilder:
    """Строит дерево ResponseComponent под разные намерения диалога."""

    def build_startup(self) -> ResponseComponent:
        return TextLeaf("Голосовой ассистент запущен")

    def build_music_ok(self) -> ResponseComponent:
        return TextLeaf("Воспроизвожу музыку")

    def build_music_empty(self) -> ResponseComponent:
        return TextLeaf("Ничего не найдено")

    def build_info(self, text: str) -> ResponseComponent:
        return TextLeaf(text)

    def build_news(self, topic: str, items: List[str]) -> ResponseComponent:

        main = NewsResponseGroup(topic)

        main.build_from_items(items)

        sport = ResponseGroup()
        sport.add(TextLeaf("Вложенный раздел спорта."))

        football = ResponseGroup()
        football.add(TextLeaf("Футбол: Австрия VS Португалия"))
        football.add(TextLeaf("Футбол: Россия VS США"))

        sport.add(football)
        sport.add(TextLeaf("Это были главные новости спорта"))
        sport.add(TextLeaf(""))

        main.add(sport)
        return main

    def build_news_empty(self) -> ResponseComponent:
        return TextLeaf("Новостей нет")

    def build_volume_ok(self, level: int) -> ResponseComponent:
        return TextLeaf(f"Громкость установлена: {level}")

    def build_volume_error(self) -> ResponseComponent:
        return TextLeaf("Неверный уровень громкости")

    def build_unknown(self) -> ResponseComponent:
        return TextLeaf("Команда не распознана")

    def build_error(self) -> ResponseComponent:
        return TextLeaf("Произошла ошибка. Повторите запрос.")

    def build_goodbye(self) -> ResponseComponent:
        return TextLeaf("Завершение работы")

    def build_ml_stub(self, raw: object) -> ResponseComponent:
        return TextLeaf(f"ML NLU (заглушка): распознан сырой ввод {raw!r}")
