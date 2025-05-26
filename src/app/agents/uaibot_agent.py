"""
Labeeb Agent Implementation

This module implements the main Labeeb agent class.
"""

import logging
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent
from ..agent_tools.base_tool import BaseAgentTool
from ..platform_core.ui_interface import UIInterface
from ..platform_core.net_interface import NetInterface
from ..platform_core.fs_interface import FSInterface
from ..platform_core.audio_interface import AudioInterface

logger = logging.getLogger(__name__)

class LabeebAgent(BaseAgent):
    """Labeeb agent implementation that follows A2A, MCP, and SmolAgents patterns."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Labeeb agent.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._ui_interface = None
        self._net_interface = None
        self._fs_interface = None
        self._audio_interface = None
    
    def initialize(self) -> bool:
        """Initialize the Labeeb agent.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize platform interfaces
            self._ui_interface = UIInterface(self._config.get('ui', {}))
            self._net_interface = NetInterface(self._config.get('net', {}))
            self._fs_interface = FSInterface(self._config.get('fs', {}))
            self._audio_interface = AudioInterface(self._config.get('audio', {}))
            
            # Initialize base agent
            if not super().initialize():
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Labeeb agent: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up Labeeb agent resources."""
        try:
            # Clean up platform interfaces
            if self._ui_interface:
                self._ui_interface.cleanup()
            if self._net_interface:
                self._net_interface.cleanup()
            if self._fs_interface:
                self._fs_interface.cleanup()
            if self._audio_interface:
                self._audio_interface.cleanup()
            
            # Clean up base agent
            super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up Labeeb agent: {e}")
    
    def _register_default_tools(self) -> None:
        """Register default tools for the Labeeb agent."""
        # Register platform-specific tools
        self._register_platform_tools()
        
        # Register agent-specific tools
        self._register_agent_tools()
    
    def _register_platform_tools(self) -> None:
        """Register platform-specific tools."""
        # UI tools
        self.register_tool(UITool, {'interface': self._ui_interface})
        
        # Network tools
        self.register_tool(NetworkTool, {'interface': self._net_interface})
        
        # File system tools
        self.register_tool(FileSystemTool, {'interface': self._fs_interface})
        
        # Audio tools
        self.register_tool(AudioTool, {'interface': self._audio_interface})
    
    def _register_agent_tools(self) -> None:
        """Register agent-specific tools."""
        # Agent-specific tools will be implemented here
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the Labeeb agent.
        
        Returns:
            Dict[str, Any]: Dictionary containing agent information
        """
        info = super().get_agent_info()
        info.update({
            'platform_interfaces': {
                'ui': bool(self._ui_interface),
                'net': bool(self._net_interface),
                'fs': bool(self._fs_interface),
                'audio': bool(self._audio_interface)
            }
        })
        return info

