from uaibot.core.ai.tool_base import Tool

class MouseControlTool(Tool):
    name = "mouse"

    def execute(self, action: str, params: dict) -> any:
        if action == "move":
            return {"moved": True, "x": params.get("x"), "y": params.get("y")}
        else:
            return f"Unknown mouse control tool action: {action}" 