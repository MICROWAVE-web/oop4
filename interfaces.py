"""Абстрактные интерфейсы всех сервисов умной колонки."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple


class MusicService(ABC):
    """Интерфейс музыкального сервиса: поиск, воспроизведение и метаданные треков."""

    def __init__(self, is_offline: bool=False) -> None:
        self.is_offline = is_offline


    @abstractmethod
    def search(self, query: str) -> List[str]:
        """Ищет треки по запросу. Возвращает список идентификаторов."""
        pass

    @abstractmethod
    def play(self, track_id: str) -> None:
        """Запускает воспроизведение трека по идентификатору."""
        pass

    @abstractmethod
    def pause(self) -> None:
        """Ставит воспроизведение на паузу."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Останавливает воспроизведение."""
        pass

    @abstractmethod
    def get_metadata(self, track_id: str) -> Dict[str, Any]:
        """Возвращает метаданные трека (название, исполнитель и т.д.)."""
        pass


class InfoService(ABC):
    """Интерфейс справочного сервиса: информация по запросу и новости."""

    @abstractmethod
    def get_info(self, query: str) -> str:
        """Возвращает текстовый ответ на произвольный запрос."""
        pass

    @abstractmethod
    def get_news(self, topic: str, count: int = 5) -> List[str]:
        """Возвращает список новостей по теме (до count штук)."""
        pass


class Player(ABC):
    """Интерфейс аудиоплеера: воспроизведение потока, громкость, вывод."""

    @abstractmethod
    def play_audio(self, audio_stream: bytes) -> None:
        """Воспроизводит переданный аудиопоток."""
        pass

    @abstractmethod
    def set_volume(self, level: int) -> None:
        """Устанавливает уровень громкости (обычно 0–10)."""
        pass

    @abstractmethod
    def connect_output(self, output_type: str) -> None:
        """Подключает вывод к указанному устройству (динамик, Bluetooth и т.д.)."""
        pass


class ASRModule(ABC):
    """Интерфейс модуля распознавания речи (Automatic Speech Recognition)."""

    @abstractmethod
    def recognize(self, audio_data: bytes) -> str:
        """Преобразует аудиоданные в текст."""
        pass

    @abstractmethod
    def set_language(self, lang: str) -> None:
        """Задаёт язык распознавания."""
        pass


class NLUModule(ABC):
    """Интерфейс модуля понимания естественного языка (Intent + сущности)."""

    @abstractmethod
    def parse(self, text: str) -> Tuple[str, Any]:
        """Определяет намерение и связанные данные. Возвращает (intent, data)."""
        pass

    @abstractmethod
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Извлекает именованные сущности из текста."""
        pass


class TTSModule(ABC):
    """Интерфейс модуля синтеза речи (Text-to-Speech)."""

    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Преобразует текст в аудиобайты."""
        pass

    @abstractmethod
    def set_voice(self, voice_name: str) -> None:
        """Выбирает голос для синтеза."""
        pass


class VoiceInterface(ABC):
    """Интерфейс голосового ввода/вывода: захват аудио и воспроизведение."""

    @abstractmethod
    def listen(self) -> bytes:
        """Захватывает аудио с микрофона (или имитация ввода). Возвращает байты."""
        pass

    @abstractmethod
    def speak(self, audio: bytes) -> None:
        """Воспроизводит переданное аудио (динамик, консоль и т.д.)."""
        pass
