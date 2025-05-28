"""
ShellTool: Cross-platform shell command execution tool for Labeeb.
All platform-specific logic is delegated to PlatformManager (see platform_core/platform_manager.py).

A2A, MCP, SmolAgents compliant: This tool is minimal, composable, and delegates all platform-specific logic to PlatformManager.
"""
from labeeb.core.ai.tools.base_tool import BaseTool
import subprocess
import shlex
import os
import platform
from typing import Dict, Any, Optional, List
from labeeb.core.platform_core.platform_manager import PlatformManager
from labeeb.core.exceptions import CommandError, SecurityError
import arabic_reshaper
from bidi.algorithm import get_display

class ShellTool(BaseTool):
    """Enhanced shell tool with multi-language support and platform-specific optimizations."""
    
    def __init__(self, safe_mode: bool = True, enable_dangerous_command_check: bool = True, debug: bool = False):
        """Initialize the shell tool with safety features."""
        super().__init__(
            name="shell",
            description={
                'en': "Execute shell commands with safety checks and platform-specific optimizations",
                'ar': "تنفيذ أوامر الشل مع فحوصات الأمان وتحسينات خاصة بالمنصة"
            }
        )
        self.safe_mode = safe_mode
        self.enable_dangerous_command_check = enable_dangerous_command_check
        self.debug = debug
        self.platform_manager = PlatformManager()
        self._current_platform = platform.system().lower()
        self._supported_platforms = ['darwin', 'linux', 'windows']
        
        # Initialize platform-specific settings
        self._init_platform_settings()
        
    def _init_platform_settings(self) -> None:
        """Initialize platform-specific settings and capabilities."""
        self.platform_capabilities = {
            'darwin': {
                'shell': '/bin/zsh',
                'env': {'LANG': 'en_US.UTF-8'},
                'dangerous_commands': ['rm -rf', 'mkfs', 'dd if='],
                'safe_commands': ['ls', 'pwd', 'echo', 'cat', 'grep']
            },
            'linux': {
                'shell': '/bin/bash',
                'env': {'LANG': 'en_US.UTF-8'},
                'dangerous_commands': ['rm -rf', 'mkfs', 'dd if='],
                'safe_commands': ['ls', 'pwd', 'echo', 'cat', 'grep']
            },
            'windows': {
                'shell': 'cmd.exe',
                'env': {'LANG': 'en_US.UTF-8'},
                'dangerous_commands': ['format', 'del /s /q', 'rd /s /q'],
                'safe_commands': ['dir', 'cd', 'echo', 'type', 'findstr']
            }
        }
        
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if a command is potentially dangerous."""
        if not self.enable_dangerous_command_check:
            return False
            
        platform_dangerous = self.platform_capabilities.get(self._current_platform, {}).get('dangerous_commands', [])
        return any(dangerous in command.lower() for dangerous in platform_dangerous)
        
    def _is_safe_command(self, command: str) -> bool:
        """Check if a command is in the safe list."""
        platform_safe = self.platform_capabilities.get(self._current_platform, {}).get('safe_commands', [])
        return any(safe in command.lower() for safe in platform_safe)
        
    def _process_command(self, command: str) -> str:
        """Process command for platform-specific requirements."""
        if self._current_platform == 'windows':
            # Windows-specific command processing
            return command
        else:
            # Unix-like systems
            return shlex.quote(command)
            
    def _format_output(self, output: str, language: str = 'en') -> str:
        """Format command output based on language."""
        if language == 'ar':
            # Process Arabic text
            output = arabic_reshaper.reshape(output)
            output = get_display(output)
        return output
        
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a shell tool action with enhanced error handling and multi-language support."""
        params = kwargs
        debug = params.get('debug', self.debug)
        language = params.get('language', 'en')
        
        try:
            if action == 'execute':
                command = params.get('command')
                if not command:
                    return {"status": "error", "message": self._format_output("No command provided.", language)}
                    
                if self.safe_mode and not self._is_safe_command(command):
                    if self._is_dangerous_command(command):
                        raise SecurityError("Potentially dangerous command detected")
                    return {"status": "error", "message": self._format_output("Command not in safe list", language)}
                    
                try:
                    if debug:
                        print(f"[DEBUG] ShellTool executing: {command}")
                        
                    # Process command for platform
                    processed_command = self._process_command(command)
                    
                    # Execute using platform manager
                    result = self.platform_manager.execute_shell_command(processed_command, debug=debug)
                    
                    # Format output based on language
                    return {
                        "status": "success",
                        "message": self._format_output(result, language)
                    }
                    
                except subprocess.CalledProcessError as e:
                    return {
                        "status": "error",
                        "message": self._format_output(f"Command failed: {e.output.decode()}", language)
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "message": self._format_output(f"ShellTool error: {str(e)}", language)
                    }
                    
            elif action == 'safety_check':
                command = params.get('command')
                if not command:
                    return {"status": "error", "message": self._format_output("No command provided.", language)}
                return {"status": "success", "result": self.platform_manager.safety_check(command)}
                
            elif action == 'detect_target':
                command = params.get('command', '')
                context = params.get('context', '')
                return {"status": "success", "result": self.platform_manager.detect_target(command, context)}
                
            elif action == 'list_usb':
                return {"status": "success", "result": self.platform_manager.list_usb_devices()}
                
            elif action == 'browser_content':
                browser_name = params.get('browser_name')
                return {"status": "success", "result": self.platform_manager.get_browser_content(browser_name)}
                
            else:
                return {
                    "status": "error",
                    "message": self._format_output(f"Unknown shell tool action: {action}", language)
                }
                
        except SecurityError as e:
            return {
                "status": "error",
                "message": self._format_output(f"Security error: {str(e)}", language)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": self._format_output(f"Unexpected error: {str(e)}", language)
            }
            
    def get_available_actions(self) -> Dict[str, str]:
        """Get available actions for this tool."""
        return {
            'execute': 'Execute a shell command',
            'safety_check': 'Check if a command is safe to execute',
            'detect_target': 'Detect the target of a command',
            'list_usb': 'List connected USB devices',
            'browser_content': 'Get browser content'
        } 