#!/usr/bin/env python3
"""
Test script for the simulation mode of UaiBot.
Tests the ability to simulate mouse and keyboard input.
"""
import os
import sys
import time
import unittest
import traceback

# Add parent directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from uaibot.core.command_processor.input_control.mouse_keyboard_handler import MouseKeyboardHandler
    print("Successfully imported MouseKeyboardHandler")
except ImportError as e:
    print(f"Error importing MouseKeyboardHandler: {e}")
    traceback.print_exc()
    sys.exit(1)

class TestSimulationMode(unittest.TestCase):
    """Test cases for the simulation mode functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.handler = MouseKeyboardHandler(quiet_mode=True)
    
    def test_mouse_movement(self):
        """Test mouse movement simulation."""
        # Get current mouse position
        start_pos = self.handler.get_mouse_position()

        # Move mouse to a new position
        target_pos = (start_pos[0] + 100, start_pos[1] + 100)
        self.handler.move_mouse_to(target_pos[0], target_pos[1])
        
        # Wait for movement to complete
        time.sleep(0.5)

        # Get new position
        end_pos = self.handler.get_mouse_position()
        
        # Check if mouse moved to target position
        self.assertAlmostEqual(end_pos[0], target_pos[0], delta=5)
        self.assertAlmostEqual(end_pos[1], target_pos[1], delta=5)
    
    def test_mouse_click(self):
        """Test mouse click simulation."""
        # Get current mouse position
        start_pos = self.handler.get_mouse_position()
        
        # Perform click
        self.handler.click_mouse()
        
        # Wait for click to complete
        time.sleep(0.5)
        
        # Get new position (should be same as start)
        end_pos = self.handler.get_mouse_position()
        
        # Check if mouse position didn't change
        self.assertEqual(end_pos, start_pos)
    
    def test_keyboard_input(self):
        """Test keyboard input simulation."""
        # Test string to type
        test_string = "Hello, UaiBot!"
        
        # Type the string
        self.handler.type_text(test_string)

        # Wait for typing to complete
        time.sleep(0.5)
        
        # Note: We can't easily verify the output
        # This test mainly ensures the function doesn't raise exceptions
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
