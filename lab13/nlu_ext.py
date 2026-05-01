"""Расширенный NLU: добавляет к правилам ЛР4 команды snapshot/restore/mute/unmute и stop."""

from __future__ import annotations

from typing import Any, Tuple

from nlu import RuleBasedNLU


class ExtendedRuleBasedNLU(RuleBasedNLU):
    """Дополняет RuleBasedNLU намерениями для Memento и State."""

    def parse(self, text: str) -> Tuple[str, Any]:
        # Сначала проверяем новые ключевые слова — они должны иметь приоритет.
        if "запомни" in text:
            return ("snapshot", None)
        if "восстанови" in text:
            return ("restore", None)
        if "не беспокой" in text:
            return ("mute", None)
        if "вернись" in text:
            return ("unmute", None)
        if "стоп" in text:
            # «стоп» в режиме Playing — это остановка трека, а не выход.
            return ("system", "stop")
        return super().parse(text)
