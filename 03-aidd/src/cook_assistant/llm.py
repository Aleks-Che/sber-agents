"""LLM client for OpenRouter."""
import asyncio
import logging
from typing import List, Dict, Optional

import openai
from .config import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — Кулинарный помощник, эксперт в области кулинарии, питания и гастрономии. Твоя задача — помогать пользователям с любыми вопросами, связанными с приготовлением пищи.

Ты должен:
- Давать чёткие, практичные советы и рецепты.
- Учитывать диетические ограничения (вегетарианство, аллергии, диеты).
- Предлагать замены ингредиентов, если чего‑то нет под рукой.
- Объяснять шаги приготовления простым языком.
- Поддерживать дружелюбный, мотивирующий тон.
- Избегать вредных или опасных рекомендаций.
- Если вопрос не по кулинарии, вежливо направлять разговор в соответствующее русло.

Формат ответов: текст с эмодзи для наглядности, списки, где уместно."""


class LLMClient:
    """Client for OpenRouter API."""

    def __init__(self) -> None:
        self.client = openai.AsyncOpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            timeout=30.0,
        )
        self.model = config.LLM_MODEL

    async def generate_response(
        self, user_message: str, history: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """Generate LLM response for given user message and optional history."""
        messages = self._build_messages(user_message, history)
        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                )
                return response.choices[0].message.content
            except asyncio.TimeoutError:
                logger.warning(f"LLM request timeout (attempt {attempt})")
                if attempt == max_attempts:
                    logger.error("LLM request timed out after all attempts")
                    return None
            except Exception as e:
                logger.error(f"LLM request failed (attempt {attempt}): {e}")
                if attempt == max_attempts:
                    return None
                await asyncio.sleep(1)
        return None

    def _build_messages(
        self, user_message: str, history: Optional[List[Dict]]
    ) -> List[Dict[str, str]]:
        """Build messages list with system prompt, history, and user message."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            # history is list of dicts with "role" and "content"
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return messages


llm_client = LLMClient()