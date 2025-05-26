"""
Tests for platform-specific handlers.

This module contains tests for the platform-specific handlers,
ensuring they work correctly on their respective platforms.
"""
import os
import sys
import unittest
from typing import Dict, Any, Optional
from src.app.platform_core.platform_manager import platform_manager
from src.app.platform_core.common.base_handler import BaseHandler
from src.app.platform_core.mac.input_handler import MacInputHandler
from src.app.platform_core.mac.audio_handler import MacAudioHandler
from src.app.platform_core.mac.display_handler import MacDisplayHandler
from src.app.platform_core.mac.usb_handler import MacUSBHandler

class TestPlatformManager(unittest.TestCase):
    """Tests for the platform manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = platform_manager
    
    def test_platform_detection(self):
        """Test platform detection."""
        platform = self.manager.get_platform()
        self.assertIn(platform, ['macos', 'ubuntu', 'windows', 'unknown'])
    
    def test_platform_support(self):
        """Test platform support check."""
        is_supported = self.manager.is_platform_supported()
        self.assertIsInstance(is_supported, bool)
    
    def test_handler_initialization(self):
        """Test handler initialization."""
        # Initialize platform manager
        self.assertTrue(self.manager.initialize())
        
        # Check available handlers
        handlers = self.manager.get_available_handlers()
        self.assertIsInstance(handlers, list)
        
        # Check each handler
        for handler_type in handlers:
            handler = self.manager.get_handler(handler_type)
            self.assertIsNotNone(handler)
            self.assertTrue(handler.is_available())
    
    def test_configuration_management(self):
        """Test configuration management."""
        # Get current config
        config = self.manager.get_config()
        self.assertIsInstance(config, dict)
        
        # Update config
        new_config = {'test': {'enabled': True}}
        self.assertTrue(self.manager.update_config(new_config))
        
        # Verify update
        updated_config = self.manager.get_config()
        self.assertIn('test', updated_config)
        self.assertTrue(updated_config['test']['enabled'])

class TestBaseHandler(unittest.TestCase):
    """Tests for the base handler."""
    
    def setUp(self):
        """Set up test environment."""
        self.handler = BaseHandler()
    
    def test_initialization(self):
        """Test handler initialization."""
        self.assertTrue(self.handler.initialize())
        self.assertTrue(self.handler.is_available())
    
    def test_cleanup(self):
        """Test handler cleanup."""
        self.handler.initialize()
        self.handler.cleanup()
        self.assertFalse(self.handler.is_available())
    
    def test_configuration_management(self):
        """Test configuration management."""
        # Get config
        config = self.handler.get_config()
        self.assertIsInstance(config, dict)
        
        # Update config
        new_config = {'test': {'enabled': True}}
        self.assertTrue(self.handler.update_config(new_config))
        
        # Verify update
        updated_config = self.handler.get_config()
        self.assertIn('test', updated_config)
        self.assertTrue(updated_config['test']['enabled'])
    
    def test_feature_management(self):
        """Test feature management."""
        # Set up test feature
        self.handler.update_config({'test_feature': {'enabled': True}})
        
        # Get feature config
        feature_config = self.handler.get_feature_config('test_feature')
        self.assertIsInstance(feature_config, dict)
        self.assertTrue(feature_config['enabled'])
        
        # Check feature enabled
        self.assertTrue(self.handler.is_feature_enabled('test_feature'))
    
    def test_platform_specific_path(self):
        """Test platform-specific path handling."""
        path = self.handler.get_platform_specific_path('test')
        self.assertIsInstance(path, str)
        self.assertTrue(os.path.exists(os.path.dirname(path)))

@unittest.skipIf(sys.platform != 'darwin', "macOS-specific tests")
class TestMacHandlers(unittest.TestCase):
    """Tests for macOS-specific handlers."""
    
    def setUp(self):
        """Set up test environment."""
        self.input_handler = MacInputHandler()
        self.audio_handler = MacAudioHandler()
        self.display_handler = MacDisplayHandler()
        self.usb_handler = MacUSBHandler()
    
    def test_input_handler(self):
        """Test input handler."""
        # Initialize
        self.assertTrue(self.input_handler.initialize())
        self.assertTrue(self.input_handler.is_available())
        
        # Test mouse position
        pos = self.input_handler.get_mouse_position()
        self.assertIsInstance(pos, tuple)
        self.assertEqual(len(pos), 2)
        
        # Test mouse movement
        self.assertTrue(self.input_handler.move_mouse(100, 100))
        
        # Test mouse click
        self.assertTrue(self.input_handler.click_mouse())
        
        # Test keyboard input
        self.assertTrue(self.input_handler.type_text("test"))
        
        # Cleanup
        self.input_handler.cleanup()
        self.assertFalse(self.input_handler.is_available())
    
    def test_audio_handler(self):
        """Test audio handler."""
        # Initialize
        self.assertTrue(self.audio_handler.initialize())
        self.assertTrue(self.audio_handler.is_available())
        
        # Test device listing
        input_devices = self.audio_handler.get_input_devices()
        self.assertIsInstance(input_devices, list)
        
        output_devices = self.audio_handler.get_output_devices()
        self.assertIsInstance(output_devices, list)
        
        # Test volume control
        volume = self.audio_handler.get_volume()
        self.assertIsInstance(volume, float)
        self.assertTrue(0.0 <= volume <= 1.0)
        
        # Test mute control
        muted = self.audio_handler.is_muted()
        self.assertIsInstance(muted, bool)
        
        # Cleanup
        self.audio_handler.cleanup()
        self.assertFalse(self.audio_handler.is_available())
    
    def test_display_handler(self):
        """Test display handler."""
        # Initialize
        self.assertTrue(self.display_handler.initialize())
        self.assertTrue(self.display_handler.is_available())
        
        # Test display listing
        displays = self.display_handler.get_displays()
        self.assertIsInstance(displays, list)
        self.assertTrue(len(displays) > 0)
        
        # Test main display
        main_display = self.display_handler.get_main_display()
        self.assertIsNotNone(main_display)
        
        # Test screen capture
        screen_data = self.display_handler.capture_screen()
        self.assertIsInstance(screen_data, bytes)
        
        # Test display resolution
        resolution = self.display_handler.get_display_resolution()
        self.assertIsInstance(resolution, tuple)
        self.assertEqual(len(resolution), 2)
        
        # Cleanup
        self.display_handler.cleanup()
        self.assertFalse(self.display_handler.is_available())
    
    def test_usb_handler(self):
        """Test USB handler."""
        # Initialize
        self.assertTrue(self.usb_handler.initialize())
        self.assertTrue(self.usb_handler.is_available())
        
        # Test device listing
        devices = self.usb_handler.get_devices()
        self.assertIsInstance(devices, list)
        
        # Test device properties
        if devices:
            device = devices[0]
            self.assertIn('id', device)
            self.assertIn('name', device)
            self.assertIn('vendor_id', device)
            self.assertIn('product_id', device)
            
            # Test device speed
            speed = self.usb_handler.get_device_speed(device['id'])
            self.assertIsInstance(speed, str)
            
            # Test device power
            power = self.usb_handler.get_device_power(device['id'])
            self.assertIsInstance(power, (float, type(None)))
            
            # Test device interfaces
            interfaces = self.usb_handler.get_device_interfaces(device['id'])
            self.assertIsInstance(interfaces, list)
        
        # Cleanup
        self.usb_handler.cleanup()
        self.assertFalse(self.usb_handler.is_available())

if __name__ == '__main__':
    unittest.main() 