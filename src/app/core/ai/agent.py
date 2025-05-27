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
        # Use conversation context
        last_agent_reply = self.memory.conversation[-1]["agent"] if self.memory.conversation else None
        plan_dict = self.planner.plan(command, {})
        print(f"[DEBUG] BaseAgent.plan: plan_dict={plan_dict}")
        # Defensive: check for valid tool/action
        if isinstance(plan_dict, dict) and "tool" in plan_dict and plan_dict["tool"] and "action" in plan_dict and plan_dict["action"]:
            params = plan_dict.get("params", {})
            plan = MultiStepPlan(steps=[PlanStep(action=plan_dict["tool"], parameters=params)])
            print(f"[DEBUG] BaseAgent.plan: MultiStepPlan={plan}")
            return plan

        # --- Improved fallback planner logic ---
        lc = command.lower().strip()
        # Normalize common misspellings and synonyms
        lc = lc.replace("waether", "weather").replace("mose", "mouse").replace("labebb", "labeeb")
        # System info
        if re.search(r"cpu|memory|system|stats|disk|ram|usage|sysinfo|resources|مواصفات|معلومات النظام", lc):
            return MultiStepPlan(steps=[PlanStep(action="system", parameters={"action": "info"})])
        # Weather
        if re.search(r"weather|طقس|جو|حالة الجو|درجة الحرارة|temperature", lc):
            location = None
            match = re.search(r"weather in ([\w\s,]+)", lc)
            if match:
                location = match.group(1).strip()
            ar_match = re.search(r"طقس (.+)", lc)
            if ar_match:
                location = ar_match.group(1).strip()
            params = {"action": "current"}
            if location:
                params["location"] = location
            return MultiStepPlan(steps=[PlanStep(action="weather", parameters=params)])
        # File operations
        if re.search(r"list files|show files|عرض الملفات|ls|list directory|عرض محتويات|find content|show content|محتوى|documents folder|مجلد الوثائق", lc):
            # Try to extract directory
            match = re.search(r"in ([\w/\\.]+)", lc)
            ar_match = re.search(r"في ([\w/\\.]+)", lc)
            path = "."
            if match:
                path = match.group(1).strip()
            elif ar_match:
                path = ar_match.group(1).strip()
            elif "documents" in lc or "مجلد الوثائق" in lc:
                path = "Documents"
            return MultiStepPlan(steps=[PlanStep(action="file", parameters={"action": "list", "path": path})])
        # Date/time
        if re.search(r"date|time|now|الوقت|التاريخ|الساعة|كم الساعة|clock|what time", lc):
            return MultiStepPlan(steps=[PlanStep(action="datetime", parameters={"action": "now"})])
        # Calculator
        if re.search(r"calculate|math|احسب|كم يساوي|[\d\s\+\-\*/\^\(\)\.]+|what is|كم الناتج|result of", lc):
            expr = command
            match = re.search(r"calculate (.+)", lc)
            ar_match = re.search(r"احسب (.+)", lc)
            if match:
                expr = match.group(1).strip()
            elif ar_match:
                expr = ar_match.group(1).strip()
            elif "what is" in lc:
                expr = lc.split("what is", 1)[-1].strip()
            return MultiStepPlan(steps=[PlanStep(action="calculator", parameters={"action": "calculate", "expression": expr})])
        # Browser
        if re.search(r"open browser|search in browser|search for|brave browser|firefox|chrome|افتح المتصفح|ابحث في المتصفح|ابحث عن", lc):
            # Extract search query if present
            search_query = None
            match = re.search(r"search for ([\w\s,]+)", lc)
            if match:
                search_query = match.group(1).strip()
            ar_match = re.search(r"ابحث عن (.+)", lc)
            if ar_match:
                search_query = ar_match.group(1).strip()
            params = {"action": "open"}
            if search_query:
                params["query"] = search_query
            return MultiStepPlan(steps=[PlanStep(action="browser", parameters=params)])
        # Mouse
        if re.search(r"mouse|مؤشر|move the mouse|move mouse|click the mouse|click mouse|حرك المؤشر|انقر المؤشر|move the mose|click the mose", lc):
            # Extract coordinates or click type
            match = re.search(r"move (?:the )?mouse to ([\d]+)[, ]+([\d]+)", lc)
            ar_match = re.search(r"حرك المؤشر إلى ([\d]+)[, ]+([\d]+)", lc)
            if match:
                x, y = match.group(1), match.group(2)
                return MultiStepPlan(steps=[PlanStep(action="mouse", parameters={"action": "move", "x": int(x), "y": int(y)})])
            elif ar_match:
                x, y = ar_match.group(1), ar_match.group(2)
                return MultiStepPlan(steps=[PlanStep(action="mouse", parameters={"action": "move", "x": int(x), "y": int(y)})])
            elif "click" in lc or "انقر" in lc:
                count = 2 if "twice" in lc or "مرتين" in lc else 1
                return MultiStepPlan(steps=[PlanStep(action="mouse", parameters={"action": "click", "count": count})])
        # Screenshot
        if re.search(r"screenshot|screen shot|لقطة شاشة|التقط الشاشة|take screenshot|التقط صورة", lc):
            return MultiStepPlan(steps=[PlanStep(action="screen", parameters={"action": "screenshot"})])
        # Who are you/self-knowledge
        if any(word in lc for word in ["who are you", "your name", "what is labeeb", "about you", "من انت", "ما اسمك", "لبيب"]):
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": _(f"I am Labeeb, your multilingual, multi-system AI assistant. How can I help you today? 😊")})])
        # Remember/recall/teach/forget (memory/skills)
        if lc.startswith("remember "):
            fact = command[len("remember "):].strip()
            self.memory.context.setdefault("facts", []).append(fact)
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": _(f"I will remember: {fact}")})])
        if lc.startswith("recall") or lc.startswith("what did you remember") or lc.startswith("تذكر"):
            facts = self.memory.context.get("facts", [])
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": _(f"I remember: {', '.join(facts)}" if facts else "I have nothing remembered yet.")})])
        if lc.startswith("forget") or lc.startswith("انس"):
            self.memory.context["facts"] = []
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": _(f"I have forgotten all remembered facts.")})])
        # Follow-up/clarification
        if "repeat" in lc or "again" in lc or "كرر" in lc:
            if last_agent_reply:
                return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": last_agent_reply})])
            else:
                return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": _(f"I have nothing to repeat yet.")})])
        # Clarification for unknown/ambiguous input
        if len(command.strip()) < 3 or command.strip() in ["?", "help", "مساعدة"]:
            return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": _(f"How can I help you? You can ask about the weather, system info, calculations, or teach me something new!")})])
        # Fallback: friendly clarification
        return MultiStepPlan(steps=[PlanStep(action="echo", parameters={"text": _(f"Sorry, I didn't understand that. Can you rephrase or try a different request? 😊")})])

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
        self.logger = logging.getLogger("LabeebAgent")
        # Register default tools (add more as needed)
        self.register_tool(EchoTool())
        self.register_tool(FileTool({}))
        self.register_tool(SystemResourceTool({}))
        self.register_tool(DateTimeTool({}))
        self.register_tool(CalculatorTool({}))
        self.register_tool(WeatherTool({}))
        # Register browser tool
        from src.app.core.ai.tools.browser_automation_tool import BrowserAutomationTool
        self.register_tool(BrowserAutomationTool({"browser_type": "chrome", "headless": True}))
        # Register mouse tool
        from src.app.core.ai.tools.mouse_tool import MouseTool
        self.register_tool(MouseTool({}))
        # Register keyboard input tool
        from src.app.core.ai.tools.keyboard_input_tool import KeyboardInputTool
        self.register_tool(KeyboardInputTool({}))
        # Register screen tool (screenshot)
        try:
            from src.app.core.ai.tools.screen_control_tool import ScreenControlTool
            # Wrap as a BaseTool if needed
            class ScreenToolWrapper(BaseTool):
                def __init__(self):
                    super().__init__(name="screen", description="Screen control and screenshot tool")
                    self._tool = ScreenControlTool()
                async def _execute_command(self, command: str, args=None):
                    if command == "screenshot":
                        result = self._tool.take_screenshot()
                        return {"status": result.get("status"), "action": "screenshot", "message": result.get("message", ""), "error": result.get("error", "")}
                    return {"error": f"Unknown screen tool command: {command}"}
            self.register_tool(ScreenToolWrapper())
        except Exception:
            pass

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