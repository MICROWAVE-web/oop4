"""Iterator: обход дерева ResponseComponent разными стратегиями."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import List

from .composite import ResponseComponent, TextLeaf

# Два пробела на уровень вложенности (визуально в консоли).
_INDENT_UNIT = "  "


class ResponseIterator(ABC):
    """Интерфейс итератора текстовых фрагментов (без привязки к структуре коллекции)."""

    @abstractmethod
    def has_next(self) -> bool:
        """Есть ли ещё фрагмент для выдачи."""

    @abstractmethod
    def next_fragment(self) -> str:
        """Следующий текстовый фрагмент (вызывать только при has_next() == True)."""


class DepthFirstTextIterator(ResponseIterator):
    """Обход в глубину (pre-order): сначала листья слева направо в каждой ветви."""

    def __init__(self, root: ResponseComponent) -> None:
        self._queue: List[str] = []
        self._flatten_dfs(root, depth=-1)
        self._index = 0

    def _flatten_dfs(self, node: ResponseComponent, depth: int) -> None:
        if isinstance(node, TextLeaf):
            pad = _INDENT_UNIT * max(0, depth)
            self._queue.append(f"{pad}{node.text}")
            return
        next_depth = depth + 1
        for ch in node.get_children():
            self._flatten_dfs(ch, next_depth)

    def has_next(self) -> bool:
        return self._index < len(self._queue)

    def next_fragment(self) -> str:
        t = self._queue[self._index]
        self._index += 1
        return t


class BreadthFirstTextIterator(ResponseIterator):
    """
    Обход в ширину по узлам: тексты листьев собираются в порядке появления уровнями.
    Подходит для демонстрации отличия от DFS на деревьях с вложенностью > 1.
    """

    def __init__(self, root: ResponseComponent) -> None:
        self._queue_fragments: List[str] = []
        q: deque[tuple[ResponseComponent, int]] = deque([(root, -1)])
        while q:
            node, depth = q.popleft()
            if isinstance(node, TextLeaf):
                pad = _INDENT_UNIT * max(0, depth)
                self._queue_fragments.append(f"{pad}{node.text}")
            else:
                next_depth = depth + 1
                for ch in node.get_children():
                    q.append((ch, next_depth))
        self._index = 0

    def has_next(self) -> bool:
        return self._index < len(self._queue_fragments)

    def next_fragment(self) -> str:
        t = self._queue_fragments[self._index]
        self._index += 1
        return t


class ResponseIteratorFactory:
    """Фабрика: выбор стратегии обхода (конфигурирование Iterator)."""

    STRATEGY_DFS = "dfs"
    STRATEGY_BFS = "bfs"

    def create(self, strategy: str, root: ResponseComponent) -> ResponseIterator:
        if strategy == self.STRATEGY_DFS:
            return DepthFirstTextIterator(root)
        if strategy == self.STRATEGY_BFS:
            return BreadthFirstTextIterator(root)
        raise ValueError(f"Неизвестная стратегия обхода: {strategy!r}")
