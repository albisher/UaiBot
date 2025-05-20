#!/usr/bin/env python3
"""
Test suite for UaiBot file operations.
Tests the functionality of file operation detection and execution.
"""
import os
import sys
import shutil
import unittest
import tempfile
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.abspath('..'))

# Import file operations functions
try:
    from main import handle_file_operations, detect_file_operation
except ImportError:
    # Fall back to importing from a different location
    sys.path.insert(0, os.path.abspath('.'))
    try:
        from main import handle_file_operations, detect_file_operation
    except ImportError:
        print("Error: Could not import file operations functions")
        sys.exit(1)

class TestFileOperations(unittest.TestCase):
    """Test cases for file operations functionality."""
    
    def setUp(self):
        """Set up temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create some test files
        with open('test1.txt', 'w') as f:
            f.write('This is test file 1')
        with open('test2.txt', 'w') as f:
            f.write('This is test file 2')
        
    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_detect_file_operation(self):
        """Test file operation detection from queries."""
        self.assertEqual(detect_file_operation('create file test.txt'), 'create')
        self.assertEqual(detect_file_operation('read the file test.txt'), 'read')
        self.assertEqual(detect_file_operation('write to file test.txt'), 'write')
        self.assertEqual(detect_file_operation('append to file test.txt'), 'append')
        self.assertEqual(detect_file_operation('delete file test.txt'), 'delete')
        self.assertEqual(detect_file_operation('search for files containing test'), 'search')
        self.assertEqual(detect_file_operation('list all files'), 'list')
    
    def test_create_operation(self):
        """Test file creation operation."""
        result = handle_file_operations('create file new.txt with content "Hello World"', 'create')
        self.assertIn('Created file', result)
        self.assertTrue(os.path.exists('new.txt'))
        with open('new.txt', 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Hello World')
    
    def test_read_operation(self):
        """Test file reading operation."""
        result = handle_file_operations('read file test1.txt', 'read')
        self.assertIn('This is test file 1', result)
    
    def test_write_operation(self):
        """Test file writing operation."""
        result = handle_file_operations('write to file test1.txt content "New content"', 'write')
        self.assertIn('Wrote to file', result)
        with open('test1.txt', 'r') as f:
            content = f.read()
        self.assertEqual(content, 'New content')
    
    def test_append_operation(self):
        """Test file append operation."""
        result = handle_file_operations('append to file test1.txt content " appended text"', 'append')
        self.assertIn('Appended to file', result)
        with open('test1.txt', 'r') as f:
            content = f.read()
        self.assertEqual(content, 'This is test file 1 appended text')
    
    def test_delete_operation(self):
        """Test file deletion operation."""
        result = handle_file_operations('delete file test2.txt', 'delete')
        self.assertIn('Deleted file', result)
        self.assertFalse(os.path.exists('test2.txt'))
    
    def test_list_operation(self):
        """Test file listing operation."""
        result = handle_file_operations('list files', 'list')
        self.assertIn('test1.txt', result)
        self.assertIn('test2.txt', result)
    
    def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Test file not found
        result = handle_file_operations('read file nonexistent.txt', 'read')
        self.assertIn('Error: File not found', result)
        
        # Test invalid operation
        result = handle_file_operations('invalid operation', 'invalid')
        self.assertIn('Error: Unsupported file operation', result)


if __name__ == '__main__':
    unittest.main()
