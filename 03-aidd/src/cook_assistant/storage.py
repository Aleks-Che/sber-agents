"""In-memory storage for dialog context."""
from typing import Dict, List, Optional
from datetime import datetime

from .config import config


class DialogStorage:
    """Simple in-memory storage for dialog messages."""

    def __init__(self) -> None:
        self._storage: Dict[int, List[Dict]] = {}

    def get_messages(self, chat_id: int) -> List[Dict]:
        """Get message history for a chat."""
        return self._storage.get(chat_id, [])

    def add_message(
        self, chat_id: int, role: str, content: str
    ) -> None:
        """Add a message to history."""
        if chat_id not in self._storage:
            self._storage[chat_id] = []
        self._storage[chat_id].append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
            }
        )
        # Trim history to max length
        if len(self._storage[chat_id]) > config.MAX_HISTORY_LENGTH:
            self._storage[chat_id] = self._storage[chat_id][
                -config.MAX_HISTORY_LENGTH:
            ]

    def clear(self, chat_id: int) -> None:
        """Clear history for a chat."""
        self._storage.pop(chat_id, None)


storage = DialogStorage()