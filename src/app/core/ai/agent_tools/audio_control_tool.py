"""
Audio control tool with A2A, MCP, and SmolAgents compliance.

This tool provides audio control functionality while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import os
import platform
from typing import Dict, Any, List, Optional, Union
import sounddevice as sd
import soundfile as sf
import numpy as np
from app.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class AudioControlTool(BaseTool):
    """Tool for controlling audio playback and recording with platform-specific optimizations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the audio control tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="audio_control",
            description="Tool for controlling audio playback and recording with platform-specific optimizations",
            config=config
        )
        self._sample_rate = config.get('sample_rate', 44100)
        self._channels = config.get('channels', 2)
        self._device = config.get('device', None)
        self._stream = None
        self._is_recording = False
        self._is_playing = False
        self._current_file = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Initialize audio device
            if self._device is None:
                self._device = sd.default.device
            
            # Test audio device
            sd.check_input_settings(device=self._device, channels=self._channels, samplerate=self._sample_rate)
            sd.check_output_settings(device=self._device, channels=self._channels, samplerate=self._sample_rate)
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize AudioControlTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up AudioControlTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'play': True,
            'record': True,
            'stop': True,
            'pause': True,
            'resume': True,
            'get_devices': True,
            'get_status': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'sample_rate': self._sample_rate,
            'channels': self._channels,
            'device': self._device,
            'is_recording': self._is_recording,
            'is_playing': self._is_playing,
            'current_file': self._current_file
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
        if command == 'play':
            return await self._play_audio(args)
        elif command == 'record':
            return await self._record_audio(args)
        elif command == 'stop':
            return await self._stop_audio()
        elif command == 'pause':
            return await self._pause_audio()
        elif command == 'resume':
            return await self._resume_audio()
        elif command == 'get_devices':
            return await self._get_audio_devices()
        else:
            return {'error': f'Unknown command: {command}'}
    
    async def _play_audio(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Play audio from a file.
        
        Args:
            args: Playback arguments
            
        Returns:
            Dict[str, Any]: Result of playback
        """
        try:
            if not args or 'file' not in args:
                return {'error': 'Missing file parameter'}
            
            file_path = args['file']
            if not os.path.exists(file_path):
                return {'error': f'File not found: {file_path}'}
            
            # Stop any current playback
            if self._is_playing:
                await self._stop_audio()
            
            # Load and play audio
            data, sample_rate = sf.read(file_path)
            self._stream = sd.OutputStream(
                samplerate=sample_rate,
                channels=data.shape[1] if len(data.shape) > 1 else 1,
                device=self._device
            )
            self._stream.start()
            self._stream.write(data)
            self._is_playing = True
            self._current_file = file_path
            
            return {
                'status': 'success',
                'action': 'play',
                'file': file_path
            }
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return {'error': str(e)}
    
    async def _record_audio(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record audio to a file.
        
        Args:
            args: Recording arguments
            
        Returns:
            Dict[str, Any]: Result of recording
        """
        try:
            if not args or 'file' not in args:
                return {'error': 'Missing file parameter'}
            
            file_path = args['file']
            duration = args.get('duration', 5)  # seconds
            
            # Stop any current recording
            if self._is_recording:
                await self._stop_audio()
            
            # Start recording
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                device=self._device
            )
            self._stream.start()
            self._is_recording = True
            
            # Record audio
            data = self._stream.read(int(duration * self._sample_rate))
            sf.write(file_path, data[0], self._sample_rate)
            
            return {
                'status': 'success',
                'action': 'record',
                'file': file_path,
                'duration': duration
            }
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return {'error': str(e)}
    
    async def _stop_audio(self) -> Dict[str, Any]:
        """Stop audio playback or recording.
        
        Returns:
            Dict[str, Any]: Result of stop operation
        """
        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            
            self._is_playing = False
            self._is_recording = False
            self._current_file = None
            
            return {
                'status': 'success',
                'action': 'stop'
            }
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
            return {'error': str(e)}
    
    async def _pause_audio(self) -> Dict[str, Any]:
        """Pause audio playback.
        
        Returns:
            Dict[str, Any]: Result of pause operation
        """
        try:
            if not self._is_playing:
                return {'error': 'No audio is currently playing'}
            
            if self._stream:
                self._stream.stop()
                self._is_playing = False
            
            return {
                'status': 'success',
                'action': 'pause'
            }
        except Exception as e:
            logger.error(f"Error pausing audio: {e}")
            return {'error': str(e)}
    
    async def _resume_audio(self) -> Dict[str, Any]:
        """Resume audio playback.
        
        Returns:
            Dict[str, Any]: Result of resume operation
        """
        try:
            if self._is_playing:
                return {'error': 'Audio is already playing'}
            
            if not self._current_file:
                return {'error': 'No audio file to resume'}
            
            return await self._play_audio({'file': self._current_file})
        except Exception as e:
            logger.error(f"Error resuming audio: {e}")
            return {'error': str(e)}
    
    async def _get_audio_devices(self) -> Dict[str, Any]:
        """Get available audio devices.
        
        Returns:
            Dict[str, Any]: List of audio devices
        """
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            output_devices = [d for d in devices if d['max_output_channels'] > 0]
            
            return {
                'status': 'success',
                'action': 'get_devices',
                'input_devices': input_devices,
                'output_devices': output_devices
            }
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
            return {'error': str(e)} 