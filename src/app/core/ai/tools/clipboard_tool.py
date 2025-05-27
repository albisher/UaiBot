import logging
from typing import Dict, Any, List, Optional, Union
from labeeb.tools.base_tool import BaseAgentTool
from labeeb.platform_core.platform_manager import PlatformManager
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol

logger = logging.getLogger(__name__)

class ClipboardTool(BaseAgentTool, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    """Tool for managing clipboard operations with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the clipboard tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._platform_manager = None
        self._platform_info = None
        self._handlers = None
        self._clipboard_handler = None
        self._max_text_length = config.get('max_text_length', 1000000)
        self._supported_formats = config.get('supported_formats', ['text', 'html', 'rtf'])
        self._clear_on_exit = config.get('clear_on_exit', False)
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()
    
    def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Notify A2A protocol before initialization
            self.a2a_protocol.notify_action("initialize", {})
            # Use MCP for initialization
            self.mcp_protocol.execute_action("initialize", {})
            
            self._platform_manager = PlatformManager()
            self._platform_info = self._platform_manager.get_platform_info()
            self._handlers = self._platform_manager.get_handlers()
            self._clipboard_handler = self._handlers.get('clipboard')
            if not self._clipboard_handler:
                error_msg = "Clipboard handler not found"
                self.a2a_protocol.notify_error("initialize", error_msg)
                logger.error(error_msg)
                return False
            self._initialized = True
            
            # Notify SmolAgent protocol after initialization
            self.smol_protocol.notify_completion("initialize", {"status": "success"})
            return True
        except Exception as e:
            error_msg = f"Failed to initialize ClipboardTool: {e}"
            self.a2a_protocol.notify_error("initialize", error_msg)
            logger.error(error_msg)
            return False
    
    def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            # Notify A2A protocol before cleanup
            self.a2a_protocol.notify_action("cleanup", {})
            # Use MCP for cleanup
            self.mcp_protocol.execute_action("cleanup", {})
            
            if self._clear_on_exit:
                self._clipboard_handler.clear()
            self._platform_manager = None
            self._platform_info = None
            self._handlers = None
            self._clipboard_handler = None
            self._initialized = False
            
            # Notify SmolAgent protocol after cleanup
            self.smol_protocol.notify_completion("cleanup", {"status": "success"})
        except Exception as e:
            error_msg = f"Error cleaning up ClipboardTool: {e}"
            self.a2a_protocol.notify_error("cleanup", error_msg)
            logger.error(error_msg)
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        return {
            'text': True,
            'html': True,
            'rtf': True,
            'image': True,
            'files': True,
            'clear': True,
            'get_formats': True,
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
            'max_text_length': self._max_text_length,
            'supported_formats': self._supported_formats,
            'clear_on_exit': self._clear_on_exit
        }
    
    async def execute(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            # Notify A2A protocol before command execution
            await self.a2a_protocol.notify_action(command, args or {})
            # Use MCP for command execution
            await self.mcp_protocol.execute_action(command, args or {})
            
            result = None
            if command == 'set_text':
                result = self._set_text(args)
            elif command == 'get_text':
                result = self._get_text()
            elif command == 'set_html':
                result = self._set_html(args)
            elif command == 'get_html':
                result = self._get_html()
            elif command == 'set_rtf':
                result = self._set_rtf(args)
            elif command == 'get_rtf':
                result = self._get_rtf()
            elif command == 'set_image':
                result = self._set_image(args)
            elif command == 'get_image':
                result = self._get_image()
            elif command == 'set_files':
                result = self._set_files(args)
            elif command == 'get_files':
                result = self._get_files()
            elif command == 'clear':
                result = self._clear()
            elif command == 'get_formats':
                result = self._get_formats()
            else:
                result = {'error': f'Unknown command: {command}'}
            
            # Notify SmolAgent protocol after command execution
            await self.smol_protocol.notify_completion(command, result)
            return result
        except Exception as e:
            error_msg = f"Error executing command {command}: {e}"
            await self.a2a_protocol.notify_error(command, error_msg)
            logger.error(error_msg)
            return {'error': str(e)}
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands for this tool.
        
        Returns:
            List[str]: List of available command names
        """
        return [
            'set_text',
            'get_text',
            'set_html',
            'get_html',
            'set_rtf',
            'get_rtf',
            'set_image',
            'get_image',
            'set_files',
            'get_files',
            'clear',
            'get_formats'
        ]
    
    def get_command_help(self, command: str) -> Dict[str, Any]:
        """Get help information for a specific command.
        
        Args:
            command: Command name to get help for
            
        Returns:
            Dict[str, Any]: Help information for the command
        """
        help_info = {
            'set_text': {
                'description': 'Set text content in clipboard',
                'args': {
                    'text': 'Text content to set'
                }
            },
            'get_text': {
                'description': 'Get text content from clipboard',
                'args': {}
            },
            'set_html': {
                'description': 'Set HTML content in clipboard',
                'args': {
                    'html': 'HTML content to set'
                }
            },
            'get_html': {
                'description': 'Get HTML content from clipboard',
                'args': {}
            },
            'set_rtf': {
                'description': 'Set RTF content in clipboard',
                'args': {
                    'rtf': 'RTF content to set'
                }
            },
            'get_rtf': {
                'description': 'Get RTF content from clipboard',
                'args': {}
            },
            'set_image': {
                'description': 'Set image content in clipboard',
                'args': {
                    'image_data': 'Image data in bytes'
                }
            },
            'get_image': {
                'description': 'Get image content from clipboard',
                'args': {}
            },
            'set_files': {
                'description': 'Set file list in clipboard',
                'args': {
                    'files': 'List of file paths'
                }
            },
            'get_files': {
                'description': 'Get file list from clipboard',
                'args': {}
            },
            'clear': {
                'description': 'Clear clipboard contents',
                'args': {}
            },
            'get_formats': {
                'description': 'Get available clipboard formats',
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
        
        if command in ['set_text', 'set_html', 'set_rtf']:
            if not args or not any(k in args for k in ['text', 'html', 'rtf']):
                return False
            if not isinstance(args.get('text', args.get('html', args.get('rtf'))), str):
                return False
        
        elif command == 'set_image':
            if not args or 'image_data' not in args:
                return False
            if not isinstance(args['image_data'], bytes):
                return False
        
        elif command == 'set_files':
            if not args or 'files' not in args:
                return False
            if not isinstance(args['files'], list):
                return False
            if not all(isinstance(f, str) for f in args['files']):
                return False
        
        return True
    
    def _set_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set text content in clipboard.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            text = args['text']
            if len(text) > self._max_text_length:
                return {'error': f'Text length exceeds maximum allowed ({self._max_text_length})'}
            
            self._clipboard_handler.set_text(text)
            return {
                'status': 'success',
                'action': 'set_text',
                'length': len(text)
            }
        except Exception as e:
            logger.error(f"Error setting text: {e}")
            return {'error': str(e)}
    
    def _get_text(self) -> Dict[str, Any]:
        """Get text content from clipboard.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            text = self._clipboard_handler.get_text()
            return {
                'status': 'success',
                'action': 'get_text',
                'text': text,
                'length': len(text) if text else 0
            }
        except Exception as e:
            logger.error(f"Error getting text: {e}")
            return {'error': str(e)}
    
    def _set_html(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set HTML content in clipboard.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            html = args['html']
            if len(html) > self._max_text_length:
                return {'error': f'HTML length exceeds maximum allowed ({self._max_text_length})'}
            
            self._clipboard_handler.set_html(html)
            return {
                'status': 'success',
                'action': 'set_html',
                'length': len(html)
            }
        except Exception as e:
            logger.error(f"Error setting HTML: {e}")
            return {'error': str(e)}
    
    def _get_html(self) -> Dict[str, Any]:
        """Get HTML content from clipboard.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            html = self._clipboard_handler.get_html()
            return {
                'status': 'success',
                'action': 'get_html',
                'html': html,
                'length': len(html) if html else 0
            }
        except Exception as e:
            logger.error(f"Error getting HTML: {e}")
            return {'error': str(e)}
    
    def _set_rtf(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set RTF content in clipboard.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            rtf = args['rtf']
            if len(rtf) > self._max_text_length:
                return {'error': f'RTF length exceeds maximum allowed ({self._max_text_length})'}
            
            self._clipboard_handler.set_rtf(rtf)
            return {
                'status': 'success',
                'action': 'set_rtf',
                'length': len(rtf)
            }
        except Exception as e:
            logger.error(f"Error setting RTF: {e}")
            return {'error': str(e)}
    
    def _get_rtf(self) -> Dict[str, Any]:
        """Get RTF content from clipboard.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            rtf = self._clipboard_handler.get_rtf()
            return {
                'status': 'success',
                'action': 'get_rtf',
                'rtf': rtf,
                'length': len(rtf) if rtf else 0
            }
        except Exception as e:
            logger.error(f"Error getting RTF: {e}")
            return {'error': str(e)}
    
    def _set_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set image content in clipboard.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            image_data = args['image_data']
            self._clipboard_handler.set_image(image_data)
            return {
                'status': 'success',
                'action': 'set_image',
                'size': len(image_data)
            }
        except Exception as e:
            logger.error(f"Error setting image: {e}")
            return {'error': str(e)}
    
    def _get_image(self) -> Dict[str, Any]:
        """Get image content from clipboard.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            image_data = self._clipboard_handler.get_image()
            return {
                'status': 'success',
                'action': 'get_image',
                'image_data': image_data,
                'size': len(image_data) if image_data else 0
            }
        except Exception as e:
            logger.error(f"Error getting image: {e}")
            return {'error': str(e)}
    
    def _set_files(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set file list in clipboard.
        
        Args:
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            files = args['files']
            self._clipboard_handler.set_files(files)
            return {
                'status': 'success',
                'action': 'set_files',
                'count': len(files)
            }
        except Exception as e:
            logger.error(f"Error setting files: {e}")
            return {'error': str(e)}
    
    def _get_files(self) -> Dict[str, Any]:
        """Get file list from clipboard.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            files = self._clipboard_handler.get_files()
            return {
                'status': 'success',
                'action': 'get_files',
                'files': files,
                'count': len(files)
            }
        except Exception as e:
            logger.error(f"Error getting files: {e}")
            return {'error': str(e)}
    
    def _clear(self) -> Dict[str, Any]:
        """Clear clipboard contents.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            self._clipboard_handler.clear()
            return {
                'status': 'success',
                'action': 'clear'
            }
        except Exception as e:
            logger.error(f"Error clearing clipboard: {e}")
            return {'error': str(e)}
    
    def _get_formats(self) -> Dict[str, Any]:
        """Get available clipboard formats.
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            formats = self._clipboard_handler.get_formats()
            return {
                'status': 'success',
                'action': 'get_formats',
                'formats': formats
            }
        except Exception as e:
            logger.error(f"Error getting formats: {e}")
            return {'error': str(e)}
    
    # A2A Protocol Methods
    async def register_agent(self, agent_id: str, capabilities: Dict[str, Any]) -> None:
        await self.a2a_protocol.register_agent(agent_id, capabilities)

    async def unregister_agent(self, agent_id: str) -> None:
        await self.a2a_protocol.unregister_agent(agent_id)

    # MCP Protocol Methods
    async def register_channel(self, channel_id: str, channel_type: str) -> None:
        await self.mcp_protocol.register_channel(channel_id, channel_type)

    async def unregister_channel(self, channel_id: str) -> None:
        await self.mcp_protocol.unregister_channel(channel_id)

    # SmolAgent Protocol Methods
    async def register_capability(self, capability: str, handler: callable) -> None:
        await self.smol_protocol.register_capability(capability, handler)

    async def unregister_capability(self, capability: str) -> None:
        await self.smol_protocol.unregister_capability(capability) 