#!/usr/bin/env python3
"""
Test the AI-driven command extraction functionality.
Tests the ability to extract commands from structured AI responses without relying on patterns.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.command_processor.ai_command_extractor import AICommandExtractor

class TestAICommandExtractor(unittest.TestCase):
    """Test the AI-driven command extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = AICommandExtractor()
    
    def test_extract_command_from_json_format1(self):
        """Test extracting a command from FORMAT 1 JSON."""
        ai_response = """```json
{
  "command": "ls -la",
  "explanation": "Lists all files in current directory with details",
  "alternatives": ["find . -maxdepth 1", "dir"],
  "requires_implementation": false
}
```"""
        success, command, metadata = self.extractor.extract_command(ai_response)
        
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "json")
        self.assertEqual(metadata["explanation"], "Lists all files in current directory with details")
        self.assertEqual(metadata["suggested_alternatives"], ["find . -maxdepth 1", "dir"])
    
    def test_extract_command_from_json_format2(self):
        """Test extracting a command from FORMAT 2 JSON (file operation)."""
        ai_response = """```json
{
  "file_operation": "create",
  "operation_params": {
    "filename": "test.txt",
    "content": "Hello world"
  },
  "explanation": "Creates a new file with content"
}
```"""
        # Mock the _generate_command_from_file_operation method to return a command
        self.extractor._generate_command_from_file_operation = MagicMock(
            return_value='echo "Hello world" > test.txt'
        )
        
        success, command, metadata = self.extractor.extract_command(ai_response)
        
        self.assertTrue(success)
        self.assertEqual(command, 'echo "Hello world" > test.txt')
        self.assertEqual(metadata["file_operation"], "create")
        self.assertEqual(metadata["operation_params"]["filename"], "test.txt")
        self.assertEqual(metadata["operation_params"]["content"], "Hello world")
    
    def test_extract_error_from_json_format3(self):
        """Test extracting an error from FORMAT 3 JSON."""
        ai_response = """```json
{
  "error": true,
  "error_message": "Cannot delete system files",
  "requires_implementation": true,
  "suggested_approach": "Try using a file manager with appropriate permissions"
}
```"""
        success, command, metadata = self.extractor.extract_command(ai_response)
        
        self.assertFalse(success)
        self.assertIsNone(command)
        self.assertTrue(metadata["is_error"])
        self.assertEqual(metadata["error_message"], "Cannot delete system files")
        self.assertEqual(metadata["suggested_approach"], "Try using a file manager with appropriate permissions")
    
    def test_extract_info_from_json_format4(self):
        """Test extracting information from FORMAT 4 JSON."""
        ai_response = """```json
{
  "info_type": "system_info",
  "response": "Linux is a free and open-source operating system kernel.",
  "related_command": "uname -a",
  "explanation": "Shows detailed system information"
}
```"""
        success, command, metadata = self.extractor.extract_command(ai_response)
        
        self.assertTrue(success)
        self.assertEqual(command, "uname -a")
        self.assertEqual(metadata["info_type"], "system_info")
        self.assertEqual(metadata["info_response"], "Linux is a free and open-source operating system kernel.")
    
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
    
    def test_extract_command_from_inline_code(self):
        """Test extracting a command from inline code."""
        ai_response = "To list files, you can use the `ls -la` command."
        
        success, command, metadata = self.extractor.extract_command(ai_response)
        
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "inline_code")
    
    def test_format_ai_prompt(self):
        """Test AI prompt formatting."""
        platform_info = {
            "system": "Linux",
            "linux_distro": "Ubuntu",
            "version": "22.04"
        }
        
        prompt = self.extractor.format_ai_prompt("list files in my directory", platform_info)
        
        # Check that the prompt contains key elements
        self.assertIn("list files in my directory", prompt)
        self.assertIn("OS: Linux", prompt)
        self.assertIn("Ubuntu", prompt)
        self.assertIn("CORE PRINCIPLES:", prompt)
        self.assertIn("FORMAT 1", prompt)
        self.assertIn("FORMAT 2", prompt)
        self.assertIn("FORMAT 3", prompt)
        self.assertIn("FORMAT 4", prompt)

if __name__ == "__main__":
    unittest.main()
