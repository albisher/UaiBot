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
from src.app.core.ai.tools.file_tool import FileTool
from src.app.core.ai.tools.system_resource_tool import SystemResourceTool
from src.app.core.ai.tools.datetime_tool import DateTimeTool
from src.app.core.ai.tools.weather_tool import WeatherTool
from src.app.core.ai.tools.calculator_tool import CalculatorTool
from src.app.core.ai.tools.keyboard_input_tool import KeyboardInputTool
from src.app.core.ai.tools.browser_automation_tool import BrowserAutomationTool
from src.app.core.ai.tools.web_surfing_tool import WebSurfingTool
from src.app.core.ai.tools.web_searching_tool import WebSearchingTool
from src.app.core.ai.tools.file_and_document_organizer_tool import FileAndDocumentOrganizerTool
from src.app.core.ai.tools.code_path_updater_tool import CodePathUpdaterTool
from src.app.core.tools.app_control_tool import AppControlTool
from src.app.core.ai.tool_base import Tool, BaseTool
import requests
import json
from .a2a_protocol import A2AProtocol, Message, MessageRole
from .mcp_protocol import MCPProtocol, MCPRequest, MCPResponse
from .smol_agent import SmolAgent, AgentState, AgentResult
from smolagents import Tool
import sys
import re
import gettext
import logging
from pathlib import Path
from .base_agent import BaseAgent, Agent, AgentState, AgentResult
from .a2a_protocol import A2AProtocol
from .mcp_protocol import MCPProtocol
from .smol_agent import SmolAgentProtocol

# Setup translation (i18n)
_ = gettext.gettext

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
            print(f"[DEBUG] ToolRegistry: Tool '{tool_name}' not found.")
            raise ValueError(f"Tool {tool_name} not found")
        print(f"[DEBUG] ToolRegistry: Executing tool '{tool_name}' with params {params}")
        # Use forward for smolagents.Tool, _execute_command for BaseTool
        if hasattr(tool, 'forward') and callable(getattr(tool, 'forward')):
            if 'text' in params:
                result = await tool.forward(params['text'])
            else:
                # For app_control tool, ensure action is in params
                if tool_name == 'app_control' and 'action' not in params:
                    params['action'] = params.get('params', {}).get('action')
                result = await tool.forward(**params)
            print(f"[DEBUG] ToolRegistry: Result from '{tool_name}': {result}")
            return result
        elif hasattr(tool, '_execute_command') and callable(getattr(tool, '_execute_command')):
            action = params.get('action', None)
            args = params.copy()
            if action:
                args.pop('action')
            result = await tool._execute_command(action, args)
            print(f"[DEBUG] ToolRegistry: Result from '{tool_name}': {result}")
            return result
        else:
            print(f"[DEBUG] ToolRegistry: Tool '{tool_name}' does not support execution interface.")
            raise TypeError(f"Tool {tool_name} does not support execution interface")

@dataclass
class AgentMemory:
    """Rich memory/state for multi-step workflows."""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    conversation: List[Dict[str, str]] = field(default_factory=list)  # [{"user": ..., "agent": ...}]

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

    def add_conversation(self, user: str, agent: str):
        self.conversation.append({"user": user, "agent": agent})
        if len(self.conversation) > 20:
            self.conversation.pop(0)

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
    """A single step in a multi-step plan."""
    action: str
    params: Dict[str, Any]
    description: str
    required_tools: List[str]
    expected_result: Optional[Any] = None

@dataclass
class MultiStepPlan:
    """A plan consisting of multiple steps."""
    steps: List[PlanStep]
    description: str
    required_tools: List[str]
    expected_result: Optional[Any] = None

