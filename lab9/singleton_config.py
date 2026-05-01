"""Singleton-конфигурация для ЛР09."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class _ConfigState:
    profile: str = "offline"
    music_source: str = "local"
    pool_max_size: int = 2
    pool_grow: bool = True
    prototype_defaults: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "nlu": {"kind": "rule", "language": "ru"},
            "tts": {"kind": "basic", "voice": "default"},
        }
    )


class AssistantConfig:
    """Единый объект конфигурации приложения.

    Создавать экземпляр напрямую через ``AssistantConfig()`` нельзя —
    только ``AssistantConfig.get_instance()``.
    """

    _instance: Optional["AssistantConfig"] = None
    _constructing: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> "AssistantConfig":
        if not cls._constructing:
            raise RuntimeError(
                "AssistantConfig — singleton: используйте AssistantConfig.get_instance(), "
                "а не AssistantConfig()."
            )
        return super().__new__(cls)

    def __init__(self) -> None:
        self._state = _ConfigState()

    @classmethod
    def get_instance(cls) -> "AssistantConfig":
        if cls._instance is None:
            cls._constructing = True
            try:
                inst = super().__new__(cls)
                cls._instance = inst
                inst.__init__()
            finally:
                cls._constructing = False
        return cls._instance

    def configure(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self._state, key):
                setattr(self._state, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self._state, key, default)
