"""Модули понимания естественного языка: на правилах и ML (имитация)."""

from interfaces import NLUModule
from typing import Any, Dict, Tuple


class RuleBasedNLU(NLUModule):
    """Определение намерения по ключевым словам: музыка, новости, громкость, выход, справка."""

    def parse(self, text: str) -> Tuple[str, Any]:
        """Возвращает (intent, data): music/news/volume/exit/info и связанные данные (текст, число и т.д.)."""
        if "музыку" in text or "песню" in text or "трек" in text or "музыка" in text:
            return ("music", text)
        if "новости" in text:
            return ("news", text.replace("новости", "").strip())
        if "громкость" in text:
            parts = text.split()
            for p in parts:
                if p.isdigit():
                    return ("volume", int(p))
            return ("volume", 5)
        if "выключись" in text or "стоп" in text:
            return ("exit", None)
        return ("info", text)

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Сущности не извлекаются — пустой словарь."""
        return {}


class MLNLUModule(NLUModule):
    """Имитация NLU на основе ML-модели; всегда один intent с сырым текстом."""

    def parse(self, text: str) -> Tuple[str, Any]:
        """Возвращает фиксированный intent и сырой текст в data."""
        return ("intent_ml", {"raw": text})

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Пустой список сущностей (заглушка)."""
        return {"entities": []}
