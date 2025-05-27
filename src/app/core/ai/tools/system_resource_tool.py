from src.app.core.ai.tool_base import BaseTool
import psutil

class SystemResourceTool(BaseTool):
    def __init__(self, config=None):
        super().__init__(
            name="system",
            description="Tool for system resource information",
            config=config or {}
        )

    async def _execute_command(self, command: str, args=None):
        if command == "info":
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage("/")._asdict()
            }
        else:
            return {"error": f"Unknown system resource tool command: {command}"} 