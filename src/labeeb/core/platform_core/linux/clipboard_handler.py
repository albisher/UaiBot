import pyperclip
from src.app.core.platform_core.common.base_handler import BaseHandler
from typing import Optional, Dict, Any

class LinuxClipboardHandler(BaseHandler):
    """Clipboard handler for Linux using pyperclip."""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def set_text(self, text: str) -> None:
        pyperclip.copy(text)

    def get_text(self) -> str:
        return pyperclip.paste()

    def clear(self) -> None:
        pyperclip.copy("")

    def cleanup(self) -> None:
        self._initialized = False 