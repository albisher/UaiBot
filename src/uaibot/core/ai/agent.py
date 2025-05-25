"""
Agent base class and tool registry for agentic architecture.

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
from typing import Any, Dict, List, Optional, Callable, Union, Protocol, TypeVar, Generic
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
import logging
import os
from pathlib import Path

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
    """A single step in a multi-step plan."""
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MultiStepPlan:
    """A plan consisting of multiple steps."""
    steps: List[PlanStep] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    current_step: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class Tool(Protocol):
    """Protocol defining the interface for tools."""
    name: str
    description: str
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        ...

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
    Base agent class for UaiBot.
    
    This class provides core functionality for:
    - Tool management
    - Command planning and execution
    - Memory management
    - Logging and error handling
    """
    
    def __init__(self, name: str = "BaseAgent"):
        """Initialize the agent."""
        self.name = name
        self.tools: Dict[str, Tool] = {}
        self.memory = AgentMemory()
        self.logger = logging.getLogger(f"UaiAgent.{name}")
    
    def register_tool(self, tool: Tool) -> None:
        """Register a new tool with the agent."""
        self.tools[tool.name] = tool
        self.logger.debug(f"Registered tool: {tool.name}")
    
    def plan_and_execute(self, command: str, **kwargs) -> Any:
        """
        Plan and execute a command.
        
        Args:
            command (str): The command to execute
            **kwargs: Additional parameters for the command
            
        Returns:
            Any: The result of the command execution
        """
        self.logger.info(f"Processing command: {command}")
        
        # Create a plan
        plan = self._create_plan(command, **kwargs)
        
        # Execute the plan
        result = self._execute_plan(plan)
        
        # Add to memory
        self.memory.add_step(command, plan.steps[0].action if plan.steps else "unknown", 
                           plan.steps[0].parameters if plan.steps else {}, result)
        
        return result
    
    def _create_plan(self, command: str, **kwargs) -> MultiStepPlan:
        """Create a plan for executing the command."""
        # This is a simplified version - subclasses should override this
        return MultiStepPlan(steps=[
            PlanStep(action=command, parameters=kwargs)
        ])
    
    def _execute_plan(self, plan: MultiStepPlan) -> Any:
        """Execute a plan step by step."""
        plan.status = "in_progress"
        
        for i, step in enumerate(plan.steps):
            plan.current_step = i
            step.status = "in_progress"
            
            try:
                # Execute the step
                if step.action in self.tools:
                    step.result = self.tools[step.action].execute(**step.parameters)
                    step.status = "completed"
                else:
                    step.status = "failed"
                    step.error = f"Unknown action: {step.action}"
                    break
                
            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                self.logger.error(f"Error executing step {i}: {str(e)}")
                break
        
        # Update plan status
        if all(step.status == "completed" for step in plan.steps):
            plan.status = "completed"
            plan.completed_at = datetime.now()
        else:
            plan.status = "failed"
        
        return plan.steps[-1].result if plan.steps else None
    
    def get_memory(self) -> List[AgentStep]:
        """Get the agent's memory."""
        return self.memory.get_full_history()

# Minimal test agent usage
if __name__ == "__main__":
    agent = Agent("TestAgent")
    agent.register_tool(EchoTool())
    result = agent.plan_and_execute("echo", text="Hello, agent world!")
    print(f"Result: {result}")
    print("\nAgent memory steps:")
    for step in agent.get_memory():
        print(step) 