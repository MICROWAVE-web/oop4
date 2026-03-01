"""Модули синтеза речи: базовый и нейросетевой (имитация)."""

from interfaces import TTSModule


class BasicTTS(TTSModule):
    """Простой синтез речи (имитация)."""

    def synthesize(self, text: str) -> bytes:
        """Преобразует текст в аудиобайты (заглушка)."""
        return b"audio_bytes_basic"

    def set_voice(self, voice_name: str) -> None:
        """Выбор голоса (заглушка)."""
        pass


class NeuralTTS(TTSModule):
    """Имитация нейросетевого TTS (более естественное звучание)."""

    def synthesize(self, text: str) -> bytes:
        """Возвращает аудио, сгенерированное нейросетью (заглушка)."""
        return b"audio_bytes_neural"

    def set_voice(self, voice_name: str) -> None:
        """Выбор голоса (заглушка)."""
        pass