class LLMPlanner:
    """
    Stub for an LLM-based planner. In a real system, this would call an LLM to interpret natural language and return a plan.
    """
    def plan(self, command: str, params: Dict[str, Any]) -> Union[Dict[str, Any], MultiStepPlan]:
        # Add app_control tool routing
        lc = command.lower()
        if any(keyword in lc for keyword in ["open app", "close app", "focus app", "minimize app", "maximize app"]):
            # Extract action and app name
            for action in ["open", "close", "focus", "minimize", "maximize"]:
                if action + " app" in lc:
                    # Try to extract app name
                    parts = lc.split(action + " app", 1)
                    app_name = parts[1].strip() if len(parts) > 1 else ""
                    return {"tool": "app_control", "action": action, "params": {"app": app_name}}
        # Existing logic for known tools
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
        # Add app_control tool routing
        lc = command.lower()
        if any(keyword in lc for keyword in ["open app", "close app", "focus app", "minimize app", "maximize app"]):
            for action in ["open", "close", "focus", "minimize", "maximize"]:
                if action + " app" in lc:
                    parts = lc.split(action + " app", 1)
                    app_name = parts[1].strip() if len(parts) > 1 else ""
                    return {"tool": "app_control", "action": action, "params": {"app": app_name}}
        # Existing logic...
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
        # Use conversation context
        last_agent_reply = self.memory.conversation[-1]["agent"] if self.memory.conversation else None
        plan_dict = self.planner.plan(command, {})
        print(f"[DEBUG] BaseAgent.plan: plan_dict={plan_dict}")
        
        # Application commands in English and Arabic
        app_commands = {
            'open calculator': 'calculator',
            'open calc': 'calculator',
            'افتح الحاسبة': 'calculator',
            'تشغيل الحاسبة': 'calculator',
            'move mouse': 'calculator',
            'تحريك الماوس': 'calculator',
            'click': 'calculator',
            'نقر': 'calculator',
            'type': 'calculator',
            'كتابة': 'calculator',
            'press enter': 'calculator',
            'اضغط انتر': 'calculator',
            'get result': 'calculator',
            'الحصول على النتيجة': 'calculator'
        }
        
        # File operations in English and Arabic
        file_commands = {
            'create directory': 'file_tool',
            'create folder': 'file_tool',
            'إنشاء مجلد': 'file_tool',
            'إنشاء دليل': 'file_tool',
            'list files': 'file_tool',
            'show files': 'file_tool',
            'عرض الملفات': 'file_tool',
            'عرض محتويات': 'file_tool',
            'create file': 'file_tool',
            'إنشاء ملف': 'file_tool',
            'write file': 'file_tool',
            'كتابة ملف': 'file_tool'
        }
        
        lc = command.lower()
        
        # Check for application commands first
        for cmd, tool in app_commands.items():
            if cmd in lc:
                app_name = cmd.split('open')[-1].strip() if 'open' in cmd else cmd.split('افتح')[-1].strip()
                params = {
                    "action": "open",
                    "app": app_name
                }
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="app_control",
                        params=params,
                        description=f"Open {app_name}",
                        required_tools=["app_control"]
                    )],
                    description=f"Open {app_name}",
                    required_tools=["app_control"]
                )
        
        # Then check for file commands
        for cmd, tool in file_commands.items():
            if cmd in lc:
                if 'create' in cmd or 'إنشاء' in cmd:
                    if 'file' in cmd or 'ملف' in cmd:
                        # Extract file path and content
                        parts = command.split('with content', 1)
                        if len(parts) == 2:
                            path = parts[0].split(cmd)[-1].strip()
                            content = parts[1].strip()
                            return MultiStepPlan(
                                steps=[PlanStep(
                                    action=tool,
                                    params={"action": "create_file", "path": path, "content": content},
                                    description=f"Create file {path} with content",
                                    required_tools=[tool]
                                )],
                                description=f"Create file {path} with content",
                                required_tools=[tool]
                            )
                    else:
                        # Extract directory name
                        dir_name = command.split(cmd)[-1].strip()
                        return MultiStepPlan(
                            steps=[PlanStep(
                                action=tool,
                                params={"action": "create_directory", "path": dir_name},
                                description=f"Create directory {dir_name}",
                                required_tools=[tool]
                            )],
                            description=f"Create directory {dir_name}",
                            required_tools=[tool]
                        )
                elif 'list' in cmd or 'show' in cmd or 'عرض' in cmd:
                    # Extract directory path if provided
                    path = "."
                    if 'in' in lc:
                        path = command.split('in')[-1].strip()
                    elif 'في' in lc:
                        path = command.split('في')[-1].strip()
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action=tool,
                            params={"action": "list_files", "directory": path},
                            description=f"List files in {path}",
                            required_tools=[tool]
                        )],
                        description=f"List files in {path}",
                        required_tools=[tool]
                    )
        
        # Defensive: check for valid tool/action
        if isinstance(plan_dict, dict) and "tool" in plan_dict and plan_dict["tool"] and "action" in plan_dict and plan_dict["action"]:
            params = plan_dict.get("params", {})
            if "action" not in params:
                params["action"] = plan_dict["action"]
            plan = MultiStepPlan(steps=[PlanStep(action=plan_dict["tool"], params=params, description=f"Execute {plan_dict['tool']} with {params}", required_tools=[plan_dict["tool"]])], description=f"Execute {plan_dict['tool']} with {params}", required_tools=[plan_dict["tool"]])
            print(f"[DEBUG] BaseAgent.plan: MultiStepPlan={plan}")
            return plan

    async def execute(self, plan: MultiStepPlan) -> Any:
        """Execute a plan and return the result."""
        return await self._execute_plan(plan)
    
    async def _execute_plan(self, plan: MultiStepPlan) -> Any:
        """Execute a multi-step plan."""
        results = []
        for step in plan.steps:
            # Skip step if condition is not met
            if hasattr(step, 'condition') and step.condition and not step.condition(self.memory.context):
                continue
            result = await self.tools.execute_tool(step.action, step.params)
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
        self.logger = logging.getLogger("LabeebAgent")
        # Register all tools
        self.tools.register(FileTool())
        self.tools.register(SystemResourceTool())
        self.tools.register(DateTimeTool())
        self.tools.register(WeatherTool())
        self.tools.register(CalculatorTool())
        self.tools.register(KeyboardInputTool())
        self.tools.register(BrowserAutomationTool({"browser_type": "chrome", "headless": True}))
        self.tools.register(WebSurfingTool({"browser_type": "chrome", "headless": True}))
        self.tools.register(WebSearchingTool({"browser_type": "chrome", "headless": True}))
        self.tools.register(FileAndDocumentOrganizerTool())
        self.tools.register(CodePathUpdaterTool())
        self.tools.register(AppControlTool())

    async def plan(self, command: str) -> MultiStepPlan:
        self.logger.debug(f"Planning for command: {command}")
        plan = await super().plan(command)
        self.logger.debug(f"Generated plan: {plan}")
        return plan

    async def execute(self, plan: MultiStepPlan) -> Any:
        self.logger.debug(f"Executing plan: {plan}")
        result = await self._execute_plan(plan)
        self.logger.debug(f"Execution result: {result}")
        return result

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