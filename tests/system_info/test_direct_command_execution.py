#!/usr/bin/env python3
"""
Test script for direct command execution in UaiBot.
This tests the integration between CommandProcessor and the run_command utility.
"""
import os
import sys
import platform
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the UaiBot modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import UaiBot modules
from core.utils import run_command
from core.shell_handler import ShellHandler

# Dynamically load the CommandProcessor from the main directory
from importlib.machinery import SourceFileLoader
cp_module = SourceFileLoader("command_processor_main", 
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                    "command_processor.py")).load_module()
CommandProcessor = cp_module.CommandProcessor

class TestDirectCommandExecution(unittest.TestCase):
    """Test direct command execution functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.ai_handler = MagicMock()
        self.shell_handler = ShellHandler(safe_mode=False, enable_dangerous_command_check=False)
        self.command_processor = CommandProcessor(self.ai_handler, self.shell_handler)

    def test_direct_command_recognition(self):
        """Test that direct commands are properly recognized."""
        # Test straightforward command
        self.assertTrue(self.command_processor._looks_like_direct_command("ls -la"))
        
        # Test with action verb
        self.assertTrue(self.command_processor._looks_like_direct_command("run ls -la"))
        
        # Test natural language formulation that should be recognized
        self.assertTrue(self.command_processor._looks_like_direct_command("show me the current directory"))
        
        # This should not be recognized as a direct command
        self.assertFalse(self.command_processor._looks_like_direct_command("what is the weather like today"))

    def test_command_extraction(self):
        """Test that commands are properly extracted from natural language inputs."""
        # Test direct command
        self.assertEqual(self.command_processor._extract_command("ls -la"), "ls -la")
        
        # Test with action verb
        self.assertEqual(self.command_processor._extract_command("run ls -la"), "ls -la")
        
        # Test special cases for macOS
        if platform.system() == 'Darwin':
            self.assertEqual(self.command_processor._extract_command("open Notes"), 'open -a "Notes"')
            self.assertEqual(self.command_processor._extract_command("show my Notes folders"), 
                           """osascript -e 'tell application "Notes" to get name of every folder'""")

    @patch('core.utils.run_command')
    def test_command_execution(self, mock_run_command):
        """Test that commands are properly executed."""
        # Mock successful command execution
        mock_run_command.return_value = {
            'returncode': 0,
            'success': True,
            'stdout': 'Command output',
            'stderr': ''
        }
        
        # Test direct command execution
        result = self.command_processor._try_direct_execution("ls -la")
        self.assertIn("✅ Command executed", result)
        self.assertIn("Command output", result)
        mock_run_command.assert_called_with("ls -la", shell=True, capture_output=True, text=True)
        
        # Test command extraction and execution
        mock_run_command.reset_mock()
        result = self.command_processor._try_direct_execution("run ls -la")
        self.assertIn("✅ Command executed", result)
        mock_run_command.assert_called_with("ls -la", shell=True, capture_output=True, text=True)
        
    def test_notes_commands(self):
        """Test that Notes-specific commands work correctly."""
        # We can't actually execute Notes commands in a test, but we can verify the extraction
        if platform.system() == 'Darwin':
            cmd = self.command_processor._extract_command("show my Notes folders")
            self.assertIn("osascript", cmd)
            self.assertIn("Notes", cmd)
            self.assertIn("every folder", cmd)
            
            cmd = self.command_processor._extract_command("open Notes in Robotic World")
            self.assertIn("open -a Notes", cmd)
            self.assertIn("Robotic", cmd)

if __name__ == '__main__':
    unittest.main()
