"""
Keyboard control tool with A2A, MCP, and SmolAgents compliance.

This tool provides keyboard control functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import platform
from typing import Dict, Any, List, Optional, Union
import pyautogui
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class KeyboardControlTool(BaseTool):
    """Tool for controlling keyboard input with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the keyboard control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="keyboard_control",
            description="Tool for controlling keyboard input with platform-specific optimizations",
            config=config
        )
        self._typing_speed = config.get('typing_speed', 0.1)
        self._key_press_delay = config.get('key_press_delay', 0.1)
        self._fail_safe = config.get('fail_safe', True)
        self._platform = platform.system().lower()
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = self._fail_safe
        pyautogui.PAUSE = self._key_press_delay
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Configure platform-specific settings
            if self._platform == 'darwin':
                pyautogui.MAC_OS = True
            elif self._platform == 'windows':
                pyautogui.WINDOWS = True
            elif self._platform == 'linux':
                pyautogui.LINUX = True
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize KeyboardControlTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            # Reset PyAutoGUI settings
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up KeyboardControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'type_text': True,
            'press_key': True,
            'hold_key': True,
            'release_key': True,
            'hotkey': True,
            'get_platform': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'typing_speed': self._typing_speed,
            'key_press_delay': self._key_press_delay,
            'fail_safe': self._fail_safe,
            'platform': self._platform
        }
        return {**base_status, **tool_status}
    
    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific command.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if command == 'type_text':
            return await self._type_text(args)
        elif command == 'press_key':
            return await self._press_key(args)
        elif command == 'hold_key':
            return await self._hold_key(args)
        elif command == 'release_key':
            return await self._release_key(args)
        elif command == 'hotkey':
            return await self._press_hotkey(args)
        elif command == 'get_platform':
            return await self._get_platform()
        else:
            return {'error': f'Unknown command: {command}'}
    
    async def _type_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Type text using the keyboard.
        
        Args:
            args: Typing arguments
            
        Returns:
            Dict[str, Any]: Result of typing operation
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text parameter'}
            
            text = args['text']
            interval = args.get('interval', self._typing_speed)
            
            pyautogui.write(text, interval=interval)
            
            return {
                'status': 'success',
                'action': 'type_text',
                'text': text,
                'interval': interval
            }
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return {'error': str(e)}
    
    async def _press_key(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Press a key.
        
        Args:
            args: Key press arguments
            
        Returns:
            Dict[str, Any]: Result of key press operation
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing key parameter'}
            
            key = args['key']
            pyautogui.press(key)
            
            return {
                'status': 'success',
                'action': 'press_key',
                'key': key
            }
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return {'error': str(e)}
    
    async def _hold_key(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Hold a key down.
        
        Args:
            args: Key hold arguments
            
        Returns:
            Dict[str, Any]: Result of key hold operation
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing key parameter'}
            
            key = args['key']
            pyautogui.keyDown(key)
            
            return {
                'status': 'success',
                'action': 'hold_key',
                'key': key
            }
        except Exception as e:
            logger.error(f"Error holding key: {e}")
            return {'error': str(e)}
    
    async def _release_key(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Release a held key.
        
        Args:
            args: Key release arguments
            
        Returns:
            Dict[str, Any]: Result of key release operation
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing key parameter'}
            
            key = args['key']
            pyautogui.keyUp(key)
            
            return {
                'status': 'success',
                'action': 'release_key',
                'key': key
            }
        except Exception as e:
            logger.error(f"Error releasing key: {e}")
            return {'error': str(e)}
    
    async def _press_hotkey(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Press a combination of keys.
        
        Args:
            args: Hotkey arguments
            
        Returns:
            Dict[str, Any]: Result of hotkey operation
        """
        try:
            if not args or 'keys' not in args:
                return {'error': 'Missing keys parameter'}
            
            keys = args['keys']
            if not isinstance(keys, list):
                keys = [keys]
            
            pyautogui.hotkey(*keys)
            
            return {
                'status': 'success',
                'action': 'hotkey',
                'keys': keys
            }
        except Exception as e:
            logger.error(f"Error pressing hotkey: {e}")
            return {'error': str(e)}
    
    async def _get_platform(self) -> Dict[str, Any]:
        """Get the current platform information.
        
        Returns:
            Dict[str, Any]: Platform information
        """
        try:
            return {
                'status': 'success',
                'action': 'get_platform',
                'platform': self._platform,
                'pyautogui_platform': {
                    'mac_os': pyautogui.MAC_OS,
                    'windows': pyautogui.WINDOWS,
                    'linux': pyautogui.LINUX
                }
            }
        except Exception as e:
            logger.error(f"Error getting platform info: {e}")
            return {'error': str(e)} 