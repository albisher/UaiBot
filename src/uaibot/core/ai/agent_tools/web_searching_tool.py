from uaibot.core.ai.tool_base import Tool

class WebSearchingTool(Tool):
    name = "web_searching"

    def execute(self, action: str, params: dict) -> any:
        if action == "search":
            return {"results": ["result1", "result2"]}
        else:
            return f"Unknown web searching tool action: {action}" 