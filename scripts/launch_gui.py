#!/usr/bin/env python3
"""
UaiBot GUI launcher.
Uses the agentic core with A2A, MCP, and SmolAgents.
"""
import os
import sys
import asyncio
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from uaibot.core.ai.smol_agent import SmolAgent
from uaibot.core.ai.a2a_protocol import A2AProtocol, Message, TextContent, MessageRole, AgentCard, AgentCapability
from uaibot.core.ai.mcp_protocol import MCPProtocol, MCPTool
from uaibot.core.ai.channels.websocket_channel import WebSocketTool

class UaiBotGUI(SmolAgent):
    """UaiBot GUI agent implementation."""
    def __init__(self):
        super().__init__("uaibot_gui")
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self._setup_protocols()

    def _setup_protocols(self):
        """Set up A2A and MCP protocols."""
        # Register self as A2A server
        agent_card = AgentCard(
            agent_id=self.agent_id,
            name="UaiBot GUI",
            description="UaiBot graphical user interface agent",
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
                ),
                AgentCapability(
                    name="update_gui",
                    description="Update GUI elements",
                    parameters={"element": "string", "value": "any"},
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
        elif task == "update_gui":
            return await self._update_gui(params.get("element", ""), params.get("value"))
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
                conversation_id="gui_session",
                metadata={"agent_id": self.agent_id}
            )

            # Send message through A2A protocol
            response = await self.a2a_protocol.send_message(message)
            return {"response": response.content.text}
        except Exception as e:
            return {"error": str(e)}

    async def _update_gui(self, element: str, value: any) -> dict:
        """Update GUI elements."""
        try:
            # Handle different GUI element updates
            if element == "output":
                self.output_text.insert(tk.END, f"{value}\n")
                self.output_text.see(tk.END)
            elif element == "status":
                self.status_label.config(text=str(value))
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

class UaiBotApp:
    """UaiBot GUI application."""
    def __init__(self, root):
        self.root = root
        self.root.title("UaiBot")
        self.root.geometry("800x600")
        
        # Create agent
        self.agent = UaiBotGUI()
        
        # Create GUI elements
        self._create_widgets()
        
        # Set up event loop
        self.loop = asyncio.get_event_loop()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_widgets(self):
        """Create GUI widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create output text area
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create input field
        self.input_field = ttk.Entry(main_frame, width=70)
        self.input_field.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.input_field.bind("<Return>", self.on_input)
        
        # Create send button
        self.send_button = ttk.Button(main_frame, text="Send", command=self.on_input)
        self.send_button.grid(row=1, column=1, sticky=(tk.E))
        
        # Create status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

    async def process_input(self, user_input: str):
        """Process user input asynchronously."""
        # Update status
        await self.agent.execute("update_gui", {
            "element": "status",
            "value": "Processing..."
        })
        
        # Process input
        result = await self.agent.execute("process_input", {"input": user_input})
        
        # Update output
        if "error" in result:
            await self.agent.execute("update_gui", {
                "element": "output",
                "value": f"Error: {result['error']}"
            })
        else:
            await self.agent.execute("update_gui", {
                "element": "output",
                "value": f"Bot: {result['response']}"
            })
        
        # Update status
        await self.agent.execute("update_gui", {
            "element": "status",
            "value": "Ready"
        })

    def on_input(self, event=None):
        """Handle user input."""
        user_input = self.input_field.get()
        if user_input:
            # Clear input field
            self.input_field.delete(0, tk.END)
            
            # Add user input to output
            self.output_text.insert(tk.END, f"You: {user_input}\n")
            self.output_text.see(tk.END)
            
            # Process input
            asyncio.run_coroutine_threadsafe(
                self.process_input(user_input),
                self.loop
            )

    def on_closing(self):
        """Handle window closing."""
        self.loop.stop()
        self.root.destroy()

def main():
    """Main entry point."""
    root = tk.Tk()
    app = UaiBotApp(root)
    
    # Run event loop in a separate thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    def run_loop():
        loop.run_forever()
    
    import threading
    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()
    
    # Start GUI
    root.mainloop()

if __name__ == "__main__":
    main() 