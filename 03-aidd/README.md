# Кулинарный помощник в Telegram

Telegram-бот с LLM-ассистентом для кулинарных вопросов.

## Функциональность

- Ответы на кулинарные вопросы через LLM (OpenRouter)
- Поддержка контекста диалога
- Команды `/start`, `/help`, `/reset`, `/recipe`
- Логирование и обработка ошибок

## Установка

1. Клонируйте репозиторий.
2. Установите зависимости через `uv`:
   ```bash
   uv sync
   ```
3. Создайте файл `.env` на основе `.env.example` и заполните токены.
4. Запустите бота:
   ```bash
   make run
   ```

## Конфигурация

Обязательные переменные окружения:

- `TELEGRAM_BOT_TOKEN` — токен бота, полученный от @BotFather.
- `OPENROUTER_API_KEY` — ключ API OpenRouter.

Опциональные переменные:

- `OPENROUTER_BASE_URL` — базовый URL OpenRouter (по умолчанию `https://openrouter.ai/api/v1`).
- `LLM_MODEL` — модель LLM (по умолчанию `gpt-3.5-turbo`). Вы можете выбрать любую модель, поддерживаемую OpenRouter (например, `gpt-4`, `claude-3-haiku`, `llama-3.2-3b-instruct`). Список доступных моделей: https://openrouter.ai/models.
- `MAX_HISTORY_LENGTH` — максимальная длина истории диалога (по умолчанию `10`).
- `LOG_LEVEL` — уровень логирования (по умолчанию `INFO`).

## Структура проекта

```
cook-assistant/
├── src/cook_assistant/
│   ├── bot.py          # основной код бота
│   ├── llm.py          # клиент для LLM
│   ├── config.py       # загрузка конфигурации
│   ├── storage.py      # хранение контекста
│   └── utils.py        # вспомогательные функции
├── docs/               # документация
├── pyproject.toml      # зависимости
├── Makefile            # команды управления
└── README.md           # этот файл
```

## Разработка

Проект разрабатывается итеративно согласно [tasklist.md](docs/tasklist.md).

### Команды

- `make run` — запуск бота.
- `make install` — установка зависимостей.
- `make lint` — проверка кода с помощью ruff.
- `make test` — запуск тестов.
- `make clean` — очистка временных файлов.

## Лицензия

MIT
