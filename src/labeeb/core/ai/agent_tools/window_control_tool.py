"""
Window control tool with A2A, MCP, and SmolAgents compliance.

This tool provides window control functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import platform
from typing import Dict, Any, List, Optional, Union
import pyautogui
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class WindowControlTool(BaseTool):
    """Tool for controlling windows with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the window control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="window_control",
            description="Tool for controlling windows with platform-specific optimizations",
            config=config
        )
        self._platform = platform.system().lower()
        self._window_list = []
        self._active_window = None
        self._window_positions = {}
        self._window_sizes = {}
    
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
            
            # Get initial window list
            await self._refresh_window_list()
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize WindowControlTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._window_list = []
            self._active_window = None
            self._window_positions = {}
            self._window_sizes = {}
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up WindowControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'list_windows': True,
            'activate_window': True,
            'move_window': True,
            'resize_window': True,
            'minimize_window': True,
            'maximize_window': True,
            'close_window': True,
            'get_window_info': True
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
            'window_count': len(self._window_list),
            'active_window': self._active_window,
            'window_positions': self._window_positions,
            'window_sizes': self._window_sizes
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
        if command == 'list_windows':
            return await self._list_windows()
        elif command == 'activate_window':
            return await self._activate_window(args)
        elif command == 'move_window':
            return await self._move_window(args)
        elif command == 'resize_window':
            return await self._resize_window(args)
        elif command == 'minimize_window':
            return await self._minimize_window(args)
        elif command == 'maximize_window':
            return await self._maximize_window(args)
        elif command == 'close_window':
            return await self._close_window(args)
        elif command == 'get_window_info':
            return await self._get_window_info(args)
        else:
            return {'error': f'Unknown command: {command}'}
    
    async def _refresh_window_list(self) -> None:
        """Refresh the list of windows."""
        try:
            # Get window list based on platform
            if self._platform == 'darwin':
                # macOS specific window listing
                import Quartz
                window_list = []
                for window in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID):
                    if window.get(Quartz.kCGWindowLayer, 0) == 0:
                        window_list.append({
                            'id': window.get(Quartz.kCGWindowNumber, 0),
                            'title': window.get(Quartz.kCGWindowName, ''),
                            'owner': window.get(Quartz.kCGWindowOwnerName, ''),
                            'bounds': window.get(Quartz.kCGWindowBounds, {})
                        })
            elif self._platform == 'windows':
                # Windows specific window listing
                import win32gui
                window_list = []
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        windows.append({
                            'id': hwnd,
                            'title': win32gui.GetWindowText(hwnd),
                            'owner': win32gui.GetClassName(hwnd),
                            'bounds': win32gui.GetWindowRect(hwnd)
                        })
                    return True
                win32gui.EnumWindows(enum_windows_callback, window_list)
            else:
                # Linux specific window listing
                import Xlib.display
                display = Xlib.display.Display()
                root = display.screen().root
                window_list = []
                for window in root.query_tree().children:
                    if window.get_wm_name():
                        window_list.append({
                            'id': window.id,
                            'title': window.get_wm_name(),
                            'owner': window.get_wm_class()[0] if window.get_wm_class() else '',
                            'bounds': window.get_geometry()
                        })
            
            self._window_list = window_list
        except Exception as e:
            logger.error(f"Error refreshing window list: {e}")
    
    async def _list_windows(self) -> Dict[str, Any]:
        """Get list of windows.
        
        Returns:
            Dict[str, Any]: List of windows
        """
        try:
            await self._refresh_window_list()
            return {
                'status': 'success',
                'action': 'list_windows',
                'windows': self._window_list
            }
        except Exception as e:
            logger.error(f"Error listing windows: {e}")
            return {'error': str(e)}
    
    async def _activate_window(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Activate a window.
        
        Args:
            args: Window activation arguments
            
        Returns:
            Dict[str, Any]: Result of window activation
        """
        try:
            if not args or 'window_id' not in args:
                return {'error': 'Missing window_id parameter'}
            
            window_id = args['window_id']
            
            # Activate window based on platform
            if self._platform == 'darwin':
                import Quartz
                Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)
            elif self._platform == 'windows':
                import win32gui
                win32gui.SetForegroundWindow(window_id)
            else:
                import Xlib.display
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                window.set_input_focus()
            
            self._active_window = window_id
            return {
                'status': 'success',
                'action': 'activate_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error activating window: {e}")
            return {'error': str(e)}
    
    async def _move_window(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Move a window to a new position.
        
        Args:
            args: Window move arguments
            
        Returns:
            Dict[str, Any]: Result of window move
        """
        try:
            if not args or 'window_id' not in args or 'x' not in args or 'y' not in args:
                return {'error': 'Missing required parameters'}
            
            window_id = args['window_id']
            x = args['x']
            y = args['y']
            
            # Move window based on platform
            if self._platform == 'darwin':
                import Quartz
                window = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)[0]
                bounds = window.get(Quartz.kCGWindowBounds, {})
                bounds['X'] = x
                bounds['Y'] = y
                Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)
            elif self._platform == 'windows':
                import win32gui
                win32gui.MoveWindow(window_id, x, y, 0, 0, True)
            else:
                import Xlib.display
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                window.configure(x=x, y=y)
            
            self._window_positions[window_id] = (x, y)
            return {
                'status': 'success',
                'action': 'move_window',
                'window_id': window_id,
                'position': (x, y)
            }
        except Exception as e:
            logger.error(f"Error moving window: {e}")
            return {'error': str(e)}
    
    async def _resize_window(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resize a window.
        
        Args:
            args: Window resize arguments
            
        Returns:
            Dict[str, Any]: Result of window resize
        """
        try:
            if not args or 'window_id' not in args or 'width' not in args or 'height' not in args:
                return {'error': 'Missing required parameters'}
            
            window_id = args['window_id']
            width = args['width']
            height = args['height']
            
            # Resize window based on platform
            if self._platform == 'darwin':
                import Quartz
                window = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)[0]
                bounds = window.get(Quartz.kCGWindowBounds, {})
                bounds['Width'] = width
                bounds['Height'] = height
                Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)
            elif self._platform == 'windows':
                import win32gui
                x, y = self._window_positions.get(window_id, (0, 0))
                win32gui.MoveWindow(window_id, x, y, width, height, True)
            else:
                import Xlib.display
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                window.configure(width=width, height=height)
            
            self._window_sizes[window_id] = (width, height)
            return {
                'status': 'success',
                'action': 'resize_window',
                'window_id': window_id,
                'size': (width, height)
            }
        except Exception as e:
            logger.error(f"Error resizing window: {e}")
            return {'error': str(e)}
    
    async def _minimize_window(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Minimize a window.
        
        Args:
            args: Window minimize arguments
            
        Returns:
            Dict[str, Any]: Result of window minimize
        """
        try:
            if not args or 'window_id' not in args:
                return {'error': 'Missing window_id parameter'}
            
            window_id = args['window_id']
            
            # Minimize window based on platform
            if self._platform == 'darwin':
                import Quartz
                Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)
            elif self._platform == 'windows':
                import win32gui
                win32gui.ShowWindow(window_id, win32gui.SW_MINIMIZE)
            else:
                import Xlib.display
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                window.iconify()
            
            return {
                'status': 'success',
                'action': 'minimize_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")
            return {'error': str(e)}
    
    async def _maximize_window(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Maximize a window.
        
        Args:
            args: Window maximize arguments
            
        Returns:
            Dict[str, Any]: Result of window maximize
        """
        try:
            if not args or 'window_id' not in args:
                return {'error': 'Missing window_id parameter'}
            
            window_id = args['window_id']
            
            # Maximize window based on platform
            if self._platform == 'darwin':
                import Quartz
                Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)
            elif self._platform == 'windows':
                import win32gui
                win32gui.ShowWindow(window_id, win32gui.SW_MAXIMIZE)
            else:
                import Xlib.display
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                window.configure(state='zoomed')
            
            return {
                'status': 'success',
                'action': 'maximize_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error maximizing window: {e}")
            return {'error': str(e)}
    
    async def _close_window(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Close a window.
        
        Args:
            args: Window close arguments
            
        Returns:
            Dict[str, Any]: Result of window close
        """
        try:
            if not args or 'window_id' not in args:
                return {'error': 'Missing window_id parameter'}
            
            window_id = args['window_id']
            
            # Close window based on platform
            if self._platform == 'darwin':
                import Quartz
                Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)
            elif self._platform == 'windows':
                import win32gui
                win32gui.PostMessage(window_id, win32gui.WM_CLOSE, 0, 0)
            else:
                import Xlib.display
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                window.send_event(display.icccm_wm_protocols('WM_DELETE_WINDOW'))
            
            # Remove window from tracking
            if window_id in self._window_positions:
                del self._window_positions[window_id]
            if window_id in self._window_sizes:
                del self._window_sizes[window_id]
            if self._active_window == window_id:
                self._active_window = None
            
            return {
                'status': 'success',
                'action': 'close_window',
                'window_id': window_id
            }
        except Exception as e:
            logger.error(f"Error closing window: {e}")
            return {'error': str(e)}
    
    async def _get_window_info(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get information about a window.
        
        Args:
            args: Window info arguments
            
        Returns:
            Dict[str, Any]: Window information
        """
        try:
            if not args or 'window_id' not in args:
                return {'error': 'Missing window_id parameter'}
            
            window_id = args['window_id']
            
            # Get window info based on platform
            if self._platform == 'darwin':
                import Quartz
                window = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, window_id)[0]
                info = {
                    'id': window.get(Quartz.kCGWindowNumber, 0),
                    'title': window.get(Quartz.kCGWindowName, ''),
                    'owner': window.get(Quartz.kCGWindowOwnerName, ''),
                    'bounds': window.get(Quartz.kCGWindowBounds, {}),
                    'layer': window.get(Quartz.kCGWindowLayer, 0),
                    'alpha': window.get(Quartz.kCGWindowAlpha, 1.0)
                }
            elif self._platform == 'windows':
                import win32gui
                info = {
                    'id': window_id,
                    'title': win32gui.GetWindowText(window_id),
                    'owner': win32gui.GetClassName(window_id),
                    'bounds': win32gui.GetWindowRect(window_id),
                    'style': win32gui.GetWindowLong(window_id, win32gui.GWL_STYLE),
                    'ex_style': win32gui.GetWindowLong(window_id, win32gui.GWL_EXSTYLE)
                }
            else:
                import Xlib.display
                display = Xlib.display.Display()
                window = display.create_resource_object('window', window_id)
                info = {
                    'id': window.id,
                    'title': window.get_wm_name(),
                    'owner': window.get_wm_class()[0] if window.get_wm_class() else '',
                    'bounds': window.get_geometry(),
                    'state': window.get_wm_state(),
                    'protocols': window.get_wm_protocols()
                }
            
            return {
                'status': 'success',
                'action': 'get_window_info',
                'window_id': window_id,
                'info': info
            }
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return {'error': str(e)} 