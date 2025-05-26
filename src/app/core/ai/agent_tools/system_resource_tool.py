from labeeb.core.ai.tool_base import Tool
import psutil

class SystemResourceTool(Tool):
    name = "system"

    def execute(self, action: str, params: dict) -> any:
        if action == "info":
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage("/")._asdict()
            }
        else:
            return f"Unknown system resource tool action: {action}" 