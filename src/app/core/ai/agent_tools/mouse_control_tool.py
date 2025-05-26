"""
Mouse control tool with A2A, MCP, and SmolAgents compliance.

This tool provides mouse control functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import platform
from typing import Dict, Any, List, Optional, Union, Tuple
import pyautogui
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class MouseControlTool(BaseTool):
    """Tool for controlling mouse input with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mouse control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="mouse_control",
            description="Tool for controlling mouse input with platform-specific optimizations",
            config=config
        )
        self._platform = platform.system().lower()
        self._movement_speed = config.get('movement_speed', 0.5)
        self._click_delay = config.get('click_delay', 0.1)
        self._fail_safe = config.get('fail_safe', True)
        self._safety_margin = config.get('safety_margin', 10)
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = self._fail_safe
        pyautogui.PAUSE = self._click_delay
    
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
            logger.error(f"Failed to initialize MouseControlTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            # Reset PyAutoGUI settings
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up MouseControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'move': True,
            'click': True,
            'double_click': True,
            'right_click': True,
            'drag': True,
            'scroll': True,
            'get_position': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'platform': self._platform,
            'movement_speed': self._movement_speed,
            'click_delay': self._click_delay,
            'fail_safe': self._fail_safe,
            'safety_margin': self._safety_margin,
            'current_position': pyautogui.position()
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
        if command == 'move':
            return await self._move_mouse(args)
        elif command == 'click':
            return await self._click_mouse(args)
        elif command == 'double_click':
            return await self._double_click_mouse(args)
        elif command == 'right_click':
            return await self._right_click_mouse(args)
        elif command == 'drag':
            return await self._drag_mouse(args)
        elif command == 'scroll':
            return await self._scroll_mouse(args)
        elif command == 'get_position':
            return await self._get_mouse_position()
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _validate_position(self, x: int, y: int) -> Tuple[int, int]:
        """Validate and adjust mouse position to stay within safe bounds.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple[int, int]: Validated coordinates
        """
        screen_width, screen_height = pyautogui.size()
        x = max(self._safety_margin, min(x, screen_width - self._safety_margin))
        y = max(self._safety_margin, min(y, screen_height - self._safety_margin))
        return x, y
    
    async def _move_mouse(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Move the mouse to a position.
        
        Args:
            args: Movement arguments
            
        Returns:
            Dict[str, Any]: Result of mouse movement
        """
        try:
            if not args or 'x' not in args or 'y' not in args:
                return {'error': 'Missing x or y parameter'}
            
            x = args['x']
            y = args['y']
            duration = args.get('duration', self._movement_speed)
            
            # Validate position
            x, y = self._validate_position(x, y)
            
            # Move mouse
            pyautogui.moveTo(x, y, duration=duration)
            
            return {
                'status': 'success',
                'action': 'move',
                'position': (x, y),
                'duration': duration
            }
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
            return {'error': str(e)}
    
    async def _click_mouse(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Click the mouse at current position.
        
        Args:
            args: Click arguments
            
        Returns:
            Dict[str, Any]: Result of mouse click
        """
        try:
            button = args.get('button', 'left') if args else 'left'
            clicks = args.get('clicks', 1) if args else 1
            interval = args.get('interval', self._click_delay) if args else self._click_delay
            
            pyautogui.click(button=button, clicks=clicks, interval=interval)
            
            return {
                'status': 'success',
                'action': 'click',
                'button': button,
                'clicks': clicks,
                'interval': interval
            }
        except Exception as e:
            logger.error(f"Error clicking mouse: {e}")
            return {'error': str(e)}
    
    async def _double_click_mouse(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Double click the mouse at current position.
        
        Args:
            args: Double click arguments
            
        Returns:
            Dict[str, Any]: Result of mouse double click
        """
        try:
            button = args.get('button', 'left') if args else 'left'
            interval = args.get('interval', self._click_delay) if args else self._click_delay
            
            pyautogui.doubleClick(button=button, interval=interval)
            
            return {
                'status': 'success',
                'action': 'double_click',
                'button': button,
                'interval': interval
            }
        except Exception as e:
            logger.error(f"Error double clicking mouse: {e}")
            return {'error': str(e)}
    
    async def _right_click_mouse(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Right click the mouse at current position.
        
        Args:
            args: Right click arguments
            
        Returns:
            Dict[str, Any]: Result of mouse right click
        """
        try:
            interval = args.get('interval', self._click_delay) if args else self._click_delay
            
            pyautogui.rightClick(interval=interval)
            
            return {
                'status': 'success',
                'action': 'right_click',
                'interval': interval
            }
        except Exception as e:
            logger.error(f"Error right clicking mouse: {e}")
            return {'error': str(e)}
    
    async def _drag_mouse(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Drag the mouse from current position to target position.
        
        Args:
            args: Drag arguments
            
        Returns:
            Dict[str, Any]: Result of mouse drag
        """
        try:
            if not args or 'x' not in args or 'y' not in args:
                return {'error': 'Missing x or y parameter'}
            
            x = args['x']
            y = args['y']
            duration = args.get('duration', self._movement_speed)
            button = args.get('button', 'left')
            
            # Validate position
            x, y = self._validate_position(x, y)
            
            # Drag mouse
            pyautogui.dragTo(x, y, duration=duration, button=button)
            
            return {
                'status': 'success',
                'action': 'drag',
                'position': (x, y),
                'duration': duration,
                'button': button
            }
        except Exception as e:
            logger.error(f"Error dragging mouse: {e}")
            return {'error': str(e)}
    
    async def _scroll_mouse(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scroll the mouse wheel.
        
        Args:
            args: Scroll arguments
            
        Returns:
            Dict[str, Any]: Result of mouse scroll
        """
        try:
            if not args or 'clicks' not in args:
                return {'error': 'Missing clicks parameter'}
            
            clicks = args['clicks']
            x = args.get('x')
            y = args.get('y')
            
            if x is not None and y is not None:
                # Validate position
                x, y = self._validate_position(x, y)
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                pyautogui.scroll(clicks)
            
            return {
                'status': 'success',
                'action': 'scroll',
                'clicks': clicks,
                'position': (x, y) if x is not None and y is not None else None
            }
        except Exception as e:
            logger.error(f"Error scrolling mouse: {e}")
            return {'error': str(e)}
    
    async def _get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse position.
        
        Returns:
            Dict[str, Any]: Current mouse position
        """
        try:
            x, y = pyautogui.position()
            return {
                'status': 'success',
                'action': 'get_position',
                'position': (x, y)
            }
        except Exception as e:
            logger.error(f"Error getting mouse position: {e}")
            return {'error': str(e)} 