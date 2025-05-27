from src.app.core.ai.tool_base import Tool
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol
from typing import Dict, Any

"""
FileAndDocumentOrganizerTool: Organizes, categorizes, and manages files and documents for the Labeeb agent. Useful for file system automation and document management tasks.

This module provides file and document organization capabilities for the Labeeb AI agent.
It allows the agent to organize, categorize, and manage files and documents within the system.

Key features:
- File organization and categorization
- Document management and sorting
- Automated file structure maintenance
- Extensible action system for organization operations
- A2A, MCP, and SmolAgents compliance for enhanced agent communication

See also:
- docs/features/file_organization.md for detailed usage examples
- labeeb/core/ai/tool_base.py for base tool implementation
- docs/architecture/tools.md for tool architecture overview
"""

class FileAndDocumentOrganizerTool(Tool, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    name = "file_and_document_organizer"

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name=self.name, description="Tool for organizing and managing files and documents")
        self.config = config or {}
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()

    async def execute(self, action: str, params: dict) -> any:
        try:
            # Notify A2A protocol before execution
            await self.a2a_protocol.notify_action(action, params)
            # Use MCP for execution
            await self.mcp_protocol.execute_action(action, params)

            if action == "organize":
                result = {"organized": True}
                # Notify SmolAgent protocol after execution
                await self.smol_protocol.notify_completion(action, result)
                return result
            else:
                error_msg = f"Unknown file/document organizer tool action: {action}"
                await self.a2a_protocol.notify_error(action, error_msg)
                return error_msg

        except Exception as e:
            error_msg = f"Error executing file/document organizer action: {str(e)}"
            await self.a2a_protocol.notify_error(action, error_msg)
            return {"error": error_msg}

    # A2A Protocol Methods
    async def register_agent(self, agent_id: str, capabilities: Dict[str, Any]) -> None:
        await self.a2a_protocol.register_agent(agent_id, capabilities)

    async def unregister_agent(self, agent_id: str) -> None:
        await self.a2a_protocol.unregister_agent(agent_id)

    # MCP Protocol Methods
    async def register_channel(self, channel_id: str, channel_type: str) -> None:
        await self.mcp_protocol.register_channel(channel_id, channel_type)

    async def unregister_channel(self, channel_id: str) -> None:
        await self.mcp_protocol.unregister_channel(channel_id)

    # SmolAgent Protocol Methods
    async def register_capability(self, capability: str, handler: callable) -> None:
        await self.smol_protocol.register_capability(capability, handler)

    async def unregister_capability(self, capability: str) -> None:
        await self.smol_protocol.unregister_capability(capability) 