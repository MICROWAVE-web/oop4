"""Abstract Factory профилей ассистента."""

from __future__ import annotations

from abc import ABC, abstractmethod

from asr import CloudASR, SimpleASR
from info_services import GoogleInfoService, WikipediaInfoService, YandexInfoService
from interfaces import ASRModule, InfoService, MusicService, NLUModule, Player, TTSModule, VoiceInterface
from nlu import MLNLUModule, RuleBasedNLU
from player import BasicPlayer, BluetoothPlayer, StreamingPlayer
from tts import BasicTTS, NeuralTTS
from voice_interfaces import ConsoleInterface, MicrophoneInterface

from lab9.factory_method import MusicServiceCreator, build_music_creator
from lab9.singleton_config import AssistantConfig


class AssistantComponentFactory(ABC):
    """Создает согласованное семейство компонентов."""

    def __init__(self, config: AssistantConfig) -> None:
        self.config = config
        self.music_creator: MusicServiceCreator = build_music_creator(config.get("music_source", "local"))

    @abstractmethod
    def get_info(self) -> str:
        """Краткое текстовое описание набора компонентов этого профиля фабрики."""

    @abstractmethod
    def create_music_service(self) -> MusicService:
        raise NotImplementedError

    @abstractmethod
    def create_info_service(self) -> InfoService:
        raise NotImplementedError

    @abstractmethod
    def create_player(self) -> Player:
        raise NotImplementedError

    @abstractmethod
    def create_asr(self) -> ASRModule:
        raise NotImplementedError

    @abstractmethod
    def create_nlu(self) -> NLUModule:
        raise NotImplementedError

    @abstractmethod
    def create_tts(self) -> TTSModule:
        raise NotImplementedError

    @abstractmethod
    def create_voice_interface(self) -> VoiceInterface:
        raise NotImplementedError


class OfflineFactory(AssistantComponentFactory):

    def get_info(self) -> str:
        return (
            "Профиль offline:\n"
            "  Сервис информации: WikipediaInfoService\n"
            "  Плеер: BasicPlayer\n"
            "  ASR: SimpleASR\n"
            "  NLU: RuleBasedNLU\n"
            "  TTS: BasicTTS\n"
            "  Голосовой интерфейс: ConsoleInterface\n"
            "  Музыка: через MusicServiceCreator (источник из конфига)"
        )

    def create_music_service(self) -> MusicService:
        return self.music_creator.create_music_service()

    def create_info_service(self) -> InfoService:
        return WikipediaInfoService()

    def create_player(self) -> Player:
        return BasicPlayer()

    def create_asr(self) -> ASRModule:
        return SimpleASR()

    def create_nlu(self) -> NLUModule:
        return RuleBasedNLU()

    def create_tts(self) -> TTSModule:
        return BasicTTS()

    def create_voice_interface(self) -> VoiceInterface:
        return ConsoleInterface()


class SmartFactory(AssistantComponentFactory):

    def get_info(self) -> str:
        return (
            "Профиль smart:\n"
            "  Сервис информации: GoogleInfoService\n"
            "  Плеер: BluetoothPlayer\n"
            "  ASR: CloudASR\n"
            "  NLU: MLNLUModule\n"
            "  TTS: NeuralTTS\n"
            "  Голосовой интерфейс: MicrophoneInterface\n"
            "  Музыка: через MusicServiceCreator (источник из конфига)"
        )

    def create_music_service(self) -> MusicService:
        return self.music_creator.create_music_service()

    def create_info_service(self) -> InfoService:
        return GoogleInfoService()

    def create_player(self) -> Player:
        return BluetoothPlayer()

    def create_asr(self) -> ASRModule:
        return CloudASR()

    def create_nlu(self) -> NLUModule:
        return MLNLUModule()

    def create_tts(self) -> TTSModule:
        return NeuralTTS()

    def create_voice_interface(self) -> VoiceInterface:
        return MicrophoneInterface()


class CarFactory(AssistantComponentFactory):

    def get_info(self) -> str:
        return (
            "Профиль car:\n"
            "  Сервис информации: YandexInfoService\n"
            "  Плеер: StreamingPlayer\n"
            "  ASR: SimpleASR\n"
            "  NLU: RuleBasedNLU\n"
            "  TTS: NeuralTTS\n"
            "  Голосовой интерфейс: MicrophoneInterface\n"
            "  Музыка: через MusicServiceCreator (источник из конфига)"
        )

    def create_music_service(self) -> MusicService:
        return self.music_creator.create_music_service()

    def create_info_service(self) -> InfoService:
        return YandexInfoService()

    def create_player(self) -> Player:
        return StreamingPlayer()

    def create_asr(self) -> ASRModule:
        return SimpleASR()

    def create_nlu(self) -> NLUModule:
        return RuleBasedNLU()

    def create_tts(self) -> TTSModule:
        return NeuralTTS()

    def create_voice_interface(self) -> VoiceInterface:
        return MicrophoneInterface()


def build_component_factory(config: AssistantConfig) -> AssistantComponentFactory:
    profile = str(config.get("profile", "offline")).lower()
    if profile == "smart":
        return SmartFactory(config)
    if profile == "car":
        return CarFactory(config)
    return OfflineFactory(config)