# Platform-specific tool implementations
class UITool(BaseAgentTool):
    """Tool for UI operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._interface = config.get('interface')
    
    def initialize(self) -> bool:
        return bool(self._interface)
    
    def cleanup(self) -> None:
        pass
    
    def get_capabilities(self) -> Dict[str, bool]:
        return self._interface.get_capabilities() if self._interface else {}
    
    def get_status(self) -> Dict[str, Any]:
        return self._interface.get_status() if self._interface else {'error': 'Not initialized'}
    
    def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._interface:
            return {'error': 'Not initialized'}
        
        try:
            if command == 'get_screen_info':
                return self._interface.get_screen_info()
            elif command == 'get_window_list':
                return self._interface.get_window_list()
            elif command == 'get_window_info':
                return self._interface.get_window_info(args.get('window_id', ''))
            elif command == 'get_active_window':
                return self._interface.get_active_window()
            elif command == 'get_mouse_position':
                return {'position': self._interface.get_mouse_position()}
            elif command == 'get_keyboard_layout':
                return {'layout': self._interface.get_keyboard_layout()}
            elif command == 'get_clipboard_content':
                return {'content': self._interface.get_clipboard_content()}
            elif command == 'set_clipboard_content':
                return {'success': self._interface.set_clipboard_content(args.get('content', ''))}
            elif command == 'get_ui_theme':
                return self._interface.get_ui_theme()
            elif command == 'get_ui_scale':
                return {'scale': self._interface.get_ui_scale()}
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_available_commands(self) -> List[str]:
        return [
            'get_screen_info',
            'get_window_list',
            'get_window_info',
            'get_active_window',
            'get_mouse_position',
            'get_keyboard_layout',
            'get_clipboard_content',
            'set_clipboard_content',
            'get_ui_theme',
            'get_ui_scale'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        help_info = {
            'get_screen_info': {
                'description': 'Get information about all screens/displays',
                'args': {}
            },
            'get_window_list': {
                'description': 'Get list of all windows',
                'args': {}
            },
            'get_window_info': {
                'description': 'Get information about a specific window',
                'args': {'window_id': 'Window identifier'}
            },
            'get_active_window': {
                'description': 'Get information about the currently active window',
                'args': {}
            },
            'get_mouse_position': {
                'description': 'Get current mouse cursor position',
                'args': {}
            },
            'get_keyboard_layout': {
                'description': 'Get current keyboard layout',
                'args': {}
            },
            'get_clipboard_content': {
                'description': 'Get current clipboard content',
                'args': {}
            },
            'set_clipboard_content': {
                'description': 'Set clipboard content',
                'args': {'content': 'Content to set in clipboard'}
            },
            'get_ui_theme': {
                'description': 'Get current UI theme information',
                'args': {}
            },
            'get_ui_scale': {
                'description': 'Get current UI scaling factor',
                'args': {}
            }
        }
        return help_info.get(command, {'error': f'Unknown command: {command}'})
    
    def validate_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> bool:
        if command not in self.get_available_commands():
            return False
        
        if command == 'get_window_info' and not args.get('window_id'):
            return False
        
        if command == 'set_clipboard_content' and 'content' not in args:
            return False
        
        return True

class NetworkTool(BaseAgentTool):
    """Tool for network operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._interface = config.get('interface')
    
    def initialize(self) -> bool:
        return bool(self._interface)
    
    def cleanup(self) -> None:
        pass
    
    def get_capabilities(self) -> Dict[str, bool]:
        return self._interface.get_capabilities() if self._interface else {}
    
    def get_status(self) -> Dict[str, Any]:
        return self._interface.get_status() if self._interface else {'error': 'Not initialized'}
    
    def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._interface:
            return {'error': 'Not initialized'}
        
        try:
            if command == 'get_interfaces':
                return self._interface.get_interfaces()
            elif command == 'get_interface_info':
                return self._interface.get_interface_info(args.get('interface_id', ''))
            elif command == 'get_connections':
                return self._interface.get_connections()
            elif command == 'get_connection_info':
                return self._interface.get_connection_info(args.get('connection_id', ''))
            elif command == 'get_routes':
                return self._interface.get_routes()
            elif command == 'get_dns_servers':
                return self._interface.get_dns_servers()
            elif command == 'get_hostname':
                return {'hostname': self._interface.get_hostname()}
            elif command == 'get_ip_addresses':
                return self._interface.get_ip_addresses()
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_available_commands(self) -> List[str]:
        return [
            'get_interfaces',
            'get_interface_info',
            'get_connections',
            'get_connection_info',
            'get_routes',
            'get_dns_servers',
            'get_hostname',
            'get_ip_addresses'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        help_info = {
            'get_interfaces': {
                'description': 'Get list of network interfaces',
                'args': {}
            },
            'get_interface_info': {
                'description': 'Get information about a specific interface',
                'args': {'interface_id': 'Interface identifier'}
            },
            'get_connections': {
                'description': 'Get list of network connections',
                'args': {}
            },
            'get_connection_info': {
                'description': 'Get information about a specific connection',
                'args': {'connection_id': 'Connection identifier'}
            },
            'get_routes': {
                'description': 'Get network routing table',
                'args': {}
            },
            'get_dns_servers': {
                'description': 'Get DNS server addresses',
                'args': {}
            },
            'get_hostname': {
                'description': 'Get system hostname',
                'args': {}
            },
            'get_ip_addresses': {
                'description': 'Get all IP addresses',
                'args': {}
            }
        }
        return help_info.get(command, {'error': f'Unknown command: {command}'})
    
    def validate_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> bool:
        if command not in self.get_available_commands():
            return False
        
        if command in ['get_interface_info', 'get_connection_info'] and not args.get(f'{command.split("_")[1]}_id'):
            return False
        
        return True

class FileSystemTool(BaseAgentTool):
    """Tool for file system operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._interface = config.get('interface')
    
    def initialize(self) -> bool:
        return bool(self._interface)
    
    def cleanup(self) -> None:
        pass
    
    def get_capabilities(self) -> Dict[str, bool]:
        return self._interface.get_capabilities() if self._interface else {}
    
    def get_status(self) -> Dict[str, Any]:
        return self._interface.get_status() if self._interface else {'error': 'Not initialized'}
    
    def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._interface:
            return {'error': 'Not initialized'}
        
        try:
            if command == 'list_directory':
                return self._interface.list_directory(args.get('path', ''))
            elif command == 'get_file_info':
                return self._interface.get_file_info(args.get('path', ''))
            elif command == 'create_directory':
                return self._interface.create_directory(args.get('path', ''))
            elif command == 'delete_file':
                return self._interface.delete_file(args.get('path', ''))
            elif command == 'move_file':
                return self._interface.move_file(
                    args.get('source', ''),
                    args.get('destination', '')
                )
            elif command == 'copy_file':
                return self._interface.copy_file(
                    args.get('source', ''),
                    args.get('destination', '')
                )
            elif command == 'read_file':
                return self._interface.read_file(args.get('path', ''))
            elif command == 'write_file':
                return self._interface.write_file(
                    args.get('path', ''),
                    args.get('content', '')
                )
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_available_commands(self) -> List[str]:
        return [
            'list_directory',
            'get_file_info',
            'create_directory',
            'delete_file',
            'move_file',
            'copy_file',
            'read_file',
            'write_file'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        help_info = {
            'list_directory': {
                'description': 'List contents of a directory',
                'args': {'path': 'Directory path'}
            },
            'get_file_info': {
                'description': 'Get information about a file',
                'args': {'path': 'File path'}
            },
            'create_directory': {
                'description': 'Create a new directory',
                'args': {'path': 'Directory path'}
            },
            'delete_file': {
                'description': 'Delete a file',
                'args': {'path': 'File path'}
            },
            'move_file': {
                'description': 'Move a file',
                'args': {
                    'source': 'Source file path',
                    'destination': 'Destination file path'
                }
            },
            'copy_file': {
                'description': 'Copy a file',
                'args': {
                    'source': 'Source file path',
                    'destination': 'Destination file path'
                }
            },
            'read_file': {
                'description': 'Read file contents',
                'args': {'path': 'File path'}
            },
            'write_file': {
                'description': 'Write contents to a file',
                'args': {
                    'path': 'File path',
                    'content': 'File contents'
                }
            }
        }
        return help_info.get(command, {'error': f'Unknown command: {command}'})
    
    def validate_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> bool:
        if command not in self.get_available_commands():
            return False
        
        if command in ['list_directory', 'get_file_info', 'create_directory', 'delete_file', 'read_file']:
            if not args.get('path'):
                return False
        
        if command in ['move_file', 'copy_file']:
            if not args.get('source') or not args.get('destination'):
                return False
        
        if command == 'write_file':
            if not args.get('path') or 'content' not in args:
                return False
        
        return True

class AudioTool(BaseAgentTool):
    """Tool for audio operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._interface = config.get('interface')
    
    def initialize(self) -> bool:
        return bool(self._interface)
    
    def cleanup(self) -> None:
        pass
    
    def get_capabilities(self) -> Dict[str, bool]:
        return self._interface.get_capabilities() if self._interface else {}
    
    def get_status(self) -> Dict[str, Any]:
        return self._interface.get_status() if self._interface else {'error': 'Not initialized'}
    
    def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._interface:
            return {'error': 'Not initialized'}
        
        try:
            if command == 'get_devices':
                return self._interface.get_devices()
            elif command == 'get_device_info':
                return self._interface.get_device_info(args.get('device_id', ''))
            elif command == 'get_default_device':
                return self._interface.get_default_device()
            elif command == 'set_default_device':
                return self._interface.set_default_device(args.get('device_id', ''))
            elif command == 'get_volume':
                return {'volume': self._interface.get_volume()}
            elif command == 'set_volume':
                return self._interface.set_volume(args.get('volume', 0))
            elif command == 'is_muted':
                return {'muted': self._interface.is_muted()}
            elif command == 'set_muted':
                return self._interface.set_muted(args.get('muted', False))
            else:
                return {'error': f'Unknown command: {command}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_available_commands(self) -> List[str]:
        return [
            'get_devices',
            'get_device_info',
            'get_default_device',
            'set_default_device',
            'get_volume',
            'set_volume',
            'is_muted',
            'set_muted'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        help_info = {
            'get_devices': {
                'description': 'Get list of audio devices',
                'args': {}
            },
            'get_device_info': {
                'description': 'Get information about a specific device',
                'args': {'device_id': 'Device identifier'}
            },
            'get_default_device': {
                'description': 'Get default audio device',
                'args': {}
            },
            'set_default_device': {
                'description': 'Set default audio device',
                'args': {'device_id': 'Device identifier'}
            },
            'get_volume': {
                'description': 'Get current volume level',
                'args': {}
            },
            'set_volume': {
                'description': 'Set volume level',
                'args': {'volume': 'Volume level (0-100)'}
            },
            'is_muted': {
                'description': 'Check if audio is muted',
                'args': {}
            },
            'set_muted': {
                'description': 'Set mute state',
                'args': {'muted': 'Mute state (true/false)'}
            }
        }
        return help_info.get(command, {'error': f'Unknown command: {command}'})
    
    def validate_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> bool:
        if command not in self.get_available_commands():
            return False
        
        if command in ['get_device_info', 'set_default_device'] and not args.get('device_id'):
            return False
        
        if command == 'set_volume':
            volume = args.get('volume')
            if not isinstance(volume, (int, float)) or not 0 <= volume <= 100:
                return False
        
        if command == 'set_muted' and not isinstance(args.get('muted'), bool):
            return False
        
        return True 