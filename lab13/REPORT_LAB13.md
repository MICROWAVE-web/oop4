«Алтайский государственный технический университет им. И. И. Ползунова»  
Факультет информационных технологий  
Кафедра прикладной математики  

**Отчёт**  
По лабораторной работе **№13**  
по дисциплине «ООП: Архитектурное проектирование и паттерны программирования - 4 семестр»  

Студент группы **ПИ-32** Кованов Алексей  
Преподаватель Крючкова Елена Николаевна  
Барнаул 2026

---

## Лабораторная работа 13 (2 часа)

**Тема:** Паттерны поведения 1 — реализация (**State**, **Memento**, **Observer**).

**Основа:** архитектура ЛР4 (`interfaces.py`, `dialog_manager.py`, реализации сервисов в корне репозитория) + сборка профилей через Builder из ЛР11 (`lab11/builder.py`).

---

## 1. Краткое описание назначения классов реализации каждого паттерна

### State — `lab13/states.py`

- `AssistantState` — абстрактный базовый класс с методами `name()` (имя состояния) и `handle(ctx, intent, data)` (обработка намерения в контексте `StatefulDialogManager`).
- `IdleState` — режим ожидания: на «включи музыку» запускает трек и переключает контекст в `PlayingState`. Поддерживает все обычные команды (громкость, info, news, snapshot/restore, mute, exit).
- `PlayingState` — режим воспроизведения: на повторное «включи музыку» отвечает «уже играет», на `system stop` останавливает трек и возвращает контекст в `IdleState`. На `mute` останавливает трек и переходит в `MutedState`.
- `MutedState` — режим «не беспокоить»: реагирует только на `unmute` (возврат в `IdleState`) и `exit`. Все прочие команды игнорируются.

Переключение состояний выполняют сами состояния через `ctx.set_state(...)`, что соответствует «варианту 2» из лекционного материала (каждое состояние программируется индивидуально, контекст лишь хранит ссылку).

### Memento — `lab13/memento.py`

- `SettingsMemento` — иммутабельный (`@dataclass(frozen=True)`) снимок настроек: `volume`, `current_track`, `state_name`. Не содержит логики — только данные.
- `SettingsCaretaker` — хранитель снимков. Хранит стек, предоставляет операции `save(memento)`, `restore()`, `has_snapshot()`, `count()`. Не имеет доступа к внутренним полям контекста — работает только с готовыми объектами `SettingsMemento`, что соблюдает инкапсуляцию.

### Observer — `lab13/observer.py`

- `EventObserver` — абстрактный наблюдатель с методом `update(event_name, payload)`.
- `EventSubject` — субъект: ведёт список подписчиков, методы `attach(o)`, `detach(o)`, `notify(name, payload)`.
- `LoggerObserver` — записывает события в открытый текстовый поток (например, `run.log`).
- `StatisticsObserver` — накапливает счётчики событий за сеанс (сколько раз случилось `track_started`, `volume_changed` и т.д.) и формирует итоговый отчёт `report()`.
- `ScreenObserver` — имитация экрана колонки: на каждое значимое событие печатает строку «текущий экран» (`mode`, `track`, `vol`).

### Расширение исходных модулей ЛР4

- `lab13/nlu_ext.py` — `ExtendedRuleBasedNLU(RuleBasedNLU)`. Добавляет ключевые слова: «запомни» → `snapshot`, «восстанови» → `restore`, «не беспокой» → `mute`, «вернись» → `unmute`, «стоп» → `system/stop`. Прочие команды передаются базовому NLU из ЛР4.
- `lab13/dialog_manager_ext.py` — `StatefulDialogManager(DialogManager)`. Делегирует `handle_intent` текущему состоянию, публикует события через `EventSubject`, владеет `SettingsCaretaker`. Добавляет операции `start_music`, `stop_music`, `change_volume`, `save_snapshot`, `restore_snapshot`, `delegate_info`, `delegate_news`.

---

## 2. Реализация конфигурирования системы

Конфигурирование переиспользует Builder из ЛР11 и расширяет результат тремя поведенческими паттернами.

```13:60:lab13/main.py
def build_assistant(
    log_file: TextIO,
) -> tuple[StatefulDialogManager, StatisticsObserver]:
    """Собирает офлайн-конфигурацию через Builder из ЛР11 и подменяет менеджер на расширенный."""
    director = AssistantDirector()
    scripted = ScriptedVoiceInterface(SCRIPT)

    assembly = director.construct(
        builder=OfflineAssistantBuilder(),
        voice_override=scripted,
    )
```

Шаги конфигурирования:

