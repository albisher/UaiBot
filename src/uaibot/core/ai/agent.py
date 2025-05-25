"""
Agent base class and tool registry for agentic architecture (SmolAgents pattern).

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

Classes:
- Tool: Base class for agent tools.
- ToolRegistry: Registry for tool discovery and invocation.
- AgentStep: Structured memory for each step.
- AgentMemory: Rich memory/state for multi-step workflows.
- MultiStepPlan: Structure for multi-step plans.
- LLMPlanner: Returns single or multi-step plans.
- Agent: Base agent class with plan/execute loop and workflow orchestration.
"""
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from uaibot.core.ai.agent_tools.file_tool import FileTool
from uaibot.core.ai.agent_tools.system_resource_tool import SystemResourceTool
from uaibot.core.ai.agent_tools.datetime_tool import DateTimeTool
from uaibot.core.ai.agent_tools.weather_tool import WeatherTool
from uaibot.core.ai.agent_tools.calculator_tool import CalculatorTool
from uaibot.core.ai.agent_tools.system_awareness_tool import SystemAwarenessTool
from uaibot.core.ai.agent_tools.mouse_control_tool import MouseControlTool
from uaibot.core.ai.agent_tools.keyboard_input_tool import KeyboardInputTool
from uaibot.core.ai.agent_tools.browser_automation_tool import BrowserAutomationTool
from uaibot.core.ai.agent_tools.web_surfing_tool import WebSurfingTool
from uaibot.core.ai.agent_tools.web_searching_tool import WebSearchingTool
from uaibot.core.ai.agent_tools.file_and_document_organizer_tool import FileAndDocumentOrganizerTool
from uaibot.core.ai.agent_tools.code_path_updater_tool import CodePathUpdaterTool
import requests
import json
from uaibot.core.ai.tool_base import Tool

def safe_path(filename: str, category: str = "test") -> str:
    """
    Ensure files are saved in the correct directory based on category.
    category: 'test', 'log', 'state', etc.
    """
    base_dirs = {
        "test": "tests/fixtures/",
        "log": "log/",
        "state": "src/uaibot/state/",
        "core": "src/uaibot/core/"
    }
    if category in base_dirs:
        os.makedirs(base_dirs[category], exist_ok=True)
        return os.path.join(base_dirs[category], filename)
    return filename

@dataclass
class AgentStep:
    step_number: int
    command: str
    action: str
    params: Dict[str, Any]
    result: Any
    timestamp: str

@dataclass
class AgentMemory:
    """
    Rich agent memory/state for multi-step workflows.
    Stores each step as a structured object.
    """
    steps: List[AgentStep] = field(default_factory=list)

    def add_step(self, command: str, action: str, params: Dict[str, Any], result: Any):
        step = AgentStep(
            step_number=len(self.steps) + 1,
            command=command,
            action=action,
            params=params,
            result=result,
            timestamp=datetime.utcnow().isoformat()
        )
        self.steps.append(step)

    def get_full_history(self) -> List[AgentStep]:
        return self.steps

    def get_last_step(self) -> Optional[AgentStep]:
        return self.steps[-1] if self.steps else None

    def prune(self, max_steps: int = 50):
        if len(self.steps) > max_steps:
            self.steps = self.steps[-max_steps:]

@dataclass
class PlanStep:
    tool: str
    action: str
    params: Dict[str, Any]
    condition: Optional[str] = None  # For future conditional logic
    parallel: bool = False           # For future parallel execution

@dataclass
class MultiStepPlan:
    steps: List[PlanStep]
    plan_type: str = "sequential"  # Could be 'sequential', 'parallel', 'conditional'

class ToolRegistry:
    """
    Registry for agent tools. Allows agents to discover and invoke tools by name.

    Methods:
        register(tool: Tool): Register a tool.
        get(tool_name: str) -> Optional[Tool]: Retrieve a tool by name.
        list_tools() -> List[str]: List all registered tool names.
    """
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> Optional[Tool]:
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

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

