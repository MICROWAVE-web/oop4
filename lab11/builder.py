"""Реализация паттерна Builder для сборки конфигураций ассистента."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from asr import SimpleASR
from dialog_manager import DialogManager
from info_services import GoogleInfoService, WikipediaInfoService, YandexInfoService
from interfaces import ASRModule, InfoService, MusicService, NLUModule, Player, TTSModule, VoiceInterface
from music_services import ProxyMusicService, SpotifyMusicService, VKMusicService
from nlu import RuleBasedNLU
from player import BasicPlayer
from tts import BasicTTS, NeuralTTS
from voice_interfaces import ConsoleInterface, MicrophoneInterface


@dataclass
class AssistantAssembly:
    """Промежуточный продукт сборки: готовый набор зависимостей."""

    music_service: MusicService | None = None
    info_service: InfoService | None = None
    player: Player | None = None
    asr: ASRModule | None = None
    nlu: NLUModule | None = None
    tts: TTSModule | None = None
    voice_interface: VoiceInterface | None = None

    def to_dialog_manager(self) -> DialogManager:
        """Создаёт DialogManager из собранных частей."""
        missing = [
            name
            for name, value in (
                ("music_service", self.music_service),
                ("info_service", self.info_service),
                ("player", self.player),
                ("asr", self.asr),
                ("nlu", self.nlu),
                ("tts", self.tts),
                ("voice_interface", self.voice_interface),
            )
            if value is None
        ]
        if missing:
            raise RuntimeError(f"Сборка не завершена, отсутствуют поля: {', '.join(missing)}")
        return DialogManager(
            music_service=self.music_service,
            info_service=self.info_service,
            player=self.player,
            asr=self.asr,
            nlu=self.nlu,
            tts=self.tts,
            voice_interface=self.voice_interface,
        )


class AssistantBuilder(ABC):
    """Абстрактный строитель ассистента."""

    def __init__(self) -> None:
        self._assembly = AssistantAssembly()

    def reset(self) -> None:
        """Начинает новую сборку продукта."""
        self._assembly = AssistantAssembly()

    @abstractmethod
    def build_music(self) -> None:
        pass

    @abstractmethod
    def build_info(self) -> None:
        pass

    @abstractmethod
    def build_player(self) -> None:
        pass

    @abstractmethod
    def build_asr(self) -> None:
        pass

    @abstractmethod
    def build_nlu(self) -> None:
        pass

    @abstractmethod
    def build_tts(self) -> None:
        pass

    @abstractmethod
    def build_voice(self) -> None:
        pass

    def set_voice_interface(self, voice_interface: VoiceInterface) -> None:
        """Позволяет подменить интерфейс ввода/вывода для тестового сценария."""
        self._assembly.voice_interface = voice_interface

    def get_result(self) -> AssistantAssembly:
        """Возвращает собранный продукт."""
        return self._assembly


class OfflineAssistantBuilder(AssistantBuilder):
    """Сборка офлайн-конфигурации ассистента."""

    def build_music(self) -> None:
        self._assembly.music_service = ProxyMusicService(SpotifyMusicService(), offline=True)

    def build_info(self) -> None:
        self._assembly.info_service = WikipediaInfoService()

    def build_player(self) -> None:
        self._assembly.player = BasicPlayer()

    def build_asr(self) -> None:
        self._assembly.asr = SimpleASR()

    def build_nlu(self) -> None:
        self._assembly.nlu = RuleBasedNLU()

    def build_tts(self) -> None:
        self._assembly.tts = BasicTTS()

    def build_voice(self) -> None:
        self._assembly.voice_interface = ConsoleInterface()


class SmartAssistantBuilder(AssistantBuilder):
    """Сборка «умной» онлайн-конфигурации ассистента."""

    def build_music(self) -> None:
        self._assembly.music_service = ProxyMusicService(SpotifyMusicService(), offline=False)

    def build_info(self) -> None:
        self._assembly.info_service = GoogleInfoService()

    def build_player(self) -> None:
        self._assembly.player = BasicPlayer()
        self._assembly.player.connect_output("bluetooth")

    def build_asr(self) -> None:
        self._assembly.asr = SimpleASR()

    def build_nlu(self) -> None:
        self._assembly.nlu = RuleBasedNLU()

    def build_tts(self) -> None:
        self._assembly.tts = NeuralTTS()

    def build_voice(self) -> None:
        self._assembly.voice_interface = MicrophoneInterface()


class CarAssistantBuilder(AssistantBuilder):
    """Сборка автомобильной конфигурации ассистента."""

    def build_music(self) -> None:
        self._assembly.music_service = VKMusicService()

    def build_info(self) -> None:
        self._assembly.info_service = YandexInfoService()

    def build_player(self) -> None:
        self._assembly.player = BasicPlayer()

    def build_asr(self) -> None:
        self._assembly.asr = SimpleASR()

    def build_nlu(self) -> None:
        self._assembly.nlu = RuleBasedNLU()

    def build_tts(self) -> None:
        self._assembly.tts = NeuralTTS()

    def build_voice(self) -> None:
        self._assembly.voice_interface = MicrophoneInterface()


class AssistantDirector:
    """Директор задаёт порядок шагов сборки."""

    def construct(
        self,
        builder: AssistantBuilder,
        voice_override: VoiceInterface | None = None,
    ) -> AssistantAssembly:
        builder.reset()
        builder.build_music()
        builder.build_info()
        builder.build_player()
        builder.build_asr()
        builder.build_nlu()
        builder.build_tts()
        builder.build_voice()
        if voice_override is not None:
            builder.set_voice_interface(voice_override)
        return builder.get_result()
