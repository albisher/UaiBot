import logging
from typing import Dict, Any, List, Optional, Tuple
from app.agent_tools.base_tool import BaseAgentTool
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class MouseControlTool(BaseAgentTool):
    """Tool for controlling mouse input with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mouse control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._platform_manager = None
        self._platform_info = None
        self._handlers = None
        self._mouse_handler = None
        self._move_speed = config.get('move_speed', 1.0)
        self._click_delay = config.get('click_delay', 0.1)
        self._double_click_delay = config.get('double_click_delay', 0.2)
        self._scroll_speed = config.get('scroll_speed', 1.0)
    
    def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._platform_manager = PlatformManager()
            self._platform_info = self._platform_manager.get_platform_info()
            self._handlers = self._platform_manager.get_handlers()
            self._mouse_handler = self._handlers.get('mouse')
            if not self._mouse_handler:
                logger.error("Mouse handler not found")
                return False
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MouseControlTool: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._platform_manager = None
            self._platform_info = None
            self._handlers = None
            self._mouse_handler = None
            self._initialized = False
        except Exception as e:
            logger.error(f"Error cleaning up MouseControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        return {
            'move': True,
            'click': True,
            'double_click': True,
            'right_click': True,
            'drag': True,
            'scroll': True,
            'get_position': True,
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
            'move_speed': self._move_speed,
            'click_delay': self._click_delay,
            'double_click_delay': self._double_click_delay,
            'scroll_speed': self._scroll_speed
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
            if command == 'move_to':
                return self._move_to(args)
            elif command == 'click':
                return self._click(args)
            elif command == 'double_click':
                return self._double_click(args)
            elif command == 'right_click':
                return self._right_click(args)
            elif command == 'drag':
                return self._drag(args)
            elif command == 'scroll':
                return self._scroll(args)
            elif command == 'get_position':
                return self._get_position()
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
            'move_to',
            'click',
            'double_click',
            'right_click',
            'drag',
            'scroll',
            'get_position'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        """Get help information for a specific command.
        
        Args:
            command: Command name to get help for
            
        Returns:
            Dict[str, Any]: Help information for the command
        """
        help_info = {
            'move_to': {
                'description': 'Move mouse cursor to specified coordinates',
                'args': {
                    'x': 'X coordinate (int)',
                    'y': 'Y coordinate (int)',
                    'relative': 'Optional boolean to use relative coordinates'
                }
            },
            'click': {
                'description': 'Perform a mouse click',
                'args': {
                    'button': 'Optional button to click (left, right, middle)'
                }
            },
            'double_click': {
                'description': 'Perform a double click',
                'args': {
                    'button': 'Optional button to click (left, right, middle)'
                }
            },
            'right_click': {
                'description': 'Perform a right click',
                'args': {}
            },
            'drag': {
                'description': 'Perform a drag operation',
                'args': {
                    'start_x': 'Start X coordinate',
                    'start_y': 'Start Y coordinate',
                    'end_x': 'End X coordinate',
                    'end_y': 'End Y coordinate',
                    'button': 'Optional button to use (left, right, middle)'
                }
            },
            'scroll': {
                'description': 'Perform a scroll operation',
                'args': {
                    'amount': 'Amount to scroll (positive for up, negative for down)',
                    'horizontal': 'Optional boolean to scroll horizontally'
                }
            },
            'get_position': {
                'description': 'Get current mouse cursor position',
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
        
        if command == 'move_to':
            if not args or 'x' not in args or 'y' not in args:
                return False
            if not isinstance(args['x'], int) or not isinstance(args['y'], int):
                return False
        
        elif command == 'drag':
            if not args or not all(k in args for k in ['start_x', 'start_y', 'end_x', 'end_y']):
                return False
            if not all(isinstance(args[k], int) for k in ['start_x', 'start_y', 'end_x', 'end_y']):
                return False
        
        elif command == 'scroll':
            if not args or 'amount' not in args:
                return False
            if not isinstance(args['amount'], (int, float)):
                return False
        
        return True
    
    def _move_to(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Move mouse cursor to specified coordinates.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            x = args['x']
            y = args['y']
            relative = args.get('relative', False)
            
            self._mouse_handler.move_to(x, y, relative)
            return {
                'status': 'success',
                'x': x,
                'y': y,
                'relative': relative,
                'action': 'move'
            }
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            return {'error': str(e)}
    
    def _click(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a mouse click.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            button = args.get('button', 'left')
            self._mouse_handler.click(button)
            return {
                'status': 'success',
                'button': button,
                'action': 'click'
            }
        except Exception as e:
            logger.error(f"Error clicking mouse: {e}")
            return {'error': str(e)}
    
    def _double_click(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a double click.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            button = args.get('button', 'left')
            self._mouse_handler.double_click(button)
            return {
                'status': 'success',
                'button': button,
                'action': 'double_click'
            }
        except Exception as e:
            logger.error(f"Error double clicking mouse: {e}")
            return {'error': str(e)}
    
    def _right_click(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a right click.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            self._mouse_handler.right_click()
            return {
                'status': 'success',
                'action': 'right_click'
            }
        except Exception as e:
            logger.error(f"Error right clicking mouse: {e}")
            return {'error': str(e)}
    
    def _drag(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a drag operation.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            start_x = args['start_x']
            start_y = args['start_y']
            end_x = args['end_x']
            end_y = args['end_y']
            button = args.get('button', 'left')
            
            self._mouse_handler.drag(start_x, start_y, end_x, end_y, button)
            return {
                'status': 'success',
                'start': (start_x, start_y),
                'end': (end_x, end_y),
                'button': button,
                'action': 'drag'
            }
        except Exception as e:
            logger.error(f"Error dragging mouse: {e}")
            return {'error': str(e)}
    
    def _scroll(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a scroll operation.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            amount = args['amount']
            horizontal = args.get('horizontal', False)
            
            self._mouse_handler.scroll(amount, horizontal)
            return {
                'status': 'success',
                'amount': amount,
                'horizontal': horizontal,
                'action': 'scroll'
            }
        except Exception as e:
            logger.error(f"Error scrolling mouse: {e}")
            return {'error': str(e)}
    
    def _get_position(self) -> Dict[str, Any]:
        """Get current mouse cursor position.
        
        Returns:
            Dict[str, Any]: Current position information
        """
        try:
            x, y = self._mouse_handler.get_position()
            return {
                'status': 'success',
                'x': x,
                'y': y,
                'action': 'get_position'
            }
        except Exception as e:
            logger.error(f"Error getting mouse position: {e}")
            return {'error': str(e)} 