"""Паттерн Memento: снимок настроек ассистента и хранитель снимков."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class SettingsMemento:
    """Иммутабельный снимок настроек: громкость, текущий трек, имя состояния."""

    volume: int
    current_track: Optional[str]
    state_name: str


class SettingsCaretaker:
    """Хранитель снимков. Работает только с готовыми SettingsMemento."""

    def __init__(self) -> None:
        self._stack: List[SettingsMemento] = []

    def save(self, memento: SettingsMemento) -> None:
        """Кладёт снимок в стек."""
        self._stack.append(memento)

    def restore(self) -> SettingsMemento:
        """Возвращает последний сохранённый снимок (без удаления)."""
        if not self._stack:
            raise RuntimeError("Нет сохранённых снимков")
        return self._stack[-1]

    def has_snapshot(self) -> bool:
        """Есть ли хотя бы один снимок."""
        return bool(self._stack)

    def count(self) -> int:
        """Сколько снимков в стеке."""
        return len(self._stack)
