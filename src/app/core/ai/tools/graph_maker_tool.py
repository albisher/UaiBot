"""
GraphMakerTool: Generates graphs from folder data using InformationCollectorAgent and matplotlib.
Outputs are saved in a dedicated work folder under Documents.
"""
from typing import Dict, Any
from src.app.core.ai.base_agent import BaseAgent, Agent
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol
import os
import matplotlib.pyplot as plt
from src.app.core.ai.agents.information_collector import InformationCollectorAgent

class GraphMakerTool(BaseAgent, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    """
    Tool for generating graphs from folder data.
    Uses InformationCollectorAgent and other agents/tools to collect info and matplotlib to generate graphs.
    Can consult with other agents to decide the best graph to generate.
    Implements A2A, MCP, and SmolAgents protocols for enhanced agent communication and coordination.
    """
    name = "graph_maker"
    description = "Tool for generating graphs from folder data"
    
    def __init__(self, work_dir=None, collector_agent=None, *args, **kwargs):
        super().__init__(name=self.name, *args, **kwargs)
        if work_dir is None:
            work_dir = os.path.expanduser("~/Documents/graph_maker")
        self.work_dir = work_dir
        os.makedirs(self.work_dir, exist_ok=True)
        self.collector_agent = collector_agent  # Do not instantiate by default
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()

    async def execute(self, command: str, params: dict = None, action: str = None) -> any:
        """Execute the agent's main functionality."""
        params = params or {}
        debug = params.get('debug', False)
        if debug:
            print(f"[DEBUG] GraphMakerTool received command: {command} with params: {params}")

        try:
            # Notify A2A protocol before execution
            await self.a2a_protocol.notify_action("execute", {"command": command, "params": params})
            # Use MCP for execution
            await self.mcp_protocol.execute_action("execute", {"command": command, "params": params})

            # Step 1: Collect info (consult collector agent)
            folder = params.get("folder", ".")
            if self.collector_agent is None:
                self.collector_agent = InformationCollectorAgent()
            file_list = await self.collector_agent.execute("list", {"directory": folder})
            if debug:
                print(f"[DEBUG] Files found: {file_list}")
            if not file_list or (isinstance(file_list, str) and not file_list.strip()):
                error_msg = f"No files found in {folder}"
                await self.a2a_protocol.notify_error("execute", error_msg)
                return error_msg

            # Step 2: Decide best graph (consultation logic, stub: file type distribution)
            ext_counts = {}
            for fname in file_list:
                ext = os.path.splitext(fname)[1][1:] or "no_ext"
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
            if debug:
                print(f"[DEBUG] File type counts: {ext_counts}")

            # Step 3: Generate graph
            fig, ax = plt.subplots()
            ax.bar(ext_counts.keys(), ext_counts.values())
            ax.set_title("File Type Distribution")
            ax.set_xlabel("Extension")
            ax.set_ylabel("Count")
            graph_path = os.path.join(self.work_dir, "file_type_distribution.png")
            plt.savefig(graph_path)
            plt.close(fig)
            if debug:
                print(f"[DEBUG] Graph saved to: {graph_path}")

            result = {"graph": graph_path, "summary": ext_counts}
            # Notify SmolAgent protocol after execution
            await self.smol_protocol.notify_completion("execute", result)
            return result

        except Exception as e:
            error_msg = f"Error in execute: {str(e)}"
            await self.a2a_protocol.notify_error("execute", error_msg)
            if debug:
                print(f"[DEBUG] Error: {error_msg}")
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