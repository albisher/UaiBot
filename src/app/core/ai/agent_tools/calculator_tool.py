from labeeb.core.ai.tool_base import Tool

class CalculatorTool(Tool):
    name = "calculator"

    def execute(self, action: str, params: dict) -> any:
        if action == "eval":
            expr = params.get("expression")
            try:
                return eval(expr, {"__builtins__": {}})
            except Exception as e:
                return f"Calculator error: {e}"
        else:
            return f"Unknown calculator tool action: {action}" 