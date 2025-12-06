"""Telegram bot with LLM culinary assistant."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from .config import config
from .llm import llm_client

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "Привет! Я кулинарный помощник. "
        "Задавайте мне любые вопросы по кулинарии, и я постараюсь помочь! 🍳"
    )


@dp.message()
async def handle_message(message: Message) -> None:
    """Handle user message with LLM."""
    user_id = message.from_user.id
    text = message.text or ""
    logger.info(f"Message from {user_id}: {text}")

    if not text.strip():
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return

    # Show typing indicator
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Generate LLM response
    response = await llm_client.generate_response(text)
    if response is None:
        logger.error(f"LLM failed for user {user_id}")
        response = (
            "Извините, сейчас не могу ответить. "
            "Попробуйте позже или задайте вопрос иначе."
        )

    logger.info(f"Response to {user_id}: {response[:100]}...")
    await message.answer(response)


async def main() -> None:
    """Start the bot."""
    config.validate()
    logger.info("Starting bot with LLM...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())