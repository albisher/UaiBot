"""
Image tool with A2A, MCP, and SmolAgents compliance.

This tool provides image processing capabilities while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import aiohttp
import io
from PIL import Image
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class ImageTool(BaseTool):
    """Tool for performing image operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the image tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="image",
            description="Tool for performing image operations",
            config=config
        )
        self._max_image_size = config.get('max_image_size', 10 * 1024 * 1024)  # 10MB
        self._max_dimensions = config.get('max_dimensions', (4096, 4096))
        self._allowed_formats = config.get('allowed_formats', ['JPEG', 'PNG', 'GIF', 'BMP'])
        self._quality = config.get('quality', 85)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Image cache
        self._cache_duration = config.get('cache_duration', 3600)  # 1 hour
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize cache
            self._cache = {}
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize ImageTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up ImageTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'resize': True,
            'crop': True,
            'rotate': True,
            'flip': True,
            'filter': True,
            'convert': True,
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
            'max_image_size': self._max_image_size,
            'max_dimensions': self._max_dimensions,
            'allowed_formats': self._allowed_formats,
            'quality': self._quality,
            'cache_duration': self._cache_duration,
            'cache_size': len(self._cache),
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
        if command == 'resize':
            return await self._resize_image(args)
        elif command == 'crop':
            return await self._crop_image(args)
        elif command == 'rotate':
            return await self._rotate_image(args)
        elif command == 'flip':
            return await self._flip_image(args)
        elif command == 'filter':
            return await self._apply_filter(args)
        elif command == 'convert':
            return await self._convert_format(args)
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
    
    def _get_cache_key(self, image_data: bytes, operation: str, **kwargs) -> str:
        """Generate a cache key for image data.
        
        Args:
            image_data: Image data
            operation: Operation performed
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        import hashlib
        params = [hashlib.md5(image_data).hexdigest(), operation]
        for key, value in sorted(kwargs.items()):
            params.append(f"{key}={value}")
        return "|".join(params)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key]['timestamp']
        return time.time() - cache_time < self._cache_duration
    
    def _validate_image(self, image_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate image data.
        
        Args:
            image_data: Image data to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if len(image_data) > self._max_image_size:
            return False, f'Image exceeds maximum size ({self._max_image_size} bytes)'
        
        try:
            image = Image.open(io.BytesIO(image_data))
            if image.format not in self._allowed_formats:
                return False, f'Unsupported image format: {image.format}'
            
            width, height = image.size
            max_width, max_height = self._max_dimensions
            if width > max_width or height > max_height:
                return False, f'Image dimensions exceed maximum ({max_width}x{max_height})'
            
            return True, None
        except Exception as e:
            return False, f'Invalid image data: {str(e)}'
    
    async def _process_image(self, image_data: bytes, operation: str, **kwargs) -> Dict[str, Any]:
        """Process an image with the given operation.
        
        Args:
            image_data: Image data to process
            operation: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            # Validate image
            is_valid, error = self._validate_image(image_data)
            if not is_valid:
                return {'error': error}
            
            # Check cache
            cache_key = self._get_cache_key(image_data, operation, **kwargs)
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Process image
            image = Image.open(io.BytesIO(image_data))
            
            if operation == 'resize':
                width = kwargs.get('width')
                height = kwargs.get('height')
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            elif operation == 'crop':
                left = kwargs.get('left', 0)
                top = kwargs.get('top', 0)
                right = kwargs.get('right', image.width)
                bottom = kwargs.get('bottom', image.height)
                image = image.crop((left, top, right, bottom))
            elif operation == 'rotate':
                angle = kwargs.get('angle', 0)
                image = image.rotate(angle, expand=True)
            elif operation == 'flip':
                direction = kwargs.get('direction', 'horizontal')
                if direction == 'horizontal':
                    image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                else:
                    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            elif operation == 'filter':
                filter_type = kwargs.get('filter_type')
                if filter_type == 'blur':
                    from PIL import ImageFilter
                    image = image.filter(ImageFilter.BLUR)
                elif filter_type == 'sharpen':
                    from PIL import ImageFilter
                    image = image.filter(ImageFilter.SHARPEN)
                elif filter_type == 'grayscale':
                    image = image.convert('L')
            elif operation == 'convert':
                format = kwargs.get('format')
                if format not in self._allowed_formats:
                    return {'error': f'Unsupported format: {format}'}
                image = image.convert('RGB')
            
            # Save processed image
            output = io.BytesIO()
            image.save(output, format=image.format, quality=self._quality)
            processed_data = output.getvalue()
            
            # Cache result
            self._cache[cache_key] = {
                'data': {
                    'status': 'success',
                    'action': operation,
                    'image_data': processed_data,
                    'format': image.format,
                    'size': len(processed_data),
                    'dimensions': image.size
                },
                'timestamp': time.time()
            }
            
            return self._cache[cache_key]['data']
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {'error': str(e)}
    
    async def _resize_image(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resize an image.
        
        Args:
            args: Resize arguments
            
        Returns:
            Dict[str, Any]: Resize result
        """
        try:
            if not args or 'image_data' not in args or 'width' not in args or 'height' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_image(
                args['image_data'],
                'resize',
                width=args['width'],
                height=args['height']
            )
            
            if 'error' not in result:
                self._add_to_history('resize', {
                    'width': args['width'],
                    'height': args['height'],
                    'format': result['format'],
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return {'error': str(e)}
    
    async def _crop_image(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crop an image.
        
        Args:
            args: Crop arguments
            
        Returns:
            Dict[str, Any]: Crop result
        """
        try:
            if not args or 'image_data' not in args:
                return {'error': 'Missing image data'}
            
            result = await self._process_image(
                args['image_data'],
                'crop',
                left=args.get('left', 0),
                top=args.get('top', 0),
                right=args.get('right'),
                bottom=args.get('bottom')
            )
            
            if 'error' not in result:
                self._add_to_history('crop', {
                    'format': result['format'],
                    'size': result['size'],
                    'dimensions': result['dimensions']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            return {'error': str(e)}
    
    async def _rotate_image(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Rotate an image.
        
        Args:
            args: Rotate arguments
            
        Returns:
            Dict[str, Any]: Rotate result
        """
        try:
            if not args or 'image_data' not in args:
                return {'error': 'Missing image data'}
            
            result = await self._process_image(
                args['image_data'],
                'rotate',
                angle=args.get('angle', 0)
            )
            
            if 'error' not in result:
                self._add_to_history('rotate', {
                    'angle': args.get('angle', 0),
                    'format': result['format'],
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error rotating image: {e}")
            return {'error': str(e)}
    
    async def _flip_image(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Flip an image.
        
        Args:
            args: Flip arguments
            
        Returns:
            Dict[str, Any]: Flip result
        """
        try:
            if not args or 'image_data' not in args:
                return {'error': 'Missing image data'}
            
            result = await self._process_image(
                args['image_data'],
                'flip',
                direction=args.get('direction', 'horizontal')
            )
            
            if 'error' not in result:
                self._add_to_history('flip', {
                    'direction': args.get('direction', 'horizontal'),
                    'format': result['format'],
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error flipping image: {e}")
            return {'error': str(e)}
    
    async def _apply_filter(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply a filter to an image.
        
        Args:
            args: Filter arguments
            
        Returns:
            Dict[str, Any]: Filter result
        """
        try:
            if not args or 'image_data' not in args or 'filter_type' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_image(
                args['image_data'],
                'filter',
                filter_type=args['filter_type']
            )
            
            if 'error' not in result:
                self._add_to_history('filter', {
                    'filter_type': args['filter_type'],
                    'format': result['format'],
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            return {'error': str(e)}
    
    async def _convert_format(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert image format.
        
        Args:
            args: Convert arguments
            
        Returns:
            Dict[str, Any]: Convert result
        """
        try:
            if not args or 'image_data' not in args or 'format' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_image(
                args['image_data'],
                'convert',
                format=args['format']
            )
            
            if 'error' not in result:
                self._add_to_history('convert', {
                    'format': args['format'],
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error converting format: {e}")
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