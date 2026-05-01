"""Паттерн State: режимы работы ассистента."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lab13.dialog_manager_ext import StatefulDialogManager


class AssistantState(ABC):
    """Базовый класс состояния ассистента."""

    @abstractmethod
    def name(self) -> str:
        """Возвращает строковое имя состояния (для логов и снимков)."""

    @abstractmethod
    def handle(self, ctx: "StatefulDialogManager", intent: str, data: Any) -> None:
        """Обрабатывает намерение в текущем состоянии и при необходимости меняет его."""


class IdleState(AssistantState):
    """Режим ожидания: ассистент готов принять любую команду."""

    def name(self) -> str:
        return "Idle"

    def handle(self, ctx: "StatefulDialogManager", intent: str, data: Any) -> None:
        if intent == "music":
            ctx.start_music(data)
            ctx.set_state(PlayingState())
        elif intent == "volume":
            ctx.change_volume(data)
        elif intent == "info":
            ctx.delegate_info(data)
        elif intent == "news":
            ctx.delegate_news(data)
        elif intent == "snapshot":
            ctx.save_snapshot()
        elif intent == "restore":
            ctx.restore_snapshot()
        elif intent == "mute":
            ctx.set_state(MutedState())
        elif intent == "unmute":
            ctx.say("Уже в обычном режиме")
        elif intent == "exit":
            ctx.stop()
        else:
            ctx.say("Команда не распознана")


class PlayingState(AssistantState):
    """Режим воспроизведения музыки."""

    def name(self) -> str:
        return "Playing"

    def handle(self, ctx: "StatefulDialogManager", intent: str, data: Any) -> None:
        if intent == "music":
            ctx.say(f"Уже играет: {ctx.current_track}")
        elif intent == "volume":
            ctx.change_volume(data)
        elif intent == "system" and data == "stop":
            ctx.stop_music()
            ctx.set_state(IdleState())
        elif intent == "info":
            ctx.delegate_info(data)
        elif intent == "news":
            ctx.delegate_news(data)
        elif intent == "snapshot":
            ctx.save_snapshot()
        elif intent == "restore":
            ctx.restore_snapshot()
        elif intent == "mute":
            ctx.stop_music()
            ctx.set_state(MutedState())
        elif intent == "exit":
            ctx.stop_music()
            ctx.stop()
        else:
            ctx.say("Команда не распознана")


class MutedState(AssistantState):
    """Режим «не беспокоить»: пользовательские команды игнорируются."""

    def name(self) -> str:
        return "Muted"

    def handle(self, ctx: "StatefulDialogManager", intent: str, data: Any) -> None:
        if intent == "unmute":
            ctx.set_state(IdleState())
        elif intent == "exit":
            ctx.stop()
        else:
            ctx.say("Не беспокоить: команда проигнорирована")
