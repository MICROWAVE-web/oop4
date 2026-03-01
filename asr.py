"""Модули распознавания речи: локальный (simple) и облачный."""

from interfaces import ASRModule


class SimpleASR(ASRModule):
    """Локальное распознавание; при текстовом вводе (ConsoleInterface) возвращает его как распознанный текст."""

    def recognize(self, audio_data: bytes) -> str:
        """Если audio_data — UTF-8 текст (консоль), возвращает его; иначе — фиксированную заглушку."""
        try:
            text = audio_data.decode("utf-8").strip()
            if text:
                return text
        except (UnicodeDecodeError, AttributeError):
            pass
        return "распознанный текст (simple)"

    def set_language(self, lang: str) -> None:
        """Установка языка (заглушка)."""
        pass


class CloudASR(ASRModule):
    """Имитация облачного ASR (внешний API)."""

    def recognize(self, audio_data: bytes) -> str:
        """Возвращает результат распознавания (заглушка)."""
        return "распознанный текст (cloud)"

    def set_language(self, lang: str) -> None:
        """Установка языка (заглушка)."""
        pass
