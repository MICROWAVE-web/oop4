«Алтайский государственный технический университет им. И. И. Ползунова»  
Факультет информационных технологий  
Кафедра прикладной математики  

**Отчёт**  
По лабораторной работе **№15**  
по дисциплине «ООП: Архитектурное проектирование и паттерны программирования - 4 семестр»  

Студент группы **ПИ-32** Кованов Алексей  
Преподаватель Крючкова Елена Николаевна  
Барнаул 2026

---

## Лабораторная работа 15 (2 часа)

**Тема:** Паттерны поведения 2 — реализация (**Command**, **Chain of Responsibility**, **Visitor**).

**Основа:** только корневые модули ЛР4 (`interfaces.py`, `dialog_manager.py`, `music_services.py`, `info_services.py`, `player.py`, `nlu.py`, `tts.py`). Builder из ЛР11 и State/Memento/Observer из ЛР13 не используются — конфигурация собирается вручную в `lab15/main.py`.

Запуск: `python -m lab15.main` из корня репозитория.

---

## 1. Краткое описание назначения классов реализации каждого паттерна

### Command — `lab15/commands.py`

| Класс | Назначение |
|-------|------------|
| `Command` | Абстрактная команда: методы `execute()` (выполнить) и `accept(visitor)` (двойная диспетчеризация для Visitor). |
| `PlayMusicCommand` | Запуск трека. Receiver — `MusicService`. Поле `played_track` сохраняется для аналитики визиторами. |
| `SetVolumeCommand` | Установка громкости. Receiver — `Player`. Парсит число; `level=None` если ввод некорректный. |
| `GetInfoCommand` | Справочный запрос. Receiver — `InfoService.get_info`. |
| `GetNewsCommand` | Запрос новостей. Receiver — `InfoService.get_news`; озвучивает каждую новость через `manager.say`. |
| `ExitCommand` | Завершение сеанса. Receiver — сам `DialogManager` (вызывает `stop()`). |
| `UnknownCommand` | Фоллбэк для нераспознанных намерений; хранит исходный текст для последующего анализа. |
| `CommandFactory` | Фабрика: по `(intent, data)` собирает нужную команду. Receiver-сервисы переданы один раз через конструктор. |
| `CommandInvoker` | Инвокер: `execute(cmd)` запускает команду и сохраняет в публичный список `history`. |

### Chain of Responsibility — `lab15/preprocessing.py`

| Класс | Назначение |
|-------|------------|
| `TextHandler` | Базовый обработчик: `set_next(handler)` связывает с преемником, шаблонный `handle(text) -> Optional[str]` сначала вызывает `_process()`, потом передаёт дальше. `None` от любого звена прерывает цепочку. |
| `StripHandler` | Удаляет пробельные символы по краям строки. |
| `EmptyTextHandler` | Прерывает цепочку, если строка пустая (после `strip()`). |
| `LowercaseHandler` | Приводит текст к нижнему регистру; печатает преобразование, если регистр изменился. |
| `LoggingHandler` | Финальное звено: фиксирует, что текст прошёл все фильтры, и пропускает его без изменений. |
| `build_default_chain()` | Утилита: собирает стандартную цепочку `Strip → Empty → Lowercase → Logging` и возвращает первое звено. |

### Visitor — `lab15/visitors.py`

| Класс | Назначение |
|-------|------------|
| `CommandVisitor` | Базовый визитор; все методы `visit_xxx` пустые по умолчанию. Конкретные визиторы переопределяют только нужные. |
| `CommandStatisticsVisitor` | Считает количество команд каждого типа за сеанс; `report()` возвращает строку `[STATS] music=… , …`. |
| `CommandLogVisitor` | Формирует человекочитаемый журнал из истории команд (что и с какими данными выполнялось). |
| `UnknownCommandsVisitor` | Выбирает все нераспознанные запросы — для анализа покрытия NLU. |
| `visit_all(visitor, history)` | Утилита: применяет визитор к каждой команде истории через `cmd.accept(v)`. |

