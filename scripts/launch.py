#!/usr/bin/env python3
"""
UaiBot CLI launcher.
Uses the agentic core with A2A, MCP, and SmolAgents.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from uaibot.core.ai.smol_agent import SmolAgent
from uaibot.core.ai.a2a_protocol import A2AProtocol, Message, TextContent, MessageRole, AgentCard, AgentCapability
from uaibot.core.ai.mcp_protocol import MCPProtocol, MCPTool
from uaibot.core.ai.channels.websocket_channel import WebSocketTool

class UaiBotCLI(SmolAgent):
    """UaiBot CLI agent implementation."""
    def __init__(self):
        super().__init__("uaibot_cli")
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self._setup_protocols()

    def _setup_protocols(self):
        """Set up A2A and MCP protocols."""
        # Register self as A2A server
        agent_card = AgentCard(
            agent_id=self.agent_id,
            name="UaiBot CLI",
            description="UaiBot command-line interface agent",
            capabilities=[
                AgentCapability(
                    name="execute_command",
                    description="Execute shell commands",
                    parameters={"command": "string"},
                    required=True
                ),
                AgentCapability(
                    name="process_input",
                    description="Process user input",
                    parameters={"input": "string"},
                    required=True
                )
            ]
        )
        self.a2a_protocol.register_agent(self, agent_card)

        # Register WebSocket tool
        ws_tool = WebSocketTool("ws://localhost:8765", "websocket")
        self.mcp_protocol.register_tool("websocket", ws_tool)

    async def execute(self, task: str, params: dict = None) -> dict:
        """Execute a task."""
        if task == "execute_command":
            return await self._execute_command(params.get("command", ""))
        elif task == "process_input":
            return await self._process_input(params.get("input", ""))
        else:
            return {"error": f"Unknown task: {task}"}

    async def _execute_command(self, command: str) -> dict:
        """Execute a shell command."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else ""
            }
        except Exception as e:
            return {"error": str(e)}

    async def _process_input(self, user_input: str) -> dict:
        """Process user input."""
        try:
            # Create A2A message
            message = Message(
                content=TextContent(text=user_input),
                role=MessageRole.USER,
                conversation_id="cli_session",
                metadata={"agent_id": self.agent_id}
            )

            # Send message through A2A protocol
            response = await self.a2a_protocol.send_message(message)
            return {"response": response.content.text}
        except Exception as e:
            return {"error": str(e)}

async def main():
    """Main entry point."""
    cli = UaiBotCLI()
    print("UaiBot CLI started. Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() == "exit":
                break

            result = await cli.execute("process_input", {"input": user_input})
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(result["response"])

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 