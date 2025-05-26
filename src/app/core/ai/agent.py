"""
Labeeb AI Agent

This module defines the base agent class for Labeeb's AI system.

This module implements the core agent functionality following:
- SmolAgents pattern for minimal, efficient agent implementation
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support

Agents/Tools:
- EchoTool: Echoes text
- FileTool: File operations (create, read, etc.)
- SystemResourceTool: System resource info (CPU, memory, disk)
- DateTimeTool: Returns current date/time
- WeatherTool: Returns weather info (stub)
- CalculatorTool: Evaluates math expressions
- OllamaLLMPlanner: Uses Ollama (e.g., gemma3:4b) for plan decomposition

Agent Lifecycle:
1. Initialize agent with memory and tool registry.
2. Receive a command/goal via `plan_and_execute`.
3. Agent plans steps (optionally using LLM or planner).
4. Agent invokes tools to perform actions (supports multi-step workflows).
5. Agent updates memory/history after each step.
6. Agent returns result/output.

Workflow Orchestration:
- Supports plan decomposition into multiple steps (sequential, parallel, conditional).
- Each step is executed and tracked in memory.
- Parallel/conditional logic is stubbed for future extension.
"""
from typing import Any, Dict, List, Optional, Callable, Union, Protocol, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from app.core.ai.agent_tools.file_tool import FileTool
from app.core.ai.agent_tools.system_resource_tool import SystemResourceTool
from app.core.ai.agent_tools.datetime_tool import DateTimeTool
from app.core.ai.agent_tools.weather_tool import WeatherTool
from app.core.ai.agent_tools.calculator_tool import CalculatorTool
from app.core.ai.agent_tools.system_awareness_tool import SystemAwarenessTool
from app.core.ai.agent_tools.mouse_control_tool import MouseControlTool
from app.core.ai.agent_tools.keyboard_input_tool import KeyboardInputTool
from app.core.ai.agent_tools.browser_automation_tool import BrowserAutomationTool
from app.core.ai.agent_tools.web_surfing_tool import WebSurfingTool
from app.core.ai.agent_tools.web_searching_tool import WebSearchingTool
from app.core.ai.agent_tools.file_and_document_organizer_tool import FileAndDocumentOrganizerTool
from app.core.ai.agent_tools.code_path_updater_tool import CodePathUpdaterTool
import requests
import json
from app.core.ai.tool_base import Tool
import logging
import os
from pathlib import Path
from .a2a_protocol import A2AProtocol, Message, MessageRole
from .mcp_protocol import MCPProtocol, MCPRequest, MCPResponse
from .smol_agent import SmolAgent, AgentState, AgentResult

def safe_path(filename: str, category: str = "test") -> str:
    """
    Ensure files are saved in the correct directory based on category.
    category: 'test', 'log', 'state', etc.
    """
    base_dirs = {
        "test": "tests/fixtures/",
        "log": "log/",
        "state": "src/labeeb/state/",
        "core": "src/labeeb/core/"
    }
    if category in base_dirs:
        os.makedirs(base_dirs[category], exist_ok=True)
        return os.path.join(base_dirs[category], filename)
    return filename

@dataclass
class Tool(Protocol):
    """Protocol defining the interface for tools."""
    name: str
    description: str
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        ...

