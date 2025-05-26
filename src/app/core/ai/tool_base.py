"""
Base tool implementation with A2A, MCP, and SmolAgents compliance.

This module provides the base class for all agent tools, ensuring compliance with:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime
import logging
from .a2a_protocol import A2AProtocol, Message, MessageRole
from .mcp_protocol import MCPProtocol, MCPRequest, MCPResponse
from .smol_agent import SmolAgent, AgentState, AgentResult

@dataclass
class ToolState:
    """State management for tools following SmolAgents pattern."""
    name: str
    initialized: bool = False
    last_used: Optional[str] = None
    usage_count: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseTool:
    """Base class for all agent tools with A2A, MCP, and SmolAgents compliance."""
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the base tool.
        
        Args:
            name: Tool name
            description: Tool description
            config: Optional configuration dictionary
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.state = ToolState(name=name)
        self.logger = logging.getLogger(f"Tool.{name}")
        
        # Initialize protocols
        self._a2a_protocol = A2AProtocol()
        self._mcp_protocol = MCPProtocol()
        
        # Register tool with protocols
        self._register_with_protocols()
    
    def _register_with_protocols(self):
        """Register tool with A2A and MCP protocols."""
        self._a2a_protocol.register_tool(self)
        self._mcp_protocol.register_tool(self)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.state.initialized = True
            self.state.last_used = datetime.utcnow().isoformat()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {e}")
            self.state.error_count += 1
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self.state.initialized = False
            self.state.last_used = datetime.utcnow().isoformat()
        except Exception as e:
            self.logger.error(f"Error cleaning up {self.name}: {e}")
            self.state.error_count += 1
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        return {
            'a2a_compliant': True,
            'mcp_compliant': True,
            'smol_agent_compliant': True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        return {
            'name': self.name,
            'description': self.description,
            'initialized': self.state.initialized,
            'last_used': self.state.last_used,
            'usage_count': self.state.usage_count,
            'error_count': self.state.error_count,
            'metadata': self.state.metadata
        }
    
    async def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command using this tool.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if not self.state.initialized:
            return {'error': 'Tool not initialized'}
        
        try:
            self.state.usage_count += 1
            self.state.last_used = datetime.utcnow().isoformat()
            
            # Create A2A message for command execution
            message = Message(
                role=MessageRole.TOOL,
                content=f"Executing command: {command}",
                metadata={'command': command, 'args': args}
            )
            
            # Create MCP request for command execution
            request = MCPRequest(
                tool_name=self.name,
                command=command,
                parameters=args or {}
            )
            
            # Execute command and get result
            result = await self._execute_command(command, args)
            
            # Update state
            self.state.metadata['last_result'] = result
            
            return result
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            self.state.error_count += 1
            return {'error': str(e)}
    
    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific command. Override this method in subclasses.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        raise NotImplementedError("Subclasses must implement _execute_command")
    
    async def handle_a2a_message(self, message: Message) -> Message:
        """Handle an A2A message.
        
        Args:
            message: A2A message to handle
            
        Returns:
            Message: Response message
        """
        try:
            if message.role == MessageRole.TOOL:
                result = await self.execute(
                    message.metadata.get('command', ''),
                    message.metadata.get('args')
                )
                return Message(
                    role=MessageRole.TOOL,
                    content="Command executed successfully",
                    metadata={'result': result}
                )
            return Message(
                role=MessageRole.TOOL,
                content="Unsupported message role",
                metadata={'error': 'Unsupported message role'}
            )
        except Exception as e:
            self.logger.error(f"Error handling A2A message: {e}")
            return Message(
                role=MessageRole.TOOL,
                content="Error handling message",
                metadata={'error': str(e)}
            )
    
    async def handle_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Handle an MCP request.
        
        Args:
            request: MCP request to handle
            
        Returns:
            MCPResponse: Response to the request
        """
        try:
            result = await self.execute(request.command, request.parameters)
            return MCPResponse(
                success=True,
                data=result
            )
        except Exception as e:
            self.logger.error(f"Error handling MCP request: {e}")
            return MCPResponse(
                success=False,
                error=str(e)
            ) 