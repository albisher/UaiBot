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
import os

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
        # 1. Vision/Image Analysis (expanded patterns)
        vision_patterns = [
            r"analyze the image ['\"]?([^'\" ]+)['\"]?.*",
            r"حلل الصورة ['\"]?([^'\" ]+)['\"]?.*",
            r"describe what you see on my screen",
            r"what is on my screen now",
            r"analyze my screen",
            r"what do you see on the screen",
            r"صف ما يظهر على الشاشة",
            r"ماذا ترى على الشاشة",
            r"حلل الشاشة",
            r"اعرض لي وصف الشاشة",
            r"ما الموجود في الصورة ['\"]?([^'\" ]+)['\"]?",
            r"صف الصورة ['\"]?([^'\" ]+)['\"]?"
        ]
        for pattern in vision_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                image_path = match.groups()[-1].strip("'\"") if match.groups() else None
                if image_path and not any(x in image_path for x in ["screen", "الشاشة"]):
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="vision",
                            params={"action": "analyze_image", "image_path": image_path},
                            description=f"Analyze image {image_path}",
                            required_tools=["vision"]
                        )],
                        description=f"Analyze image {image_path}",
                        required_tools=["vision"]
                    )
                else:
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="vision",
                            params={"action": "analyze_image"},
                            description="Analyze the current screen",
                            required_tools=["vision"]
                        )],
                        description="Analyze the current screen",
                        required_tools=["vision"]
                    )
        # 2. Screenshot (robust filename/folder extraction)
        screenshot_patterns = [
            r"take (a )?screenshot( and save it in ([^ ]+)( as ([^ ]+))?)?",
            r"capture (a )?screenshot( and save it in ([^ ]+)( as ([^ ]+))?)?",
            r"get (a )?screenshot( and save it in ([^ ]+)( as ([^ ]+))?)?",
            r"لقط الشاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?",
            r"صور الشاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?",
            r"خذ لقطة شاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?",
            r"صوّر الشاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?"
        ]
        for pattern in screenshot_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                folder = None
                filename = None
                # English: ...and save it in <folder> as <filename>
                if match.lastindex:
                    if match.lastindex >= 5 and match.group(5):
                        filename = match.group(5).strip()
                    if match.lastindex >= 3 and match.group(3):
                        folder = match.group(3).strip()
                # Arabic: ...في <folder> باسم <filename>
                if not filename and match.lastindex and match.lastindex >= 5 and match.group(5):
                    filename = match.group(5).strip()
                if not folder and match.lastindex and match.lastindex >= 3 and match.group(3):
                    folder = match.group(3).strip()
                # Expand user tilde if present
                if folder:
                    folder = os.path.expanduser(folder)
                # Build full path if folder/filename provided
                file_path = None
                if filename and folder:
                    os.makedirs(folder, exist_ok=True)
                    file_path = os.path.join(folder, filename)
                elif filename:
                    file_path = os.path.expanduser(filename)
                elif folder:
                    os.makedirs(folder, exist_ok=True)
                    dt = datetime.now().strftime('%Y%m%d-%H%M%S')
                    file_path = os.path.join(folder, f'screenshot-{dt}.png')
                params = {"action": "take_screenshot"}
                if file_path:
                    params["filename"] = file_path
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="screen_control",
                        params=params,
                        description=f"Take a screenshot and save to {file_path or 'default location'}",
                        required_tools=["screen_control"]
                    )],
                    description=f"Take a screenshot and save to {file_path or 'default location'}",
                    required_tools=["screen_control"]
                )
        # 3. Mouse
        mouse_patterns = [
            r"move mouse to (\d+),\s*(\d+)",
            r"click( at)? (\d+),\s*(\d+)",
            r"حرك الفأرة إلى (\d+),\s*(\d+)", r"انقر في (\d+),\s*(\d+)"
        ]
        for pattern in mouse_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                if 'move' in pattern or 'حرك' in pattern:
                    x, y = match.groups()[-2:]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="mouse",
                            params={"action": "move", "x": int(x), "y": int(y)},
                            description=f"Move mouse to {x},{y}",
                            required_tools=["mouse"]
                        )],
                        description=f"Move mouse to {x},{y}",
                        required_tools=["mouse"]
                    )
                elif 'click' in pattern or 'انقر' in pattern:
                    x, y = match.groups()[-2:]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="mouse",
                            params={"action": "click", "x": int(x), "y": int(y)},
                            description=f"Click at {x},{y}",
                            required_tools=["mouse"]
                        )],
                        description=f"Click at {x},{y}",
                        required_tools=["mouse"]
                    )
        # 4. Keyboard
        keyboard_patterns = [
            r"type ['\"](.+?)['\"]",
            r"press key ['\"]?(\w+)['\"]?",
            r"اكتب ['\"](.+?)['\"]", r"اضغط (زر|مفتاح) ['\"]?(\w+)['\"]?"
        ]
        for pattern in keyboard_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                if 'type' in pattern or 'اكتب' in pattern:
                    text = match.groups()[-1]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="keyboard_input",
                            params={"action": "type", "text": text},
                            description=f"Type '{text}'",
                            required_tools=["keyboard_input"]
                        )],
                        description=f"Type '{text}'",
                        required_tools=["keyboard_input"]
                    )
                elif 'press' in pattern or 'اضغط' in pattern:
                    key = match.groups()[-1]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="keyboard_input",
                            params={"action": "press", "key": key},
                            description=f"Press key '{key}'",
                            required_tools=["keyboard_input"]
                        )],
                        description=f"Press key '{key}'",
                        required_tools=["keyboard_input"]
                    )
        # 5. Clipboard
        clipboard_patterns = [
            r"copy (.+)", r"paste", r"what is on my clipboard",
            r"ما الموجود في الحافظة", r"انسخ (.+)", r"ألصق"
        ]
        for pattern in clipboard_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                if 'copy' in pattern or 'انسخ' in pattern:
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
                elif 'paste' in pattern or 'ألصق' in pattern:
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
        # 6. File/Folder (file creation logic, English & Arabic)
        file_create_patterns = [
            # English: Create a file called test.txt in folder mydir and write 'Hello'
            r"create (a )?file (called|named)? ['\"]?([^'\" ]+)['\"]?( in ([^ ]+))?( and write| with content)? ['\"]([^'\"]+)['\"]?",
            r"write ['\"]([^'\"]+)['\"]? to (a )?file (called|named)? ['\"]?([^'\" ]+)['\"]?( in ([^ ]+))?",
            # Arabic: اكتب ملف اسمه test.txt في mydir وضع فيه هذا نص تجريبي
            r"اكتب ملف اسمه ([^ ]+) في ([^ ]+) وضع فيه هذا (.+)",
            r"انشئ ملف باسم ([^ ]+) في ([^ ]+) واكتب فيه ['\"]?([^'\"]+)['\"]?",
            r"إنشاء ملف ([^ ]+) بالمحتوى ['\"]?([^'\"]+)['\"]?",
            r"اكتب ['\"]?([^'\"]+)['\"]? في ملف ([^ ]+)",
            # More dialectal/creative Arabic
            r"سوي لي ملف اسمه ([^ ]+) وحط فيه ['\"]?([^'\"]+)['\"]?",
            r"ابي ملف ([^ ]+) فيه ['\"]?([^'\"]+)['\"]?",
            r"خلي ملف ([^ ]+) يحتوي على ['\"]?([^'\"]+)['\"]?",
            r"اكتب في ملف ([^ ]+) النص ['\"]?([^'\"]+)['\"]?",
            r"جهز لي ملف ([^ ]+) واكتب فيه ['\"]?([^'\"]+)['\"]?"
        ]
        for pattern in file_create_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                # English patterns
                if 'create' in pattern or 'write' in pattern:
                    if 'and write' in pattern or 'with content' in pattern:
                        filename = match.group(3)
                        directory = match.group(5) if match.lastindex >= 5 else None
                        content = match.group(7)
                    elif 'to' in pattern:
                        content = match.group(1)
                        filename = match.group(4)
                        directory = match.group(6) if match.lastindex >= 6 else None
                    else:
                        filename = match.group(3)
                        directory = match.group(5) if match.lastindex >= 5 else None
                        content = match.group(7) if match.lastindex >= 7 else ''
                # Arabic patterns
                elif 'اكتب ملف اسمه' in pattern:
                    filename = match.group(1)
                    directory = match.group(2)
                    content = match.group(3)
                elif 'انشئ ملف باسم' in pattern:
                    filename = match.group(1)
                    directory = match.group(2)
                    content = match.group(3)
                elif 'إنشاء ملف' in pattern:
                    filename = match.group(1)
                    directory = None
                    content = match.group(2)
                elif 'اكتب' in pattern and 'في ملف' in pattern:
                    content = match.group(1)
                    filename = match.group(2)
                    directory = None
                elif 'سوي لي ملف اسمه' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'ابي ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'خلي ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'اكتب في ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'جهز لي ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                else:
                    continue
                # Build the path
                if not directory:
                    directory = self.main_folder
                path = f"{directory.rstrip('/')}/{filename}"
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="file",
                        params={"action": "create_file", "path": path, "content": content},
                        description=f"Create file {path} with content",
                        required_tools=["file"]
                    )],
                    description=f"Create file {path} with content",
                    required_tools=["file"]
                )
        # Last-chance fallback for file creation (Arabic/English)
        if ("ملف" in command or "file" in command) and ("اكتب" in command or "write" in command or "حط" in command or "ضع" in command or "contains" in command):
            # Try to extract filename and content
            filename_match = re.search(r"ملف(?: اسمه)? ([^ ]+)", command)
            if not filename_match:
                filename_match = re.search(r"file(?: called| named)? ([^ ]+)", command)
            content_match = re.search(r"(?:اكتب|حط|ضع|contains|with content|and write) ['\"]?([^'\"]+)['\"]?", command)
            filename = filename_match.group(1) if filename_match else "untitled.txt"
            content = content_match.group(1) if content_match else ""
            path = f"{self.main_folder.rstrip('/')}/{filename}"
            return MultiStepPlan(
                steps=[PlanStep(
                    action="file",
                    params={"action": "create_file", "path": path, "content": content},
                    description=f"Create file {path} with content (fallback)",
                    required_tools=["file"]
                )],
                description=f"Create file {path} with content (fallback)",
                required_tools=["file"]
            )
        # 7. Calculator
        calculator_patterns = [
            r"calculate (.+)", r"what is (.+)", r"احسب (.+)"
        ]
        for pattern in calculator_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                expr = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="calculator",
                        params={"action": "eval", "expression": expr},
                        description=f"Calculate '{expr}'",
                        required_tools=["calculator"]
                    )],
                    description=f"Calculate '{expr}'",
                    required_tools=["calculator"]
                )
        # 8. Ollama/LLM fallback
        # If no other tool matches, pass to ollama planner
        plan_dict = self.planner.plan(command, {})
        # Ensure the result is always a MultiStepPlan
        if isinstance(plan_dict, MultiStepPlan):
            return plan_dict
        elif isinstance(plan_dict, dict) and "tool" in plan_dict and "action" in plan_dict:
            params = plan_dict.get("params", {})
            if "action" not in params:
                params["action"] = plan_dict["action"]
            return MultiStepPlan(
                steps=[PlanStep(
                    action=plan_dict["tool"],
                    params=params,
                    description=f"Execute {plan_dict['tool']} with {params}",
                    required_tools=[plan_dict["tool"]]
                )],
                description=f"Execute {plan_dict['tool']} with {params}",
                required_tools=[plan_dict["tool"]]
            )
        else:
            raise ValueError("Planner did not return a valid plan or tool dict.")

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
        super().__init__(name="LabeebAgent")
        self.name = "LabeebAgent"
        self.logger = logging.getLogger("LabeebAgent")
        self.main_folder = os.path.expanduser("~/Documents/Labeeb/files_and_folders_tests")
        # Register all tools globally via ToolRegistry
        ToolRegistry.register(FileTool)
        ToolRegistry.register(SystemResourceTool)
        ToolRegistry.register(DateTimeTool)
        ToolRegistry.register(WeatherTool)
        ToolRegistry.register(CalculatorTool)
        ToolRegistry.register(KeyboardInputTool)
        ToolRegistry.register(FileAndDocumentOrganizerTool)
        ToolRegistry.register(CodePathUpdaterTool)
        ToolRegistry.register(AppControlTool)
        ToolRegistry.register(ClipboardTool)
        ToolRegistry.register(ScreenControlTool)

    def set_main_folder(self, folder_path: str):
        self.main_folder = os.path.expanduser(folder_path)

    async def plan(self, command: str) -> MultiStepPlan:
        self.logger.debug(f"Planning for command: {command}")
        # --- Robust, extensible, multi-language, multi-tool plan decomposition ---
        # 1. Vision/Image Analysis (expanded patterns)
        vision_patterns = [
            r"analyze the image ['\"]?([^'\" ]+)['\"]?.*",
            r"حلل الصورة ['\"]?([^'\" ]+)['\"]?.*",
            r"describe what you see on my screen",
            r"what is on my screen now",
            r"analyze my screen",
            r"what do you see on the screen",
            r"صف ما يظهر على الشاشة",
            r"ماذا ترى على الشاشة",
            r"حلل الشاشة",
            r"اعرض لي وصف الشاشة",
            r"ما الموجود في الصورة ['\"]?([^'\" ]+)['\"]?",
            r"صف الصورة ['\"]?([^'\" ]+)['\"]?"
        ]
        for pattern in vision_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                image_path = match.groups()[-1].strip("'\"") if match.groups() else None
                if image_path and not any(x in image_path for x in ["screen", "الشاشة"]):
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="vision",
                            params={"action": "analyze_image", "image_path": image_path},
                            description=f"Analyze image {image_path}",
                            required_tools=["vision"]
                        )],
                        description=f"Analyze image {image_path}",
                        required_tools=["vision"]
                    )
                else:
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="vision",
                            params={"action": "analyze_image"},
                            description="Analyze the current screen",
                            required_tools=["vision"]
                        )],
                        description="Analyze the current screen",
                        required_tools=["vision"]
                    )
        # 2. Screenshot (robust filename/folder extraction)
        screenshot_patterns = [
            r"take (a )?screenshot( and save it in ([^ ]+)( as ([^ ]+))?)?",
            r"capture (a )?screenshot( and save it in ([^ ]+)( as ([^ ]+))?)?",
            r"get (a )?screenshot( and save it in ([^ ]+)( as ([^ ]+))?)?",
            r"لقط الشاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?",
            r"صور الشاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?",
            r"خذ لقطة شاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?",
            r"صوّر الشاشة( و(حفظها|خزنها) في ([^ ]+)( باسم ([^ ]+))?)?"
        ]
        for pattern in screenshot_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                folder = None
                filename = None
                # English: ...and save it in <folder> as <filename>
                if match.lastindex:
                    if match.lastindex >= 5 and match.group(5):
                        filename = match.group(5).strip()
                    if match.lastindex >= 3 and match.group(3):
                        folder = match.group(3).strip()
                # Arabic: ...في <folder> باسم <filename>
                if not filename and match.lastindex and match.lastindex >= 5 and match.group(5):
                    filename = match.group(5).strip()
                if not folder and match.lastindex and match.lastindex >= 3 and match.group(3):
                    folder = match.group(3).strip()
                # Expand user tilde if present
                if folder:
                    folder = os.path.expanduser(folder)
                # Build full path if folder/filename provided
                file_path = None
                if filename and folder:
                    os.makedirs(folder, exist_ok=True)
                    file_path = os.path.join(folder, filename)
                elif filename:
                    file_path = os.path.expanduser(filename)
                elif folder:
                    os.makedirs(folder, exist_ok=True)
                    dt = datetime.now().strftime('%Y%m%d-%H%M%S')
                    file_path = os.path.join(folder, f'screenshot-{dt}.png')
                params = {"action": "take_screenshot"}
                if file_path:
                    params["filename"] = file_path
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="screen_control",
                        params=params,
                        description=f"Take a screenshot and save to {file_path or 'default location'}",
                        required_tools=["screen_control"]
                    )],
                    description=f"Take a screenshot and save to {file_path or 'default location'}",
                    required_tools=["screen_control"]
                )
        # 3. Mouse
        mouse_patterns = [
            r"move mouse to (\d+),\s*(\d+)",
            r"click( at)? (\d+),\s*(\d+)",
            r"حرك الفأرة إلى (\d+),\s*(\d+)", r"انقر في (\d+),\s*(\d+)"
        ]
        for pattern in mouse_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                if 'move' in pattern or 'حرك' in pattern:
                    x, y = match.groups()[-2:]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="mouse",
                            params={"action": "move", "x": int(x), "y": int(y)},
                            description=f"Move mouse to {x},{y}",
                            required_tools=["mouse"]
                        )],
                        description=f"Move mouse to {x},{y}",
                        required_tools=["mouse"]
                    )
                elif 'click' in pattern or 'انقر' in pattern:
                    x, y = match.groups()[-2:]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="mouse",
                            params={"action": "click", "x": int(x), "y": int(y)},
                            description=f"Click at {x},{y}",
                            required_tools=["mouse"]
                        )],
                        description=f"Click at {x},{y}",
                        required_tools=["mouse"]
                    )
        # 4. Keyboard
        keyboard_patterns = [
            r"type ['\"](.+?)['\"]",
            r"press key ['\"]?(\w+)['\"]?",
            r"اكتب ['\"](.+?)['\"]", r"اضغط (زر|مفتاح) ['\"]?(\w+)['\"]?"
        ]
        for pattern in keyboard_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                if 'type' in pattern or 'اكتب' in pattern:
                    text = match.groups()[-1]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="keyboard_input",
                            params={"action": "type", "text": text},
                            description=f"Type '{text}'",
                            required_tools=["keyboard_input"]
                        )],
                        description=f"Type '{text}'",
                        required_tools=["keyboard_input"]
                    )
                elif 'press' in pattern or 'اضغط' in pattern:
                    key = match.groups()[-1]
                    return MultiStepPlan(
                        steps=[PlanStep(
                            action="keyboard_input",
                            params={"action": "press", "key": key},
                            description=f"Press key '{key}'",
                            required_tools=["keyboard_input"]
                        )],
                        description=f"Press key '{key}'",
                        required_tools=["keyboard_input"]
                    )
        # 5. Clipboard
        clipboard_patterns = [
            r"copy (.+)", r"paste", r"what is on my clipboard",
            r"ما الموجود في الحافظة", r"انسخ (.+)", r"ألصق"
        ]
        for pattern in clipboard_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                if 'copy' in pattern or 'انسخ' in pattern:
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
                elif 'paste' in pattern or 'ألصق' in pattern:
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
        # 6. File/Folder (file creation logic, English & Arabic)
        file_create_patterns = [
            # English: Create a file called test.txt in folder mydir and write 'Hello'
            r"create (a )?file (called|named)? ['\"]?([^'\" ]+)['\"]?( in ([^ ]+))?( and write| with content)? ['\"]([^'\"]+)['\"]?",
            r"write ['\"]([^'\"]+)['\"]? to (a )?file (called|named)? ['\"]?([^'\" ]+)['\"]?( in ([^ ]+))?",
            # Arabic: اكتب ملف اسمه test.txt في mydir وضع فيه هذا نص تجريبي
            r"اكتب ملف اسمه ([^ ]+) في ([^ ]+) وضع فيه هذا (.+)",
            r"انشئ ملف باسم ([^ ]+) في ([^ ]+) واكتب فيه ['\"]?([^'\"]+)['\"]?",
            r"إنشاء ملف ([^ ]+) بالمحتوى ['\"]?([^'\"]+)['\"]?",
            r"اكتب ['\"]?([^'\"]+)['\"]? في ملف ([^ ]+)",
            # More dialectal/creative Arabic
            r"سوي لي ملف اسمه ([^ ]+) وحط فيه ['\"]?([^'\"]+)['\"]?",
            r"ابي ملف ([^ ]+) فيه ['\"]?([^'\"]+)['\"]?",
            r"خلي ملف ([^ ]+) يحتوي على ['\"]?([^'\"]+)['\"]?",
            r"اكتب في ملف ([^ ]+) النص ['\"]?([^'\"]+)['\"]?",
            r"جهز لي ملف ([^ ]+) واكتب فيه ['\"]?([^'\"]+)['\"]?"
        ]
        for pattern in file_create_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                # English patterns
                if 'create' in pattern or 'write' in pattern:
                    if 'and write' in pattern or 'with content' in pattern:
                        filename = match.group(3)
                        directory = match.group(5) if match.lastindex >= 5 else None
                        content = match.group(7)
                    elif 'to' in pattern:
                        content = match.group(1)
                        filename = match.group(4)
                        directory = match.group(6) if match.lastindex >= 6 else None
                    else:
                        filename = match.group(3)
                        directory = match.group(5) if match.lastindex >= 5 else None
                        content = match.group(7) if match.lastindex >= 7 else ''
                # Arabic patterns
                elif 'اكتب ملف اسمه' in pattern:
                    filename = match.group(1)
                    directory = match.group(2)
                    content = match.group(3)
                elif 'انشئ ملف باسم' in pattern:
                    filename = match.group(1)
                    directory = match.group(2)
                    content = match.group(3)
                elif 'إنشاء ملف' in pattern:
                    filename = match.group(1)
                    directory = None
                    content = match.group(2)
                elif 'اكتب' in pattern and 'في ملف' in pattern:
                    content = match.group(1)
                    filename = match.group(2)
                    directory = None
                elif 'سوي لي ملف اسمه' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'ابي ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'خلي ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'اكتب في ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                elif 'جهز لي ملف' in pattern:
                    filename = match.group(1)
                    content = match.group(2)
                    directory = None
                else:
                    continue
                # Build the path
                if not directory:
                    directory = self.main_folder
                path = f"{directory.rstrip('/')}/{filename}"
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="file",
                        params={"action": "create_file", "path": path, "content": content},
                        description=f"Create file {path} with content",
                        required_tools=["file"]
                    )],
                    description=f"Create file {path} with content",
                    required_tools=["file"]
                )
        # Last-chance fallback for file creation (Arabic/English)
        if ("ملف" in command or "file" in command) and ("اكتب" in command or "write" in command or "حط" in command or "ضع" in command or "contains" in command):
            # Try to extract filename and content
            filename_match = re.search(r"ملف(?: اسمه)? ([^ ]+)", command)
            if not filename_match:
                filename_match = re.search(r"file(?: called| named)? ([^ ]+)", command)
            content_match = re.search(r"(?:اكتب|حط|ضع|contains|with content|and write) ['\"]?([^'\"]+)['\"]?", command)
            filename = filename_match.group(1) if filename_match else "untitled.txt"
            content = content_match.group(1) if content_match else ""
            path = f"{self.main_folder.rstrip('/')}/{filename}"
            return MultiStepPlan(
                steps=[PlanStep(
                    action="file",
                    params={"action": "create_file", "path": path, "content": content},
                    description=f"Create file {path} with content (fallback)",
                    required_tools=["file"]
                )],
                description=f"Create file {path} with content (fallback)",
                required_tools=["file"]
            )
        # 7. Calculator
        calculator_patterns = [
            r"calculate (.+)", r"what is (.+)", r"احسب (.+)"
        ]
        for pattern in calculator_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                expr = match.groups()[-1]
                return MultiStepPlan(
                    steps=[PlanStep(
                        action="calculator",
                        params={"action": "eval", "expression": expr},
                        description=f"Calculate '{expr}'",
                        required_tools=["calculator"]
                    )],
                    description=f"Calculate '{expr}'",
                    required_tools=["calculator"]
                )
        # 8. Ollama/LLM fallback
        # If no other tool matches, pass to ollama planner
        plan_dict = self.planner.plan(command, {})
        # Ensure the result is always a MultiStepPlan
        if isinstance(plan_dict, MultiStepPlan):
            return plan_dict
        elif isinstance(plan_dict, dict) and "tool" in plan_dict and "action" in plan_dict:
            params = plan_dict.get("params", {})
            if "action" not in params:
                params["action"] = plan_dict["action"]
            return MultiStepPlan(
                steps=[PlanStep(
                    action=plan_dict["tool"],
                    params=params,
                    description=f"Execute {plan_dict['tool']} with {params}",
                    required_tools=[plan_dict["tool"]]
                )],
                description=f"Execute {plan_dict['tool']} with {params}",
                required_tools=[plan_dict["tool"]]
            )
        else:
            raise ValueError("Planner did not return a valid plan or tool dict.")

    async def execute(self, plan: MultiStepPlan) -> Any:
        self.logger.debug(f"Executing plan: {plan}")
        result = await self._execute_plan(plan)
        self.logger.debug(f"Execution result: {result}")
        return result

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