class Agent:
    """
    Base agent class. Implements state, memory, plan/execute loop, and tool usage.
    Now includes a basic planning step (LLMPlanner stub) and rich memory for multi-step workflows.

    Attributes:
        memory (AgentMemory): Agent's memory/state.
        tools (ToolRegistry): Registry of available tools.
        planner (LLMPlanner): Planner for command decomposition.
    Methods:
        plan_and_execute(command: str, params: Dict[str, Any], action: Optional[str] = None) -> Any: Plan and execute a command.
    """
    def __init__(self, memory: Optional[AgentMemory] = None, tools: Optional[ToolRegistry] = None, planner: Optional[LLMPlanner] = None):
        self.memory = memory or AgentMemory()
        self.tools = tools or ToolRegistry()
        self.tools.register(EchoTool())
        self.tools.register(FileTool())
        self.tools.register(SystemResourceTool())
        self.tools.register(DateTimeTool())
        self.tools.register(WeatherTool())
        self.tools.register(CalculatorTool())
        self.tools.register(SystemAwarenessTool())
        self.tools.register(MouseControlTool())
        self.tools.register(KeyboardInputTool())
        self.tools.register(BrowserAutomationTool())
        self.tools.register(WebSurfingTool())
        self.tools.register(WebSearchingTool())
        self.tools.register(FileAndDocumentOrganizerTool())
        self.tools.register(CodePathUpdaterTool())
        # Do NOT instantiate or register GraphMakerAgent or InformationCollectorAgent here
        # Register ShellTool
        try:
            from uaibot.core.ai.agent_tools.shell_tool import ShellTool
            self.tools.register(ShellTool())
        except ImportError:
            pass
        self.planner = planner or OllamaLLMPlanner()

    def plan_and_execute(self, command: str, params: Dict[str, Any], action: Optional[str] = None) -> Any:
        """
        Plan and execute a command. If the command is a tool, call it directly. Otherwise, use the planner to decompose.
        """
        tool = self.tools.get(command)
        if tool:
            # If action is provided, use it; else default to 'say' for echo, 'create' for file, etc.
            tool_action = action or ("say" if command == "echo" else "create")
            result = tool.execute(tool_action, params)
            self.memory.add_step(command, tool_action, params, result)
            print(f"[DEBUG] Agent.plan_and_execute result: {result}")
            return result
        # Use planner to decompose
        plan = self.planner.plan(command, params)
        # Multi-step plan support
        if isinstance(plan, MultiStepPlan):
            results = []
            for step in plan.steps:
                tool = self.tools.get(step.tool)
                if not tool:
                    raise ValueError(f"Tool '{step.tool}' not found.")
                # (Stub) Parallel/conditional logic can be added here
                result = tool.execute(step.action, step.params)
                self.memory.add_step(step.tool, step.action, step.params, result)
                results.append(result)
            return results
        # Single-step plan
        tool = self.tools.get(plan["tool"])
        if not tool:
            raise ValueError(f"Tool '{plan['tool']}' not found.")
        result = tool.execute(plan["action"], plan["params"])
        self.memory.add_step(command, plan["action"], plan["params"], result)
        return result

# Minimal test agent usage
if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register(EchoTool())
    registry.register(FileTool())
    registry.register(SystemResourceTool())
    agent = Agent(tools=registry)
    print(agent.plan_and_execute("echo", {"text": "Hello, agent world!"}))
    # Use safe_path for test files
    test_file1 = safe_path("test_agent_file.txt", "test")
    test_file2 = safe_path("test_agent_file2.txt", "test")
    print(agent.plan_and_execute("file", {"filename": test_file1, "content": "Agent file content!", "directory": None, "pattern": None}, action="create"))
    print(agent.plan_and_execute("file", {"filename": test_file1}, action="read"))
    # Multi-step plan: create and read file
    print(agent.plan_and_execute("create and read file", {"filename": test_file2, "content": "Multi-step!", "directory": None}))
    # Show full memory history
    print("\nAgent memory steps:")
    for step in agent.memory.get_full_history():
        print(step) 