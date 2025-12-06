"""Telegram bot with LLM culinary assistant."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ErrorEvent
from aiogram.filters import Command

from .config import config
from .llm import llm_client
from .storage import storage

# Configure logging
def setup_logging():
    """Setup logging with configurable level, format, and file."""
    root_logger = logging.getLogger()
    root_logger.setLevel(config.LOG_LEVEL)

    formatter = logging.Formatter(config.LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if LOG_FILE is set
    if config.LOG_FILE:
        file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

setup_logging()
logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.error()
async def error_handler(event: ErrorEvent) -> None:
    """Global error handler."""
    logger.error(f"Unhandled exception: {event.exception}", exc_info=event.exception)


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "Привет! Я кулинарный помощник. "
        "Задавайте мне любые вопросы по кулинарии, и я постараюсь помочь! 🍳"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    help_text = (
        "📚 *Доступные команды:*\n"
        "/start – приветствие и описание бота\n"
        "/help – эта справка\n"
        "/reset – очистить историю диалога\n"
        "/recipe <запрос> – поиск рецепта по ключевым словам\n"
        "\n"
        "💡 *Примеры запросов:*\n"
        "• Как приготовить омлет?\n"
        "• Что можно сделать из курицы и картофеля?\n"
        "• Рецепт борща\n"
        "• Сколько варить макароны?\n"
        "\n"
        "Просто напишите ваш кулинарный вопрос, и я постараюсь помочь! 🍽️"
    )
    await message.answer(help_text, parse_mode="Markdown")


@dp.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    """Handle /reset command."""
    chat_id = message.chat.id
    storage.clear(chat_id)
    logger.info(f"History cleared for chat {chat_id}")
    await message.answer(
        "История диалога очищена. "
        "Теперь я не помню предыдущие сообщения. 🧹"
    )


@dp.message(Command("recipe"))
async def cmd_recipe(message: Message) -> None:
    """Handle /recipe command."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or ""
    logger.info(f"Recipe command from {user_id}: {text}")

    # Extract query after /recipe
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Пожалуйста, укажите запрос после команды /recipe.\n"
            "Например: /recipe паста карбонара"
        )
        return
    query = parts[1].strip()
    if not query:
        await message.answer("Запрос не может быть пустым.")
        return

    # Show typing indicator
    await bot.send_chat_action(chat_id=chat_id, action="typing")

    # Generate recipe-specific response
    response = await llm_client.generate_recipe_response(query)
    if response is None:
        logger.error(f"LLM recipe failed for user {user_id}")
        response = (
            "Извините, сейчас не могу найти рецепт. "
            "Попробуйте позже или уточните запрос.\n"
            "Если проблема повторяется, попробуйте очистить историю диалога командой /reset."
        )

    logger.info(f"Recipe response to {user_id}: {response[:100]}...")
    await message.answer(response)

    # Store interaction in history? Optionally, we can store as user/assistant messages
    storage.add_message(chat_id, "user", f"/recipe {query}")
    storage.add_message(chat_id, "assistant", response)


@dp.message()
async def handle_message(message: Message) -> None:
    """Handle user message with LLM."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text or ""
    logger.info(f"Message from {user_id}: {text}")

    if not text.strip():
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    # Check for help keywords
    help_keywords = ["help", "помощь", "команды", "управление"]
    lower_text = text.lower()
    if any(keyword in lower_text for keyword in help_keywords):
        help_text = (
            "📚 *Доступные команды:*\n"
            "/start – приветствие и описание бота\n"
            "/help – эта справка\n"
            "/reset – очистить историю диалога\n"
            "/recipe <запрос> – поиск рецепта по ключевым словам\n"
            "\n"
            "💡 *Примеры запросов:*\n"
            "• Как приготовить омлет?\n"
            "• Что можно сделать из курицы и картофеля?\n"
            "• Рецепт борща\n"
            "• Сколько варить макароны?\n"
            "\n"
            "Просто напишите ваш кулинарный вопрос, и я постараюсь помочь! 🍽️"
        )
        await message.answer(help_text, parse_mode="Markdown")
        return

    # Show typing indicator
    await bot.send_chat_action(chat_id=chat_id, action="typing")

    # Get dialog history
    history = storage.get_messages(chat_id)

    # Generate LLM response with history
    response = await llm_client.generate_response(text, history)
    if response is None:
        logger.error(f"LLM failed for user {user_id}")
        response = (
            "Извините, сейчас не могу ответить. "
            "Попробуйте позже или задайте вопрос иначе.\n"
            "Если проблема повторяется, попробуйте очистить историю диалога командой /reset."
        )

    logger.info(f"Response to {user_id}: {response[:100]}...")
    await message.answer(response)

    # Store user message and assistant response
    storage.add_message(chat_id, "user", text)
    storage.add_message(chat_id, "assistant", response)


async def main() -> None:
    """Start the bot."""
    config.validate()
    logger.info("Starting bot with LLM...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())