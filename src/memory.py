import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.config import BASE_DIR


class ConversationMemory:
    """
    Stores a clean log of user and assistant turns in memory and persists
    them to a local JSON file (`chat_history.json`) for session continuity and auditing.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (BASE_DIR / "chat_history.json")
        self.turns: list[dict[str, str]] = []
        self._load_from_disk()

    def _load_from_disk(self):
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.turns = data
            except Exception:
                self.turns = []

    def _save_to_disk(self):
        try:
            self.storage_path.write_text(
                json.dumps(self.turns, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception:
            pass

    def add_turn(self, user_message: str, model_response: str):
        self.turns.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": user_message,
            "assistant": model_response
        })
        self._save_to_disk()

    def clear(self):
        self.turns.clear()
        if self.storage_path.exists():
            try:
                self.storage_path.unlink()
            except Exception:
                pass
