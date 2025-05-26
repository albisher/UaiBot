import logging
from typing import Dict, Any, List, Optional
from app.agent_tools.base_tool import BaseAgentTool
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class KeyboardControlTool(BaseAgentTool):
    """Tool for controlling keyboard input with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the keyboard control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._platform_manager = None
        self._platform_info = None
        self._handlers = None
        self._keyboard_handler = None
        self._key_delay = config.get('key_delay', 0.1)
        self._key_press_duration = config.get('key_press_duration', 0.1)
        self._modifier_keys = config.get('modifier_keys', {
            'ctrl': 'control',
            'alt': 'alt',
            'shift': 'shift',
            'cmd': 'command',
            'win': 'windows'
        })
    
    def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._platform_manager = PlatformManager()
            self._platform_info = self._platform_manager.get_platform_info()
            self._handlers = self._platform_manager.get_handlers()
            self._keyboard_handler = self._handlers.get('keyboard')
            if not self._keyboard_handler:
                logger.error("Keyboard handler not found")
                return False
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize KeyboardControlTool: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._platform_manager = None
            self._platform_info = None
            self._handlers = None
            self._keyboard_handler = None
            self._initialized = False
        except Exception as e:
            logger.error(f"Error cleaning up KeyboardControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        return {
            'key_press': True,
            'key_release': True,
            'key_combination': True,
            'text_input': True,
            'hotkey_support': True,
            'platform_specific_optimization': bool(self._platform_info)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        return {
            'initialized': self._initialized,
            'platform': self._platform_info.get('name') if self._platform_info else None,
            'key_delay': self._key_delay,
            'key_press_duration': self._key_press_duration,
            'modifier_keys': self._modifier_keys
        }
    
    def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command using this tool.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if not self._initialized:
            return {'error': 'Tool not initialized'}
        
        try:
            if command == 'press_key':
                return self._press_key(args)
            elif command == 'release_key':
                return self._release_key(args)
            elif command == 'type_text':
                return self._type_text(args)
            elif command == 'press_hotkey':
                return self._press_hotkey(args)
            elif command == 'get_keyboard_layout':
                return self._get_keyboard_layout()
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return {'error': str(e)}
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands for this tool.
        
        Returns:
            List[str]: List of available command names
        """
        return [
            'press_key',
            'release_key',
            'type_text',
            'press_hotkey',
            'get_keyboard_layout'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        """Get help information for a specific command.
        
        Args:
            command: Command name to get help for
            
        Returns:
            Dict[str, Any]: Help information for the command
        """
        help_info = {
            'press_key': {
                'description': 'Press a single key',
                'args': {
                    'key': 'Key to press (e.g., "a", "enter", "space")'
                }
            },
            'release_key': {
                'description': 'Release a single key',
                'args': {
                    'key': 'Key to release (e.g., "a", "enter", "space")'
                }
            },
            'type_text': {
                'description': 'Type a text string',
                'args': {
                    'text': 'Text to type'
                }
            },
            'press_hotkey': {
                'description': 'Press a combination of keys',
                'args': {
                    'keys': 'List of keys to press (e.g., ["ctrl", "c"])'
                }
            },
            'get_keyboard_layout': {
                'description': 'Get current keyboard layout information',
                'args': {}
            }
        }
        return help_info.get(command, {'error': f'Unknown command: {command}'})
    
    def validate_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> bool:
        """Validate if a command and its arguments are valid.
        
        Args:
            command: Command to validate
            args: Optional arguments to validate
            
        Returns:
            bool: True if command and arguments are valid, False otherwise
        """
        if command not in self.get_available_commands():
            return False
        
        if command in ['press_key', 'release_key']:
            if not args or 'key' not in args:
                return False
            if not isinstance(args['key'], str):
                return False
        
        elif command == 'type_text':
            if not args or 'text' not in args:
                return False
            if not isinstance(args['text'], str):
                return False
        
        elif command == 'press_hotkey':
            if not args or 'keys' not in args:
                return False
            if not isinstance(args['keys'], list):
                return False
            if not all(isinstance(key, str) for key in args['keys']):
                return False
        
        return True
    
    def _press_key(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Press a single key.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            key = args['key']
            self._keyboard_handler.press_key(key)
            return {
                'status': 'success',
                'key': key,
                'action': 'press'
            }
        except Exception as e:
            logger.error(f"Error pressing key: {e}")
            return {'error': str(e)}
    
    def _release_key(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Release a single key.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            key = args['key']
            self._keyboard_handler.release_key(key)
            return {
                'status': 'success',
                'key': key,
                'action': 'release'
            }
        except Exception as e:
            logger.error(f"Error releasing key: {e}")
            return {'error': str(e)}
    
    def _type_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Type a text string.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            text = args['text']
            self._keyboard_handler.type_text(text)
            return {
                'status': 'success',
                'text': text,
                'action': 'type'
            }
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return {'error': str(e)}
    
    def _press_hotkey(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Press a combination of keys.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            keys = args['keys']
            self._keyboard_handler.press_hotkey(keys)
            return {
                'status': 'success',
                'keys': keys,
                'action': 'hotkey'
            }
        except Exception as e:
            logger.error(f"Error pressing hotkey: {e}")
            return {'error': str(e)}
    
    def _get_keyboard_layout(self) -> Dict[str, Any]:
        """Get current keyboard layout information.
        
        Returns:
            Dict[str, Any]: Keyboard layout information
        """
        try:
            layout = self._keyboard_handler.get_keyboard_layout()
            return {
                'status': 'success',
                'layout': layout
            }
        except Exception as e:
            logger.error(f"Error getting keyboard layout: {e}")
            return {'error': str(e)} 