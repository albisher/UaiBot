#!/usr/bin/env python3
"""
Unit tests for the simulation mode of the input control system.
"""
import os
import sys
import unittest
from unittest import mock

# Add project root to path for importing
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

class SimulationModeTest(unittest.TestCase):
    """Test case for the simulation mode of the input control system."""
    
    def setUp(self):
        """Set up the test case."""
        # Save original display
        self.original_display = os.environ.get('DISPLAY')
        
        # Set empty display to force simulation mode
        os.environ['DISPLAY'] = ''
        
    def tearDown(self):
        """Clean up after the test case."""
        # Restore original display
        if self.original_display is None:
            del os.environ['DISPLAY']
        else:
            os.environ['DISPLAY'] = self.original_display
            
    def test_simulation_mode_activation(self):
        """Test that simulation mode is activated when DISPLAY is empty."""
        # Import with empty DISPLAY
        from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
        handler = MouseKeyboardHandler()
        
        # Check if simulation mode is active
        self.assertTrue(hasattr(handler, '_simulate_only'))
        self.assertTrue(handler._simulate_only)
        
    def test_simulation_mode_functions(self):
        """Test that functions work in simulation mode."""
        # Import with simulation mode
        from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
        handler = MouseKeyboardHandler()
        
        # Test basic functions
        position = handler.get_mouse_position()
        self.assertIsInstance(position, tuple)
        
        size = handler.get_screen_size()
        self.assertIsInstance(size, tuple)
        
        # Move mouse in simulation mode
        handler.move_mouse(200, 200)
        new_position = handler.get_mouse_position()
        self.assertEqual(new_position, (200, 200))
        
    def test_simulation_mode_environment(self):
        """Test that simulation mode is activated based on environment variables."""
        # Test with empty DISPLAY
        os.environ['DISPLAY'] = ''
        from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
        handler = MouseKeyboardHandler()
        self.assertTrue(handler._simulate_only)
        
        # Test with non-empty DISPLAY
        os.environ['DISPLAY'] = ':0'
        handler = MouseKeyboardHandler()
        self.assertFalse(handler._simulate_only)
        
    def test_simulation_mode_import(self):
        """Test that simulation mode is activated during import."""
        # Test with empty DISPLAY
        os.environ['DISPLAY'] = ''
        from uaibot.platform_uai.common.input_control.mouse_keyboard_handler import MouseKeyboardHandler
        handler = MouseKeyboardHandler()
        self.assertTrue(handler._simulate_only)
        
        # Test with non-empty DISPLAY
        os.environ['DISPLAY'] = ':0'
        handler = MouseKeyboardHandler()
        self.assertFalse(handler._simulate_only)


if __name__ == "__main__":
    unittest.main()
