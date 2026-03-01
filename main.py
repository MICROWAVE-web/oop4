"""Точка входа: сборка конфигураций и запуск диалогового менеджера."""

from interfaces import *
from music_services import *
from info_services import *
from player import *
from asr import *
from nlu import *
from tts import *
from voice_interfaces import *
from dialog_manager import DialogManager

# Локальная офлайн-конфигурация (Standalone)
dialog_offline = DialogManager(
    music_service=ProxyMusicService(SpotifyMusicService(), offline=True),
    info_service=WikipediaInfoService(),
    player=BasicPlayer(),
    asr=SimpleASR(),
    nlu=RuleBasedNLU(),
    tts=BasicTTS(),
    voice_interface=ConsoleInterface(),
)

# Облачная мультимедийная конфигурация (Smart Home)
dialog_smart = DialogManager(
    music_service=ProxyMusicService(SpotifyMusicService()),
    info_service=GoogleInfoService(),
    player=BluetoothPlayer(),
    asr=CloudASR(),
    nlu=MLNLUModule(),
    tts=NeuralTTS(),
    voice_interface=MicrophoneInterface(),
)

# Гибридная конфигурация (Автомобильный ассистент)
dialog_car = DialogManager(
    music_service=VKMusicService(),
    info_service=YandexInfoService(),
    player=StreamingPlayer(),
    asr=SimpleASR(),
    nlu=RuleBasedNLU(),
    tts=NeuralTTS(),
    voice_interface=MicrophoneInterface(),
)

if __name__ == "__main__":
    dialog_offline.run()
    # dialog_smart.run()
    # dialog_car.run()
