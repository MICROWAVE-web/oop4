"""Composite: иерархия «ответа» ассистента (листья и контейнеры)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pprint import pprint
from typing import List


class ResponseComponent(ABC):
    """Общий интерфейс узла дерева ответа."""

    @abstractmethod
    def get_children(self) -> List["ResponseComponent"]:
        """Дочерние узлы (для листа — пустой список)."""


class TextLeaf(ResponseComponent):
    """Лист: один текстовый фрагмент для озвучивания."""

    def __init__(self, text: str) -> None:
        self.text = text
        self._children: List[ResponseComponent] = []


    def add(self, child: ResponseComponent) -> None:
        self._children.append(child)

    def get_children(self) -> List[ResponseComponent]:
        return list(self._children)




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
        self.add(TextLeaf(f"Новости по теме «{self._topic.strip() or 'общее'}»."))
        for i, item in enumerate(items, start=1):
            self.add(TextLeaf(f"Пункт {i}. {item}"))
        self.add(TextLeaf("Это были главные заголовки."))



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
        group = NewsResponseGroup(topic)
        group.build_from_items(items)

        group2 = NewsResponseGroup("СПОРТ")

        football_theme = TextLeaf("Футбол")
        football = TextLeaf("Футбол: Россия VS США")
        football_theme.add(football)
        group2.add(football_theme)
        # group2.build_from_items(["футбол", "волейбол"])

        group.add(group2)

        ch = group.get_children()
        for child in ch:
            print(child)
        return group

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
