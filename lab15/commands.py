"""Паттерн Command: упаковка намерений пользователя в объекты-команды.

Receiver-сервисы (MusicService, Player, InfoService, DialogManager) приходят
из ЛР4 без изменений. Каждая конкретная команда хранит ссылку на свой
Receiver и реализует execute(). Метод accept(visitor) нужен для паттерна
Visitor — обхода истории команд после завершения сеанса.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, TYPE_CHECKING

from interfaces import InfoService, MusicService, Player

if TYPE_CHECKING:
    # Циклический импорт только для аннотаций типов.
    from dialog_manager import DialogManager
    from lab15.visitors import CommandVisitor


class Command(ABC):
    """Абстрактная команда: знает, как выполнить операцию и принять визитора."""

    @abstractmethod
    def execute(self) -> None:
        """Выполняет операцию у своего Receiver."""

    @abstractmethod
    def accept(self, visitor: "CommandVisitor") -> None:
        """Принимает визитора (двойная диспетчеризация по типу команды)."""


class PlayMusicCommand(Command):
    """Запуск трека через MusicService. Receiver — music_service."""

    def __init__(self, music_service: MusicService, manager: "DialogManager", query: Any) -> None:
        self.music_service = music_service
        self.manager = manager
        self.query = query
        self.played_track: str | None = None

    def execute(self) -> None:
        tracks = self.music_service.search(self.query)
        if not tracks:
            self.manager.say("Ничего не найдено")
            return
        track_id = tracks[0]
        self.music_service.play(track_id)
        self.played_track = track_id
        self.manager.say("Воспроизвожу музыку")

    def accept(self, visitor: "CommandVisitor") -> None:
        visitor.visit_play_music(self)


class SetVolumeCommand(Command):
    """Установка громкости через Player. Receiver — player."""

    def __init__(self, player: Player, manager: "DialogManager", level: Any) -> None:
        self.player = player
        self.manager = manager
        self.level_raw = level
        self.level: int | None = None

    def execute(self) -> None:
        try:
            level = int(self.level_raw)
        except (TypeError, ValueError):
            self.manager.say("Неверный уровень громкости")
            return
        self.level = level
        self.player.set_volume(level)
        self.manager.say(f"Громкость установлена: {level}")

    def accept(self, visitor: "CommandVisitor") -> None:
        visitor.visit_set_volume(self)


class GetInfoCommand(Command):
    """Справочный запрос. Receiver — info_service."""

    def __init__(self, info_service: InfoService, manager: "DialogManager", query: Any) -> None:
        self.info_service = info_service
        self.manager = manager
        self.query = query

    def execute(self) -> None:
        result = self.info_service.get_info(self.query)
        self.manager.say(result)

    def accept(self, visitor: "CommandVisitor") -> None:
        visitor.visit_get_info(self)


class GetNewsCommand(Command):
    """Запрос новостей. Receiver — info_service."""

    def __init__(self, info_service: InfoService, manager: "DialogManager", topic: Any) -> None:
        self.info_service = info_service
        self.manager = manager
        self.topic = topic

    def execute(self) -> None:
        news = self.info_service.get_news(self.topic)
        if not news:
            self.manager.say("Новостей нет")
            return
        for item in news:
            self.manager.say(item)

    def accept(self, visitor: "CommandVisitor") -> None:
        visitor.visit_get_news(self)


class ExitCommand(Command):
    """Завершение работы ассистента. Receiver — DialogManager."""

    def __init__(self, manager: "DialogManager") -> None:
        self.manager = manager

    def execute(self) -> None:
        self.manager.stop()

    def accept(self, visitor: "CommandVisitor") -> None:
        visitor.visit_exit(self)


class UnknownCommand(Command):
    """Фоллбэк для нераспознанных намерений. Хранит исходный текст для анализа."""

    def __init__(self, manager: "DialogManager", raw_text: Any) -> None:
        self.manager = manager
        self.raw_text = raw_text

    def execute(self) -> None:
        self.manager.say("Команда не распознана")

    def accept(self, visitor: "CommandVisitor") -> None:
        visitor.visit_unknown(self)


class CommandFactory:
    """Фабрика: по (intent, data) собирает команду со ссылкой на нужный Receiver.

    Все Receiver-сервисы передаются один раз через конструктор —
    клиентский код фабрики не знает об их составе.
    """

    def __init__(
        self,
        music_service: MusicService,
        info_service: InfoService,
        player: Player,
        manager: "DialogManager",
    ) -> None:
        self.music_service = music_service
        self.info_service = info_service
        self.player = player
        self.manager = manager

    def create(self, intent: str, data: Any) -> Command:
        """Возвращает конкретную команду под интент NLU."""
        if intent == "music":
            return PlayMusicCommand(self.music_service, self.manager, data)
        if intent == "volume":
            return SetVolumeCommand(self.player, self.manager, data)
        if intent == "news":
            return GetNewsCommand(self.info_service, self.manager, data)
        if intent == "info":
            return GetInfoCommand(self.info_service, self.manager, data)
        if intent == "exit":
            return ExitCommand(self.manager)
        # Любое неопознанное намерение упаковываем в UnknownCommand,
        # чтобы Visitor мог потом его проанализировать.
        return UnknownCommand(self.manager, data)


class CommandInvoker:
    """Инвокер: выполняет команды и хранит историю для последующего обхода Visitor'ами."""

    def __init__(self) -> None:
        self.history: List[Command] = []

    def execute(self, command: Command) -> None:
        """Запускает команду и фиксирует её в истории."""
        command.execute()
        self.history.append(command)
