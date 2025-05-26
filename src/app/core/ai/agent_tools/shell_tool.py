"""
ShellTool: Cross-platform shell command execution tool for Labeeb.
All platform-specific logic is delegated to PlatformManager (see platform_core/platform_manager.py).

A2A, MCP, SmolAgents compliant: This tool is minimal, composable, and delegates all platform-specific logic to PlatformManager.
"""
from app.core.ai.tools.base_tool import LabeebTool
import subprocess
import shlex
from app.platform_core.platform_manager import PlatformManager

class ShellTool(LabeebTool):
    name = "shell"
    def __init__(self, safe_mode=True, enable_dangerous_command_check=True, debug=False):
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        self.debug = debug
        self.platform_manager = PlatformManager()

    def execute(self, action: str, params: dict) -> any:
        debug = params.get('debug', self.debug)
        if action == 'execute':
            command = params.get('command')
            if not command:
                return "No command provided."
            try:
                if debug:
                    print(f"[DEBUG] ShellTool executing: {command}")
                # Use platform manager for shell execution
                return self.platform_manager.execute_shell_command(command, debug=debug)
            except Exception as e:
                return f"ShellTool error: {e}"
        elif action == 'safety_check':
            command = params.get('command')
            if not command:
                return "No command provided."
            return self.platform_manager.safety_check(command)
        elif action == 'detect_target':
            command = params.get('command', '')
            context = params.get('context', '')
            return self.platform_manager.detect_target(command, context)
        elif action == 'list_usb':
            return self.platform_manager.list_usb_devices()
        elif action == 'browser_content':
            browser_name = params.get('browser_name')
            return self.platform_manager.get_browser_content(browser_name)
        else:
            return f"Unknown shell tool action: {action}" 