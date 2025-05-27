from labeeb.core.ai.tool_base import BaseTool
from datetime import datetime

class DateTimeTool(BaseTool):
    def __init__(self, config=None):
        super().__init__(
            name="datetime",
            description="Tool for date and time information",
            config=config or {}
        )

    async def _execute_command(self, command: str, args=None):
        if command == "now":
            return {"datetime": datetime.now().isoformat()}
        else:
            return {"error": f"Unknown datetime tool command: {command}"} 