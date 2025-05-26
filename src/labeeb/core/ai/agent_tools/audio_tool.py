"""
Audio tool with A2A, MCP, and SmolAgents compliance.

This tool provides audio processing capabilities while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import time
import io
import wave
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class AudioTool(BaseTool):
    """Tool for performing audio operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the audio tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="audio",
            description="Tool for performing audio operations",
            config=config
        )
        self._max_audio_size = config.get('max_audio_size', 50 * 1024 * 1024)  # 50MB
        self._max_duration = config.get('max_duration', 3600)  # 1 hour
        self._allowed_formats = config.get('allowed_formats', ['WAV', 'MP3', 'OGG', 'FLAC'])
        self._sample_rate = config.get('sample_rate', 44100)
        self._channels = config.get('channels', 2)
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._cache = {}  # Audio cache
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
            logger.error(f"Failed to initialize AudioTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            self._cache = {}
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up AudioTool: {e}")
    
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
            'normalize': True,
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
            'max_audio_size': self._max_audio_size,
            'max_duration': self._max_duration,
            'allowed_formats': self._allowed_formats,
            'sample_rate': self._sample_rate,
            'channels': self._channels,
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
            return await self._trim_audio(args)
        elif command == 'merge':
            return await self._merge_audio(args)
        elif command == 'split':
            return await self._split_audio(args)
        elif command == 'normalize':
            return await self._normalize_audio(args)
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
    
    def _get_cache_key(self, audio_data: bytes, operation: str, **kwargs) -> str:
        """Generate a cache key for audio data.
        
        Args:
            audio_data: Audio data
            operation: Operation performed
            **kwargs: Additional parameters
            
        Returns:
            str: Cache key
        """
        import hashlib
        params = [hashlib.md5(audio_data).hexdigest(), operation]
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
    
    def _validate_audio(self, audio_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate audio data.
        
        Args:
            audio_data: Audio data to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if len(audio_data) > self._max_audio_size:
            return False, f'Audio exceeds maximum size ({self._max_audio_size} bytes)'
        
        try:
            with wave.open(io.BytesIO(audio_data), 'rb') as wav:
                if wav.getnchannels() not in [1, 2]:
                    return False, f'Unsupported number of channels: {wav.getnchannels()}'
                
                if wav.getsampwidth() not in [1, 2, 4]:
                    return False, f'Unsupported sample width: {wav.getsampwidth()}'
                
                duration = wav.getnframes() / wav.getframerate()
                if duration > self._max_duration:
                    return False, f'Audio exceeds maximum duration ({self._max_duration} seconds)'
            
            return True, None
        except Exception as e:
            return False, f'Invalid audio data: {str(e)}'
    
    async def _process_audio(self, audio_data: bytes, operation: str, **kwargs) -> Dict[str, Any]:
        """Process audio data with the given operation.
        
        Args:
            audio_data: Audio data to process
            operation: Operation to perform
            **kwargs: Operation parameters
            
        Returns:
            Dict[str, Any]: Processing result
        """
        try:
            # Validate audio
            is_valid, error = self._validate_audio(audio_data)
            if not is_valid:
                return {'error': error}
            
            # Check cache
            cache_key = self._get_cache_key(audio_data, operation, **kwargs)
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]['data']
            
            # Process audio
            with wave.open(io.BytesIO(audio_data), 'rb') as wav:
                params = wav.getparams()
                frames = wav.readframes(wav.getnframes())
                audio_array = np.frombuffer(frames, dtype=np.int16)
                
                if operation == 'convert':
                    format = kwargs.get('format')
                    if format not in self._allowed_formats:
                        return {'error': f'Unsupported format: {format}'}
                    # Convert audio format
                    output = io.BytesIO()
                    with wave.open(output, 'wb') as out_wav:
                        out_wav.setparams(params)
                        out_wav.writeframes(audio_array.tobytes())
                    processed_data = output.getvalue()
                
                elif operation == 'trim':
                    start = kwargs.get('start', 0)
                    end = kwargs.get('end')
                    if end is None:
                        end = len(audio_array) / self._sample_rate
                    start_frame = int(start * self._sample_rate)
                    end_frame = int(end * self._sample_rate)
                    audio_array = audio_array[start_frame:end_frame]
                    output = io.BytesIO()
                    with wave.open(output, 'wb') as out_wav:
                        out_wav.setparams(params)
                        out_wav.writeframes(audio_array.tobytes())
                    processed_data = output.getvalue()
                
                elif operation == 'merge':
                    other_audio = kwargs.get('other_audio')
                    if not other_audio:
                        return {'error': 'Missing other audio data'}
                    with wave.open(io.BytesIO(other_audio), 'rb') as other_wav:
                        other_frames = other_wav.readframes(other_wav.getnframes())
                        other_array = np.frombuffer(other_frames, dtype=np.int16)
                        merged_array = np.concatenate([audio_array, other_array])
                    output = io.BytesIO()
                    with wave.open(output, 'wb') as out_wav:
                        out_wav.setparams(params)
                        out_wav.writeframes(merged_array.tobytes())
                    processed_data = output.getvalue()
                
                elif operation == 'split':
                    segments = kwargs.get('segments', 2)
                    segment_length = len(audio_array) // segments
                    segments_data = []
                    for i in range(segments):
                        start = i * segment_length
                        end = start + segment_length if i < segments - 1 else len(audio_array)
                        segment_array = audio_array[start:end]
                        output = io.BytesIO()
                        with wave.open(output, 'wb') as out_wav:
                            out_wav.setparams(params)
                            out_wav.writeframes(segment_array.tobytes())
                        segments_data.append(output.getvalue())
                    processed_data = segments_data
                
                elif operation == 'normalize':
                    max_value = np.max(np.abs(audio_array))
                    if max_value > 0:
                        normalized_array = (audio_array / max_value * 32767).astype(np.int16)
                    else:
                        normalized_array = audio_array
                    output = io.BytesIO()
                    with wave.open(output, 'wb') as out_wav:
                        out_wav.setparams(params)
                        out_wav.writeframes(normalized_array.tobytes())
                    processed_data = output.getvalue()
                
                elif operation == 'filter':
                    filter_type = kwargs.get('filter_type')
                    if filter_type == 'lowpass':
                        # Simple low-pass filter
                        cutoff = kwargs.get('cutoff', 1000)
                        nyquist = self._sample_rate / 2
                        normalized_cutoff = cutoff / nyquist
                        b, a = signal.butter(4, normalized_cutoff, btype='low')
                        filtered_array = signal.filtfilt(b, a, audio_array)
                    elif filter_type == 'highpass':
                        # Simple high-pass filter
                        cutoff = kwargs.get('cutoff', 1000)
                        nyquist = self._sample_rate / 2
                        normalized_cutoff = cutoff / nyquist
                        b, a = signal.butter(4, normalized_cutoff, btype='high')
                        filtered_array = signal.filtfilt(b, a, audio_array)
                    else:
                        return {'error': f'Unsupported filter type: {filter_type}'}
                    output = io.BytesIO()
                    with wave.open(output, 'wb') as out_wav:
                        out_wav.setparams(params)
                        out_wav.writeframes(filtered_array.tobytes())
                    processed_data = output.getvalue()
            
            # Cache result
            self._cache[cache_key] = {
                'data': {
                    'status': 'success',
                    'action': operation,
                    'audio_data': processed_data,
                    'format': 'WAV',
                    'size': len(processed_data),
                    'duration': len(audio_array) / self._sample_rate
                },
                'timestamp': time.time()
            }
            
            return self._cache[cache_key]['data']
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return {'error': str(e)}
    
    async def _convert_format(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert audio format.
        
        Args:
            args: Convert arguments
            
        Returns:
            Dict[str, Any]: Convert result
        """
        try:
            if not args or 'audio_data' not in args or 'format' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_audio(
                args['audio_data'],
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
    
    async def _trim_audio(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trim audio.
        
        Args:
            args: Trim arguments
            
        Returns:
            Dict[str, Any]: Trim result
        """
        try:
            if not args or 'audio_data' not in args:
                return {'error': 'Missing audio data'}
            
            result = await self._process_audio(
                args['audio_data'],
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
            logger.error(f"Error trimming audio: {e}")
            return {'error': str(e)}
    
    async def _merge_audio(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge audio files.
        
        Args:
            args: Merge arguments
            
        Returns:
            Dict[str, Any]: Merge result
        """
        try:
            if not args or 'audio_data' not in args or 'other_audio' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_audio(
                args['audio_data'],
                'merge',
                other_audio=args['other_audio']
            )
            
            if 'error' not in result:
                self._add_to_history('merge', {
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error merging audio: {e}")
            return {'error': str(e)}
    
    async def _split_audio(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Split audio into segments.
        
        Args:
            args: Split arguments
            
        Returns:
            Dict[str, Any]: Split result
        """
        try:
            if not args or 'audio_data' not in args:
                return {'error': 'Missing audio data'}
            
            result = await self._process_audio(
                args['audio_data'],
                'split',
                segments=args.get('segments', 2)
            )
            
            if 'error' not in result:
                self._add_to_history('split', {
                    'segments': args.get('segments', 2),
                    'sizes': [len(segment) for segment in result['audio_data']]
                })
            
            return result
        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            return {'error': str(e)}
    
    async def _normalize_audio(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Normalize audio.
        
        Args:
            args: Normalize arguments
            
        Returns:
            Dict[str, Any]: Normalize result
        """
        try:
            if not args or 'audio_data' not in args:
                return {'error': 'Missing audio data'}
            
            result = await self._process_audio(
                args['audio_data'],
                'normalize'
            )
            
            if 'error' not in result:
                self._add_to_history('normalize', {
                    'size': result['size']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return {'error': str(e)}
    
    async def _apply_filter(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply a filter to audio.
        
        Args:
            args: Filter arguments
            
        Returns:
            Dict[str, Any]: Filter result
        """
        try:
            if not args or 'audio_data' not in args or 'filter_type' not in args:
                return {'error': 'Missing required arguments'}
            
            result = await self._process_audio(
                args['audio_data'],
                'filter',
                filter_type=args['filter_type'],
                cutoff=args.get('cutoff', 1000)
            )
            
            if 'error' not in result:
                self._add_to_history('filter', {
                    'filter_type': args['filter_type'],
                    'cutoff': args.get('cutoff', 1000),
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