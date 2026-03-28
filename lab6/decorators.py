"""Decorator: расширение TTS без изменения исходных классов BasicTTS / адаптера."""

from __future__ import annotations

from abc import ABC
from typing import Dict

from interfaces import TTSModule


class TTSDecorator(TTSModule, ABC):
    """Базовый декоратор: хранит компонент TTSModule и делегирует вызовы по умолчанию."""

    def __init__(self, component: TTSModule) -> None:
        self._component = component

    def synthesize(self, text: str) -> bytes:
        return self._component.synthesize(text)

    def set_voice(self, voice_name: str) -> None:
        self._component.set_voice(voice_name)


class CachingTTSDecorator(TTSDecorator):
    """Кеширует результат synthesize по ключу (текст)."""

    def __init__(self, component: TTSModule) -> None:
        super().__init__(component)
        self._cache: Dict[str, bytes] = {}

    def synthesize(self, text: str) -> bytes:
        if text not in self._cache:
            self._cache[text] = self._component.synthesize(text)
        else:
            print("Возвращаю кешированный текст")
        return self._cache[text]


class LoggingTTSDecorator(TTSDecorator):
    """Перед синтезом выводит диагностическое сообщение (логирование вызовов TTS)."""

    def synthesize(self, text: str) -> bytes:
        preview = (text[:60] + "…") if len(text) > 60 else text
        # print(f"[TTS:log] synthesize: {preview!r}")
        return self._component.synthesize(text)
