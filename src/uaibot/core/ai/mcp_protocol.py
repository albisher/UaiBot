"""
Model Context Protocol (MCP) implementation.
Provides a universal, model-agnostic interface for AI agents to connect with external tools, data sources, and services.
Based on the open standard introduced by Anthropic.
"""
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import asyncio
from abc import ABC, abstractmethod
from .smol_agent import SmolAgent, AgentResult

@dataclass
class MCPRequest:
    """Standardized MCP request format based on JSON-RPC 2.0."""
    method: str
    params: Dict[str, Any]
    id: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    jsonrpc: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "method": self.method,
            "params": self.params,
            "id": self.id,
            "jsonrpc": self.jsonrpc
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPRequest':
        """Create request from dictionary."""
        return cls(**data)

@dataclass
class MCPResponse:
    """Standardized MCP response format based on JSON-RPC 2.0."""
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    jsonrpc: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "result": self.result,
            "error": self.error,
            "id": self.id,
            "jsonrpc": self.jsonrpc
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPResponse':
        """Create response from dictionary."""
        return cls(**data)

class MCPTool(ABC):
    """Abstract base class for MCP tools."""
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> MCPResponse:
        """Execute the tool with given parameters."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema describing its capabilities and parameters."""
        pass

class MCPProtocol:
    """
    Model Context Protocol implementation.
    Handles communication between AI agents and external tools/services.
    """
    def __init__(self, state_dir: Optional[str] = None):
        self.state_dir = state_dir or os.path.expanduser("~/Documents/uaibot/mcp")
        os.makedirs(self.state_dir, exist_ok=True)
        self.tools: Dict[str, MCPTool] = {}
        self.handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self._load_state()

    def register_tool(self, tool_id: str, tool: MCPTool):
        """Register a new MCP tool."""
        self.tools[tool_id] = tool
        self._save_state()

    def unregister_tool(self, tool_id: str):
        """Unregister an MCP tool."""
        if tool_id in self.tools:
            del self.tools[tool_id]
            self._save_state()

    def register_handler(self, tool_id: str, handler: Callable):
        """Register a response handler for a tool."""
        if tool_id not in self.handlers:
            self.handlers[tool_id] = []
        self.handlers[tool_id].append(handler)

    def unregister_handler(self, tool_id: str, handler: Callable):
        """Unregister a response handler from a tool."""
        if tool_id in self.handlers:
            self.handlers[tool_id].remove(handler)

    async def start(self):
        """Start the MCP protocol."""
        if self.running:
            return

        self.running = True
        # Start message processing loop
        asyncio.create_task(self._message_loop())

    async def stop(self):
        """Stop the MCP protocol."""
        if not self.running:
            return

        self.running = False

    async def call_tool(self, request: MCPRequest) -> MCPResponse:
        """Call a tool with the given request."""
        if request.method not in self.tools:
            return MCPResponse(
                error={
                    "code": -32601,
                    "message": f"Method {request.method} not found"
                },
                id=request.id
            )

        try:
            tool = self.tools[request.method]
            result = await tool.execute(request.params)
            return MCPResponse(
                result=result,
                id=request.id
            )
        except Exception as e:
            return MCPResponse(
                error={
                    "code": -32000,
                    "message": str(e)
                },
                id=request.id
            )

    async def _message_loop(self):
        """Main message processing loop."""
        while self.running:
            # Process any pending messages
            await asyncio.sleep(0.1)  # Prevent busy waiting

    def _save_state(self):
        """Save MCP protocol state to disk."""
        state = {
            "tools": {
                tool_id: tool.get_schema()
                for tool_id, tool in self.tools.items()
            },
            "handlers": {
                tool_id: [handler.__name__ for handler in handlers]
                for tool_id, handlers in self.handlers.items()
            }
        }
        
        with open(os.path.join(self.state_dir, "mcp_state.json"), 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        """Load MCP protocol state from disk."""
        state_path = os.path.join(self.state_dir, "mcp_state.json")
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                state = json.load(f)
                # Note: Tools and handlers need to be re-registered as they can't be serialized
                pass 