"""
Точка входа ЛР09: Factory Method, Abstract Factory, Singleton, Prototype, Object Pool.

Запуск из корня репозитория:
    python3 -m lab9.main
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dialog_manager import DialogManager
from lab9.abstract_factory import AssistantComponentFactory, build_component_factory
from lab9.object_pool import ObjectPool, PlayerSession
from lab9.prototype import CloneRegistry, NLUPrototype, TTSPrototype
from lab9.singleton_config import AssistantConfig


class AssistantAssembler:
    """Собирает DialogManager через порождающие паттерны."""

    def __init__(self, config: AssistantConfig) -> None:
        self.config = config
        self.factory: AssistantComponentFactory = build_component_factory(config)
        self.registry = CloneRegistry()
        self._session_counter = 0
        self.pool = ObjectPool[PlayerSession](
            factory=self._build_player_session,
            max_size=int(config.get("pool_max_size", 2)),
            grow=bool(config.get("pool_grow", True)),
        )

    def _build_player_session(self) -> PlayerSession:
        self._session_counter += 1
        return PlayerSession(session_id=self._session_counter)

    def _register_prototypes(self) -> None:
        defaults = self.config.get("prototype_defaults", {})
        nlu_defaults = defaults.get("nlu", {})
        tts_defaults = defaults.get("tts", {})

        tts1 = TTSPrototype(
            kind=str(tts_defaults.get("kind", "basic")),
            voice=str(tts_defaults.get("voice", "default")),
            metadata={"profile": self.config.get("profile", "offline")},
        )

        self.registry.register(
            "nlu",
            NLUPrototype(
                kind=str(nlu_defaults.get("kind", "rule")),
                language=str(nlu_defaults.get("language", "ru")),
                metadata={"profile": self.config.get("profile", "offline")},
            ),
        )
        self.registry.register("tts", tts1)

    def build_dialog_manager(self) -> DialogManager:
        self._register_prototypes()
        return DialogManager(
            music_service=self.factory.create_music_service(),
            info_service=self.factory.create_info_service(),
            player=self.factory.create_player(),
            asr=self.factory.create_asr(),
            nlu=self.factory.create_nlu(),
            tts=self.factory.create_tts(),
            voice_interface=self.factory.create_voice_interface(),
        )


def _run_demo(dialog: DialogManager, assembler: AssistantAssembler) -> None:
    print("=== LAB09 DEMO START ===")
    cfg_a = AssistantConfig.get_instance()
    cfg_b = AssistantConfig.get_instance()
    print(f"[Singleton] same_instance={cfg_a is cfg_b}")

    nlu_clone = assembler.registry.clone_by_key("nlu")
    tts_clone = assembler.registry.clone_by_key("tts")
    print(f"[Prototype] nlu_clone={nlu_clone}")
    print(f"[Prototype] tts_clone={tts_clone}")

    s1 = assembler.pool.acquire()
    assembler.pool.release(s1)
    assembler.pool.acquire()
    s1.in_use = True
    s1.last_track = "demo_track_1"

    print(f"[ObjectPool] acquired session_id={s1.session_id}, total={assembler.pool.total_count}")
    assembler.pool.release(s1)
    print(f"[ObjectPool] released session_id={s1.session_id}, free={assembler.pool.free_count}")

    print(f"[AbstractFactory] family={assembler.factory.__class__.__name__}")
    print("[AbstractFactory] profile:\n" + assembler.factory.get_info())
    print(f"[FactoryMethod] product={dialog.music_service.__class__.__name__}")

    demo_lines = [
        "включи музыку",
        "громкость 6",
        "новости технологии",
        "кто такой ползунов",
        "выключись",
    ]
    for line in demo_lines:
        print(f"\n>>> {line}")
        intent, data = dialog.nlu.parse(line)
        dialog.handle_intent(intent, data)
    print("=== LAB09 DEMO END ===")


def main() -> None:
    cfg = AssistantConfig.get_instance()
    cfg2 = AssistantConfig.get_instance()
    print(f"[Singleton] config={cfg}, config2={cfg2}")
    print(f"[Singleton] config={id(cfg)}, config2={id(cfg2)}")
    print("Один и тот же объект конфига\n\n")
    cfg.configure(
        profile="offline",
        music_source="vk",
        pool_max_size=1,
        pool_grow=True,
        prototype_defaults={
            "nlu": {"kind": "rule", "language": "ru"},
            "tts": {"kind": "basic", "voice": "alena"},
        },
    )
    assembler = AssistantAssembler(cfg)
    dialog = assembler.build_dialog_manager()
    _run_demo(dialog, assembler)


if __name__ == "__main__":
    main()
