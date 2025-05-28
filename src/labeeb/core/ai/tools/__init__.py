"""
Tools module for Labeeb AI system.

This module provides various tools that can be used by AI agents to perform tasks.
"""
from .tool_registry import ToolRegistry

# Import tools
from .file_tool import FileTool
from .web_tool import WebTool
from .system_tool import SystemTool
from .datetime_tool import DateTimeTool
from .file_and_document_organizer_tool import FileAndDocumentOrganizerTool
from .code_path_updater_tool import CodePathUpdaterTool
from .graph_maker_tool import GraphMakerTool
from .clipboard_tool import ClipboardTool
from .calculator_tools import CalculatorTool
from src.app.core.platform_core.app_control_tool import AppControlTool
from .vision_tool import VisionTool
from .screen_control_tool import ScreenControlTool

# Re-register all tools to ensure correct .name registration after registry fix
ToolRegistry.register(FileTool)
ToolRegistry.register(WebTool)
ToolRegistry.register(SystemTool)
ToolRegistry.register(DateTimeTool)
ToolRegistry.register(FileAndDocumentOrganizerTool)
ToolRegistry.register(CodePathUpdaterTool)
ToolRegistry.register(GraphMakerTool)
ToolRegistry.register(ClipboardTool)
ToolRegistry.register(CalculatorTool)
ToolRegistry.register(AppControlTool)
ToolRegistry.register(VisionTool)
ToolRegistry.register(ScreenControlTool)
