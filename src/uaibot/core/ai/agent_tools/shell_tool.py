from uaibot.core.ai.tool_base import Tool
import subprocess
import shlex
import platform
from uaibot.utils import get_platform_name
from uaibot.core.device_manager.usb_detector import USBDetector
from uaibot.core.browser_handler import BrowserHandler
from uaibot.core.file_search import FileSearch

class ShellTool(Tool):
    name = "shell"
    def __init__(self, safe_mode=True, enable_dangerous_command_check=True, debug=False):
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        self.debug = debug
        self.system_platform = platform.system().lower()
        self.platform_name = get_platform_name()
        self.usb_detector = USBDetector(quiet_mode=not debug)
        self.browser_handler = BrowserHandler()
        self.file_search = FileSearch(quiet_mode=not debug)

    def execute(self, action: str, params: dict) -> any:
        debug = params.get('debug', self.debug)
        if action == 'execute':
            command = params.get('command')
            if not command:
                return "No command provided."
            try:
                if debug:
                    print(f"[DEBUG] ShellTool executing: {command}")
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return result.stderr or f"Command failed with return code {result.returncode}"
                return result.stdout
            except Exception as e:
                return f"ShellTool error: {e}"
        elif action == 'safety_check':
            command = params.get('command')
            if not command:
                return "No command provided."
            # Simple safety: block rm -rf / and similar
            dangerous = ['rm -rf /', 'mkfs', 'dd if=', 'shutdown', 'reboot']
            for d in dangerous:
                if d in command:
                    return {"safe": False, "reason": f"Dangerous pattern detected: {d}"}
            return {"safe": True}
        elif action == 'detect_target':
            command = params.get('command', '')
            context = params.get('context', '')
            # Simple logic: if 'screen' or 'usb' in context, return SCREEN
            if any(x in context.lower() for x in ['screen', 'usb', 'device']):
                return 'SCREEN'
            return 'LOCAL'
        elif action == 'list_usb':
            return self.usb_detector.get_usb_devices()
        elif action == 'browser_content':
            browser_name = params.get('browser_name')
            return self.browser_handler.get_browser_content(browser_name)
        else:
            return f"Unknown shell tool action: {action}" 