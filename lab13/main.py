"""Демонстрация ЛР13: State + Memento + Observer на базе ЛР4 и сборки ЛР11."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

# Добавляем корень проекта в путь, чтобы использовать модули ЛР4 и ЛР11.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from interfaces import VoiceInterface

from lab11.builder import AssistantDirector, OfflineAssistantBuilder

from lab13.dialog_manager_ext import StatefulDialogManager
from lab13.memento import SettingsCaretaker
from lab13.nlu_ext import ExtendedRuleBasedNLU
from lab13.observer import (
    EventSubject,
    LoggerObserver,
    ScreenObserver,
    StatisticsObserver,
)
from lab13.states import IdleState


class ScriptedVoiceInterface(VoiceInterface):
    """Тестовый интерфейс: отдаёт заранее подготовленные реплики пользователя."""

    def __init__(self, phrases: list[str]) -> None:
        self._phrases = phrases
        self._index = 0

    def listen(self) -> bytes:
        if self._index >= len(self._phrases):
            raise EOFError("Сценарий завершён")
        phrase = self._phrases[self._index]
        self._index += 1
        print(f"Введите текст: [USER]: {phrase}")
        return phrase.encode("utf-8")

    def speak(self, audio: bytes) -> None:
        # Озвучка не нужна: реплики ассистента уже выводятся в say().
        _ = audio


class _Tee:
    """Дублирует поток stdout в файл (для воспроизводимого UTF-8 лога)."""

    def __init__(self, *streams: TextIO) -> None:
        self._streams = streams

    def write(self, data: str) -> int:
        for stream in self._streams:
            try:
                stream.write(data)
            except UnicodeEncodeError:
                # Консоль Windows может не поддерживать символы — пропускаем.
                stream.write(data.encode("ascii", "replace").decode("ascii"))
        return len(data)

    def flush(self) -> None:
        for stream in self._streams:
            stream.flush()


# Один связный сценарий: проходит все три паттерна.
SCRIPT: list[str] = [
    "включи музыку",        # Idle -> Playing, событие track_started
    "включи музыку",        # Idle -> Playing, событие track_started
    "громкость 7",          # volume_changed
    "запомни настройки",    # snapshot_saved
    "громкость 3",          # volume_changed
    "включи музыку",        # Playing: «уже играет»
    "не беспокой",          # Playing -> Muted (трек останавливается)
    "включи музыку",        # Muted: игнор
    "вернись",              # Muted -> Idle
    "восстанови настройки", # vol=7, state=Playing, трек снова запускается
    "выключись",            # exit
]


def build_assistant(
    log_file: TextIO,
) -> tuple[StatefulDialogManager, StatisticsObserver]:
    """Собирает офлайн-конфигурацию через Builder из ЛР11 и подменяет менеджер на расширенный."""
    director = AssistantDirector()
    scripted = ScriptedVoiceInterface(SCRIPT)

    assembly = director.construct(
        builder=OfflineAssistantBuilder(),
        voice_override=scripted,
    )
    # Подменяем NLU на расширенный, чтобы распознавать новые команды.
    assembly.nlu = ExtendedRuleBasedNLU()

    # Подписчики и хранитель снимков.
    subject = EventSubject()
    subject.attach(LoggerObserver(log_file))
    stats = StatisticsObserver()
    subject.attach(stats)
    subject.attach(ScreenObserver())

    manager = StatefulDialogManager(
        music_service=assembly.music_service,
        info_service=assembly.info_service,
        player=assembly.player,
        asr=assembly.asr,
        nlu=assembly.nlu,
        tts=assembly.tts,
        voice_interface=assembly.voice_interface,
        initial_state=IdleState(),
        caretaker=SettingsCaretaker(),
        subject=subject,
        initial_volume=5,
    )
    return manager, stats


def main() -> None:
    log_path = Path(__file__).with_name("run.log")
    log_file = log_path.open("w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = _Tee(original_stdout, log_file)

    try:
        print("Старт ЛР13: State + Memento + Observer\n")
        manager, stats = build_assistant(log_file)
        manager.run()
        print("\n" + stats.report())
    finally:
        sys.stdout = original_stdout
        log_file.close()


if __name__ == "__main__":
    main()
