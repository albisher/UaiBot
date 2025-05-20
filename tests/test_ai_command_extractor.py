import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from command_processor.ai_command_extractor import AICommandExtractor

class TestAICommandExtractor(unittest.TestCase):
    """Test the AI Command Extractor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = AICommandExtractor()
    
    def test_extract_command_from_code_block(self):
        """Test extracting a command from a code block."""
        ai_response = """I'll help you list files in your current directory.

```bash
ls -la
```

This command will show all files including hidden files with details."""

        success, command, metadata = self.extractor.extract_command(ai_response)
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "code_block")
        self.assertTrue(metadata["confidence"] > 0.8)
    
    def test_extract_command_from_inline_code(self):
        """Test extracting a command from inline code."""
        ai_response = "To list files, you can use the `ls -la` command."
        
        success, command, metadata = self.extractor.extract_command(ai_response)
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "inline_code")
    
    def test_extract_command_from_json(self):
        """Test extracting a command from JSON format."""
        ai_response = """Here's how to list files:

```json
{
  "command": "ls -la",
  "explanation": "List all files with detailed information"
}
```

This will show all files including hidden ones."""
        
        success, command, metadata = self.extractor.extract_command(ai_response)
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "json")
        self.assertEqual(metadata["explanation"], "List all files with detailed information")
    
    def test_extract_file_operation(self):
        """Test extracting a file operation from JSON."""
        ai_response = """```json
{
  "file_operation": "create",
  "operation_params": {
    "filename": "test.txt",
    "content": "Hello World"
  },
  "explanation": "Creates a new file with content"
}
