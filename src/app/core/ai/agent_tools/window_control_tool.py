import logging
from typing import Dict, Any, List, Optional, Tuple
from app.agent_tools.base_tool import BaseAgentTool
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class WindowControlTool(BaseAgentTool):
    """Tool for controlling window operations with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the window control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._platform_manager = None
        self._platform_info = None
        self._handlers = None
        self._window_handler = None
        self._min_window_size = config.get('min_window_size', (100, 100))
        self._max_window_size = config.get('max_window_size', (3840, 2160))
        self._animation_duration = config.get('animation_duration', 0.3)
        self._focus_delay = config.get('focus_delay', 0.1)
    
    def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._platform_manager = PlatformManager()
            self._platform_info = self._platform_manager.get_platform_info()
            self._handlers = self._platform_manager.get_handlers()
            self._window_handler = self._handlers.get('window')
            if not self._window_handler:
                logger.error("Window handler not found")
                return False
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WindowControlTool: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._platform_manager = None
            self._platform_info = None
            self._handlers = None
            self._window_handler = None
            self._initialized = False
        except Exception as e:
            logger.error(f"Error cleaning up WindowControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        return {
            'list_windows': True,
            'get_active_window': True,
            'activate_window': True,
            'move_window': True,
            'resize_window': True,
            'minimize_window': True,
            'maximize_window': True,
            'restore_window': True,
            'close_window': True,
            'get_window_info': True,
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
            'min_window_size': self._min_window_size,
            'max_window_size': self._max_window_size,
            'animation_duration': self._animation_duration,
            'focus_delay': self._focus_delay
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
            if command == 'list_windows':
                return self._list_windows()
            elif command == 'get_active_window':
                return self._get_active_window()
            elif command == 'activate_window':
                return self._activate_window(args)
            elif command == 'move_window':
                return self._move_window(args)
            elif command == 'resize_window':
                return self._resize_window(args)
            elif command == 'minimize_window':
                return self._minimize_window(args)
            elif command == 'maximize_window':
                return self._maximize_window(args)
            elif command == 'restore_window':
                return self._restore_window(args)
            elif command == 'close_window':
                return self._close_window(args)
            elif command == 'get_window_info':
                return self._get_window_info(args)
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
            'list_windows',
            'get_active_window',
            'activate_window',
            'move_window',
            'resize_window',
            'minimize_window',
            'maximize_window',
            'restore_window',
            'close_window',
            'get_window_info'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        """Get help information for a specific command.
        
        Args:
            command: Command name to get help for
            
        Returns:
            Dict[str, Any]: Help information for the command
        """
        help_info = {
            'list_windows': {
                'description': 'Get list of all windows',
                'args': {}
            },
            'get_active_window': {
                'description': 'Get information about the currently active window',
                'args': {}
            },
            'activate_window': {
                'description': 'Activate a window by its handle or title',
                'args': {
                    'window_id': 'Window handle or title'
                }
            },
            'move_window': {
                'description': 'Move a window to specified coordinates',
                'args': {
                    'window_id': 'Window handle or title',
                    'x': 'X coordinate',
                    'y': 'Y coordinate'
                }
            },
            'resize_window': {
                'description': 'Resize a window to specified dimensions',
                'args': {
                    'window_id': 'Window handle or title',
                    'width': 'Window width',
                    'height': 'Window height'
                }
            },
            'minimize_window': {
                'description': 'Minimize a window',
                'args': {
                    'window_id': 'Window handle or title'
                }
            },
            'maximize_window': {
                'description': 'Maximize a window',
                'args': {
                    'window_id': 'Window handle or title'
                }
            },
            'restore_window': {
                'description': 'Restore a window from minimized or maximized state',
                'args': {
                    'window_id': 'Window handle or title'
                }
            },
            'close_window': {
                'description': 'Close a window',
                'args': {
                    'window_id': 'Window handle or title'
                }
            },
            'get_window_info': {
                'description': 'Get detailed information about a window',
                'args': {
                    'window_id': 'Window handle or title'
                }
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
        
        if command in ['activate_window', 'minimize_window', 'maximize_window', 'restore_window', 'close_window', 'get_window_info']:
            if not args or 'window_id' not in args:
                return False
            if not isinstance(args['window_id'], (int, str)):
                return False
        
        elif command == 'move_window':
            if not args or not all(k in args for k in ['window_id', 'x', 'y']):
                return False
            if not isinstance(args['window_id'], (int, str)):
                return False
            if not isinstance(args['x'], int) or not isinstance(args['y'], int):
                return False
        
        elif command == 'resize_window':
            if not args or not all(k in args for k in ['window_id', 'width', 'height']):
                return False
            if not isinstance(args['window_id'], (int, str)):
                return False
            if not isinstance(args['width'], int) or not isinstance(args['height'], int):
                return False
            if args['width'] < self._min_window_size[0] or args['height'] < self._min_window_size[1]:
                return False
            if args['width'] > self._max_window_size[0] or args['height'] > self._max_window_size[1]:
                return False
        
        return True
    
    def _list_windows(self) -> Dict[str, Any]:
        """Get list of all windows.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            windows = self._window_handler.list_windows()
            return {
                'status': 'success',
                'action': 'list_windows',
                'windows': windows,
                'count': len(windows)
            }
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            return {'error': str(e)}
    
    def _get_active_window(self) -> Dict[str, Any]:
        """Get information about the currently active window.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window = self._window_handler.get_active_window()
            return {
                'status': 'success',
                'action': 'get_active_window',
                'window': window
            }
        except Exception as e:
            logger.error(f"Error getting active window: {e}")
            return {'error': str(e)}
    
    def _activate_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a window by its handle or title.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            self._window_handler.activate_window(window_id)
            return {
                'status': 'success',
                'action': 'activate_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error activating window: {e}")
            return {'error': str(e)}
    
    def _move_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Move a window to specified coordinates.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            x = args['x']
            y = args['y']
            
            self._window_handler.move_window(window_id, x, y)
            return {
                'status': 'success',
                'action': 'move_window',
                'window_id': window_id,
                'position': (x, y)
            }
        except Exception as e:
            logger.error(f"Error moving window: {e}")
            return {'error': str(e)}
    
    def _resize_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Resize a window to specified dimensions.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            width = args['width']
            height = args['height']
            
            self._window_handler.resize_window(window_id, width, height)
            return {
                'status': 'success',
                'action': 'resize_window',
                'window_id': window_id,
                'size': (width, height)
            }
        except Exception as e:
            logger.error(f"Error resizing window: {e}")
            return {'error': str(e)}
    
    def _minimize_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Minimize a window.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            self._window_handler.minimize_window(window_id)
            return {
                'status': 'success',
                'action': 'minimize_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")
            return {'error': str(e)}
    
    def _maximize_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Maximize a window.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            self._window_handler.maximize_window(window_id)
            return {
                'status': 'success',
                'action': 'maximize_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error maximizing window: {e}")
            return {'error': str(e)}
    
    def _restore_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Restore a window from minimized or maximized state.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            self._window_handler.restore_window(window_id)
            return {
                'status': 'success',
                'action': 'restore_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error restoring window: {e}")
            return {'error': str(e)}
    
    def _close_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Close a window.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            self._window_handler.close_window(window_id)
            return {
                'status': 'success',
                'action': 'close_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error closing window: {e}")
            return {'error': str(e)}
    
    def _get_window_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a window.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            window_id = args['window_id']
            info = self._window_handler.get_window_info(window_id)
            return {
                'status': 'success',
                'action': 'get_window_info',
                'window_id': window_id,
                'info': info
            }
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return {'error': str(e)} 