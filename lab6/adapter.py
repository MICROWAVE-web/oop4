"""Adapter: внешний TTS-клиент с чужим API приводится к интерфейсу TTSModule."""

from __future__ import annotations

from typing import Optional

from interfaces import TTSModule


class ExternalTTSClient:
    """
    Адаптируемый сервис (adaptee): имитация облачного TTS с методами, отличными от TTSModule.
    """

    def __init__(self) -> None:
        self._timbre = "default"

    def request_speech(self, text: str, lang: Optional[str] = None) -> bytes:
        """Генерирует «аудио» по тексту (заглушка; в имени метода отражён внешний API)."""
        tag = lang or "ru"
        return f"external_tts[{self._timbre}]({tag}):{text}".encode("utf-8")

    def choose_timbre(self, timbre: str) -> None:
        """Выбор тембра во внешнем API (аналог set_voice с другим именем)."""
        self._timbre = timbre


class ExternalTTSAdapter(TTSModule):
    """
    Адаптер: реализует TTSModule, внутри вызывает ExternalTTSClient.request_speech / choose_timbre.
    """

    def __init__(self, client: ExternalTTSClient, lang: str = "ru") -> None:
        self._client = client
        self._lang = lang

    def synthesize(self, text: str) -> bytes:
        return self._client.request_speech(text, self._lang)

    def set_voice(self, voice_name: str) -> None:
        self._client.choose_timbre(voice_name)
