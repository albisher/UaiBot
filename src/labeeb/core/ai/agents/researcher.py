from labeeb.core.ai.agent import Agent
from labeeb.core.ai.agents.information_collector import InformationCollectorAgent
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol
from typing import Dict, Any

class ResearcherAgent(Agent, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    """
    Agent that plans research, guides the information collector, and writes reports.
    Decomposes research tasks and coordinates sub-agents/tools.
    Implements A2A, MCP, and SmolAgents protocols for enhanced agent communication.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector = InformationCollectorAgent()
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()

    async def research(self, topic: str) -> dict:
        """
        Plan research, collect info, and write a summary report.
        Implements protocol-based execution and error handling.
        """
        try:
            # Notify A2A protocol before research
            await self.a2a_protocol.notify_action("research", {"topic": topic})
            # Use MCP for research execution
            await self.mcp_protocol.execute_action("research", {"topic": topic})

            # Collect info
            info = await self.collector.collect_info(topic)
            
            # Summarize (simple for now)
            report = f"Research Report on '{topic}':\n"
            for k, v in info.items():
                report += f"\n[{k.upper()}]\n{v}\n"
            
            result = {"topic": topic, "report": report, "raw": info}
            
            # Notify SmolAgent protocol after research
            await self.smol_protocol.notify_completion("research", result)
            return result

        except Exception as e:
            error_msg = f"Error in research: {str(e)}"
            await self.a2a_protocol.notify_error("research", error_msg)
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