1. **Сборка зависимостей через Builder из ЛР11.** `AssistantDirector` + `OfflineAssistantBuilder` дают `AssistantAssembly` с готовым набором сервисов (Proxy + Spotify, Wikipedia, BasicPlayer, SimpleASR, BasicTTS, ScriptedVoiceInterface).
2. **Подмена NLU.** `assembly.nlu = ExtendedRuleBasedNLU()` — теперь распознаются новые команды без правки исходного `RuleBasedNLU` из ЛР4.
3. **Регистрация наблюдателей.** Создаётся `EventSubject`, к нему подписываются `LoggerObserver`, `StatisticsObserver`, `ScreenObserver`. Наблюдатели полностью независимы — добавление/удаление любого из них не требует правок в `StatefulDialogManager`.
4. **Создание расширенного менеджера.** `StatefulDialogManager` принимает все зависимости из сборки + начальное состояние (`IdleState`), `SettingsCaretaker`, `EventSubject` и стартовый уровень громкости.
5. **Запуск сценария.** `manager.run()` крутит главный цикл `DialogManager` из ЛР4, но `handle_intent` теперь делегирован текущему состоянию.

Сценарий проходит все три паттерна:

| Реплика | Что демонстрирует |
|---------|-------------------|
| `включи музыку` | State: Idle → Playing; Observer: `track_started`, `state_changed` |
| `громкость 7` | Observer: `volume_changed` |
| `запомни настройки` | Memento: `SettingsCaretaker.save(...)`; Observer: `snapshot_saved` |
| `громкость 3` | Изменение, которое затем будет откачено |
| `включи музыку` (повтор) | State: Playing — отвечает «уже играет» |
| `не беспокой` | State: Playing → Muted; Observer: `track_stopped`, `state_changed` |
| `включи музыку` (в Muted) | State: команда игнорируется |
| `вернись` | State: Muted → Idle |
| `восстанови настройки` | Memento: восстановление громкости/трека/состояния; Observer: соответствующие события |
| `выключись` | Завершение работы |

---

## 3. Логи работы программы

Полный лог сеанса сохраняется в файл:

- `lab13/run.log`

В лог попадают строки трёх категорий:
- `[USER] / [ASSISTANT]` — реплики из исходного `DialogManager` ЛР4;
- `[LOG] event_name: payload` — записи `LoggerObserver`;
- `[SCREEN] ...` — текущий экран от `ScreenObserver`;
- `[STATS] ...` — итоговый отчёт `StatisticsObserver` после завершения сеанса.

Фрагмент лога (ключевые точки сценария):

```text
Старт ЛР13: State + Memento + Observer

[ASSISTANT]: Голосовой ассистент запущен
Введите текст: [USER]: включи музыку
Proxy: проверка прав
Этот сервис не может быть воспроизведен оффлайн
Spotify: play spotify_track_1
[ASSISTANT]: Воспроизвожу музыку
[LOG] track_started: {'track': 'spotify_track_1'}
[SCREEN] mode=Idle | track=spotify_track_1 | vol=0
[ASSISTANT]: Переход в состояние: Playing
[LOG] state_changed: {'from': 'Idle', 'to': 'Playing'}
...
Введите текст: [USER]: запомни настройки
[ASSISTANT]: Настройки сохранены
[LOG] snapshot_saved: {'volume': 7, 'current_track': 'spotify_track_1', 'state': 'Playing'}
...
Введите текст: [USER]: не беспокой
[LOG] state_changed: {'from': 'Playing', 'to': 'Muted'}
[SCREEN] mode=Muted | track=— | vol=3
Введите текст: [USER]: включи музыку
[ASSISTANT]: Не беспокоить: команда проигнорирована
...
Введите текст: [USER]: восстанови настройки
[LOG] volume_changed: {'volume': 7}
[LOG] state_changed: {'from': 'Idle', 'to': 'Playing'}
[LOG] track_started: {'track': 'spotify_track_1'}
[ASSISTANT]: Настройки восстановлены: vol=7, track=spotify_track_1, state=Playing
...
[STATS] snapshot_saved=1, state_changed=4, track_started=2, track_stopped=2, volume_changed=3
```

Что подтверждают логи:
- **State.** Команда «включи музыку» в `MutedState` действительно игнорируется, в `PlayingState` отвечает «уже играет», в `IdleState` запускает трек.
- **Memento.** После «восстанови настройки» громкость, трек и состояние возвращаются к значениям, сохранённым на «запомни настройки» (vol=7, track=spotify_track_1, state=Playing), несмотря на промежуточные изменения.
- **Observer.** На каждое значимое действие приходит уведомление сразу всем подписчикам: `LoggerObserver` пишет в файл, `ScreenObserver` обновляет «экран», `StatisticsObserver` копит счётчики и в финале выдаёт `[STATS]`.

---

## 4. Архив с исходным кодом программы

Архив исходников лабораторной:

- `lab13/lab13_source.zip`

В архив включены:
- `__init__.py`
- `states.py`
- `memento.py`
- `observer.py`
- `nlu_ext.py`
- `dialog_manager_ext.py`
- `main.py`
- `diagram_lab13.puml`
- `REPORT_LAB13.md`
- `run.log`
