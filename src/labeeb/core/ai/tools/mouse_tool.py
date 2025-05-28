import pyautogui
from src.app.core.ai.tool_base import BaseTool
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol
from typing import Dict, Any, Optional

class MouseTool(BaseTool, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    name = "mouse"
    description = "Tool for mouse movement and clicking."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="mouse", description=self.description)
        self.config = config or {}
        self._agents = {}  # For A2A protocol
        self._channels = {}  # For MCP protocol
        self._capabilities = {}  # For SmolAgent protocol

    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        args = args or {}
        if command == "move":
            x = args.get("x")
            y = args.get("y")
            if x is None or y is None:
                return {"error": "Missing x or y for move command"}
            try:
                # Notify A2A protocol before action
                await self.notify_action("mouse_move", {"x": x, "y": y})
                # Execute the actual movement
                pyautogui.moveTo(int(x), int(y))
                # Notify SmolAgent protocol after action
                await self.notify_completion("mouse_move", {"x": x, "y": y})
                return {"status": "success", "action": "move", "x": x, "y": y}
            except Exception as e:
                await self.notify_error("mouse_move", str(e))
                return {"error": str(e)}
        elif command == "click":
            count = args.get("count", 1)
            try:
                # Notify A2A protocol before action
                await self.notify_action("mouse_click", {"count": count})
                # Execute the actual click
                pyautogui.click(clicks=int(count))
                # Notify SmolAgent protocol after action
                await self.notify_completion("mouse_click", {"count": count})
                return {"status": "success", "action": "click", "count": count}
            except Exception as e:
                await self.notify_error("mouse_click", str(e))
                return {"error": str(e)}
        else:
            return {"error": f"Unknown mouse command: {command}"}

    # A2A Protocol Methods
    async def register_agent(self, agent_id: str, capabilities: Dict[str, Any]) -> None:
        self._agents[agent_id] = capabilities

    async def unregister_agent(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)

    async def notify_action(self, action: str, details: Dict[str, Any]) -> None:
        for agent_id, capabilities in self._agents.items():
            if action in capabilities:
                # Notify agent of action
                pass

    async def notify_error(self, action: str, error: str) -> None:
        for agent_id, capabilities in self._agents.items():
            if action in capabilities:
                # Notify agent of error
                pass

    # MCP Protocol Methods
    async def register_channel(self, channel_id: str, channel_type: str) -> None:
        self._channels[channel_id] = channel_type

    async def unregister_channel(self, channel_id: str) -> None:
        self._channels.pop(channel_id, None)

    # SmolAgent Protocol Methods
    async def register_capability(self, capability: str, handler: callable) -> None:
        self._capabilities[capability] = handler

    async def unregister_capability(self, capability: str) -> None:
        self._capabilities.pop(capability, None)

    async def notify_completion(self, action: str, result: Dict[str, Any]) -> None:
        if action in self._capabilities:
            handler = self._capabilities[action]
            await handler(result) 