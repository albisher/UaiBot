from uaibot.core.ai.tool_base import Tool

class KeyboardInputTool(Tool):
    name = "keyboard"

    def execute(self, action: str, params: dict) -> any:
        if action == "type":
            return {"typed": params.get("text", "")}
        else:
            return f"Unknown keyboard input tool action: {action}" 