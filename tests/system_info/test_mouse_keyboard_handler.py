#!/usr/bin/env python3
"""
Unit tests for the MouseKeyboardHandler class.

These tests verify that mouse and keyboard control functionality works as expected
according to the enhancement guidelines in /reference/enhance_knm.txt
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from app.core.command_processor.input_control.mouse_keyboard_handler import MouseKeyboardHandler


class TestMouseKeyboardHandlerWithMocks(unittest.TestCase):
    """
    Test the MouseKeyboardHandler class with mocked dependencies.
    This allows testing without actually controlling the mouse/keyboard.
    """

    def setUp(self):
        """Set up test fixtures, mocking PyAutoGUI and other libraries."""
        # Create patches for the imports
        self.pyautogui_patch = patch('pyautogui')
        self.keyboard_patch = patch('keyboard')
        self.mouse_patch = patch('mouse')
        
        # Create mock objects
        self.mock_pyautogui = self.pyautogui_patch.start()
        self.mock_keyboard = self.keyboard_patch.start()
        self.mock_mouse = self.mouse_patch.start()
        
        # Create a handler instance with mocked dependencies
        with patch('input_control.mouse_keyboard_handler.get_platform_name', return_value='Windows'):
            self.handler = MouseKeyboardHandler()
            # Force availability of all libraries for testing
            self.handler.pyautogui_available = True
            self.handler.keyboard_available = True
            self.handler.mouse_available = True
            self.handler.pyautogui = self.mock_pyautogui
            self.handler.keyboard = self.mock_keyboard
            self.handler.mouse = self.mock_mouse
    
    def tearDown(self):
        """Clean up after each test."""
        self.pyautogui_patch.stop()
        self.keyboard_patch.stop()
        self.mouse_patch.stop()
    
    def test_move_mouse(self):
        """Test that move_mouse calls pyautogui.moveTo with the right arguments."""
        self.handler.move_mouse(100, 200, duration=0.5)
        self.mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0.5)
    
    def test_click(self):
        """Test that click calls pyautogui.click with the right arguments."""
        # Test with position
        self.handler.click(100, 200, button='left', clicks=2, interval=0.1)
        self.mock_pyautogui.click.assert_called_once_with(100, 200, clicks=2, interval=0.1, button='left')
        
        # Reset mock and test without position
        self.mock_pyautogui.click.reset_mock()
        self.handler.click(button='right', clicks=1)
        self.mock_pyautogui.click.assert_called_once_with(clicks=1, interval=0.0, button='right')
    
    def test_hold_key(self):
        """Test that hold_key uses the pyautogui.hold context manager."""
        # Setup a mock action function
        mock_action = MagicMock()
        
        # Call hold_key with the action function
        self.handler.hold_key('shift', mock_action, 'arg1', kwarg1='value1')
        
        # Check that pyautogui.hold was called with 'shift'
        self.mock_pyautogui.hold.assert_called_once_with('shift')
        
        # Check that the mock action function was called with the right arguments
        mock_action.assert_called_once_with('arg1', kwarg1='value1')
    
    def test_register_keyboard_hotkey(self):
        """Test that register_keyboard_hotkey calls keyboard.add_hotkey."""
        mock_callback = MagicMock()
        self.handler.register_keyboard_hotkey('ctrl+shift+a', mock_callback)
        self.mock_keyboard.add_hotkey.assert_called_once_with('ctrl+shift+a', mock_callback)
    
    def test_register_mouse_event(self):
        """Test that register_mouse_event calls the appropriate mouse library method."""
        mock_callback = MagicMock()
        
        # Test click event
        self.handler.register_mouse_event('click', mock_callback)
        self.mock_mouse.on_click.assert_called_once_with(mock_callback)
        
        # Test right click event
        self.mock_mouse.reset_mock()
        self.handler.register_mouse_event('right_click', mock_callback)
        self.mock_mouse.on_right_click.assert_called_once_with(mock_callback)
        
        # Test unknown event type
        self.mock_mouse.reset_mock()
        result = self.handler.register_mouse_event('unknown_event', mock_callback)
        self.assertFalse(result)
        self.mock_mouse.on_click.assert_not_called()


if __name__ == '__main__':
    unittest.main()
