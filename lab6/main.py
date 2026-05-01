"""
Точка входа ЛР06: конфигурирование Dependency Injection + Adapter/Decorator/Composite/Iterator.

Запуск из корня репозитория:
    python3 -m lab6.main
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from asr import SimpleASR
from info_services import YandexInfoService
from music_services import ProxyMusicService, SpotifyMusicService
from nlu import RuleBasedNLU
from player import BasicPlayer
from voice_interfaces import ConsoleInterface

from lab6.adapter import ExternalTTSAdapter, ExternalTTSClient
from lab6.composite import ResponseBuilder
from lab6.decorators import CachingTTSDecorator, LoggingTTSDecorator
from lab6.dialog_manager import Lab6DialogManager
from lab6.iterator import ResponseIteratorFactory


def build_tts_stack() -> LoggingTTSDecorator:
    """
    Декораторы: снаружи логирование, внутри кеш поверх адаптированного внешнего TTS.
    """
    client = ExternalTTSClient()
    adapter = ExternalTTSAdapter(client, lang="ru")
    # cached = CachingTTSDecorator(adapter)
    return LoggingTTSDecorator(adapter)


def make_dialog_dfs() -> Lab6DialogManager:
    """Конфигурация по умолчанию: обход ответа DFS (как pre-order по текстам листьев)."""
    return Lab6DialogManager(
        music_service=ProxyMusicService(SpotifyMusicService(), offline=True),
        info_service=YandexInfoService(),
        player=BasicPlayer(),
        asr=SimpleASR(),
        nlu=RuleBasedNLU(),
        tts=build_tts_stack(),
        voice_interface=ConsoleInterface(),
        response_builder=ResponseBuilder(),
        iterator_factory=ResponseIteratorFactory(),
        iterator_strategy=ResponseIteratorFactory.STRATEGY_DFS,
    )


def make_dialog_bfs() -> Lab6DialogManager:
    """Альтернатива: тот же граф сервисов, но стратегия итератора BFS."""
    return Lab6DialogManager(
        music_service=ProxyMusicService(SpotifyMusicService(), offline=True),
        info_service=YandexInfoService(),
        player=BasicPlayer(),
        asr=SimpleASR(),
        nlu=RuleBasedNLU(),
        tts=build_tts_stack(),
        voice_interface=ConsoleInterface(),
        response_builder=ResponseBuilder(),
        iterator_factory=ResponseIteratorFactory(),
        iterator_strategy=ResponseIteratorFactory.STRATEGY_BFS,
    )

def make_dialog2_bfs() -> Lab6DialogManager:
    """Альтернатива: тот же граф сервисов, но стратегия итератора BFS."""
    return Lab6DialogManager(
        music_service=ProxyMusicService(SpotifyMusicService()),
        info_service=YandexInfoService(),
        player=BasicPlayer(),
        asr=SimpleASR(),
        nlu=RuleBasedNLU(),
        tts=build_tts_stack(),
        voice_interface=ConsoleInterface(),
        response_builder=ResponseBuilder(),
        iterator_factory=ResponseIteratorFactory(),
        iterator_strategy=ResponseIteratorFactory.STRATEGY_BFS,
    )


if __name__ == "__main__":
    # DFS — корректный порядок озвучки для вложенных ResponseGroup.
    make_dialog_dfs().run()
    # make_dialog_bfs().run()
    # make_dialog2_bfs().run()
