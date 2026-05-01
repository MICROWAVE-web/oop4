"""Prototype: клоны преднастроенных профилей модулей."""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict


class ModulePrototype(ABC):
    @abstractmethod
    def clone(self) -> "ModulePrototype":
        raise NotImplementedError


@dataclass
class NLUPrototype(ModulePrototype):
    kind: str
    language: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> "NLUPrototype":
        return deepcopy(self)


@dataclass
class TTSPrototype(ModulePrototype):
    kind: str
    voice: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self) -> "TTSPrototype":
        return deepcopy(self)


class CloneRegistry:
    """Реестр прототипов: хранит шаблоны и выдает их копии."""

    def __init__(self) -> None:
        self._prototypes: Dict[str, ModulePrototype] = {}

    def register(self, key: str, prototype: ModulePrototype) -> None:
        self._prototypes[key] = prototype

    def clone_by_key(self, key: str) -> ModulePrototype:
        if key not in self._prototypes:
            raise KeyError(f"Prototype '{key}' is not registered")
        return self._prototypes[key].clone()
