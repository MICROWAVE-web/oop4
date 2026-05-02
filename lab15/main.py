"""Демонстрация ЛР15: Command + Chain of Responsibility + Visitor на базе ЛР4.

Конфигурация собирается вручную в этом же файле — без Builder из ЛР11
и без State/Memento/Observer из ЛР13. Только корневые модули проекта
(ЛР4) + три новых пакета: commands, preprocessing, visitors.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

# Добавляем корень проекта в sys.path, чтобы импортировать модули ЛР4.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from interfaces import ASRModule, VoiceInterface

from info_services import WikipediaInfoService
from music_services import ProxyMusicService, SpotifyMusicService
from nlu import RuleBasedNLU
from player import BasicPlayer
from tts import BasicTTS

from lab15.commands import CommandFactory, CommandInvoker
from lab15.dialog_manager_ext import CommandDialogManager
from lab15.preprocessing import build_default_chain
from lab15.visitors import (
    CommandLogVisitor,
    CommandStatisticsVisitor,
    UnknownCommandsVisitor,
    visit_all,
)


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
        # Печатаем сырую (как ввёл пользователь) реплику — до предобработки.
        print(f"Введите текст: '{phrase}'")
        return phrase.encode("utf-8")

    def speak(self, audio: bytes) -> None:
        # Озвучка не нужна: реплики ассистента уже выводятся в say().
        _ = audio


class PassThroughASR(ASRModule):
    """ASR без потерь: возвращает текст ровно так, как пришёл от ScriptedVoiceInterface.

    SimpleASR из ЛР4 делает strip и подменяет пустую строку на заглушку — это
    мешает продемонстрировать срабатывание EmptyTextHandler в цепочке.
    """

    def recognize(self, audio_data: bytes) -> str:
        try:
            return audio_data.decode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            return ""

    def set_language(self, lang: str) -> None:
        pass


class _Tee:
    """Дублирует поток stdout в файл (для воспроизводимого UTF-8 лога)."""

    def __init__(self, *streams: TextIO) -> None:
        self._streams = streams

    def write(self, data: str) -> int:
        for stream in self._streams:
            try:
                stream.write(data)
            except UnicodeEncodeError:
                # Консоль Windows может не поддерживать символы — заменяем.
                stream.write(data.encode("ascii", "replace").decode("ascii"))
        return len(data)

    def flush(self) -> None:
        for stream in self._streams:
            stream.flush()


# Сценарий, демонстрирующий все три паттерна за один прогон.
SCRIPT: list[str] = [
    "",                     # CoR: EmptyTextHandler отбрасывает запрос
    "ПРИВЕТ   ",            # CoR: Strip + Lowercase нормализуют, далее info
    "включи музыку",        # Command: PlayMusicCommand
    "громкость 7",          # Command: SetVolumeCommand
    "новости IT",           # Command: GetNewsCommand
    "расскажи про OOP",     # Command: GetInfoCommand (fallback intent в NLU)
    "выключись",            # Command: ExitCommand
]


def build_assistant() -> CommandDialogManager:
    """Собирает офлайн-конфигурацию ЛР4 + три новых паттерна."""
    music_service = ProxyMusicService(SpotifyMusicService(), offline=True)
    info_service = WikipediaInfoService()
    player = BasicPlayer()
    asr = PassThroughASR()
    nlu = RuleBasedNLU()
    tts = BasicTTS()
    voice = ScriptedVoiceInterface(SCRIPT)

    chain = build_default_chain()
    invoker = CommandInvoker()
    # Фабрика создаётся со ссылкой на сервисы; manager присваивается ниже,
    # потому что ExitCommand'у нужна ссылка на собственный DialogManager.
    factory = CommandFactory(
        music_service=music_service,
        info_service=info_service,
        player=player,
        manager=None,  # type: ignore[arg-type]
    )
    manager = CommandDialogManager(
        music_service=music_service,
        info_service=info_service,
        player=player,
        asr=asr,
        nlu=nlu,
        tts=tts,
        voice_interface=voice,
        chain=chain,
        factory=factory,
        invoker=invoker,
    )
    factory.manager = manager
    return manager


def main() -> None:
    log_path = Path(__file__).with_name("run.log")
    log_file = log_path.open("w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = _Tee(original_stdout, log_file)

    try:
        print("Старт ЛР15: Command + Chain of Responsibility + Visitor\n")
        manager = build_assistant()
        manager.run()

        # После завершения сеанса история готова — натравливаем визиторов.
        print("\n=== Обход истории команд визиторами (Visitor) ===")
        stats = CommandStatisticsVisitor()
        log_v = CommandLogVisitor()
        unknown_v = UnknownCommandsVisitor()
        for visitor in (stats, log_v, unknown_v):
            visit_all(visitor, manager.invoker.history)

        print(stats.report())
        print(log_v.report())
        print(unknown_v.report())
    finally:
        sys.stdout = original_stdout
        log_file.close()


if __name__ == "__main__":
    main()
