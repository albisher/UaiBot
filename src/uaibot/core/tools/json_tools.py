import orjson
from typing import Any, Dict, Optional

class JSONTool:
    """Tool for fast, correct JSON handling using orjson."""
    name = 'json'
    description = "Fast, correct JSON handling (load, dump, validate, pretty-print) using orjson."

    def __init__(self, lang: str = 'en'):
        self.lang = lang

    def load(self, s: str) -> Any:
        try:
            return orjson.loads(s)
        except Exception as e:
            return self._error(f"Failed to parse JSON: {e}")

    def dump(self, obj: Any, pretty: bool = False) -> str:
        try:
            opts = orjson.OPT_INDENT_2 if pretty else 0
            return orjson.dumps(obj, option=opts).decode()
        except Exception as e:
            return self._error(f"Failed to serialize object: {e}")

    def validate(self, s: str) -> bool:
        try:
            orjson.loads(s)
            return True
        except Exception:
            return False

    def pretty_print(self, s: str) -> str:
        try:
            obj = orjson.loads(s)
            return orjson.dumps(obj, option=orjson.OPT_INDENT_2).decode()
        except Exception as e:
            return self._error(f"Failed to pretty-print JSON: {e}")

    def execute(self, action: str, **kwargs) -> Any:
        """Agent-compatible execute method for A2A/MCP/SmolAgents."""
        if action == 'load':
            return self.load(kwargs.get('s', ''))
        elif action == 'dump':
            return self.dump(kwargs.get('obj'), kwargs.get('pretty', False))
        elif action == 'validate':
            return self.validate(kwargs.get('s', ''))
        elif action == 'pretty_print':
            return self.pretty_print(kwargs.get('s', ''))
        else:
            return self._error(f"Unknown action: {action}")

    def _error(self, msg: str) -> str:
        if self.lang == 'ar':
            return f"❌ خطأ: {msg}"
        return f"❌ Error: {msg}" 