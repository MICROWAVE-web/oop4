"""DialogManager для ЛР06: ответы через Composite и обход Iterator; TTS может быть декорирован/адаптирован."""

from __future__ import annotations

import traceback
from typing import Any

from interfaces import (
    MusicService,
    InfoService,
    Player,
    ASRModule,
    NLUModule,
    TTSModule,
    VoiceInterface,
)

from .composite import ResponseBuilder, ResponseComponent
from .iterator import ResponseIteratorFactory


class Lab6DialogManager:
    def __init__(
        self,
        music_service: MusicService,
        info_service: InfoService,
        player: Player,
        asr: ASRModule,
        nlu: NLUModule,
        tts: TTSModule,
        voice_interface: VoiceInterface,
        response_builder: ResponseBuilder,
        iterator_factory: ResponseIteratorFactory,
        iterator_strategy: str = ResponseIteratorFactory.STRATEGY_DFS,
    ) -> None:
        self.music_service = music_service
        self.info_service = info_service
        self.player = player
        self.asr = asr
        self.nlu = nlu
        self.tts = tts
        self.voice = voice_interface
        self._builder = response_builder
        self._iterator_factory = iterator_factory
        self._iterator_strategy = iterator_strategy
        self.context: dict[str, Any] = {}
        self.is_running = False

    def run(self) -> None:
        self.is_running = True
        self.say(self._builder.build_startup())
        while self.is_running:
            try:
                audio = self.voice.listen()
                text = self.asr.recognize(audio)
                if not text:
                    continue
                print(f"[USER]: {text}")
                intent, data = self.nlu.parse(text)
                self.handle_intent(intent, data)
            except EOFError:
                break
            except Exception as e:
                traceback.print_exc()
                self.say(self._builder.build_error())
                print(f"[ERROR]: {e}")

    def stop(self) -> None:
        self.is_running = False
        self.say(self._builder.build_goodbye())

    def handle_intent(self, intent: str, data: Any) -> None:
        handlers = {
            "music": self.handle_music,
            "info": self.handle_info,
            "news": self.handle_news,
            "system": self.handle_system,
            "volume": self.handle_volume,
            "intent_ml": self.handle_ml,
            "exit": lambda _: self.stop(),
        }
        handlers.get(intent, self.handle_unknown)(data)

    def handle_music(self, data: Any) -> None:
        tracks = self.music_service.search(str(data))
        if not tracks:
            self.say(self._builder.build_music_empty())
            return
        self.music_service.play(tracks[0])
        self.say(self._builder.build_music_ok())

    def handle_info(self, data: Any) -> None:
        result = self.info_service.get_info(str(data))
        self.say(self._builder.build_info(result))

    def handle_news(self, data: Any) -> None:
        topic = str(data).strip() or "общее"
        news = self.info_service.get_news(topic, count=3)


        if not news:
            self.say(self._builder.build_news_empty())
            return

        self.say(self._builder.build_news(topic, news))

    def handle_system(self, data: Any) -> None:
        if data == "stop":
            self.stop()

    def handle_volume(self, data: Any) -> None:
        try:
            level = int(data)
            self.player.set_volume(level)
            self.say(self._builder.build_volume_ok(level))
        except (TypeError, ValueError):
            self.say(self._builder.build_volume_error())

    def handle_ml(self, data: Any) -> None:
        self.say(self._builder.build_ml_stub(data))

    def handle_unknown(self, data: Any) -> None:
        _ = data
        self.say(self._builder.build_unknown())

    def say(self, component: ResponseComponent) -> None:
        """Озвучивание составного ответа: Iterator выдаёт фрагменты, TTS+Voice — по одному."""
        iterator = self._iterator_factory.create(self._iterator_strategy, component)
        while iterator.has_next():
            fragment = iterator.next_fragment()
            print(f"[ASSISTANT]: {fragment}")
            audio = self.tts.synthesize(fragment)
            self.voice.speak(audio)