### Расширение менеджера — `lab15/dialog_manager_ext.py`

- `CommandDialogManager(DialogManager)` — наследник `DialogManager` из ЛР4. В конструктор добавлены три новых зависимости: `chain` (первое звено CoR), `factory` (фабрика команд), `invoker`. Переопределён `run()`: после ASR текст идёт в цепочку, при `None` итерация пропускается, иначе из `(intent, data)` собирается команда и отдаётся инвокеру. `say()`, `stop()`, обработка `EOFError` и `Exception` унаследованы без изменений.

---

## 2. Реализация конфигурирования системы

Конфигурирование вынесено в [lab15/main.py](main.py) и полностью повторяет схему DI из корневого `main.py` ЛР4 — без Builder-ов и без сторонних паттернов.

```python
def build_assistant() -> CommandDialogManager:
    music_service = ProxyMusicService(SpotifyMusicService(), offline=True)
    info_service = WikipediaInfoService()
    player = BasicPlayer()
    asr = PassThroughASR()
    nlu = RuleBasedNLU()
    tts = BasicTTS()
    voice = ScriptedVoiceInterface(SCRIPT)

    chain = build_default_chain()
    invoker = CommandInvoker()
    factory = CommandFactory(music_service, info_service, player, manager=None)
    manager = CommandDialogManager(
        music_service, info_service, player, asr, nlu, tts, voice,
        chain=chain, factory=factory, invoker=invoker,
    )
    factory.manager = manager
    return manager
```

Шаги конфигурирования:

1. **Базовые сервисы ЛР4.** Стандартный офлайн-набор — без изменений по сравнению с корневым `main.py`. Дополнительно используется `PassThroughASR` (декодирует байты в строку без `strip` и без подстановки заглушки) — это нужно, чтобы пустой ввод дошёл до `EmptyTextHandler` и продемонстрировал срабатывание цепочки.
2. **Chain of Responsibility.** `build_default_chain()` собирает звенья `Strip → Empty → Lowercase → Logging`. Состав и порядок задаются здесь и могут быть изменены без правки `CommandDialogManager`.
3. **Command.** Создаётся `CommandFactory` с тремя Receiver-сервисами; ссылка на сам `manager` (для `ExitCommand`) проставляется после создания менеджера, чтобы разрешить циклическую зависимость. `CommandInvoker` создаётся один на сеанс.
4. **Сборка менеджера.** `CommandDialogManager` принимает все зависимости ЛР4 + `chain` + `factory` + `invoker`.
5. **Сценарий и Visitor.** В `main()` запускается `manager.run()`. После завершения главного цикла история команд готова — три визитора (`CommandStatisticsVisitor`, `CommandLogVisitor`, `UnknownCommandsVisitor`) обходят `manager.invoker.history` через утилиту `visit_all`.

Сценарий, демонстрирующий все три паттерна одним прогоном:

| Реплика пользователя | Что демонстрирует |
|----------------------|-------------------|
| `""` (пустая строка) | CoR: `EmptyTextHandler` отбрасывает запрос; NLU не вызывается. |
| `"ПРИВЕТ   "` | CoR: `StripHandler` убирает пробелы, `LowercaseHandler` нормализует регистр; NLU → `info` → `GetInfoCommand`. |
| `"включи музыку"` | Command: `PlayMusicCommand` → `MusicService.search/play`. |
| `"громкость 7"` | Command: `SetVolumeCommand` → `Player.set_volume(7)`. |
| `"новости IT"` | CoR: лоуэркейс → `новости it`; Command: `GetNewsCommand`. |
| `"расскажи про OOP"` | CoR: лоуэркейс; Command: `GetInfoCommand` (фоллбэк-интент NLU). |
| `"выключись"` | Command: `ExitCommand` → `manager.stop()`. |

После цикла визиторы пробегают историю и печатают свои отчёты.

---

## 3. Логи работы программы

Полный лог сеанса сохраняется в файл [run.log](run.log) (UTF-8). В лог попадают:

