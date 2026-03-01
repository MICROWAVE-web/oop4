"""Реализации аудиоплееров: базовый, потоковый, Bluetooth."""

from interfaces import Player


class BasicPlayer(Player):
    """Плеер для локального воспроизведения (динамик/наушники)."""

    def play_audio(self, audio_stream: bytes) -> None:
        """Воспроизводит переданный аудиопоток (имитация)."""
        print("BasicPlayer: playing")

    def set_volume(self, level: int) -> None:
        """Устанавливает громкость (0–10)."""
        print(f"vol {level}")

    def connect_output(self, output_type: str) -> None:
        """Подключает вывод к указанному устройству."""
        print(f"Connected to {output_type}")


class StreamingPlayer(Player):
    """Плеер для потокового воспроизведения (стриминг)."""

    def play_audio(self, audio_stream: bytes) -> None:
        """Запускает потоковое воспроизведение (имитация)."""
        print("StreamingPlayer: stream play")

    def set_volume(self, level: int) -> None:
        """Уровень громкости (заглушка)."""
        pass

    def connect_output(self, output_type: str) -> None:
        """Подключение вывода (заглушка)."""
        pass


class BluetoothPlayer(Player):
    """Плеер с выводом на Bluetooth-устройство."""

    def play_audio(self, audio_stream: bytes) -> None:
        """Воспроизведение через Bluetooth (имитация)."""
        print("Bluetooth: play")

    def set_volume(self, level: int) -> None:
        """Громкость (заглушка)."""
        pass

    def connect_output(self, output_type: str) -> None:
        """Подключение Bluetooth (заглушка)."""
        pass
