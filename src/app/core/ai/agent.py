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
from src.app.core.ai.tools.clipboard_tool import ClipboardTool
from src.app.core.ai.tools.screen_control_tool import ScreenControlTool
from src.app.core.ai.tools.tool_registry import ToolRegistry

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
            return {"tool": command, "action": "say" if command == "echo" else "create_file", "params": params}
        # Example: if command is 'create and read file', decompose into two steps
        if command == "create and read file":
            return MultiStepPlan(steps=[
                PlanStep(tool="file", action="create_file", params=params),
                PlanStep(tool="file", action="read_file", params={"path": params.get("filename")})
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
            return {"tool": "file", "action": "list_files", "params": {"directory": "."}}
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
        self.tools = ToolRegistry
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
        
        # --- Improved folder creation mapping ---
        folder_patterns = [
            r"create (a )?(folder|directory) called ([\w\-_]+)",
            r"make (a )?(folder|directory) named ([\w\-_]+)",
            r"أنشئ مجلد اسمه ([\w\-_]+)",
            r"أنشئ مجلد باسم ([\w\-_]+)",
            r"أنشئ مجلد ([\w\-_]+)",
            r"إنشاء مجلد ([\w\-_]+)"
        ]
        for pattern in folder_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                folder_name = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="file_tool",
                        params={"action": "create_directory", "path": folder_name},
                        description=f"Create directory {folder_name}",
                        required_tools=["file_tool"]
                    )],
                    description=f"Create directory {folder_name}",
                    required_tools=["file_tool"]
                )
        # --- End improved folder creation mapping ---
        # --- Improved file creation mapping ---
        file_patterns = [
            r"create (a )?file named ([\w\-_\.]+) and write: (.+)",
            r"make (a )?file named ([\w\-_\.]+) and write: (.+)",
            r"write (a )?file named ([\w\-_\.]+) with content: (.+)",
            r"أنشئ ملف اسمه ([\w\-_\.]+) واكتب فيه: (.+)",
            r"اكتب ملف اسمه ([\w\-_\.]+) وضع فيه: (.+)",
            r"إنشاء ملف ([\w\-_\.]+) بمحتوى: (.+)"
        ]
        for pattern in file_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                file_name = match.groups()[-2]
                content = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="file_tool",
                        params={"action": "create_file", "path": f"labeeb_tool_tests/{file_name}", "content": content},
                        description=f"Create file {file_name} with content",
                        required_tools=["file_tool"]
                    )],
                    description=f"Create file {file_name} with content",
                    required_tools=["file_tool"]
                )
        # --- End improved file creation mapping ---
        # --- Improved file listing mapping ---
        list_patterns = [
            r"show me all the files in ([\w\-_]+)",
            r"list all files in ([\w\-_]+)",
            r"اعرض لي كل الملفات الموجودة في ([\w\-_]+)",
            r"ما هي الملفات في ([\w\-_]+)",
            r"عرض الملفات في ([\w\-_]+)"
        ]
        for pattern in list_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                dir_name = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="file_tool",
                        params={"action": "list_files", "directory": dir_name},
                        description=f"List files in {dir_name}",
                        required_tools=["file_tool"]
                    )],
                    description=f"List files in {dir_name}",
                    required_tools=["file_tool"]
                )
        # --- End improved file listing mapping ---
        # --- Improved file reading mapping ---
        read_patterns = [
            r"read the contents of ([\w\-_/.]+)",
            r"show me what's in ([\w\-_/.]+)",
            r"اعرض محتوى ([\w\-_/.]+)",
            r"اقرأ ملف ([\w\-_/.]+)"
        ]
        for pattern in read_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                file_path = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="file_tool",
                        params={"action": "read_file", "path": file_path},
                        description=f"Read file {file_path}",
                        required_tools=["file_tool"]
                    )],
                    description=f"Read file {file_path}",
                    required_tools=["file_tool"]
                )
        # --- End improved file reading mapping ---
        # --- Improved file deletion mapping ---
        delete_patterns = [
            r"delete file ([\w\-_/.]+)",
            r"remove file ([\w\-_/.]+)",
            r"احذف ملف ([\w\-_/.]+)",
            r"امسح ملف ([\w\-_/.]+)"
        ]
        for pattern in delete_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                file_path = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="file_tool",
                        params={"action": "delete_file", "path": file_path},
                        description=f"Delete file {file_path}",
                        required_tools=["file_tool"]
                    )],
                    description=f"Delete file {file_path}",
                    required_tools=["file_tool"]
                )
        # --- End improved file deletion mapping ---
        # --- Improved system resource mapping ---
        sys_patterns = [
            r"cpu and memory usage",
            r"system resources",
            r"system info",
            r"كم تبقى من مساحة القرص",
            r"ما هي حالة النظام"
        ]
        for pattern in sys_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="system_resource_tool",
                        params={"action": "status"},
                        description="Get system resource info",
                        required_tools=["system_resource_tool"]
                    )],
                    description="Get system resource info",
                    required_tools=["system_resource_tool"]
                )
        # --- End improved system resource mapping ---
        # --- Improved translation mapping ---
        translation_patterns = [
            r"translate (.+) to english",
            r"ترجم كلمة ([^ ]+) إلى الإنجليزية"
        ]
        for pattern in translation_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                text = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="translation",
                        params={"command": "translate", "text": text, "target_language": "en"},
                        description=f"Translate '{text}' to English",
                        required_tools=["translation"]
                    )],
                    description=f"Translate '{text}' to English",
                    required_tools=["translation"]
                )
        # --- End improved translation mapping ---
        # --- Improved clipboard mapping (Kuwaiti, Moroccan, English) ---
        clipboard_patterns = [
            r"what is on my clipboard",
            r"show clipboard",
            r"ما الموجود في الحافظة",
            r"شنو في الحافظة",  # Kuwaiti
            r"شنو كاين فالكليپبورد",  # Moroccan
            r"شنو نسخت",  # Moroccan
            r"شنو نسخت آخر مرة",  # Moroccan
            r"شنو آخر شي نسخته",  # Kuwaiti
            r"شنو آخر شي نسخناه",  # Kuwaiti
            r"copy (.+)",
            r"انسخ (.+)",
            r"نسخ (.+)",
            r"حط (.+) في الحافظة",  # Kuwaiti/Moroccan
            r"paste",
            r"ألصق",
            r"لسق",
            r"لسّق"
        ]
        for pattern in clipboard_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                if 'copy' in pattern or 'انسخ' in pattern or 'نسخ' in pattern or 'حط' in pattern:
                    text = match.groups()[-1] if match.groups() else ''
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="clipboard_tool",
                            params={"action": "copy", "text": text},
                            description=f"Copy '{text}' to clipboard",
                            required_tools=["clipboard_tool"]
                        )],
                        description=f"Copy '{text}' to clipboard",
                        required_tools=["clipboard_tool"]
                    )
                elif 'paste' in pattern or 'ألصق' in pattern or 'لسق' in pattern or 'لسّق' in pattern:
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="clipboard_tool",
                            params={"action": "paste"},
                            description="Paste clipboard content",
                            required_tools=["clipboard_tool"]
                        )],
                        description="Paste clipboard content",
                        required_tools=["clipboard_tool"]
                    )
                else:
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="clipboard_tool",
                            params={"action": "get_clipboard"},
                            description="Get clipboard content",
                            required_tools=["clipboard_tool"]
                        )],
                        description="Get clipboard content",
                        required_tools=["clipboard_tool"]
                    )
        # --- End improved clipboard mapping ---
        # --- Improved screenshot mapping (English/Arabic/Kuwaiti/Moroccan) ---
        screenshot_patterns = [
            r"take a screenshot",
            r"screenshot",
            r"لقط الشاشة",
            r"خذ لقطة شاشة",
            r"صور الشاشة",
            r"صوّر الشاشة",  # Kuwaiti
            r"دير سكرينشوت",  # Moroccan
            r"دير لقطة شاشة"  # Moroccan
        ]
        for pattern in screenshot_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="screen_control_tool",
                        params={"action": "take_screenshot"},
                        description="Take a screenshot",
                        required_tools=["screen_control_tool"]
                    )],
                    description="Take a screenshot",
                    required_tools=["screen_control_tool"]
                )
        # --- End improved screenshot mapping ---
        # --- Improved clipboard clear mapping (English/Arabic) ---
        clear_patterns = [
            r"clear the clipboard",
            r"empty the clipboard",
            r"افرغ الحافظة",
            r"امسح الحافظة",
            r"صفر الحافظة",
            r"نظف الحافظة"
        ]
        for pattern in clear_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="clipboard_tool",
                        params={"action": "clear"},
                        description="Clear clipboard content",
                        required_tools=["clipboard_tool"]
                    )],
                    description="Clear clipboard content",
                    required_tools=["clipboard_tool"]
                )
        # --- End improved clipboard clear mapping ---
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
            result = await self.execute_tool(step.action, step.params)
            results.append(result)
        return results[-1] if results else None

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool by name using the shared ToolRegistry."""
        from src.app.core.ai.tools.tool_registry import ToolRegistry
        tool_class = ToolRegistry.get_tool(tool_name)
        if not tool_class:
            raise ValueError(f"Tool {tool_name} not found in registry")
        tool = tool_class()
        # Prefer async forward or _execute_command if available
        if hasattr(tool, 'forward') and callable(getattr(tool, 'forward')):
            return await tool.forward(**params)
        elif hasattr(tool, '_execute_command') and callable(getattr(tool, '_execute_command')):
            action = params.get('action', None)
            args = params.copy()
            if action:
                args.pop('action')
            return await tool._execute_command(action, args)
        elif hasattr(tool, 'execute') and callable(getattr(tool, 'execute')):
            action = params.get('action', None)
            args = params.copy()
            if action:
                args.pop('action')
            return await tool.execute(action, **args)
        else:
            raise TypeError(f"Tool {tool_name} does not support execution interface")

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
        self.tools.register(EchoTool)
        self.tools.register(FileTool)
        self.tools.register(SystemResourceTool)
        self.tools.register(DateTimeTool)
        self.tools.register(WeatherTool)
        self.tools.register(CalculatorTool)
        self.tools.register(KeyboardInputTool)
        self.tools.register(FileAndDocumentOrganizerTool)
        self.tools.register(CodePathUpdaterTool)
        self.tools.register(AppControlTool)
        self.tools.register(ClipboardTool)
        self.tools.register(ScreenControlTool)

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