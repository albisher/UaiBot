from uaibot.core.ai.tool_base import Tool

class WeatherTool(Tool):
    name = "weather"

    def execute(self, action: str, params: dict) -> any:
        if action == "current":
            return {"weather": "sunny", "temp_c": 25}
        else:
            return f"Unknown weather tool action: {action}" 