"""
WebSocket implementation for Model Context Protocol.
Provides real-time communication over WebSocket connections using JSON-RPC 2.0.
"""
from typing import Any, Dict, Optional
import asyncio
import json
import websockets
from ..mcp_protocol import MCPTool, MCPRequest, MCPResponse

class WebSocketTool(MCPTool):
    """
    WebSocket tool implementation for MCP.
    Handles real-time communication over WebSocket connections.
    """
    def __init__(self, url: str, tool_id: str):
        self.url = url
        self.tool_id = tool_id
        self.websocket = None
        self.connected = False
        self._message_queue = asyncio.Queue()

    async def execute(self, params: Dict[str, Any]) -> MCPResponse:
        """Execute the WebSocket tool with given parameters."""
        if not self.connected or not self.websocket:
            return MCPResponse(
                error={
                    "code": -32000,
                    "message": "WebSocket not connected"
                }
            )

        try:
            # Create MCP request
            request = MCPRequest(
                method=self.tool_id,
                params=params
            )

            # Send request
            await self.websocket.send(json.dumps(request.to_dict()))

            # Wait for response
            response_data = await self._message_queue.get()
            return MCPResponse.from_dict(response_data)
        except Exception as e:
            return MCPResponse(
                error={
                    "code": -32000,
                    "message": str(e)
                }
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get the WebSocket tool's schema."""
        return {
            "name": self.tool_id,
            "description": "WebSocket communication tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to send"
                    }
                },
                "required": ["message"]
            }
        }

    async def connect(self) -> bool:
        """Connect to the WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            # Start message receiving loop
            asyncio.create_task(self._receive_loop())
            return True
        except Exception as e:
            print(f"Failed to connect to WebSocket server: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from the WebSocket server."""
        if self.websocket:
            try:
                await self.websocket.close()
                self.connected = False
                return True
            except Exception as e:
                print(f"Failed to disconnect from WebSocket server: {e}")
                return False
        return True

    async def _receive_loop(self):
        """Background loop for receiving messages."""
        while self.connected and self.websocket:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                response = MCPResponse.from_dict(data)
                await self._message_queue.put(response)
            except websockets.exceptions.ConnectionClosed:
                self.connected = False
                break
            except Exception as e:
                print(f"Error in WebSocket receive loop: {e}")
                await asyncio.sleep(1)  # Prevent busy waiting on error 