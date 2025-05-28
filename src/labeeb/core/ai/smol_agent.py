"""
SmolAgent Implementation.

This module implements the SmolAgent pattern for minimal, efficient agent implementation.
The SmolAgent pattern emphasizes:
- Minimal dependencies
- Clear state management
- Efficient tool usage
- Simple but powerful interfaces
- Easy testing and debugging

Key Features:
- State Management: Clear state transitions and persistence
- Tool Integration: Simple tool registration and execution
- Error Handling: Robust error handling and recovery
- Testing: Easy to test with clear interfaces
- Debugging: Built-in logging and state inspection

Agent Lifecycle:
1. Initialize agent with optional state directory
2. Register tools and handlers
3. Execute actions and update state
4. Persist state when needed
5. Clean up resources

State Management:
- In-memory state for active operations
- Persistent state for long-term storage
- Clear state transitions
- State validation and recovery

Tool Integration:
- Simple tool registration
- Tool discovery and execution
- Tool result handling
- Tool error recovery
"""

from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import os
import asyncio
from pathlib import Path

class SmolAgentProtocol(Protocol):
    """Protocol for SmolAgent compliance."""
    name: str
    state: Any
    def register_tool(self, tool: Any): ...
    def unregister_tool(self, tool_name: str): ...
    async def execute_tool(self, tool_name: str, **kwargs) -> Any: ...

@dataclass
class AgentState:
    """Agent state structure."""
    name: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tools: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tools": self.tools,
            "context": self.context,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """Create state from dictionary."""
        return cls(
            name=data["name"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            tools=data["tools"],
            context=data["context"],
            history=data["history"]
        )

@dataclass
class AgentResult:
    """Result of an agent action."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResult':
        """Create result from dictionary."""
        return cls(
            success=data["success"],
            data=data["data"],
            error=data.get("error"),
            metadata=data.get("metadata", {})
        )

class Tool(Protocol):
    """Protocol defining the interface for tools."""
    name: str
    description: str
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        ...

class SmolAgent:
    """
    Base class for SmolAgent implementation.
    
    This class provides:
    - State management
    - Tool integration
    - Error handling
    - Logging
    - Testing support
    """
    
    def __init__(self, name: str, state_dir: Optional[str] = None):
        """Initialize the agent."""
        self.name = name
        self.state_dir = state_dir or os.path.expanduser("~/Documents/labeeb/agents")
        os.makedirs(self.state_dir, exist_ok=True)
        
        self.logger = logging.getLogger(f"SmolAgent.{name}")
        self.state = AgentState(name=name)
        self.tools: Dict[str, Tool] = {}
        
        # Load state if exists
        self._load_state()
    
    def register_tool(self, tool: Tool):
        """Register a tool with the agent."""
        self.tools[tool.name] = tool
        self.state.tools.append(tool.name)
        self.state.updated_at = datetime.utcnow().isoformat()
        self._save_state()
        self.logger.info(f"Registered tool: {tool.name}")
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool from the agent."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.state.tools.remove(tool_name)
            self.state.updated_at = datetime.utcnow().isoformat()
            self._save_state()
            self.logger.info(f"Unregistered tool: {tool_name}")
    
    async def execute_tool(self, tool_name: str, **kwargs) -> AgentResult:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters for the tool
            
        Returns:
            AgentResult: Result of the tool execution
            
        Raises:
            ToolNotFoundError: If tool not found
            ToolExecutionError: If tool execution fails
        """
        if tool_name not in self.tools:
            raise ToolNotFoundError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        
        try:
            # Execute tool
            result = await tool.execute(**kwargs)
            
            # Create success result
            agent_result = AgentResult(
                success=True,
                data=result,
                metadata={"tool": tool_name}
            )
            
            # Update state
            self.state.history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "tool": tool_name,
                "params": kwargs,
                "result": agent_result.to_dict()
            })
            self.state.updated_at = datetime.utcnow().isoformat()
            self._save_state()
            
            return agent_result
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            
            # Create error result
            agent_result = AgentResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"tool": tool_name}
            )
            
            # Update state
            self.state.history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "tool": tool_name,
                "params": kwargs,
                "result": agent_result.to_dict()
            })
            self.state.updated_at = datetime.utcnow().isoformat()
            self._save_state()
            
            raise ToolExecutionError(f"Failed to execute tool {tool_name}: {str(e)}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        return self.state.to_dict()
    
    def clear_state(self):
        """Clear agent state."""
        self.state = AgentState(name=self.name)
        self._save_state()
        self.logger.info("Cleared agent state")
    
    def _save_state(self):
        """Save agent state to disk."""
        state_path = os.path.join(self.state_dir, f"{self.name}.json")
        with open(state_path, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2)
    
    def _load_state(self):
        """Load agent state from disk."""
        state_path = os.path.join(self.state_dir, f"{self.name}.json")
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                self.state = AgentState.from_dict(json.load(f))

class SmolAgentError(Exception):
    """Base class for SmolAgent errors."""
    pass

class ToolNotFoundError(SmolAgentError):
    """Raised when a tool is not found."""
    pass

class ToolExecutionError(SmolAgentError):
    """Raised when a tool execution fails."""
    pass 