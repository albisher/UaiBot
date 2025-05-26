"""
Platform initialization module for UaiBot

This module handles initializing the appropriate platform-specific components
based on the detected system (Mac, Jetson, or Ubuntu).
"""
import os
import sys
import importlib
import platform
from uaibot.utils import get_platform_name, get_project_root, load_config
import logging
from uaibot.platform_uai.mac.apple_silicon import apple_silicon_optimizer
from uaibot.platform_uai.platform_utils import get_audio_handler, get_usb_handler, get_input_handler
from typing import Dict, Optional, List, Union
from dataclasses import dataclass

@dataclass
class PlatformInfo:
    """Information about the current platform."""
    system: str
    release: str
    version: str
    machine: str
    processor: str
    is_supported: bool

class PlatformManager:
    """Manages platform-specific functionality and compatibility."""
    
    def __init__(self):
        """Initialize the platform manager."""
        self.supported_platforms = ['Darwin', 'Linux', 'Windows']
        self.platform_info = self._get_platform_info()
        self._validate_platform()
        self.platform_name = get_platform_name()
        self.config = load_config()
        self.audio_handler = None
        self.usb_handler = None
        self.input_handler = None
        self.apple_silicon_optimizer = None
        self.is_apple_silicon = False
        
    def _get_platform_info(self) -> PlatformInfo:
        """Get information about the current platform.
        
        Returns:
            PlatformInfo object containing platform details.
        """
        system = platform.system()
        return PlatformInfo(
            system=system,
            release=platform.release(),
            version=platform.version(),
            machine=platform.machine(),
            processor=platform.processor(),
            is_supported=system in self.supported_platforms
        )
    
    def _validate_platform(self) -> None:
        """Validate that the current platform is supported.
        
        Raises:
            RuntimeError: If the platform is not supported.
        """
        if not self.platform_info.is_supported:
            raise RuntimeError(
                f"Unsupported platform: {self.platform_info.system}. "
                f"Supported platforms are: {', '.join(self.supported_platforms)}"
            )
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get platform information as a dictionary.
        
        Returns:
            Dictionary containing platform information.
        """
        return {
            'system': self.platform_info.system,
            'release': self.platform_info.release,
            'version': self.platform_info.version,
            'machine': self.platform_info.machine,
            'processor': self.platform_info.processor,
            'is_supported': str(self.platform_info.is_supported)
        }
    
    def get_platform_specific_path(self, path: str) -> str:
        """Convert a path to be platform-specific.
        
        Args:
            path: Path to convert.
            
        Returns:
            Platform-specific path.
        """
        if self.platform_info.system == 'Windows':
            return path.replace('/', '\\')
        return path.replace('\\', '/')
    
    def get_platform_specific_command(self, command: str) -> str:
        """Convert a command to be platform-specific.
        
        Args:
            command: Command to convert.
            
        Returns:
            Platform-specific command.
        """
        if self.platform_info.system == 'Windows':
            # Handle Windows-specific command conversions
            if command.startswith('ls'):
                return command.replace('ls', 'dir')
            elif command.startswith('rm'):
                return command.replace('rm', 'del')
            elif command.startswith('cp'):
                return command.replace('cp', 'copy')
            elif command.startswith('mv'):
                return command.replace('mv', 'move')
        return command
    
    def is_platform_supported(self) -> bool:
        """Check if the current platform is supported.
        
        Returns:
            True if the platform is supported, False otherwise.
        """
        return self.platform_info.is_supported
    
    def get_platform_specific_environment(self) -> Dict[str, str]:
        """Get platform-specific environment variables.
        
        Returns:
            Dictionary containing platform-specific environment variables.
        """
        env = os.environ.copy()
        
        if self.platform_info.system == 'Windows':
            # Add Windows-specific environment variables
            env['COMSPEC'] = os.environ.get('COMSPEC', 'cmd.exe')
        elif self.platform_info.system == 'Darwin':
            # Add macOS-specific environment variables
            env['SHELL'] = os.environ.get('SHELL', '/bin/zsh')
        elif self.platform_info.system == 'Linux':
            # Add Linux-specific environment variables
            env['SHELL'] = os.environ.get('SHELL', '/bin/bash')
        
        return env
    
    def initialize(self, mode='interactive', fast_mode=False):
        """Initialize all platform-specific components with mode awareness."""
        if not self.platform_info.is_supported:
            print("Cannot initialize - platform not supported")
            return False
        logger = logging.getLogger("UaiBot.PlatformManager")
        try:
            # Initialize audio handler
            self.audio_handler = get_audio_handler()
            if not self.audio_handler:
                logger.warning(f"Audio handler not initialized for {self.platform_info.system}")
            # Initialize USB handler
            self.usb_handler = get_usb_handler()
            if not self.usb_handler:
                logger.warning(f"USB handler not initialized for {self.platform_info.system}")
            # Initialize Input handler
            self.input_handler = get_input_handler()
            if not self.input_handler:
                logger.warning(f"Input handler not initialized for {self.platform_info.system}")
            # In non-interactive or fast mode, do not block or prompt
            if mode != 'interactive' or fast_mode:
                return True
            return all([self.audio_handler, self.usb_handler, self.input_handler])
        except ImportError as e:
            logger.warning(f"Failed to import platform utilities: {e}")
            return False
    
    def get_audio_handler(self):
        """Get the platform-specific audio handler"""
        return self.audio_handler
    
    def get_usb_handler(self):
        """Get the platform-specific USB handler"""
        return self.usb_handler
    
    def get_input_handler(self):
        """Get the platform-specific input handler"""
        return self.input_handler
    
    def get_ml_optimizations(self):
        """Get machine learning optimizations for the current platform"""
        if self.is_apple_silicon and self.apple_silicon_optimizer:
            return self.apple_silicon_optimizer.get_optimized_ml_config()
        
        # Default configuration for non-Apple Silicon platforms
        return {
            'use_metal': False,
            'use_neural_engine': False,
            'optimized_threading': True,
            'thread_count': os.cpu_count() or 4,
            'memory_limit': 1024  # in MB
        }
    
    def get_tensor_optimizations(self):
        """Get tensor operation optimizations for the current platform"""
        if self.is_apple_silicon and self.apple_silicon_optimizer:
            return self.apple_silicon_optimizer.get_optimized_tensor_config()
            
        # Default configuration for non-Apple Silicon platforms
        return {
            'backend': 'default',
            'precision': 'float32',
            'use_gpu': False,
            'use_metal': False
        }
        
    def optimize_process(self):
        """Apply platform-specific process optimizations"""
        if self.is_apple_silicon and self.apple_silicon_optimizer:
            self.apple_silicon_optimizer.optimize_process_priority()
    
    def check_simulation_mode(self):
        """Check if we're running in simulation mode"""
        # Simulation mode is active when no display is available
        # or when the DISPLAY environment variable is empty
        return not os.environ.get('DISPLAY') and platform.system() != 'Darwin'
    
    def cleanup(self):
        """Clean up platform-specific resources"""
        if self.audio_handler and hasattr(self.audio_handler, 'cleanup'):
            self.audio_handler.cleanup()
            
        if self.usb_handler and hasattr(self.usb_handler, 'cleanup'):
            self.usb_handler.cleanup()
            
        if self.input_handler and hasattr(self.input_handler, 'cleanup'):
            self.input_handler.cleanup()
