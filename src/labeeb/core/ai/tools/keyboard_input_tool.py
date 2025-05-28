"""
KeyboardInputTool: Simulates keyboard input for the Labeeb agent, enabling automation of typing and keyboard shortcuts.

This tool provides keyboard input functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
from typing import Dict, Any, List, Optional, Union
import pyautogui
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class KeyboardInputTool(BaseTool):
    """Tool for simulating keyboard input with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the keyboard input tool.
        
        Args:
            config: Optional configuration dictionary
        """
        if config is None:
            config = {}
        super().__init__(
            name="keyboard_input",
            description="Tool for simulating keyboard input with platform-specific optimizations",
            config=config
        )
        self._typing_speed = config.get('typing_speed', 0.1)  # seconds between keystrokes
        self._key_press_delay = config.get('key_press_delay', 0.1)  # seconds to hold key
        self._last_key = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Configure PyAutoGUI
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize KeyboardInputTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._last_key = None
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up KeyboardInputTool: {e}")
    
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
            'hotkey': True
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
            'last_key': self._last_key
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
        if command == 'type':
            return await self._type_text(args)
        elif command == 'press':
            return await self._press_key(args)
        elif command == 'hold':
            return await self._hold_key(args)
        elif command == 'release':
            return await self._release_key(args)
        elif command == 'hotkey':
            return await self._press_hotkey(args)
        else:
            return {'error': f'Unknown command: {command}'}
    
    async def _type_text(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Type text at the current cursor position.
        
        Args:
            args: Text typing arguments
            
        Returns:
            Dict[str, Any]: Result of text typing
        """
        try:
            if not args or 'text' not in args:
                return {'error': 'Missing text parameter'}
            
            text = args['text']
            interval = args.get('interval', self._typing_speed)
            
            pyautogui.write(text, interval=interval)
            
            return {
                'status': 'success',
                'action': 'type',
                'text': text
            }
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return {'error': str(e)}
    
    async def _press_key(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Press and release a key.
        
        Args:
            args: Key press arguments
            
        Returns:
            Dict[str, Any]: Result of key press
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing key parameter'}
            
            key = args['key']
            self._last_key = key
            
            pyautogui.press(key)
            
            return {
                'status': 'success',
                'action': 'press',
                'key': key
            }
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return {'error': str(e)}
    
    async def _hold_key(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Hold down a key.
        
        Args:
            args: Key hold arguments
            
        Returns:
            Dict[str, Any]: Result of key hold
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing key parameter'}
            
            key = args['key']
            self._last_key = key
            
            pyautogui.keyDown(key)
            
            return {
                'status': 'success',
                'action': 'hold',
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
            Dict[str, Any]: Result of key release
        """
        try:
            if not args or 'key' not in args:
                return {'error': 'Missing key parameter'}
            
            key = args['key']
            self._last_key = None
            
            pyautogui.keyUp(key)
            
            return {
                'status': 'success',
                'action': 'release',
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
            Dict[str, Any]: Result of hotkey press
        """
        try:
            if not args or 'keys' not in args:
                return {'error': 'Missing keys parameter'}
            
            keys = args['keys']
            if not isinstance(keys, (list, tuple)):
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