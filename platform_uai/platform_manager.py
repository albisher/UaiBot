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
        
        # Check if the platform is supported
        if not self.platform_name:
            print(f"ERROR: Unsupported platform: {platform.system()}")
            self.platform_supported = False
        else:
            self.platform_supported = True
            
    def initialize(self):
        """Initialize all platform-specific components"""
        if not self.platform_supported:
            print("Cannot initialize - platform not supported")
            return False
            
        # Import platform utils
        try:
            from platform_uai.platform_utils import get_audio_handler, get_usb_handler
            
            # Initialize audio handler
            self.audio_handler = get_audio_handler()
            if not self.audio_handler:
                print(f"Failed to initialize audio handler for {self.platform_name}")
            
            # Initialize USB handler
            self.usb_handler = get_usb_handler()
            if not self.usb_handler:
                print(f"Failed to initialize USB handler for {self.platform_name}")
                
            # Check if both handlers were initialized successfully
            if self.audio_handler and self.usb_handler:
                print(f"Successfully initialized platform components for {self.platform_name}")
                return True
            else:
                print(f"Platform initialization incomplete for {self.platform_name}")
                return False
                
        except ImportError as e:
            print(f"Failed to import platform handlers: {e}")
            return False
            
    def get_audio_handler(self):
        """Get the platform-specific audio handler"""
        return self.audio_handler
        
    def get_usb_handler(self):
        """Get the platform-specific USB handler"""
        return self.usb_handler
        
    def get_platform_info(self):
        """Get information about the current platform"""
        if not self.platform_supported:
            return {"error": f"Unsupported platform: {platform.system()}"}
            
        # Basic platform information
        info = {
            "platform_name": self.platform_name,
            "system": platform.system(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "handlers_initialized": {
                "audio": self.audio_handler is not None,
                "usb": self.usb_handler is not None
            }
        }
        
        # Add audio device information if available
        if self.audio_handler:
            try:
                info["audio_devices"] = self.audio_handler.list_audio_devices()
            except:
                info["audio_devices"] = "Error retrieving audio devices"
                
        # Add USB device information if available
        if self.usb_handler:
            try:
                info["usb_devices"] = self.usb_handler.get_device_list()
            except:
                info["usb_devices"] = "Error retrieving USB devices"
                
        return info
