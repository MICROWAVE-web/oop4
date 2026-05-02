"""Паттерн Chain of Responsibility: предобработка пользовательского текста до NLU.

Каждое звено отвечает ровно за одну обязанность и решает, передавать ли
запрос дальше. Если handle() возвращает None — цепочка прервана, и
вызывающий код (CommandDialogManager) пропускает итерацию главного цикла.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class TextHandler(ABC):
    """Базовый обработчик: хранит ссылку на следующее звено."""

    def __init__(self) -> None:
        self._next: Optional["TextHandler"] = None

    def set_next(self, handler: "TextHandler") -> "TextHandler":
        """Связывает текущее звено со следующим. Возвращает следующее — для чейнинга."""
        self._next = handler
        return handler

    def handle(self, text: str) -> Optional[str]:
        """Шаблонный метод: применяет _process(), затем передаёт дальше."""
        processed = self._process(text)
        if processed is None:
            return None
        if self._next is None:
            return processed
        return self._next.handle(processed)

    @abstractmethod
    def _process(self, text: str) -> Optional[str]:
        """Конкретное преобразование. None = «прервать цепочку»."""


class StripHandler(TextHandler):
    """Удаляет ведущие и хвостовые пробелы."""

    def _process(self, text: str) -> Optional[str]:
        return text.strip()


class EmptyTextHandler(TextHandler):
    """Прерывает цепочку, если строка пустая."""

    def _process(self, text: str) -> Optional[str]:
        if text == "":
            print("[CHAIN] EmptyTextHandler: пустой запрос, итерация пропущена")
            return None
        return text


class LowercaseHandler(TextHandler):
    """Приводит текст к нижнему регистру для устойчивости NLU."""

    def _process(self, text: str) -> Optional[str]:
        lowered = text.lower()
        if lowered != text:
            print(f"[CHAIN] LowercaseHandler: '{text}' -> '{lowered}'")
        return lowered


class LoggingHandler(TextHandler):
    """Финальное звено: фиксирует, что текст прошёл все фильтры."""

    def _process(self, text: str) -> Optional[str]:
        print(f"[CHAIN] LoggingHandler: текст принят к разбору: '{text}'")
        return text


def build_default_chain() -> TextHandler:
    """Собирает стандартную цепочку: Strip -> Empty -> Lowercase -> Logging.

    Возвращает первое звено — клиент может сразу вызвать chain.handle(text).
    """
    strip = StripHandler()
    empty = EmptyTextHandler()
    lower = LowercaseHandler()
    log = LoggingHandler()

    strip.set_next(empty).set_next(lower).set_next(log)
    return strip
