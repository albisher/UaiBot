"""
File system tool with A2A, MCP, and SmolAgents compliance.

This tool provides file system operations while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import os
import shutil
import logging
import hashlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class FileSystemTool(BaseTool):
    """Tool for performing file system operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the file system tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="file_system",
            description="Tool for performing file system operations",
            config=config
        )
        self._base_path = Path(config.get('base_path', os.getcwd()))
        self._allowed_extensions = config.get('allowed_extensions', [])
        self._max_file_size = config.get('max_file_size', 100 * 1024 * 1024)  # 100MB default
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Validate base path
            if not self._base_path.exists():
                logger.error(f"Base path does not exist: {self._base_path}")
                return False
            
            # Ensure base path is absolute
            self._base_path = self._base_path.resolve()
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize FileSystemTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up FileSystemTool: {e}")
    
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
            'move': True,
            'copy': True,
            'list': True,
            'search': True,
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
            'base_path': str(self._base_path),
            'allowed_extensions': self._allowed_extensions,
            'max_file_size': self._max_file_size,
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
            return await self._read_file(args)
        elif command == 'write':
            return await self._write_file(args)
        elif command == 'delete':
            return await self._delete_file(args)
        elif command == 'move':
            return await self._move_file(args)
        elif command == 'copy':
            return await self._copy_file(args)
        elif command == 'list':
            return await self._list_directory(args)
        elif command == 'search':
            return await self._search_files(args)
        elif command == 'hash':
            return await self._hash_file(args)
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
    
    def _validate_path(self, path: Union[str, Path]) -> Path:
        """Validate and normalize a path.
        
        Args:
            path: Path to validate
            
        Returns:
            Path: Normalized path
            
        Raises:
            ValueError: If path is invalid
        """
        try:
            path = Path(path)
            if not path.is_absolute():
                path = self._base_path / path
            path = path.resolve()
            
            # Ensure path is within base path
            if not str(path).startswith(str(self._base_path)):
                raise ValueError(f"Path {path} is outside base path {self._base_path}")
            
            return path
        except Exception as e:
            raise ValueError(f"Invalid path: {e}")
    
    def _validate_file(self, path: Path) -> None:
        """Validate a file.
        
        Args:
            path: Path to validate
            
        Raises:
            ValueError: If file is invalid
        """
        if not path.exists():
            raise ValueError(f"File does not exist: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        if self._allowed_extensions and path.suffix.lower() not in self._allowed_extensions:
            raise ValueError(f"File extension not allowed: {path.suffix}")
        
        if path.stat().st_size > self._max_file_size:
            raise ValueError(f"File too large: {path}")
    
    async def _read_file(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Read a file.
        
        Args:
            args: File reading arguments
            
        Returns:
            Dict[str, Any]: Result of file reading
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing path parameter'}
            
            path = self._validate_path(args['path'])
            self._validate_file(path)
            
            encoding = args.get('encoding', 'utf-8')
            mode = args.get('mode', 'text')
            
            if mode == 'text':
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
            else:  # binary
                with open(path, 'rb') as f:
                    content = f.read()
            
            self._add_to_history('read', {
                'path': str(path),
                'mode': mode,
                'size': len(content)
            })
            
            return {
                'status': 'success',
                'action': 'read',
                'path': str(path),
                'content': content,
                'mode': mode
            }
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {'error': str(e)}
    
    async def _write_file(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Write to a file.
        
        Args:
            args: File writing arguments
            
        Returns:
            Dict[str, Any]: Result of file writing
        """
        try:
            if not args or not all(k in args for k in ['path', 'content']):
                return {'error': 'Missing required parameters'}
            
            path = self._validate_path(args['path'])
            content = args['content']
            encoding = args.get('encoding', 'utf-8')
            mode = args.get('mode', 'text')
            overwrite = args.get('overwrite', False)
            
            # Check if file exists
            if path.exists() and not overwrite:
                return {'error': f'File already exists: {path}'}
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if mode == 'text':
                with open(path, 'w', encoding=encoding) as f:
                    f.write(content)
            else:  # binary
                with open(path, 'wb') as f:
                    f.write(content)
            
            self._add_to_history('write', {
                'path': str(path),
                'mode': mode,
                'size': len(content)
            })
            
            return {
                'status': 'success',
                'action': 'write',
                'path': str(path),
                'mode': mode
            }
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return {'error': str(e)}
    
    async def _delete_file(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete a file.
        
        Args:
            args: File deletion arguments
            
        Returns:
            Dict[str, Any]: Result of file deletion
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing path parameter'}
            
            path = self._validate_path(args['path'])
            self._validate_file(path)
            
            # Get file info before deletion
            file_info = {
                'size': path.stat().st_size,
                'modified': path.stat().st_mtime
            }
            
            path.unlink()
            
            self._add_to_history('delete', {
                'path': str(path),
                'info': file_info
            })
            
            return {
                'status': 'success',
                'action': 'delete',
                'path': str(path)
            }
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return {'error': str(e)}
    
    async def _move_file(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Move a file.
        
        Args:
            args: File move arguments
            
        Returns:
            Dict[str, Any]: Result of file move
        """
        try:
            if not args or not all(k in args for k in ['source', 'destination']):
                return {'error': 'Missing required parameters'}
            
            source = self._validate_path(args['source'])
            destination = self._validate_path(args['destination'])
            
            self._validate_file(source)
            
            # Check if destination exists
            if destination.exists():
                if not args.get('overwrite', False):
                    return {'error': f'Destination already exists: {destination}'}
                destination.unlink()
            
            # Create parent directories if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Get file info before move
            file_info = {
                'size': source.stat().st_size,
                'modified': source.stat().st_mtime
            }
            
            shutil.move(str(source), str(destination))
            
            self._add_to_history('move', {
                'source': str(source),
                'destination': str(destination),
                'info': file_info
            })
            
            return {
                'status': 'success',
                'action': 'move',
                'source': str(source),
                'destination': str(destination)
            }
        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return {'error': str(e)}
    
    async def _copy_file(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Copy a file.
        
        Args:
            args: File copy arguments
            
        Returns:
            Dict[str, Any]: Result of file copy
        """
        try:
            if not args or not all(k in args for k in ['source', 'destination']):
                return {'error': 'Missing required parameters'}
            
            source = self._validate_path(args['source'])
            destination = self._validate_path(args['destination'])
            
            self._validate_file(source)
            
            # Check if destination exists
            if destination.exists():
                if not args.get('overwrite', False):
                    return {'error': f'Destination already exists: {destination}'}
                destination.unlink()
            
            # Create parent directories if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Get file info
            file_info = {
                'size': source.stat().st_size,
                'modified': source.stat().st_mtime
            }
            
            shutil.copy2(str(source), str(destination))
            
            self._add_to_history('copy', {
                'source': str(source),
                'destination': str(destination),
                'info': file_info
            })
            
            return {
                'status': 'success',
                'action': 'copy',
                'source': str(source),
                'destination': str(destination)
            }
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return {'error': str(e)}
    
    async def _list_directory(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List directory contents.
        
        Args:
            args: Directory listing arguments
            
        Returns:
            Dict[str, Any]: Result of directory listing
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing path parameter'}
            
            path = self._validate_path(args['path'])
            
            if not path.exists():
                return {'error': f'Directory does not exist: {path}'}
            
            if not path.is_dir():
                return {'error': f'Path is not a directory: {path}'}
            
            recursive = args.get('recursive', False)
            include_hidden = args.get('include_hidden', False)
            
            items = []
            if recursive:
                for root, dirs, files in os.walk(path):
                    # Filter hidden items
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        files = [f for f in files if not f.startswith('.')]
                    
                    for item in dirs + files:
                        item_path = Path(root) / item
                        items.append({
                            'name': item,
                            'path': str(item_path.relative_to(self._base_path)),
                            'type': 'directory' if item_path.is_dir() else 'file',
                            'size': item_path.stat().st_size if item_path.is_file() else None,
                            'modified': item_path.stat().st_mtime
                        })
            else:
                for item in path.iterdir():
                    # Skip hidden items
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    items.append({
                        'name': item.name,
                        'path': str(item.relative_to(self._base_path)),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None,
                        'modified': item.stat().st_mtime
                    })
            
            self._add_to_history('list', {
                'path': str(path),
                'recursive': recursive,
                'include_hidden': include_hidden,
                'count': len(items)
            })
            
            return {
                'status': 'success',
                'action': 'list',
                'path': str(path),
                'items': items
            }
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
            return {'error': str(e)}
    
    async def _search_files(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for files.
        
        Args:
            args: File search arguments
            
        Returns:
            Dict[str, Any]: Result of file search
        """
        try:
            if not args or not all(k in args for k in ['path', 'pattern']):
                return {'error': 'Missing required parameters'}
            
            path = self._validate_path(args['path'])
            pattern = args['pattern']
            recursive = args.get('recursive', True)
            include_hidden = args.get('include_hidden', False)
            
            if not path.exists():
                return {'error': f'Directory does not exist: {path}'}
            
            if not path.is_dir():
                return {'error': f'Path is not a directory: {path}'}
            
            matches = []
            if recursive:
                for root, dirs, files in os.walk(path):
                    # Filter hidden items
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        files = [f for f in files if not f.startswith('.')]
                    
                    for item in dirs + files:
                        if pattern in item:
                            item_path = Path(root) / item
                            matches.append({
                                'name': item,
                                'path': str(item_path.relative_to(self._base_path)),
                                'type': 'directory' if item_path.is_dir() else 'file',
                                'size': item_path.stat().st_size if item_path.is_file() else None,
                                'modified': item_path.stat().st_mtime
                            })
            else:
                for item in path.iterdir():
                    # Skip hidden items
                    if not include_hidden and item.name.startswith('.'):
                        continue
                    
                    if pattern in item.name:
                        matches.append({
                            'name': item.name,
                            'path': str(item.relative_to(self._base_path)),
                            'type': 'directory' if item.is_dir() else 'file',
                            'size': item.stat().st_size if item.is_file() else None,
                            'modified': item.stat().st_mtime
                        })
            
            self._add_to_history('search', {
                'path': str(path),
                'pattern': pattern,
                'recursive': recursive,
                'include_hidden': include_hidden,
                'matches': len(matches)
            })
            
            return {
                'status': 'success',
                'action': 'search',
                'path': str(path),
                'pattern': pattern,
                'matches': matches
            }
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return {'error': str(e)}
    
    async def _hash_file(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate file hash.
        
        Args:
            args: File hash arguments
            
        Returns:
            Dict[str, Any]: Result of file hash calculation
        """
        try:
            if not args or 'path' not in args:
                return {'error': 'Missing path parameter'}
            
            path = self._validate_path(args['path'])
            self._validate_file(path)
            
            algorithm = args.get('algorithm', 'sha256')
            if algorithm not in hashlib.algorithms_available:
                return {'error': f'Unsupported hash algorithm: {algorithm}'}
            
            hash_obj = hashlib.new(algorithm)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            
            hash_value = hash_obj.hexdigest()
            
            self._add_to_history('hash', {
                'path': str(path),
                'algorithm': algorithm,
                'hash': hash_value
            })
            
            return {
                'status': 'success',
                'action': 'hash',
                'path': str(path),
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