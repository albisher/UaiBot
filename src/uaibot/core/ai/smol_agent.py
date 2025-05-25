"""
SmolAgent: A minimal, efficient agent implementation based on the SmolAgents pattern.
Provides core agent functionality with minimal memory/state footprint.
"""
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

@dataclass
class AgentState:
    """Minimal agent state for tracking execution context."""
    agent_id: str
    current_step: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    memory: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def update(self, **kwargs):
        """Update agent state with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()

    def add_to_memory(self, entry: Dict[str, Any]):
        """Add an entry to agent memory."""
        self.memory.append({
            "timestamp": datetime.utcnow().isoformat(),
            "step": self.current_step,
            **entry
        })
        self.current_step += 1

    def get_memory(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get agent memory entries, optionally limited to the most recent ones."""
        if limit is None:
            return self.memory
        return self.memory[-limit:]

    def clear_memory(self):
        """Clear agent memory."""
        self.memory = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary."""
        return {
            "agent_id": self.agent_id,
            "current_step": self.current_step,
            "context": self.context,
            "memory": self.memory,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """Create agent state from dictionary."""
        return cls(**data)

@dataclass
class AgentResult:
    """Standardized agent result format."""
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
        return cls(**data)

class SmolAgent:
    """
    Base agent class implementing the SmolAgents pattern.
    Provides minimal, efficient agent functionality with standardized interfaces.
    """
    def __init__(self, agent_id: str, state_dir: Optional[str] = None):
        self.agent_id = agent_id
        self.state_dir = state_dir or os.path.expanduser("~/Documents/uaibot/agents")
        os.makedirs(self.state_dir, exist_ok=True)
        self.state = self._load_state() or AgentState(agent_id=agent_id)
        self.tools: Dict[str, Any] = {}

    def _get_state_path(self) -> str:
        """Get path to agent state file."""
        return os.path.join(self.state_dir, f"{self.agent_id}.json")

    def _save_state(self):
        """Save agent state to disk."""
        with open(self._get_state_path(), 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2)

    def _load_state(self) -> Optional[AgentState]:
        """Load agent state from disk."""
        state_path = self._get_state_path()
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                return AgentState.from_dict(json.load(f))
        return None

    def register_tool(self, name: str, tool: Any):
        """Register a tool with the agent."""
        self.tools[name] = tool
        self.state.add_to_memory({
            "action": "register_tool",
            "tool": name
        })
        self._save_state()

    def execute(self, action: str, params: Dict[str, Any]) -> AgentResult:
        """
        Execute an action with the given parameters.
        Returns a standardized AgentResult.
        """
        try:
            # Update context
            self.state.context.update(params)
            
            # Execute action
            if action in self.tools:
                result = self.tools[action].execute(params)
                self.state.add_to_memory({
                    "action": action,
                    "params": params,
                    "result": result
                })
                self._save_state()
                return AgentResult(success=True, data=result)
            
            # Handle built-in actions
            if action == "get_state":
                return AgentResult(success=True, data=self.state.to_dict())
            elif action == "clear_memory":
                self.state.clear_memory()
                self._save_state()
                return AgentResult(success=True, data="Memory cleared")
            
            return AgentResult(
                success=False,
                data=None,
                error=f"Unknown action: {action}"
            )
            
        except Exception as e:
            self.state.add_to_memory({
                "action": action,
                "params": params,
                "error": str(e)
            })
            self._save_state()
            return AgentResult(
                success=False,
                data=None,
                error=str(e)
            )

    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        return self.state.to_dict()

    def clear_memory(self):
        """Clear agent memory."""
        self.state.clear_memory()
        self._save_state()

    def get_memory(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get agent memory entries."""
        return self.state.get_memory(limit) 