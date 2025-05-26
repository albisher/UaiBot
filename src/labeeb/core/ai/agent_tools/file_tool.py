"""
File tool with A2A, MCP, and SmolAgents compliance.

This tool provides file operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import os
import shutil
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class FileTool(BaseTool):
    """Tool for performing file operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the file tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="file",
            description="Tool for performing file operations",
            config=config
        )
        self._base_dir = config.get('base_dir', '.')
        self._max_file_size = config.get('max_file_size', 100 * 1024 * 1024)  # 100MB
        self._allowed_extensions = config.get('allowed_extensions', [])
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Create base directory
            os.makedirs(self._base_dir, exist_ok=True)
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize FileTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up FileTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'read': True,
            'write': True,
            'delete': True,
            'copy': True,
            'move': True,
            'list': True,
            'hash': True,
            'history': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'base_dir': self._base_dir,
            'max_file_size': self._max_file_size,
            'allowed_extensions': self._allowed_extensions,
            'history_size': len(self._operation_history),
            'max_history': self._max_history
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
        if command == 'read':
            return await self._read(args)
        elif command == 'write':
            return await self._write(args)
        elif command == 'delete':
            return await self._delete(args)
        elif command == 'copy':
            return await self._copy(args)
        elif command == 'move':
            return await self._move(args)
        elif command == 'list':
            return await self._list(args)
        elif command == 'hash':
            return await self._hash(args)
        elif command == 'get_history':
            return await self._get_history()
        elif command == 'clear_history':
            return await self._clear_history()
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _add_to_history(self, operation: str, details: Dict[str, Any]) -> None:
        """Add an operation to history.
        
        Args:
            operation: Operation performed
            details: Operation details
        """
        self._operation_history.append({
            'operation': operation,
            'details': details,
            'timestamp': time.time()
        })
        if len(self._operation_history) > self._max_history:
            self._operation_history.pop(0)
    
    def _get_file_path(self, path: str) -> str:
        """Get absolute file path.
        
        Args:
            path: Relative file path
            
        Returns:
            str: Absolute file path
        """
        return os.path.abspath(os.path.join(self._base_dir, path))
    
    def _validate_path(self, path: str) -> bool:
        """Validate file path.
        
        Args:
            path: File path
            
        Returns:
            bool: True if path is valid, False otherwise
        """
        # Get absolute path
        abs_path = self._get_file_path(path)
        
        # Check if path is within base directory
        if not abs_path.startswith(os.path.abspath(self._base_dir)):
            return False
        
        # Check file extension
        if self._allowed_extensions:
            ext = os.path.splitext(path)[1].lower()
            if ext not in self._allowed_extensions:
                return False
        
        return True
    
    async def _read(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Read file contents.
        
        Args:
            args: Read arguments
            
        Returns:
            Dict[str, Any]: Read result
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing required arguments'}
            
            path = args['path']
            
            # Validate path
            if not self._validate_path(path):
                return {
                    'status': 'error',
                    'action': 'read',
                    'error': f'Invalid path: {path}'
                }
            
            # Get file path
            file_path = self._get_file_path(path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'status': 'error',
                    'action': 'read',
                    'error': f'File not found: {path}'
                }
            
            # Check if path is a file
            if not os.path.isfile(file_path):
                return {
                    'status': 'error',
                    'action': 'read',
                    'error': f'Not a file: {path}'
                }
            
            # Check file size
            if os.path.getsize(file_path) > self._max_file_size:
                return {
                    'status': 'error',
                    'action': 'read',
                    'error': f'File too large: {path}'
                }
            
            # Read file
            with open(file_path, 'r') as f:
                content = f.read()
            
            self._add_to_history('read', {
                'path': path,
                'size': len(content)
            })
            
            return {
                'status': 'success',
                'action': 'read',
                'path': path,
                'content': content
            }
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {'error': str(e)}
    
    async def _write(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Write file contents.
        
        Args:
            args: Write arguments
            
        Returns:
            Dict[str, Any]: Write result
        """
        try:
            if not args or 'path' not in args or 'content' not in args:
                return {'error': 'Missing required arguments'}
            
            path = args['path']
            content = args['content']
            
            # Validate path
            if not self._validate_path(path):
                return {
                    'status': 'error',
                    'action': 'write',
                    'error': f'Invalid path: {path}'
                }
            
            # Get file path
            file_path = self._get_file_path(path)
            
            # Check content size
            if len(content) > self._max_file_size:
                return {
                    'status': 'error',
                    'action': 'write',
                    'error': f'Content too large: {path}'
                }
            
            # Create directory if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(content)
            
            self._add_to_history('write', {
                'path': path,
                'size': len(content)
            })
            
            return {
                'status': 'success',
                'action': 'write',
                'path': path
            }
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return {'error': str(e)}
    
    async def _delete(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete file.
        
        Args:
            args: Delete arguments
            
        Returns:
            Dict[str, Any]: Delete result
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing required arguments'}
            
            path = args['path']
            
            # Validate path
            if not self._validate_path(path):
                return {
                    'status': 'error',
                    'action': 'delete',
                    'error': f'Invalid path: {path}'
                }
            
            # Get file path
            file_path = self._get_file_path(path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'status': 'error',
                    'action': 'delete',
                    'error': f'File not found: {path}'
                }
            
            # Check if path is a file
            if not os.path.isfile(file_path):
                return {
                    'status': 'error',
                    'action': 'delete',
                    'error': f'Not a file: {path}'
                }
            
            # Delete file
            os.remove(file_path)
            
            self._add_to_history('delete', {
                'path': path
            })
            
            return {
                'status': 'success',
                'action': 'delete',
                'path': path
            }
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return {'error': str(e)}
    
    async def _copy(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Copy file.
        
        Args:
            args: Copy arguments
            
        Returns:
            Dict[str, Any]: Copy result
        """
        try:
            if not args or 'src' not in args or 'dst' not in args:
                return {'error': 'Missing required arguments'}
            
            src = args['src']
            dst = args['dst']
            
            # Validate paths
            if not self._validate_path(src) or not self._validate_path(dst):
                return {
                    'status': 'error',
                    'action': 'copy',
                    'error': f'Invalid path: {src} or {dst}'
                }
            
            # Get file paths
            src_path = self._get_file_path(src)
            dst_path = self._get_file_path(dst)
            
            # Check if source file exists
            if not os.path.exists(src_path):
                return {
                    'status': 'error',
                    'action': 'copy',
                    'error': f'Source file not found: {src}'
                }
            
            # Check if source path is a file
            if not os.path.isfile(src_path):
                return {
                    'status': 'error',
                    'action': 'copy',
                    'error': f'Not a file: {src}'
                }
            
            # Check source file size
            if os.path.getsize(src_path) > self._max_file_size:
                return {
                    'status': 'error',
                    'action': 'copy',
                    'error': f'Source file too large: {src}'
                }
            
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(src_path, dst_path)
            
            self._add_to_history('copy', {
                'src': src,
                'dst': dst
            })
            
            return {
                'status': 'success',
                'action': 'copy',
                'src': src,
                'dst': dst
            }
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return {'error': str(e)}
    
    async def _move(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Move file.
        
        Args:
            args: Move arguments
            
        Returns:
            Dict[str, Any]: Move result
        """
        try:
            if not args or 'src' not in args or 'dst' not in args:
                return {'error': 'Missing required arguments'}
            
            src = args['src']
            dst = args['dst']
            
            # Validate paths
            if not self._validate_path(src) or not self._validate_path(dst):
                return {
                    'status': 'error',
                    'action': 'move',
                    'error': f'Invalid path: {src} or {dst}'
                }
            
            # Get file paths
            src_path = self._get_file_path(src)
            dst_path = self._get_file_path(dst)
            
            # Check if source file exists
            if not os.path.exists(src_path):
                return {
                    'status': 'error',
                    'action': 'move',
                    'error': f'Source file not found: {src}'
                }
            
            # Check if source path is a file
            if not os.path.isfile(src_path):
                return {
                    'status': 'error',
                    'action': 'move',
                    'error': f'Not a file: {src}'
                }
            
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # Move file
            shutil.move(src_path, dst_path)
            
            self._add_to_history('move', {
                'src': src,
                'dst': dst
            })
            
            return {
                'status': 'success',
                'action': 'move',
                'src': src,
                'dst': dst
            }
        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return {'error': str(e)}
    
    async def _list(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List files.
        
        Args:
            args: List arguments
            
        Returns:
            Dict[str, Any]: List result
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing required arguments'}
            
            path = args['path']
            
            # Validate path
            if not self._validate_path(path):
                return {
                    'status': 'error',
                    'action': 'list',
                    'error': f'Invalid path: {path}'
                }
            
            # Get directory path
            dir_path = self._get_file_path(path)
            
            # Check if directory exists
            if not os.path.exists(dir_path):
                return {
                    'status': 'error',
                    'action': 'list',
                    'error': f'Directory not found: {path}'
                }
            
            # Check if path is a directory
            if not os.path.isdir(dir_path):
                return {
                    'status': 'error',
                    'action': 'list',
                    'error': f'Not a directory: {path}'
                }
            
            # List files
            files = []
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path):
                    files.append({
                        'name': filename,
                        'size': os.path.getsize(file_path),
                        'modified': os.path.getmtime(file_path)
                    })
            
            self._add_to_history('list', {
                'path': path,
                'files': len(files)
            })
            
            return {
                'status': 'success',
                'action': 'list',
                'path': path,
                'files': files
            }
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {'error': str(e)}
    
    async def _hash(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate file hash.
        
        Args:
            args: Hash arguments
            
        Returns:
            Dict[str, Any]: Hash result
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing required arguments'}
            
            path = args['path']
            algorithm = args.get('algorithm', 'sha256')
            
            # Validate path
            if not self._validate_path(path):
                return {
                    'status': 'error',
                    'action': 'hash',
                    'error': f'Invalid path: {path}'
                }
            
            # Get file path
            file_path = self._get_file_path(path)
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'status': 'error',
                    'action': 'hash',
                    'error': f'File not found: {path}'
                }
            
            # Check if path is a file
            if not os.path.isfile(file_path):
                return {
                    'status': 'error',
                    'action': 'hash',
                    'error': f'Not a file: {path}'
                }
            
            # Check file size
            if os.path.getsize(file_path) > self._max_file_size:
                return {
                    'status': 'error',
                    'action': 'hash',
                    'error': f'File too large: {path}'
                }
            
            # Calculate hash
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            hash_value = hash_obj.hexdigest()
            
            self._add_to_history('hash', {
                'path': path,
                'algorithm': algorithm,
                'hash': hash_value
            })
            
            return {
                'status': 'success',
                'action': 'hash',
                'path': path,
                'algorithm': algorithm,
                'hash': hash_value
            }
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return {'error': str(e)}
    
    async def _get_history(self) -> Dict[str, Any]:
        """Get operation history.
        
        Returns:
            Dict[str, Any]: Operation history
        """
        try:
            return {
                'status': 'success',
                'action': 'get_history',
                'history': self._operation_history
            }
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return {'error': str(e)}
    
    async def _clear_history(self) -> Dict[str, Any]:
        """Clear operation history.
        
        Returns:
            Dict[str, Any]: Result of clearing history
        """
        try:
            self._operation_history = []
            return {
                'status': 'success',
                'action': 'clear_history'
            }
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return {'error': str(e)}