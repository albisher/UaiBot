"""
Base Agent Implementation.

This module provides the core interfaces and base classes for all agents in the Labeeb system.
It follows the SmolAgent pattern and implements A2A, MCP, and SmolAgent protocols.

Key Features:
- Base Agent class with common functionality
- Protocol definitions for agent communication
- Shared interfaces for tool integration
- State management and persistence
"""

from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import os
from pathlib import Path

class Agent(Protocol):
    """Base protocol for all agents in the system."""
    name: str
    description: str
    
    async def execute(self, **kwargs) -> Any:
        """Execute the agent's main functionality."""
        ...

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

class BaseAgent:
    """
    Base class for all agents in the system.
    
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
        
        self.logger = logging.getLogger(f"Agent.{name}")
        self.state = AgentState(name=name)
        self.tools: Dict[str, Any] = {}
        
        # Load state if exists
        self._load_state()
    
    def register_tool(self, tool: Any):
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

class AgentError(Exception):
    """Base class for agent errors."""
    pass

class ToolNotFoundError(AgentError):
    """Raised when a tool is not found."""
    pass

class ToolExecutionError(AgentError):
    """Raised when a tool execution fails."""
    pass 