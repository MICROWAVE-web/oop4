"""Расширение DialogManager из ЛР4: подключает Command + CoR в главный цикл.

CommandDialogManager наследуется от исходного DialogManager и переопределяет
только run(): между ASR и NLU вставляется цепочка предобработчиков, а
вместо таблицы handle_intent используется фабрика команд + инвокер.
Visitor в самом менеджере не используется — он применяется снаружи к
invoker.history после завершения сеанса.
"""

from __future__ import annotations

import traceback

from dialog_manager import DialogManager
from interfaces import (
    ASRModule,
    InfoService,
    MusicService,
    NLUModule,
    Player,
    TTSModule,
    VoiceInterface,
)

from lab15.commands import CommandFactory, CommandInvoker
from lab15.preprocessing import TextHandler


class CommandDialogManager(DialogManager):
    """DialogManager с двумя поведенческими паттернами в главном цикле: Command + CoR."""

    def __init__(
        self,
        music_service: MusicService,
        info_service: InfoService,
        player: Player,
        asr: ASRModule,
        nlu: NLUModule,
        tts: TTSModule,
        voice_interface: VoiceInterface,
        chain: TextHandler,
        factory: CommandFactory,
        invoker: CommandInvoker,
    ) -> None:
        super().__init__(
            music_service=music_service,
            info_service=info_service,
            player=player,
            asr=asr,
            nlu=nlu,
            tts=tts,
            voice_interface=voice_interface,
        )
        self.chain = chain
        self.factory = factory
        self.invoker = invoker

    def run(self) -> None:
        """Главный цикл: listen -> ASR -> CoR -> NLU -> Command -> Invoker."""
        self.is_running = True
        self.say("Голосовой ассистент запущен")
        while self.is_running:
            try:
                audio = self.voice.listen()
                text = self.asr.recognize(audio)
                # Предобработчики живут на сыром тексте.
                processed = self.chain.handle(text)
                if processed is None:
                    # Цепочка отбросила запрос — пропускаем итерацию.
                    continue
                print(f"[USER]: {processed}")
                intent, data = self.nlu.parse(processed)
                command = self.factory.create(intent, data)
                self.invoker.execute(command)
            except EOFError:
                break
            except Exception as e:
                traceback.print_exc()
                self.say("Произошла ошибка. Повторите запрос.")
                print(f"[ERROR]: {e}")
