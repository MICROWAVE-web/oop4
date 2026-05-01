"""Демонстрация ЛР11: Builder + Object Pool на базе ЛР4."""

from __future__ import annotations

import sys
from pathlib import Path

# Добавляем корень проекта в путь, чтобы использовать модули ЛР4 через импорт.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from interfaces import VoiceInterface

from lab11.builder import (
    AssistantBuilder,
    AssistantDirector,
    CarAssistantBuilder,
    OfflineAssistantBuilder,
    SmartAssistantBuilder,
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
        print(f"Введите текст: [USER]: {phrase}")
        return phrase.encode("utf-8")

    def speak(self, audio: bytes) -> None:
        # В сценарии логируем только текстовые ответы ассистента.
        _ = audio


def run_scenario(
    title: str,
    builder: AssistantBuilder,
    director: AssistantDirector,
    phrases: list[str],
) -> None:
    print(f"\n=== {title} ===")
    scripted_voice = ScriptedVoiceInterface(phrases)
    assembly = director.construct(builder=builder, voice_override=scripted_voice)
    dialog_manager = assembly.to_dialog_manager()
    dialog_manager.run()


def main() -> None:
    director = AssistantDirector()

    offline_builder = OfflineAssistantBuilder()
    smart_builder = SmartAssistantBuilder()
    car_builder = CarAssistantBuilder()

    print("Старт ЛР11: Builder")

    run_scenario(
        title="Сценарий 1: Offline",
        builder=offline_builder,
        director=director,
        phrases=["включи музыку", "громкость 7", "выключись"],
    )

    run_scenario(
        title="Сценарий 2: Smart",
        builder=smart_builder,
        director=director,
        phrases=["включи музыку", "новости технологии", "выключись"],
    )

    run_scenario(
        title="Сценарий 3: Car",
        builder=car_builder,
        director=director,
        phrases=["включи музыку", "выключись"],
    )


if __name__ == "__main__":
    main()
