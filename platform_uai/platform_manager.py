"""
Platform initialization module for UaiBot

This module handles initializing the appropriate platform-specific components
based on the detected system (Mac, Jetson, or Ubuntu).
"""
import os
import sys
import importlib
import platform
from core.utils import get_platform_name, get_project_root, load_config

class PlatformManager:
    def __init__(self):
        self.platform_name = get_platform_name()
        self.config = load_config()
        self.audio_handler = None
        self.usb_handler = None
        self.input_handler = None
        self.apple_silicon_optimizer = None
        self.is_apple_silicon = False
        
        # Check if the platform is supported
        if not self.platform_name:
            print(f"ERROR: Unsupported platform: {platform.system()}")
            self.platform_supported = False
        else:
            self.platform_supported = True
            
            # Check for Apple Silicon if on Mac
            if self.platform_name == 'mac' and platform.system() == 'Darwin' and platform.machine() == 'arm64':
                self._init_apple_silicon()
            
    def _init_apple_silicon(self):
        """Initialize Apple Silicon specific optimizations if available"""
        try:
            # Try to import the Apple Silicon optimizer
            from platform_uai.mac.apple_silicon import apple_silicon_optimizer
            self.apple_silicon_optimizer = apple_silicon_optimizer
            self.is_apple_silicon = self.apple_silicon_optimizer.is_apple_silicon
            
            if self.is_apple_silicon:
                print(f"Detected Apple Silicon: {self.apple_silicon_optimizer.chip_details.get('name', 'Unknown')}")
        except ImportError as e:
            print(f"Note: Apple Silicon optimizations not available: {e}")
            self.is_apple_silicon = False
            
    def initialize(self):
        """Initialize all platform-specific components"""
        if not self.platform_supported:
            print("Cannot initialize - platform not supported")
            return False
            
        # Import platform utils
        try:
            from platform_uai.platform_utils import get_audio_handler, get_usb_handler, get_input_handler
            
            # Initialize audio handler
            self.audio_handler = get_audio_handler()
            if not self.audio_handler:
                print(f"Failed to initialize audio handler for {self.platform_name}")
            
            # Initialize USB handler
            self.usb_handler = get_usb_handler()
            if not self.usb_handler:
                print(f"Failed to initialize USB handler for {self.platform_name}")
                
            # Initialize Input handler
            self.input_handler = get_input_handler()
            if not self.input_handler:
                print(f"Failed to initialize input handler for {self.platform_name}")
                
            return all([self.audio_handler, self.usb_handler, self.input_handler])
        except ImportError as e:
            print(f"Failed to import platform utilities: {e}")
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
    
    def get_platform_info(self):
        """Get information about the current platform"""
        info = {
            'name': self.platform_name,
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
        }
        
        # Add Apple Silicon specific info if available
        if self.is_apple_silicon and self.apple_silicon_optimizer:
            apple_silicon_info = self.apple_silicon_optimizer.get_optimization_status()
            info['apple_silicon'] = True
            info['chip_name'] = apple_silicon_info.get('chip_details', {}).get('name', 'Unknown Apple Silicon')
            info['neural_engine_available'] = apple_silicon_info.get('neural_engine_available', False)
        
        return info
    
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
