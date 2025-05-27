import pyautogui
from src.app.core.ai.tool_base import BaseTool
from typing import Dict, Any, Optional

class MouseTool(BaseTool):
    name = "mouse"
    description = "Tool for mouse movement and clicking."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="mouse", description=self.description)
        self.config = config or {}

    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        args = args or {}
        if command == "move":
            x = args.get("x")
            y = args.get("y")
            if x is None or y is None:
                return {"error": "Missing x or y for move command"}
            try:
                pyautogui.moveTo(int(x), int(y))
                return {"status": "success", "action": "move", "x": x, "y": y}
            except Exception as e:
                return {"error": str(e)}
        elif command == "click":
            count = args.get("count", 1)
            try:
                pyautogui.click(clicks=int(count))
                return {"status": "success", "action": "click", "count": count}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": f"Unknown mouse command: {command}"} 