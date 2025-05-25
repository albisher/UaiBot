from uaibot.core.ai.tool_base import Tool
from datetime import datetime

class DateTimeTool(Tool):
    name = "datetime"

    def execute(self, action: str, params: dict) -> any:
        if action == "now":
            return datetime.now().isoformat()
        else:
            return f"Unknown datetime tool action: {action}" 