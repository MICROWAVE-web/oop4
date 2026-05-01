"""Реализации музыкальных сервисов и Proxy для контроля доступа."""

from interfaces import MusicService
from typing import List, Dict, Any


class YandexMusicService(MusicService):
    """Имитация работы с API Яндекс.Музыки."""

    def search(self, query: str) -> List[str]:
        """Поиск в каталоге Яндекс.Музыки (заглушка)."""
        return ["yandex_track_1"]

    def play(self, track_id: str) -> None:
        """Запуск воспроизведения трека."""
        print(f"Yandex: play {track_id}")

    def pause(self) -> None:
        """Пауза."""
        print("Yandex: pause")

    def stop(self) -> None:
        """Остановка."""
        print("Yandex: stop")

    def get_metadata(self, track_id: str) -> Dict[str, Any]:
        """Метаданные трека (заглушка)."""
        return {"title": "...", "artist": "..."}


class VKMusicService(MusicService):
    """Имитация работы с VK Music."""

    def search(self, query: str) -> List[str]:
        """Поиск в каталоге VK (заглушка)."""
        return ["vk_track_1"]

    def play(self, track_id: str) -> None:
        """Запуск воспроизведения."""
        print(f"VK: play {track_id}")

    def pause(self) -> None:
        """Пауза."""
        print("VK: pause")

    def stop(self) -> None:
        """Остановка."""
        print("VK: stop")

    def get_metadata(self, track_id: str) -> Dict[str, Any]:
        """Метаданные трека (заглушка)."""
        return {"title": "...", "artist": "..."}


class SpotifyMusicService(MusicService):
    """Имитация работы со Spotify."""

    def search(self, query: str) -> List[str]:
        """Поиск в каталоге Spotify (заглушка)."""
        return ["spotify_track_1"]

    def play(self, track_id: str) -> None:
        """Запуск воспроизведения."""
        print(f"Spotify: play {track_id}")

    def pause(self) -> None:
        """Пауза."""
        print("Spotify: pause")

    def stop(self) -> None:
        """Остановка."""
        print("Spotify: stop")

    def get_metadata(self, track_id: str) -> Dict[str, Any]:
        """Метаданные трека (заглушка)."""
        return {"title": "...", "artist": "..."}


class LocalFileMusicService(MusicService):
    """Воспроизведение музыки с локального диска (офлайн)."""

    def search(self, query: str) -> List[str]:
        """Возвращает путь к локальному файлу (заглушка)."""
        return ["file:///music/song.mp3"]

    def play(self, track_id: str) -> None:
        """Воспроизведение локального файла по пути."""
        print(f"Local: playing {track_id}")

    def pause(self) -> None:
        """Пауза (заглушка)."""
        pass

    def stop(self) -> None:
        """Остановка (заглушка)."""
        pass

    def get_metadata(self, track_id: str) -> Dict[str, Any]:
        """Минимальные метаданные локального трека."""
        return {"title": "Local track"}


class ProxyMusicService(MusicService):
    """Прокси для MusicService: проверка прав перед воспроизведением, остальное делегирует реальному сервису."""

    def __init__(self, real: MusicService, offline: bool = False) -> None:
        """real — реальный музыкальный сервис, к которому проксируется доступ."""
        super().__init__()
        self.offline = offline
        self._real = real

    def search(self, query: str) -> List[str]:
        """Поиск без проверки прав — делегируется реальному сервису."""
        return self._real.search(query)

    def play(self, track_id: str) -> None:
        """Проверка прав, затем вызов play у реального сервиса."""
        print("Proxy: проверка прав...")
        if self.offline is True and self._real.is_offline is False:
            print("Некоторые функции этого сервиса в режиме оффлайн могут быть недоступны.")
        else:
            print("Все функции этого сервиса доступны.")
        self._real.play(track_id)


    def pause(self) -> None:
        """Делегирует pause реальному сервису."""
        self._real.pause()

    def stop(self) -> None:
        """Делегирует stop реальному сервису."""
        self._real.stop()

    def get_metadata(self, track_id: str) -> Dict[str, Any]:
        """Делегирует get_metadata реальному сервису."""
        return self._real.get_metadata(track_id)
