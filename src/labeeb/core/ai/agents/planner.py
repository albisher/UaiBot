from labeeb.core.ai.agent import Agent, MultiStepPlan, PlanStep
from labeeb.core.ai.agents.researcher import ResearcherAgent
from labeeb.core.ai.agents.information_collector import InformationCollectorAgent
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol
from typing import Dict, Any, Optional, Union

class PlannerAgent(Agent, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    """
    PlannerAgent: Decomposes high-level commands into multi-step plans.
    Can ask for research (via ResearcherAgent) or use search (via InformationCollectorAgent).
    Implements A2A, MCP, and SmolAgents protocols for enhanced agent communication.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.researcher = ResearcherAgent()
        self.collector = InformationCollectorAgent()
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()

    async def plan(self, command: str, params: Dict[str, Any]) -> Union[Dict[str, Any], MultiStepPlan]:
        """
        Decompose a command into a MultiStepPlan or delegate to sub-agents.
        """
        try:
            # Notify A2A protocol before planning
            await self.a2a_protocol.notify_action("plan", {"command": command, "params": params})
            # Use MCP for planning
            await self.mcp_protocol.execute_action("plan", {"command": command, "params": params})

            lc = command.lower()
            result = None
            if "research" in lc:
                result = {"agent": "researcher", "action": "research", "params": {"topic": command}}
            elif "search" in lc or "find" in lc:
                result = {"agent": "information_collector", "action": "collect_info", "params": {"query": command}}
            else:
                # Fallback: single-step echo
                result = {"tool": "echo", "action": "say", "params": {"text": command}}

            # Notify SmolAgent protocol after planning
            await self.smol_protocol.notify_completion("plan", result)
            return result

        except Exception as e:
            error_msg = f"Error in planning: {str(e)}"
            await self.a2a_protocol.notify_error("plan", error_msg)
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