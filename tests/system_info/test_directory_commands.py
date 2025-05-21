"""
Test cases for directory-related commands to ensure the functionality works correctly.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uaibot.core.shell_handler import ShellHandler
from command_processor.command_processor import CommandProcessor

class TestDirectoryCommands(unittest.TestCase):
    """Test directory-related command functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.ai_handler = MagicMock()
        self.shell_handler = ShellHandler()
        
        # Mock execute_command to return predetermined values
        self.shell_handler.execute_command = MagicMock()
        self.shell_handler.execute_command.return_value = "/home/user"
        
        # Create the command processor with our mocked handlers
        self.cmd_processor = CommandProcessor(self.ai_handler, self.shell_handler)
        
    def test_current_directory_query(self):
        """Test handling of 'where am I' type queries."""
        queries = [
            "where am I",
            "what is the current directory",
            "pwd",
            "current folder",
            "what is active folder now"
        ]
        
        for query in queries:
            result = self.cmd_processor.process_command(query)
            self.assertIn("Current directory", result)
    
    def test_directory_listing_query(self):
        """Test handling of directory listing queries."""
        # Mock directory listing command result
        self.shell_handler.execute_command.return_value = "file1.txt\nfile2.py\nfolder1"
        
        queries = [
            "show files in current directory",
            "list current folder",
            "what files are here",
            "show folder contents"
        ]
        
        for query in queries:
            result = self.cmd_processor.process_command(query)
            self.assertTrue(any(term in result for term in ["Files", "files", "folder", "directory"]))

if __name__ == "__main__":
    unittest.main()