- `[ASSISTANT]: …` / `[USER]: …` — реплики из исходного `DialogManager` ЛР4;
- `[CHAIN] …` — диагностические строки звеньев цепочки CoR;
- `[STATS] …`, `[LOG] …`, `[UNKNOWN] …` — отчёты визиторов после завершения сеанса.

Фактический вывод (фрагменты):

```text
Старт ЛР15: Command + Chain of Responsibility + Visitor

[ASSISTANT]: Голосовой ассистент запущен
Введите текст: ''
[CHAIN] EmptyTextHandler: пустой запрос, итерация пропущена
Введите текст: 'ПРИВЕТ   '
[CHAIN] LowercaseHandler: 'ПРИВЕТ' -> 'привет'
[CHAIN] LoggingHandler: текст принят к разбору: 'привет'
[USER]: привет
[ASSISTANT]: Wikipedia summary for привет
Введите текст: 'включи музыку'
[CHAIN] LoggingHandler: текст принят к разбору: 'включи музыку'
[USER]: включи музыку
Proxy: проверка прав...
Некоторые функции этого сервиса в режиме оффлайн могут быть недоступны.
Spotify: play spotify_track_1
[ASSISTANT]: Воспроизвожу музыку
Введите текст: 'громкость 7'
[CHAIN] LoggingHandler: текст принят к разбору: 'громкость 7'
[USER]: громкость 7
vol 7
[ASSISTANT]: Громкость установлена: 7
Введите текст: 'новости IT'
[CHAIN] LowercaseHandler: 'новости IT' -> 'новости it'
[CHAIN] LoggingHandler: текст принят к разбору: 'новости it'
[USER]: новости it
[ASSISTANT]: Новостей нет
Введите текст: 'расскажи про OOP'
[CHAIN] LowercaseHandler: 'расскажи про OOP' -> 'расскажи про oop'
[CHAIN] LoggingHandler: текст принят к разбору: 'расскажи про oop'
[USER]: расскажи про oop
[ASSISTANT]: Wikipedia summary for расскажи про oop
Введите текст: 'выключись'
[CHAIN] LoggingHandler: текст принят к разбору: 'выключись'
[USER]: выключись
[ASSISTANT]: Завершение работы

=== Обход истории команд визиторами (Visitor) ===
[STATS] music=1, volume=1, info=2, news=1, exit=1, unknown=0
[LOG] Журнал команд сеанса:
  1. info: query='привет'
  2. music: query='включи музыку', track=spotify_track_1
  3. volume: level=7
  4. news: topic='it'
  5. info: query='расскажи про oop'
  6. exit: завершение работы
[UNKNOWN] нераспознанных команд не было
```

Что подтверждают логи:

- **Chain of Responsibility.** Пустая строка отброшена `EmptyTextHandler`, для `"ПРИВЕТ   "` сработали `Strip` (виден чистый `'ПРИВЕТ'` перед лоуэркейсом) и `Lowercase` (`'ПРИВЕТ' -> 'привет'`). Финальный `LoggingHandler` фиксирует факт прохождения цепочки на каждой итерации.
- **Command.** Шесть исполненных команд за сеанс — каждая делегирует работу своему Receiver-сервису, без `if/else` в самом менеджере. История полностью совпадает со сценарием.
- **Visitor.** После цикла все три визитора прошли по `invoker.history`. `CommandStatisticsVisitor` дал агрегированные счётчики, `CommandLogVisitor` — читаемый журнал, `UnknownCommandsVisitor` — пустой список (NLU из ЛР4 покрыл все реплики). Добавление новой аналитики (например, времени выполнения команд) потребует только новый подкласс `CommandVisitor`.

---

## 4. Архив с исходным кодом программы

Архив исходников лабораторной:

- `lab15/lab15_source.zip`

В архив включены:

- `__init__.py`
- `commands.py`
- `preprocessing.py`
- `visitors.py`
- `dialog_manager_ext.py`
- `main.py`
- `diagram_lab15.puml`
- `REPORT_LAB15.md`
- `run.log`
