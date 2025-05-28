from labeeb.core.ai.agent import Agent
from labeeb.core.ai.a2a_protocol import A2AProtocol
from labeeb.core.ai.mcp_protocol import MCPProtocol
from labeeb.core.ai.smol_agent import SmolAgentProtocol
from typing import Dict, Any

class ResearchEvaluatorAgent(Agent, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    """
    Agent that evaluates research quality and checks completeness.
    Reviews outputs and provides feedback or scores.
    Implements A2A, MCP, and SmolAgents protocols for enhanced agent communication.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()

    async def evaluate(self, research_report: dict) -> dict:
        """
        Evaluate the research report for quality and completeness.
        Implements protocol-based execution and error handling.
        """
        try:
            # Notify A2A protocol before evaluation
            await self.a2a_protocol.notify_action("evaluate", {"report": research_report})
            # Use MCP for evaluation execution
            await self.mcp_protocol.execute_action("evaluate", {"report": research_report})

            report = research_report.get("report", "")
            raw = research_report.get("raw", {})
            score = 0
            feedback = []
            
            # Check for key sections
            for section in ["system", "web_search", "files"]:
                if section in raw and raw[section]:
                    score += 1
                else:
                    feedback.append(f"Missing or empty section: {section}")
            
            # Simple quality check
            if len(report) > 100:
                score += 1
            else:
                feedback.append("Report is too short.")

            result = {"score": score, "feedback": feedback, "summary": report[:200]}
            
            # Notify SmolAgent protocol after evaluation
            await self.smol_protocol.notify_completion("evaluate", result)
            return result

        except Exception as e:
            error_msg = f"Error in research evaluation: {str(e)}"
            await self.a2a_protocol.notify_error("evaluate", error_msg)
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