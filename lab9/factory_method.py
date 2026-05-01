"""Factory Method для создания музыкальных сервисов."""

from __future__ import annotations

from abc import ABC, abstractmethod

from interfaces import MusicService
from music_services import LocalFileMusicService, SpotifyMusicService, VKMusicService


class MusicServiceCreator(ABC):
    """Базовый создатель музыкального сервиса."""

    @abstractmethod
    def create_music_service(self) -> MusicService:
        raise NotImplementedError


class SpotifyCreator(MusicServiceCreator):
    def create_music_service(self) -> MusicService:
        return SpotifyMusicService()


class VKCreator(MusicServiceCreator):
    def create_music_service(self) -> MusicService:
        return VKMusicService()


class LocalFileCreator(MusicServiceCreator):
    def create_music_service(self) -> MusicService:
        service = LocalFileMusicService(is_offline=True)
        return service


def build_music_creator(source: str) -> MusicServiceCreator:
    normalized = source.strip().lower()
    if normalized in {"spotify", "sp"}:
        return SpotifyCreator()
    if normalized in {"vk", "vk_music"}:
        return VKCreator()
    return LocalFileCreator()
