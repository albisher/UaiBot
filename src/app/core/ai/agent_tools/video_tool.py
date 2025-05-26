"""
Video tool with A2A, MCP, and SmolAgents compliance.

This tool provides video processing capabilities while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import io
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class VideoTool(BaseTool):
    """Tool for performing video operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the video tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="video",
            description="Tool for performing video operations",
            config=config
        )
        self._max_video_size = config.get('max_video_size', 100 * 1024 * 1024)  # 100MB
        self._max_duration = config.get('max_duration', 3600)  # 1 hour
        self._allowed_formats = config.get('allowed_formats', ['MP4', 'AVI', 'MOV', 'MKV'])
        self._max_resolution = config.get('max_resolution', (3840, 2160))  # 4K
        self._max_fps = config.get('max_fps', 60)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Video cache
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
            logger.error(f"Failed to initialize VideoTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up VideoTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'convert': True,
            'trim': True,
            'merge': True,
            'split': True,
            'resize': True,
            'rotate': True,
            'filter': True,
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
            'max_video_size': self._max_video_size,
            'max_duration': self._max_duration,
            'allowed_formats': self._allowed_formats,
            'max_resolution': self._max_resolution,
            'max_fps': self._max_fps,
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
        if command == 'convert':
            return await self._convert_format(args)
        elif command == 'trim':
            return await self._trim_video(args)
        elif command == 'merge':
            return await self._merge_video(args)
        elif command == 'split':
            return await self._split_video(args)
        elif command == 'resize':
            return await self._resize_video(args)
        elif command == 'rotate':
            return await self._rotate_video(args)
        elif command == 'filter':
            return await self._apply_filter(args)
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
    
    def _get_cache_key(self, video_data: bytes, operation: str, **kwargs) -> str:
        """Generate a cache key for video data.
        
        Args:
            video_data: Video data
            operation: Operation performed
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        import hashlib
        params = [hashlib.md5(video_data).hexdigest(), operation]
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
    
    def _validate_video(self, video_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate video data.
        
        Args:
            video_data: Video data to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if len(video_data) > self._max_video_size:
            return False, f'Video exceeds maximum size ({self._max_video_size} bytes)'
        
        try:
            # Create a temporary file to read with OpenCV
            with io.BytesIO(video_data) as temp_file:
                cap = cv2.VideoCapture(temp_file)
                if not cap.isOpened():
                    return False, 'Invalid video data'
                
                # Get video properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Check resolution
                max_width, max_height = self._max_resolution
                if width > max_width or height > max_height:
                    return False, f'Video resolution exceeds maximum ({max_width}x{max_height})'
                
                # Check FPS
                if fps > self._max_fps:
                    return False, f'Video FPS exceeds maximum ({self._max_fps})'
                
                # Check duration
                duration = frame_count / fps
                if duration > self._max_duration:
                    return False, f'Video duration exceeds maximum ({self._max_duration} seconds)'
                
                cap.release()
                return True, None
        except Exception as e:
            return False, f'Invalid video data: {str(e)}'
    
    async def _process_video(self, video_data: bytes, operation: str, **kwargs) -> Dict[str, Any]:
        """Process video data with the given operation.
        
        Args:
            video_data: Video data to process
            operation: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            # Validate video
            is_valid, error = self._validate_video(video_data)
            if not is_valid:
                return {'error': error}
            
            # Check cache
            cache_key = self._get_cache_key(video_data, operation, **kwargs)
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Process video
            with io.BytesIO(video_data) as temp_file:
                cap = cv2.VideoCapture(temp_file)
                if not cap.isOpened():
                    return {'error': 'Failed to open video'}
                
                # Get video properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                if operation == 'convert':
                    format = kwargs.get('format')
                    if format not in self._allowed_formats:
                        return {'error': f'Unsupported format: {format}'}
                    # Convert video format
                    output = io.BytesIO()
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                        out.write(frame)
                    out.release()
                    processed_data = output.getvalue()
                
                elif operation == 'trim':
                    start = kwargs.get('start', 0)
                    end = kwargs.get('end')
                    if end is None:
                        end = frame_count / fps
                    start_frame = int(start * fps)
                    end_frame = int(end * fps)
                    output = io.BytesIO()
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                    for _ in range(end_frame - start_frame):
                        ret, frame = cap.read()
                        if not ret:
                            break
                        out.write(frame)
                    out.release()
                    processed_data = output.getvalue()
                
                elif operation == 'merge':
                    other_video = kwargs.get('other_video')
                    if not other_video:
                        return {'error': 'Missing other video data'}
                    output = io.BytesIO()
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                    # Write first video
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                        out.write(frame)
                    # Write second video
                    with io.BytesIO(other_video) as other_file:
                        other_cap = cv2.VideoCapture(other_file)
                        while other_cap.isOpened():
                            ret, frame = other_cap.read()
                            if not ret:
                                break
                            out.write(frame)
                        other_cap.release()
                    out.release()
                    processed_data = output.getvalue()
                
                elif operation == 'split':
                    segments = kwargs.get('segments', 2)
                    segment_frames = frame_count // segments
                    segments_data = []
                    for i in range(segments):
                        output = io.BytesIO()
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                        start_frame = i * segment_frames
                        end_frame = start_frame + segment_frames if i < segments - 1 else frame_count
                        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                        for _ in range(end_frame - start_frame):
                            ret, frame = cap.read()
                            if not ret:
                                break
                            out.write(frame)
                        out.release()
                        segments_data.append(output.getvalue())
                    processed_data = segments_data
                
                elif operation == 'resize':
                    new_width = kwargs.get('width', width)
                    new_height = kwargs.get('height', height)
                    output = io.BytesIO()
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output, fourcc, fps, (new_width, new_height))
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                        resized_frame = cv2.resize(frame, (new_width, new_height))
                        out.write(resized_frame)
                    out.release()
                    processed_data = output.getvalue()
                
                elif operation == 'rotate':
                    angle = kwargs.get('angle', 0)
                    output = io.BytesIO()
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                        matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)
                        rotated_frame = cv2.warpAffine(frame, matrix, (width, height))
                        out.write(rotated_frame)
                    out.release()
                    processed_data = output.getvalue()
                
                elif operation == 'filter':
                    filter_type = kwargs.get('filter_type')
                    if filter_type == 'blur':
                        kernel_size = kwargs.get('kernel_size', 5)
                        output = io.BytesIO()
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                        while cap.isOpened():
                            ret, frame = cap.read()
                            if not ret:
                                break
                            filtered_frame = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
                            out.write(filtered_frame)
                        out.release()
                        processed_data = output.getvalue()
                    elif filter_type == 'grayscale':
                        output = io.BytesIO()
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                        while cap.isOpened():
                            ret, frame = cap.read()
                            if not ret:
                                break
                            filtered_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_GRAY2BGR)
                            out.write(filtered_frame)
                        out.release()
                        processed_data = output.getvalue()
                    else:
                        return {'error': f'Unsupported filter type: {filter_type}'}
                
                cap.release()
            
            # Cache result
            self._cache[cache_key] = {
                'data': {
                    'status': 'success',
                    'action': operation,
                    'video_data': processed_data,
                    'format': 'MP4',
                    'size': len(processed_data),
                    'duration': frame_count / fps
                },
                'timestamp': time.time()
            }
            
            return self._cache[cache_key]['data']
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return {'error': str(e)}
    
    async def _convert_format(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert video format.
        
        Args:
            args: Convert arguments
            
        Returns:
            Dict[str, Any]: Convert result
        """
        try:
            if not args or 'video_data' not in args or 'format' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_video(
                args['video_data'],
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
    
    async def _trim_video(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trim video.
        
        Args:
            args: Trim arguments
            
        Returns:
            Dict[str, Any]: Trim result
        """
        try:
            if not args or 'video_data' not in args:
                return {'error': 'Missing video data'}
            
            result = await self._process_video(
                args['video_data'],
                'trim',
                start=args.get('start', 0),
                end=args.get('end')
            )
            
            if 'error' not in result:
                self._add_to_history('trim', {
                    'start': args.get('start', 0),
                    'end': args.get('end'),
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error trimming video: {e}")
            return {'error': str(e)}
    
    async def _merge_video(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge video files.
        
        Args:
            args: Merge arguments
            
        Returns:
            Dict[str, Any]: Merge result
        """
        try:
            if not args or 'video_data' not in args or 'other_video' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_video(
                args['video_data'],
                'merge',
                other_video=args['other_video']
            )
            
            if 'error' not in result:
                self._add_to_history('merge', {
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error merging video: {e}")
            return {'error': str(e)}
    
    async def _split_video(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Split video into segments.
        
        Args:
            args: Split arguments
            
        Returns:
            Dict[str, Any]: Split result
        """
        try:
            if not args or 'video_data' not in args:
                return {'error': 'Missing video data'}
            
            result = await self._process_video(
                args['video_data'],
                'split',
                segments=args.get('segments', 2)
            )
            
            if 'error' not in result:
                self._add_to_history('split', {
                    'segments': args.get('segments', 2),
                    'sizes': [len(segment) for segment in result['video_data']]
                })
            
            return result
        except Exception as e:
            logger.error(f"Error splitting video: {e}")
            return {'error': str(e)}
    
    async def _resize_video(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resize video.
        
        Args:
            args: Resize arguments
            
        Returns:
            Dict[str, Any]: Resize result
        """
        try:
            if not args or 'video_data' not in args:
                return {'error': 'Missing video data'}
            
            result = await self._process_video(
                args['video_data'],
                'resize',
                width=args.get('width'),
                height=args.get('height')
            )
            
            if 'error' not in result:
                self._add_to_history('resize', {
                    'width': args.get('width'),
                    'height': args.get('height'),
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error resizing video: {e}")
            return {'error': str(e)}
    
    async def _rotate_video(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Rotate video.
        
        Args:
            args: Rotate arguments
            
        Returns:
            Dict[str, Any]: Rotate result
        """
        try:
            if not args or 'video_data' not in args:
                return {'error': 'Missing video data'}
            
            result = await self._process_video(
                args['video_data'],
                'rotate',
                angle=args.get('angle', 0)
            )
            
            if 'error' not in result:
                self._add_to_history('rotate', {
                    'angle': args.get('angle', 0),
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error rotating video: {e}")
            return {'error': str(e)}
    
    async def _apply_filter(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply a filter to video.
        
        Args:
            args: Filter arguments
            
        Returns:
            Dict[str, Any]: Filter result
        """
        try:
            if not args or 'video_data' not in args or 'filter_type' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_video(
                args['video_data'],
                'filter',
                filter_type=args['filter_type'],
                kernel_size=args.get('kernel_size', 5)
            )
            
            if 'error' not in result:
                self._add_to_history('filter', {
                    'filter_type': args['filter_type'],
                    'kernel_size': args.get('kernel_size', 5),
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
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