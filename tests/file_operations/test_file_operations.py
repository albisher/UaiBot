#!/usr/bin/env python3
"""
Unit tests for file operations functionality in UaiBot.
Tests both the core file operations module and the command processor's file handling.
"""
import os
import sys
import unittest
import tempfile
import shutil
from src.pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.file_operations import parse_file_request, handle_file_operation
from app.command_processor.file_operations_handler import FileOperationsHandler

class TestFileRequestParsing(unittest.TestCase):
    """Test file request parsing functionality."""
    
    def test_create_file_parsing(self):
        """Test parsing of file creation requests."""
        request = "create a new file called test.txt"
        parsed = parse_file_request(request)
        
        self.assertEqual(parsed['operation'], 'create')
        self.assertTrue(any('test.txt' in path for path in parsed['potential_paths']))
    
    def test_read_file_parsing(self):
        """Test parsing of file reading requests."""
        request = "read the file config.json"
        parsed = parse_file_request(request)
        
        self.assertEqual(parsed['operation'], 'read')
        self.assertTrue(any('config.json' in path for path in parsed['potential_paths']))
    
    def test_update_file_parsing(self):
        """Test parsing of file update requests."""
        request = "update file log.txt with new content"
        parsed = parse_file_request(request)
        
        self.assertEqual(parsed['operation'], 'update')
        self.assertTrue(any('log.txt' in path for path in parsed['potential_paths']))
    
    def test_delete_file_parsing(self):
        """Test parsing of file deletion requests."""
        request = "delete the temporary file temp.txt"
        parsed = parse_file_request(request)
        
        self.assertEqual(parsed['operation'], 'delete')
        self.assertTrue(any('temp.txt' in path for path in parsed['potential_paths']))
    
    def test_arabic_request_parsing(self):
        """Test parsing of Arabic file operation requests."""
        # This is a basic test - comprehensive Arabic testing would require more test cases
        request = "انشئ ملف جديد باسم test_ar.txt"
        parsed = parse_file_request(request)
        
        self.assertIsNotNone(parsed['operation'])  # Should detect some operation

class TestFileOperationsHandler(unittest.TestCase):
    """Test the FileOperationsHandler class."""
    
    def setUp(self):
        """Set up for tests - create a temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.handler = FileOperationsHandler(quiet_mode=True)
    
    def tearDown(self):
        """Clean up after tests - remove temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_create_file(self):
        """Test file creation."""
        test_file = os.path.join(self.test_dir, "test.txt")
        result = self.handler.handle_operation("create", {"filename": test_file})
        
        self.assertTrue("Created file" in result)
        self.assertTrue(os.path.exists(test_file))
    
    def test_create_file_with_content(self):
        """Test file creation with content."""
        test_file = os.path.join(self.test_dir, "test_content.txt")
        content = "This is test content"
        result = self.handler.handle_operation("create", {
            "filename": test_file,
            "content": content
        })
        
        self.assertTrue("Created file" in result)
        
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), content)
    
    def test_read_file(self):
        """Test file reading."""
        # Create a file first
        test_file = os.path.join(self.test_dir, "read_test.txt")
        content = "This is content to read"
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Now read it
        result = self.handler.handle_operation("read", {"filename": test_file})
        
        self.assertTrue("Content of" in result)
        self.assertTrue(content in result)
    
    def test_delete_file(self):
        """Test file deletion."""
        # Create a file first
        test_file = os.path.join(self.test_dir, "delete_test.txt")
        with open(test_file, 'w') as f:
            f.write("This file will be deleted")
        
        # Now delete it
        result = self.handler.handle_operation("delete", {"filename": test_file})
        
        self.assertTrue("Deleted file" in result)
        self.assertFalse(os.path.exists(test_file))
    
    def test_list_directory(self):
        """Test directory listing."""
        # Create some files
        for i in range(3):
            with open(os.path.join(self.test_dir, f"file{i}.txt"), 'w') as f:
                f.write(f"Content of file {i}")
        
        # List the directory
        result = self.handler.handle_operation("list", {"directory": self.test_dir})
        
        self.assertTrue("Contents of" in result)
        self.assertTrue("file0.txt" in result)
        self.assertTrue("file1.txt" in result)
        self.assertTrue("file2.txt" in result)

if __name__ == "__main__":
    unittest.main()