@dataclass
class ToolRegistry:
    """
    Registry for agent tools. Allows agents to discover and invoke tools by name.
    Implements A2A and MCP protocols for tool discovery and invocation.
    """
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._a2a_protocol = A2AProtocol()
        self._mcp_protocol = MCPProtocol()

    def register(self, tool: Tool):
        """Register a tool with the registry."""
        self._tools[tool.name] = tool
        # Register tool with A2A and MCP protocols
        self._a2a_protocol.register_tool(tool)
        self._mcp_protocol.register_tool(tool)

    def get(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool with the given parameters."""
        tool = self.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        return await tool.execute(**params)

@dataclass
class AgentMemory:
    """Rich memory/state for multi-step workflows."""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_step(self, command: str, action: str, params: Dict[str, Any], result: Any):
        """Add a step to the memory."""
        self.steps.append({
            "timestamp": datetime.utcnow().isoformat(),
            "command": command,
            "action": action,
            "params": params,
            "result": result
        })
        self.updated_at = datetime.utcnow().isoformat()

    def get_steps(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get memory steps, optionally limited to the most recent ones."""
        if limit is None:
            return self.steps
        return self.steps[-limit:]

    def clear(self):
        """Clear memory."""
        self.steps = []
        self.context = {}
        self.updated_at = datetime.utcnow().isoformat()

@dataclass
class PlanStep:
    """Single step in a multi-step plan."""
    action: str
    parameters: Dict[str, Any]
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None

@dataclass
class MultiStepPlan:
    """Structure for multi-step plans."""
    steps: List[PlanStep]
    parallel: bool = False

class LLMPlanner:
    """
    Stub for an LLM-based planner. In a real system, this would call an LLM to interpret natural language and return a plan.
    """
    def plan(self, command: str, params: Dict[str, Any]) -> Union[Dict[str, Any], MultiStepPlan]:
        # Stub: if command is a known tool, return single-step plan
        known_tools = ["echo", "file"]
        if command in known_tools:
            return {"tool": command, "action": "say" if command == "echo" else "create", "params": params}
        # Example: if command is 'create and read file', decompose into two steps
        if command == "create and read file":
            return MultiStepPlan(steps=[
                PlanStep(tool="file", action="create", params=params),
                PlanStep(tool="file", action="read", params={"filename": params.get("filename")})
            ])
        # Default: single-step echo
        return {"tool": "echo", "action": "say", "params": {"text": command}}

class OllamaLLMPlanner(LLMPlanner):
    """
    Planner that uses Ollama (e.g., gemma3:4b) for natural language to plan decomposition.
    """
    def plan(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        # Try to call Ollama API (localhost:11434, model=gemma3:4b)
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "gemma3:4b",
                "prompt": f"User command: {command}\nRespond with a JSON: {{'tool': tool_name, 'action': action, 'params': params_dict}}",
                "stream": False
            }
            resp = requests.post(url, json=payload, timeout=5)
            if resp.ok:
                # Try to extract JSON from response
                text = resp.json().get("response", "")
                try:
                    plan = json.loads(text)
                    if isinstance(plan, dict) and "tool" in plan and "action" in plan:
                        return plan
                except Exception:
                    pass
        except Exception:
            pass
        # Fallback: simple keyword routing
        lc = command.lower()
        if "system" in lc or "cpu" in lc or "memory" in lc:
            return {"tool": "system", "action": "info", "params": {}}
        if "file" in lc:
            return {"tool": "file", "action": "list", "params": {"directory": "."}}
        if "date" in lc or "time" in lc:
            return {"tool": "datetime", "action": "now", "params": {}}
        if "weather" in lc:
            return {"tool": "weather", "action": "current", "params": {}}
        if "calculate" in lc or "math" in lc or any(op in lc for op in ["+", "-", "*", "/"]):
            expr = command.split("calculate", 1)[-1].strip() if "calculate" in lc else command
            return {"tool": "calculator", "action": "eval", "params": {"expression": expr}}
        return super().plan(command, params)

class EchoTool(Tool):
    name = "echo"
    def execute(self, action: str, params: dict) -> any:
        if action == "say":
            return params.get("text", "")
        raise ValueError(f"Unknown action: {action}")

class BaseAgent:
    """Base class for Labeeb AI agents."""
    
    def __init__(self):
        self.name = "Labeeb Agent"
        self.capabilities = []
        self.tools = ToolRegistry()
        self.memory = AgentMemory()
        self.logger = logging.getLogger(f"LabeebAgent.{self.name}")
        self._a2a_protocol = A2AProtocol()
        self._mcp_protocol = MCPProtocol()
    
    def register_tool(self, tool: Tool) -> None:
        """Register a new tool with the agent."""
        self.tools.register(tool)
        self.logger.debug(f"Registered tool: {tool.name}")
    
    async def plan_and_execute(self, command: str, **kwargs) -> Any:
        """
        Plan and execute a command.
        
        Args:
            command (str): The command to execute
            **kwargs: Additional parameters for the command
            
        Returns:
            Any: The result of the command execution
        """
        self.logger.info(f"Processing command: {command}")
        
        # Create and execute plan
        plan = await self._create_plan(command, **kwargs)
        result = await self._execute_plan(plan)
        
        # Update memory
        self.memory.add_step(command, plan.steps[-1].action if plan.steps else "unknown",
                           plan.steps[-1].parameters if plan.steps else {},
                           result)
        
        return result
    
    async def _create_plan(self, command: str, **kwargs) -> MultiStepPlan:
        """Create a plan for executing the command."""
        # Default to single-step plan
        return MultiStepPlan(steps=[
            PlanStep(action=command, parameters=kwargs)
        ])
    
    async def _execute_plan(self, plan: MultiStepPlan) -> Any:
        """Execute a multi-step plan."""
        results = []
        for step in plan.steps:
            if step.condition and not step.condition(self.memory.context):
                continue
            result = await self.tools.execute_tool(step.action, step.parameters)
            results.append(result)
        return results[-1] if results else None

    async def handle_a2a_message(self, message: Message) -> Message:
        """Handle an A2A message."""
        return await self._a2a_protocol.handle_message(message)

    async def handle_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Handle an MCP request."""
        return await self._mcp_protocol.handle_request(request)

    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        return {
            "name": self.name,
            "memory": {
                "steps": self.memory.steps,
                "context": self.memory.context,
                "created_at": self.memory.created_at,
                "updated_at": self.memory.updated_at
            },
            "tools": self.tools.list_tools()
        }

    def clear_memory(self):
        """Clear agent memory."""
        self.memory.clear()

# Minimal test agent usage
if __name__ == "__main__":
    agent = BaseAgent()
    agent.register_tool(EchoTool())
    result = agent.plan_and_execute("echo", text="Hello, agent world!")
    print(f"Result: {result}")
    print("\nAgent memory steps:")
    for step in agent.get_state()["memory"]["steps"]:
        print(step) 