from src.app.core.ai.agent import Agent
from src.app.core.ai.tools.system_awareness_tool import SystemAwarenessTool
from src.app.core.ai.tools.web_searching_tool import WebSearchingTool
from src.app.core.ai.tools.file_tool import FileTool
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol
from typing import Dict, Any

class InformationCollectorAgent(Agent, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    """
    Agent that gathers data from tools (system, web, files).
    Plans and executes information collection workflows.
    Implements A2A, MCP, and SmolAgents protocols for enhanced agent communication.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_tool = SystemAwarenessTool()
        self.web_search_tool = WebSearchingTool()
        self.file_tool = FileTool()
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()

    async def collect_info(self, query: str) -> dict:
        """
        Collect information from system, web, and files based on query.
        Implements protocol-based execution and error handling.
        """
        try:
            # Notify A2A protocol before collection
            await self.a2a_protocol.notify_action("collect_info", {"query": query})
            # Use MCP for collection execution
            await self.mcp_protocol.execute_action("collect_info", {"query": query})

            results = {}
            # System info
            if "system" in query or "cpu" in query or "memory" in query:
                results["system"] = await self.system_tool.execute("info", {})
            # Web search
            if "web" in query or "search" in query or "online" in query:
                results["web_search"] = await self.web_search_tool.execute("search", {"query": query})
            # File listing
            if "file" in query or "document" in query or "list" in query:
                results["files"] = await self.file_tool.execute("list", {"directory": "."})

            # Notify SmolAgent protocol after collection
            await self.smol_protocol.notify_completion("collect_info", results)
            return results

        except Exception as e:
            error_msg = f"Error in information collection: {str(e)}"
            await self.a2a_protocol.notify_error("collect_info", error_msg)
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