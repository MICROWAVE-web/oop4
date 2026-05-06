"""Диалоговый менеджер: координирует все сервисы и обрабатывает намерения пользователя."""
import traceback

from interfaces import (
    MusicService,
    InfoService,
    Player,
    ASRModule,
    NLUModule,
    TTSModule,
    VoiceInterface,
)
from typing import Any


class DialogManager:
    """Центральный компонент: делегирует ввод, ASR, NLU, музыку, справки и TTS соответствующим сервисам."""

    def __init__(
        self,
        music_service: MusicService,
        info_service: InfoService,
        player: Player,
        asr: ASRModule,
        nlu: NLUModule,
        tts: TTSModule,
        voice_interface: VoiceInterface,
    ):
        """Принимает все зависимости через конструктор (Dependency Injection)."""
        self.music_service = music_service
        self.info_service = info_service
        self.player = player
        self.asr = asr
        self.nlu = nlu
        self.tts = tts
        self.voice = voice_interface
        self.context = {}
        self.is_running = False

    def run(self):
        """Запускает главный цикл: слушаем → распознаём → NLU → обработка намерения."""
        self.is_running = True
        self.say("Голосовой ассистент запущен")
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
                self.say("Произошла ошибка. Повторите запрос.")
                print(f"[ERROR]: {e}")

    def stop(self):
        """Останавливает цикл и прощается с пользователем."""
        self.is_running = False
        self.say("Завершение работы")

    def handle_intent(self, intent: str, data: Any):
        """Вызывает обработчик по типу намерения (music, info, news, volume, exit и т.д.)."""
        handlers = {
            "music": self.handle_music,
            "info": self.handle_info,
            "news": self.handle_news,
            "system": self.handle_system,
            "volume": self.handle_volume,
            "exit": lambda _: self.stop(),
        }
        handler = handlers.get(intent, self.handle_unknown)
        handler(data)

    def handle_music(self, data):
        """Ищет треки, воспроизводит первый и сообщает пользователю."""

        if not self.music_service:
            self.say("Сервис отключен")
            return
        tracks = self.music_service.search(data)
        if not tracks:
            self.say("Ничего не найдено")
            return
        track_id = tracks[0]
        self.music_service.play(track_id)
        self.say("Воспроизвожу музыку")

    def handle_info(self, data):
        """Запрос к справочному сервису и озвучивание ответа."""
        if not self.info_service:
            self.say("Сервис отключен")
            return
        result = self.info_service.get_info(data)
        self.say(result)

    def handle_news(self, data):
        """Получение новостей по теме и озвучивание по пунктам."""
        if not self.info_service:
            self.say("Сервис отключен")
            return
        news = self.info_service.get_news(data)
        if not news:
            self.say("Новостей нет")
            return
        for item in news:
            self.say(item)

    def handle_system(self, data):
        """Системные команды (например, stop)."""
        if data == "stop":
            self.stop()

    def handle_volume(self, data):
        """Установка громкости через плеер; data — число уровня."""
        if not self.player:
            self.say("Сервис отключен")
            return
        try:
            level = int(data)
            self.player.set_volume(level)
            self.say(f"Громкость установлена: {level}")
        except (TypeError, ValueError):
            self.say("Неверный уровень громкости")

    def handle_unknown(self, data):
        """Ответ при неизвестном намерении."""
        self.say("Команда не распознана")

    def say(self, text: str):
        """Выводит текст ассистента и озвучивает через TTS и голосовой интерфейс."""
        print(f"[ASSISTANT]: {text}")
        audio = self.tts.synthesize(text)
        self.voice.speak(audio)
