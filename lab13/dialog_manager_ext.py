"""Расширенный диалоговый менеджер: интегрирует State, Memento и Observer в DialogManager из ЛР4."""

from __future__ import annotations

from typing import Any, Optional

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

from lab13.memento import SettingsCaretaker, SettingsMemento
from lab13.observer import EventSubject
from lab13.states import AssistantState, IdleState


class StatefulDialogManager(DialogManager):
    """DialogManager с тремя паттернами поведения: State, Memento, Observer."""

    def __init__(
        self,
        music_service: MusicService,
        info_service: InfoService,
        player: Player,
        asr: ASRModule,
        nlu: NLUModule,
        tts: TTSModule,
        voice_interface: VoiceInterface,
        initial_state: Optional[AssistantState] = None,
        caretaker: Optional[SettingsCaretaker] = None,
        subject: Optional[EventSubject] = None,
        initial_volume: int = 5,
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
        self.state: AssistantState = initial_state or IdleState()
        self.caretaker: SettingsCaretaker = caretaker or SettingsCaretaker()
        self.subject: EventSubject = subject or EventSubject()
        self.volume: int = initial_volume
        self.current_track: Optional[str] = None

    # --- State ---

    def set_state(self, new_state: AssistantState) -> None:
        """Переключает состояние и публикует событие state_changed."""
        old_name = self.state.name()
        new_name = new_state.name()
        if old_name == new_name:
            return
        self.state = new_state
        self.say(f"Переход в состояние: {new_name}")
        self.subject.notify("state_changed", {"from": old_name, "to": new_name})

    def handle_intent(self, intent: str, data: Any) -> None:
        """Делегирует обработку текущему состоянию."""
        self.state.handle(self, intent, data)

    # --- Действия, которые состояния вызывают на контексте ---

    def start_music(self, query: Any) -> None:
        """Поиск и запуск трека, обновление контекста, событие track_started."""
        tracks = self.music_service.search(query)
        if not tracks:
            self.say("Ничего не найдено")
            return
        track_id = tracks[0]
        self.music_service.play(track_id)
        self.current_track = track_id
        self.say("Воспроизвожу музыку")
        self.subject.notify("track_started", {"track": track_id})

    def stop_music(self) -> None:
        """Останавливает воспроизведение и сбрасывает текущий трек."""
        if self.current_track is None:
            return
        self.music_service.stop()
        stopped = self.current_track
        self.current_track = None
        self.say("Воспроизведение остановлено")
        self.subject.notify("track_stopped", {"track": stopped})

    def change_volume(self, data: Any) -> None:
        """Меняет громкость и уведомляет подписчиков."""
        try:
            level = int(data)
        except (TypeError, ValueError):
            self.say("Неверный уровень громкости")
            return
        self.volume = level
        self.player.set_volume(level)
        self.say(f"Громкость установлена: {level}")
        self.subject.notify("volume_changed", {"volume": level})

    def delegate_info(self, data: Any) -> None:
        """Делегирует справочный запрос базовому обработчику ЛР4."""
        super().handle_info(data)

    def delegate_news(self, data: Any) -> None:
        """Делегирует запрос новостей базовому обработчику ЛР4."""
        super().handle_news(data)

    # --- Memento ---

    def save_snapshot(self) -> None:
        """Создаёт снимок настроек и кладёт его в caretaker."""
        memento = SettingsMemento(
            volume=self.volume,
            current_track=self.current_track,
            state_name=self.state.name(),
        )
        self.caretaker.save(memento)
        self.say("Настройки сохранены")
        self.subject.notify(
            "snapshot_saved",
            {
                "volume": memento.volume,
                "current_track": memento.current_track,
                "state": memento.state_name,
            },
        )

    def restore_snapshot(self) -> None:
        """Восстанавливает последний снимок: громкость, трек и состояние."""
        if not self.caretaker.has_snapshot():
            self.say("Нет сохранённых настроек")
            return
        memento = self.caretaker.restore()
        # Восстанавливаем громкость через плеер.
        self.volume = memento.volume
        self.player.set_volume(memento.volume)
        self.subject.notify("volume_changed", {"volume": memento.volume})
        # Восстанавливаем состояние.
        self.set_state(_state_from_name(memento.state_name))
        # Восстанавливаем трек: если был — снова запускаем.
        if memento.current_track is not None:
            self.music_service.play(memento.current_track)
            self.current_track = memento.current_track
            self.subject.notify("track_started", {"track": memento.current_track})
        else:
            self.current_track = None
        self.say(
            f"Настройки восстановлены: vol={memento.volume}, "
            f"track={memento.current_track}, state={memento.state_name}"
        )


def _state_from_name(name: str) -> AssistantState:
    """Создаёт экземпляр состояния по его имени (для восстановления из Memento)."""
    # Импорт внутри функции, чтобы избежать циклического импорта.
    from lab13.states import IdleState, MutedState, PlayingState

    mapping = {"Idle": IdleState, "Playing": PlayingState, "Muted": MutedState}
    cls = mapping.get(name, IdleState)
    return cls()
