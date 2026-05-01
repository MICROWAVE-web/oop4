"""Object Pool: переиспользование ограниченных объектов."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Generic, List, TypeVar


class PooledResource(ABC):
    @abstractmethod
    def reset_state(self) -> None:
        raise NotImplementedError


@dataclass
class PlayerSession(PooledResource):
    session_id: int
    in_use: bool = False
    last_track: str = ""

    def reset_state(self) -> None:
        self.in_use = False
        self.last_track = ""


T = TypeVar("T", bound=PooledResource)


class ObjectPool(Generic[T]):
    def __init__(self, factory: Callable[[], T], max_size: int = 2, grow: bool = True) -> None:
        self._factory = factory
        self._max_size = max_size
        self._grow = grow
        self._all: List[T] = []
        self._free: List[T] = []

    def acquire(self) -> T:
        if self._free:
            return self._free.pop()
        if self._grow and (self._max_size <= 0 or len(self._all) < self._max_size):
            obj = self._factory()
            self._all.append(obj)
            return obj
        raise RuntimeError("ObjectPool exhausted")

    def release(self, obj: T) -> None:
        obj.reset_state()
        if obj in self._all and obj not in self._free:
            self._free.append(obj)

    @property
    def total_count(self) -> int:
        return len(self._all)

    @property
    def free_count(self) -> int:
        return len(self._free)
