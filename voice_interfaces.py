"""Реализации голосового ввода/вывода: микрофон и консоль (для тестов)."""

from interfaces import VoiceInterface


class MicrophoneInterface(VoiceInterface):
    """Захват с микрофона и вывод в динамик (имитация)."""

    def listen(self) -> bytes:
        """Возвращает захваченное с микрофона аудио (заглушка)."""
        return b"audio_from_mic"

    def speak(self, audio: bytes) -> None:
        """Воспроизводит аудио через динамик (имитация)."""
        print("Output to speaker")


class ConsoleInterface(VoiceInterface):
    """Имитация голоса через консоль: ввод текста и тихий вывод (для тестирования)."""

    def listen(self) -> bytes:
        """Читает строку из консоли и возвращает её в виде байтов UTF-8."""
        text = input("Введите текст: ")
        return text.encode("utf-8")

    def speak(self, audio: bytes) -> None:
        """Вывод не показывается (TTS уже выводится через DialogManager.say)."""
        pass
