"""Паттерн Observer: субъект событий и набор конкретных наблюдателей."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TextIO


class EventObserver(ABC):
    """Базовый интерфейс наблюдателя."""

    @abstractmethod
    def update(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Принимает событие от субъекта."""


class EventSubject:
    """Источник событий: ведёт список подписчиков и рассылает уведомления."""

    def __init__(self) -> None:
        self._observers: List[EventObserver] = []

    def attach(self, observer: EventObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: EventObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_name: str, payload: Dict[str, Any] | None = None) -> None:
        """Рассылает событие всем подписчикам."""
        data = payload or {}
        for observer in list(self._observers):
            observer.update(event_name, data)


class LoggerObserver(EventObserver):
    """Пишет события в открытый текстовый поток (например, в run.log)."""

    def __init__(self, stream: TextIO) -> None:
        self._stream = stream

    def update(self, event_name: str, payload: Dict[str, Any]) -> None:
        self._stream.write(f"[LOG] {event_name}: {payload}\n")
        self._stream.flush()


class StatisticsObserver(EventObserver):
    """Считает простые счётчики событий за сеанс."""

    def __init__(self) -> None:
        self.counters: Dict[str, int] = {}

    def update(self, event_name: str, payload: Dict[str, Any]) -> None:
        self.counters[event_name] = self.counters.get(event_name, 0) + 1

    def report(self) -> str:
        """Печатное представление накопленной статистики."""
        items = ", ".join(f"{k}={v}" for k, v in sorted(self.counters.items()))
        return f"[STATS] {items}" if items else "[STATS] нет событий"


class ScreenObserver(EventObserver):
    """Имитация экрана колонки: печатает текущий «экран» при событиях."""

    def __init__(self) -> None:
        self._volume: int = 0
        self._track: str = "—"
        self._mode: str = "Idle"

    def update(self, event_name: str, payload: Dict[str, Any]) -> None:
        if event_name == "volume_changed":
            self._volume = int(payload.get("volume", self._volume))
        elif event_name == "track_started":
            self._track = str(payload.get("track", self._track))
        elif event_name == "track_stopped":
            self._track = "—"
        elif event_name == "state_changed":
            self._mode = str(payload.get("to", self._mode))
        print(f"[SCREEN] mode={self._mode} | track={self._track} | vol={self._volume}")
