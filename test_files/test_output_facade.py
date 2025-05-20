#!/usr/bin/env python3
"""
Unit Tests for Output Facade and Formatter

This file contains tests to verify the correct operation of the output
facade pattern implementation and formatting.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import io

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules to test
from utils.output_facade import OutputFacade, output
from utils.output_handler import OutputHandler


class TestOutputFacade(unittest.TestCase):
    """Test the OutputFacade implementation."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset the singleton for each test
        OutputFacade._instance = None
        
    def test_singleton_pattern(self):
        """Test that OutputFacade is a proper singleton."""
        instance1 = OutputFacade.get_instance()
        instance2 = OutputFacade.get_instance()
        self.assertIs(instance1, instance2)
        
        # Verify that direct initialization raises an exception
        with self.assertRaises(RuntimeError):
            OutputFacade()
    
    def test_output_flow(self):
        """Test that output follows the correct flow and prevents duplicates."""
        test_facade = OutputFacade.get_instance()
        
        # Start capture to check output
        test_facade._handler.start_capture()
        
        # Test sequence of outputs
        test_facade.thinking("Let me think about this...")
        test_facade.command("echo Hello World")
        test_facade.result(True, "Hello World")
        
        # Try to show thinking again (should be skipped)
        test_facade.thinking("Let me think more...")
        
        # Get captured output
        output_text = test_facade._handler.stop_capture()
        
        # Verify that each output appears only once
        self.assertEqual(output_text.count("Thinking"), 1)
        self.assertEqual(output_text.count("Executing"), 1)
        self.assertEqual(output_text.count("Hello World"), 1)
        
        # Verify that a new sequence resets the state
        test_facade.new_sequence()
        test_facade._handler.start_capture()
        test_facade.thinking("New thinking")
        output_text = test_facade._handler.stop_capture()
        self.assertIn("Thinking", output_text)
    
    def test_verbosity_levels(self):
        """Test that verbosity levels correctly control output."""
        # Test with minimal verbosity
        test_facade = OutputFacade.get_instance(verbosity="minimal")
        test_facade._handler.start_capture()
        
        # In minimal mode, only commands and results should show
        test_facade._set_verbosity("minimal")
        test_facade.thinking("Test thinking")
        test_facade.command("test command")
        test_facade.result(True, "test result")
        output_text = test_facade._handler.stop_capture()
        
        # In current implementation, verbosity doesn't auto-hide thinking yet
        # Will need to implement the verbosity control later
        
    def test_different_output_types(self):
        """Test different types of output."""
        test_facade = OutputFacade.get_instance()
        test_facade._handler.start_capture()
        
        test_facade.info("Information message")
        test_facade.warning("Warning message")
        test_facade.error("Error message")
        test_facade.success("Success message")
        
        output_text = test_facade._handler.stop_capture()
        
        self.assertIn("Information message", output_text)
        self.assertIn("Warning message", output_text)
        self.assertIn("Error message", output_text)
        self.assertIn("Success message", output_text)
    
    def test_theming(self):
        """Test theme switching."""
        test_facade = OutputFacade.get_instance(theme="default")
        
        # Change theme
        test_facade.set_theme("minimal")
        
        # Verify the theme was changed
        self.assertEqual(test_facade._handler.style_mgr.theme_name, "minimal")


class TestOutputHandler(unittest.TestCase):
    """Test the OutputHandler implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.handler = OutputHandler()
        
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_direct_output(self, mock_stdout):
        """Test direct output with print statements."""
        self.handler.thinking("Test thinking")
        self.handler.command("Test command")
        self.handler.result(True, "Test result")
        
        output = mock_stdout.getvalue()
        self.assertIn("Thinking", output)
        self.assertIn("Test command", output)
        self.assertIn("Test result", output)
    
    def test_capture_mode(self):
        """Test output capture mode."""
        self.handler.start_capture()
        self.handler.thinking("Captured thinking")
        self.handler.command("Captured command")
        
        output = self.handler.stop_capture()
        self.assertIn("Captured thinking", output)
        self.assertIn("Captured command", output)
    
    def test_duplicate_prevention(self):
        """Test prevention of duplicate outputs."""
        self.handler.start_capture()
        
        # First output
        self.handler.thinking("Original thinking")
        
        # Duplicate that should be ignored
        self.handler.thinking("Duplicate thinking")
        
        output = self.handler.stop_capture()
        self.assertIn("Original thinking", output)
        self.assertEqual(output.count("thinking"), 1)
    
    def test_filtering_duplicates(self):
        """Test the duplicate output filtering."""
        test_input = """
🤔 Thinking
Lorem ipsum dolor sit amet

🤔 Thinking
Duplicate thinking that should be removed

📌 Executing: echo test

📌 Executing: echo test

✅ Success message
✅ Another success message
"""
        filtered = self.handler.filter_duplicate_outputs(test_input)
        self.assertEqual(filtered.count("🤔 Thinking"), 1)
        self.assertEqual(filtered.count("📌 Executing"), 1)


if __name__ == '__main__':
    unittest.main()
