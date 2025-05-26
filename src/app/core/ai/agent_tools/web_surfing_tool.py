from labeeb.core.ai.tool_base import Tool

class WebSurfingTool(Tool):
    name = "web_surfing"

    def execute(self, action: str, params: dict) -> any:
        if action == "surf":
            return {"surfed": params.get("url", "")}
        else:
            return f"Unknown web surfing tool action: {action}" 