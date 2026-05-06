"""Паттерн Visitor: обход истории команд с операциями, которые задаются извне.

Команды только реализуют accept(visitor) — сама логика анализа живёт
в визиторах. Чтобы добавить новую аналитику, достаточно создать новый
подкласс CommandVisitor; классы команд при этом не меняются.
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Dict, Iterable, List

if TYPE_CHECKING:
    from lab15.commands import (
        Command,
        ExitCommand,
        GetInfoCommand,
        GetNewsCommand,
        PlayMusicCommand,
        SetVolumeCommand,
        UnknownCommand,
    )


class CommandVisitor(ABC):
    """Базовый визитор: по умолчанию все методы — пустые заглушки.

    Конкретные визиторы переопределяют только нужные им методы.
    Это вариант с «пустыми» visit-методами     """


    def visit_play_music(self, command: "PlayMusicCommand") -> None:
        pass

    def visit_set_volume(self, command: "SetVolumeCommand") -> None:
        pass

    def visit_get_info(self, command: "GetInfoCommand") -> None:
        pass

    def visit_get_news(self, command: "GetNewsCommand") -> None:
        pass

    def visit_exit(self, command: "ExitCommand") -> None:
        pass

    def visit_unknown(self, command: "UnknownCommand") -> None:
        pass


def visit_all(visitor: CommandVisitor, history: Iterable["Command"]) -> None:
    """Утилита: применяет визитор ко всем командам истории."""
    for command in history:
        command.accept(visitor)


class CommandStatisticsVisitor(CommandVisitor):
    """Считает количество команд каждого типа за сеанс."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {
            "music": 0,
            "volume": 0,
            "info": 0,
            "news": 0,
            "exit": 0,
            "unknown": 0,
        }

    def visit_play_music(self, command: "PlayMusicCommand") -> None:
        self._counters["music"] += 1

    def visit_set_volume(self, command: "SetVolumeCommand") -> None:
        self._counters["volume"] += 1

    def visit_get_info(self, command: "GetInfoCommand") -> None:
        self._counters["info"] += 1

    def visit_get_news(self, command: "GetNewsCommand") -> None:
        self._counters["news"] += 1

    def visit_exit(self, command: "ExitCommand") -> None:
        self._counters["exit"] += 1

    def visit_unknown(self, command: "UnknownCommand") -> None:
        self._counters["unknown"] += 1

    def report(self) -> str:
        parts = [f"{name}={count}" for name, count in self._counters.items()]
        return "[STATS] " + ", ".join(parts)


class CommandLogVisitor(CommandVisitor):
    """Формирует человекочитаемый журнал из истории команд."""

    def __init__(self) -> None:
        self._lines: List[str] = []

    def visit_play_music(self, command: "PlayMusicCommand") -> None:
        track = command.played_track or "—"
        self._lines.append(f"music: query='{command.query}', track={track}")

    def visit_set_volume(self, command: "SetVolumeCommand") -> None:
        level = command.level if command.level is not None else f"!{command.level_raw}!"
        self._lines.append(f"volume: level={level}")

    def visit_get_info(self, command: "GetInfoCommand") -> None:
        self._lines.append(f"info: query='{command.query}'")

    def visit_get_news(self, command: "GetNewsCommand") -> None:
        self._lines.append(f"news: topic='{command.topic}'")

    def visit_exit(self, command: "ExitCommand") -> None:
        self._lines.append("exit: завершение работы")

    def visit_unknown(self, command: "UnknownCommand") -> None:
        self._lines.append(f"unknown: '{command.raw_text}'")

    def report(self) -> str:
        if not self._lines:
            return "[LOG] (история пуста)"
        body = "\n".join(f"  {i + 1}. {line}" for i, line in enumerate(self._lines))
        return "[LOG] Журнал команд сеанса:\n" + body


class UnknownCommandsVisitor(CommandVisitor):
    """Собирает все нераспознанные запросы — для анализа покрытия NLU."""

    def __init__(self) -> None:
        self._items: List[str] = []

    def visit_unknown(self, command: "UnknownCommand") -> None:
        self._items.append(str(command.raw_text))

    def report(self) -> str:
        if not self._items:
            return "[UNKNOWN] нераспознанных команд не было"
        body = "\n".join(f"  - '{text}'" for text in self._items)
        return f"[UNKNOWN] нераспознано {len(self._items)} запрос(ов):\n{body}"
