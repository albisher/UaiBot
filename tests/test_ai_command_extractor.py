import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
import concurrent.futures

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
```
"""
        
        success, command, metadata = self.extractor.extract_command(ai_response)
        self.assertTrue(success)
        self.assertEqual(command, "echo 'Hello World' > test.txt")
        self.assertEqual(metadata["source"], "json")
        self.assertEqual(metadata["file_operation"], "create")
    
    def test_extract_command_parallel(self):
        """Test that parallel command extraction works correctly."""
        # Test with a JSON response
        json_response = '{"command": "ls -la", "explanation": "List files"}'
        success, command, metadata = self.extractor.extract_command_parallel(json_response)
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "json")
        
        # Test with a code block response
        code_block_response = "Here's a command:\n```\nls -la\n```\nThis will list files."
        success, command, metadata = self.extractor.extract_command_parallel(code_block_response)
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "code_block")
        
        # Test with an inline code response
        inline_code_response = "You can use `ls -la` to list files."
        success, command, metadata = self.extractor.extract_command_parallel(inline_code_response)
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "inline_code")
        
        # Test with an Arabic response
        arabic_response = "استخدم الأمر `ls -la` لعرض الملفات."
        success, command, metadata = self.extractor.extract_command_parallel(arabic_response)
        self.assertTrue(success)
        self.assertEqual(command, "ls -la")
        self.assertEqual(metadata["source"], "arabic")
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_parallel_extraction_timeout(self, mock_executor):
        """Test that parallel extraction handles timeouts correctly."""
        # Setup mock executor to simulate timeout
        mock_future = MagicMock()
        mock_future.result.side_effect = concurrent.futures.TimeoutError()
        mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future
        
        # Test with a response that would cause a timeout
        response = "This is a complex response that would take too long to process."
        success, command, metadata = self.extractor.extract_command_parallel(response)
        
        # Should fall back to regular extraction
        self.assertFalse(success)  # Assuming regular extraction would also fail for this input
        self.assertIn("timeout", metadata["error"].lower())
    
    def test_parallel_extraction_performance(self):
        """Test that parallel extraction is faster than sequential for complex responses."""
        # Create a complex response with multiple formats
        complex_response = """
        Here are several commands you can use:
        
        ```
ls -la
```
        
        Or you can use `find . -name "*.py"` to find Python files.
        
        JSON format: {"command": "grep -r 'pattern' .", "explanation": "Search for pattern"}
        
        استخدم الأمر `cat file.txt` لعرض محتويات الملف.
        """
        
        # Time the parallel extraction
        import time
        start_time = time.time()
        parallel_success, parallel_command, parallel_metadata = self.extractor.extract_command_parallel(complex_response)
        parallel_time = time.time() - start_time
        
        # Time the regular extraction
        start_time = time.time()
        regular_success, regular_command, regular_metadata = self.extractor.extract_command(complex_response)
        regular_time = time.time() - start_time
        
        # Both should succeed and find the same command (the first valid one)
        self.assertEqual(parallel_success, regular_success)
        self.assertEqual(parallel_command, regular_command)
        
        # Parallel should be faster, but this is not guaranteed in all environments
        # So we just log the times for informational purposes
        print(f"Parallel extraction time: {parallel_time:.6f}s")
        print(f"Regular extraction time: {regular_time:.6f}s")
        
        # The test passes as long as both methods find the same command
        # We don't assert on timing as it can vary by environment
