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
from labeeb.core.ai.agent_tools.file_tool import FileTool
from labeeb.core.ai.agent_tools.system_resource_tool import SystemResourceTool
from labeeb.core.ai.agent_tools.datetime_tool import DateTimeTool
from labeeb.core.ai.agent_tools.weather_tool import WeatherTool
from labeeb.core.ai.agent_tools.calculator_tool import CalculatorTool
from labeeb.core.ai.agent_tools.system_awareness_tool import SystemAwarenessTool
from labeeb.core.ai.agent_tools.mouse_control_tool import MouseControlTool
from labeeb.core.ai.agent_tools.keyboard_input_tool import KeyboardInputTool
from labeeb.core.ai.agent_tools.browser_automation_tool import BrowserAutomationTool
from labeeb.core.ai.agent_tools.web_surfing_tool import WebSurfingTool
from labeeb.core.ai.agent_tools.web_searching_tool import WebSearchingTool
from labeeb.core.ai.agent_tools.file_and_document_organizer_tool import FileAndDocumentOrganizerTool
from labeeb.core.ai.agent_tools.code_path_updater_tool import CodePathUpdaterTool
import requests
import json
from labeeb.core.ai.tool_base import Tool, BaseTool
import logging
import os
from pathlib import Path
from .a2a_protocol import A2AProtocol, Message, MessageRole
from .mcp_protocol import MCPProtocol, MCPRequest, MCPResponse
from .smol_agent import SmolAgent, AgentState, AgentResult
from smolagents import Tool
import sys
import re

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
        # Use forward for smolagents.Tool, _execute_command for BaseTool
        if hasattr(tool, 'forward') and callable(getattr(tool, 'forward')):
            # EchoTool and smolagents tools
            if 'text' in params:
                return await tool.forward(params['text'])
            return await tool.forward(**params)
        elif hasattr(tool, '_execute_command') and callable(getattr(tool, '_execute_command')):
            action = params.get('action', None)
            args = params.copy()
            if action:
                args.pop('action')
            return await tool._execute_command(action, args)
        else:
            raise TypeError(f"Tool {tool_name} does not support execution interface")

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
    Planner that uses Ollama (e.g., gemma3:latest) for natural language to plan decomposition.
    """
    def __init__(self, model_name: str = "gemma3:latest", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def plan(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": f"User command: {command}\nRespond with a JSON: {{'tool': tool_name, 'action': action, 'params': params_dict}}",
                "stream": False
            }
            resp = requests.post(url, json=payload, timeout=5)
            if resp.ok:
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

def _load_llm_config():
    # Load model name and base_url from config/settings.json
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "settings.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        model = config.get("default_ollama_model", "gemma3:latest")
        base_url = config.get("ollama_base_url", "http://localhost:11434")
        return model, base_url
    return "gemma3:latest", "http://localhost:11434"

class EchoTool(Tool):
    name = "echo"
    description = "Echoes the input text."
    inputs = {"text": {"type": "string", "description": "Text to echo"}}
    outputs = {"text": {"type": "string", "description": "Echoed text"}}
    output_type = "string"

    async def forward(self, text: str) -> str:
        return text

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
        # LLM planner
        model, base_url = _load_llm_config()
        self.planner = OllamaLLMPlanner(model_name=model, base_url=base_url)
    
    def register_tool(self, tool: Tool) -> None:
        """Register a new tool with the agent."""
        self.tools.register(tool)
        self.logger.debug(f"Registered tool: {tool.name}")
    
    async def plan(self, command: str) -> MultiStepPlan:
        """Use the LLM planner to create a plan from natural language, with entity extraction and fallback."""
        plan_dict = self.planner.plan(command, {})
        # Defensive: check for valid tool/action
        if isinstance(plan_dict, dict) and "tool" in plan_dict and plan_dict["tool"] and "action" in plan_dict and plan_dict["action"]:
            params = plan_dict.get("params", {})
            return MultiStepPlan(steps=[PlanStep(action=plan_dict["tool"], parameters=params)])

        # Entity extraction (simple regex for location, time, etc.)
        lc = command.lower()
        location = None
        match = re.search(r"in ([a-zA-Z\u0600-\u06FF\s]+)", command)
        if match:
            location = match.group(1).strip()
        # Weather intent
        if "weather" in lc:
            params = {"action": "current"}
            if location:
                params["location"] = location
            return MultiStepPlan(steps=[PlanStep(action="weather", parameters=params)])
        # System info intent
        if any(word in lc for word in ["system", "cpu", "memory", "stats"]):
            return MultiStepPlan(steps=[PlanStep(action="system", parameters={"action": "info"})])
        # Date/time intent
        if any(word in lc for word in ["date", "time", "now"]):
            return MultiStepPlan(steps=[PlanStep(action="datetime", parameters={"action": "now"})])
        # Calculator intent
        if any(word in lc for word in ["calculate", "math", "+", "-", "*", "/"]):
            expr = command.split("calculate", 1)[-1].strip() if "calculate" in lc else command
            return MultiStepPlan(steps=[PlanStep(action="calculator", parameters={"action": "calculate", "expression": expr})])
        # Who are you/self-knowledge
        if any(word in lc for word in ["who are you", "your name", "what is labeeb", "about you"]):
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": "I am Labeeb, your multilingual, multi-system AI assistant."})])
        # Remember/recall/teach/forget (memory/skills)
        if lc.startswith("remember "):
            fact = command[len("remember "):].strip()
            self.memory.context.setdefault("facts", []).append(fact)
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": f"I will remember: {fact}"})])
        if lc.startswith("recall") or lc.startswith("what did you remember"):
            facts = self.memory.context.get("facts", [])
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": "I remember: " + ", ".join(facts) if facts else "I have nothing remembered yet."})])
        if lc.startswith("forget"):
            self.memory.context["facts"] = []
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": "I have forgotten all remembered facts."})])
        # Fallback: echo
        return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": command})])

    async def execute(self, plan: MultiStepPlan) -> Any:
        """Execute a plan and return the result."""
        return await self._execute_plan(plan)
    
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

class LabeebAgent(BaseAgent):
    """Main Labeeb agent class, extends BaseAgent with default tools and configuration."""
    def __init__(self):
        super().__init__()
        self.name = "LabeebAgent"
        # Register default tools (add more as needed)
        self.register_tool(EchoTool())
        self.register_tool(FileTool({}))
        self.register_tool(SystemResourceTool({}))
        self.register_tool(DateTimeTool({}))
        self.register_tool(CalculatorTool({}))
        self.register_tool(WeatherTool({}))
        # You can register more tools here as needed

__all__ = [
    "LabeebAgent",
    "BaseAgent",
    "ToolRegistry",
    "AgentMemory",
    "PlanStep",
    "MultiStepPlan",
    "LLMPlanner",
    "OllamaLLMPlanner"
]

# Minimal test agent usage
if __name__ == "__main__":
    agent = BaseAgent()
    agent.register_tool(EchoTool())
    result = agent.plan_and_execute("echo", text="Hello, agent world!")
    print(f"Result: {result}")
    print("\nAgent memory steps:")
    for step in agent.get_state()["memory"]["steps"]:
        print(step) 