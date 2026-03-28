Лабораторная работа 06 (2 часа)  
Тема: Структурные паттерны 1 — реализация (Adapter, Decorator, Composite, Iterator)

Код и точка входа: каталог `lab6/` (модуль `lab6.main`). Запуск из корня репозитория:

`python3 -m lab6.main`

---

## 1. Краткое описание назначения классов реализации каждого паттерна

### Adapter
| Класс | Назначение |
|-------|------------|
| `ExternalTTSClient` | Имитация внешнего TTS с «чужим» API (`request_speech`, `choose_timbre`), не совпадающим с `TTSModule`. |
| `ExternalTTSAdapter` | Приводит вызовы `TTSModule.synthesize` / `set_voice` к методам `ExternalTTSClient`, чтобы `Lab6DialogManager` не зависел от внешнего контракта. |

### Decorator
| Класс | Назначение |
|-------|------------|
| `TTSDecorator` | Абстрактная обёртка над `TTSModule`: делегирует `synthesize` и `set_voice` вложенному компоненту. |
| `CachingTTSDecorator` | Кеширует результат `synthesize(text)` по ключу — повторные одинаковые фразы не пересчитываются. |
| `LoggingTTSDecorator` | Перед синтезом пишет в консоль диагностическую строку (`[TTS:log]`), не меняя классы базового TTS или адаптера. |

### Composite
| Класс | Назначение |
|-------|------------|
| `ResponseComponent` | Общий интерфейс узла дерева ответа (`get_children`). |
| `TextLeaf` | Лист: один фрагмент текста для озвучивания. |
| `ResponseGroup` | Контейнер: собирает дочерние `ResponseComponent`. |
| `NewsResponseGroup` | Специализированный композит для новостей: заголовок темы, нумерованные пункты, заключение. |
| `ResponseBuilder` | Фабрика деревьев ответа под разные намерения (`build_startup`, `build_news`, и т.д.). |

### Iterator
| Класс | Назначение |
|-------|------------|
| `ResponseIterator` | Интерфейс последовательной выдачи текстовых фрагментов (`has_next`, `next_fragment`). |
| `DepthFirstTextIterator` | Обход дерева в глубину (pre-order по листьям): порядок «сверху вниз, слева направо». |
| `BreadthFirstTextIterator` | Обход в ширину: демонстрация альтернативной стратегии порядка фрагментов. |
| `ResponseIteratorFactory` | Создаёт итератор по строке конфигурации (`dfs` / `bfs`), отделяя `DialogManager` от конкретного обхода. |

Дополнительно: `Lab6DialogManager` в `dialog_manager.py` собирает бизнес-логику ЛР04 с озвучиванием через «композит + итератор» и произвольный стек `TTSModule` (адаптер и декораторы задаются при конфигурировании).

---

## 2. Реализация конфигурирования системы

Конфигурация собирается в `lab6/main.py` принципом **Dependency Injection** (как в ЛР04):

- **Музыка / справка / плеер / ASR / NLU / голос** — готовые классы из корня проекта (`music_services`, `info_services`, …).
- **Adapter + Decorator для TTS** — функция `build_tts_stack()`:
  1. `ExternalTTSClient`
  2. `ExternalTTSAdapter(client, lang="ru")`
  3. `CachingTTSDecorator(adapter)`
  4. `LoggingTTSDecorator(...)` — внешний слой (сначала лог, затем при промахе кеша — реальный синтез).
- **Composite + Iterator** — в конструктор `Lab6DialogManager` передаются `ResponseBuilder()`, `ResponseIteratorFactory()` и строка стратегии:
  - `make_dialog_dfs()` — `iterator_strategy="dfs"` (по умолчанию в `if __name__ == "__main__"`);
  - `make_dialog_bfs()` — та же сборка, но `iterator_strategy="bfs"` (в коде оставлена закомментированная альтернатива переключения).

Переключение режима обхода: раскомментировать `make_dialog_bfs().run()` и закомментировать `make_dialog_dfs().run()` в `main.py`.

---

## 3. Логи работы программы

Команда (неинтерактивный прогон из `README`/отчёта):

```bash
cd /path/to/oop4
printf 'включи музыку\nгромкость 7\nновости IT\nвыключись\n' | python3 -m lab6.main
```

Фактический вывод:

```
[ASSISTANT]: Голосовой ассистент запущен
[TTS:log] synthesize: 'Голосовой ассистент запущен'
Введите текст: [USER]: включи музыку
Proxy: проверка прав
Этот сервис не может быть воспроизведен оффлайн
Spotify: play spotify_track_1
[ASSISTANT]: Воспроизвожу музыку
[TTS:log] synthesize: 'Воспроизвожу музыку'
Введите текст: [USER]: громкость 7
vol 7
[ASSISTANT]: Громкость установлена: 7
[TTS:log] synthesize: 'Громкость установлена: 7'
Введите текст: [USER]: новости IT
[ASSISTANT]: Новости по теме «IT».
[TTS:log] synthesize: 'Новости по теме «IT».'
[ASSISTANT]: Пункт 1. Yandex news 1 about IT
[TTS:log] synthesize: 'Пункт 1. Yandex news 1 about IT'
[ASSISTANT]: Пункт 2. Yandex news 2 about IT
[TTS:log] synthesize: 'Пункт 2. Yandex news 2 about IT'
[ASSISTANT]: Пункт 3. Yandex news 3 about IT
[TTS:log] synthesize: 'Пункт 3. Yandex news 3 about IT'
[ASSISTANT]: Это были главные заголовки.
[TTS:log] synthesize: 'Это были главные заголовки.'
Введите текст: [USER]: выключись
[ASSISTANT]: Завершение работы
[TTS:log] synthesize: 'Завершение работы'
```

По логам видно:

- **Decorator**: строки `[TTS:log]` перед каждым вызовом синтеза.
- **Adapter**: в байтах, возвращаемых TTS (в реальном UI не печатается), используется формат внешнего клиента; менеджер вызывает только `TTSModule`.
- **Composite + Iterator**: ответ по «новости IT» разбит на несколько последовательных `[ASSISTANT]: …` фрагментов — дерево `NewsResponseGroup` обходится итератором.
- **ЛР04 (Proxy)** сохраняется в конфигурации: `ProxyMusicService` при `offline=True` перед `play` выводит проверку прав и сообщение об офлайн-ограничении.

---

## 4. Архив с исходным кодом программы

В каталоге `lab6/` создаётся файл **`lab6_source.zip`** — архив всей папки `lab6/` (исходники и этот отчёт), без `__pycache__` и без вложенного предыдущего zip.

Сборка архива из корня репозитория:

```bash
cd /path/to/oop4
zip -r lab6/lab6_source.zip lab6 \
  -x "lab6/__pycache__/*" \
  -x "lab6/**/__pycache__/*" \
  -x "*.pyc" \
  -x "lab6/lab6_source.zip"
```

После выполнения команды архив лежит по пути: `lab6/lab6_source.zip`.
