#!/usr/bin/env python3
"""
Test suite for file operations module.
Tests the functionality of parsing and handling file operations commands.
"""
import os
import pytest
import shutil
from pathlib import Path
from uaibot.core.file_operations import parse_file_request, handle_file_operation, process_file_flag_request, FileOperations

class TestFileOperations:
    """Test suite for file operations."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        # Create test directory
        self.test_dir = Path("test_files/t250521")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        yield
        
        # Cleanup after tests
        if self.test_dir.exists():
            for file in self.test_dir.iterdir():
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    file.rmdir()
            self.test_dir.rmdir()
        if self.test_dir.parent.exists():
            try:
                self.test_dir.parent.rmdir()
            except Exception:
                pass
    
    @pytest.fixture
    def file_ops(self):
        return FileOperations()

    @pytest.fixture
    def test_dir(self, temp_dir):
        return temp_dir

    def test_parse_file_request_english(self):
        """Test parsing English file requests."""
        # Test create file request
        request = "create file test.txt with content 'Hello'"
        result = parse_file_request(request)
        assert result['operation'] == 'create'
        assert result['filename'] == 'test.txt'
        assert result['content'] == 'Hello'
        
        # Test create file with directory
        request = "create file test.txt in folder test_files/t250521 with content 'Hello'"
        result = parse_file_request(request)
        assert result['operation'] == 'create'
        assert result['filename'] == 'test.txt'
        assert result['content'] == 'Hello'
        assert result['directory'] == 'test_files/t250521'
    
    def test_parse_file_request_arabic(self):
        """Test parsing Arabic file requests."""
        # Test create file request
        request = "إنشاء ملف test.txt بالمحتوى 'مرحبا'"
        result = parse_file_request(request)
        assert result['operation'] == 'create'
        assert result['filename'] == 'test.txt'
        assert result['content'] == 'مرحبا'
        
        # Test create file with directory
        request = "إنشاء ملف test.txt في المجلد test_files/t250521 بالمحتوى 'مرحبا'"
        result = parse_file_request(request)
        assert result['operation'] == 'create'
        assert result['filename'] == 'test.txt'
        assert result['content'] == 'مرحبا'
        assert result['directory'] == 'test_files/t250521'
    
    def test_handle_file_operation_create(self):
        """Test file creation operation."""
        request = {
            'operation': 'create',
            'filename': 'test.txt',
            'content': 'Hello',
            'directory': str(self.test_dir)
        }
        result = handle_file_operation(request)
        assert "created file" in result.lower()
        
        # Verify file was created with correct content
        file_path = self.test_dir / 'test.txt'
        assert file_path.exists()
        assert file_path.read_text() == 'Hello'
    
    def test_handle_file_operation_read(self):
        """Test file reading operation."""
        # Create a test file first
        file_path = self.test_dir / 'test.txt'
        file_path.write_text('Hello')
        
        request = {
            'operation': 'read',
            'filename': 'test.txt',
            'directory': str(self.test_dir)
        }
        result = handle_file_operation(request)
        assert 'Hello' in result
    
    def test_handle_file_operation_write(self):
        """Test file writing operation."""
        # Create a test file first
        file_path = self.test_dir / 'test.txt'
        file_path.write_text('Old content')
        
        request = {
            'operation': 'write',
            'filename': 'test.txt',
            'content': 'New content',
            'directory': str(self.test_dir)
        }
        result = handle_file_operation(request)
        assert "wrote content" in result.lower()
        
        # Verify content was updated
        assert file_path.read_text() == 'New content'
    
    def test_handle_file_operation_append(self):
        """Test file append operation."""
        # Create a test file first
        file_path = self.test_dir / 'test.txt'
        file_path.write_text('Original content')
        
        request = {
            'operation': 'append',
            'filename': 'test.txt',
            'content': 'Appended content',
            'directory': str(self.test_dir)
        }
        result = handle_file_operation(request)
        assert "appended content" in result.lower()
        
        # Verify content was appended
        assert file_path.read_text() == 'Original contentAppended content'
    
    def test_handle_file_operation_delete(self):
        """Test file deletion operation."""
        # Create a test file first
        file_path = self.test_dir / 'test.txt'
        file_path.write_text('Hello')
        
        request = {
            'operation': 'delete',
            'filename': 'test.txt',
            'directory': str(self.test_dir)
        }
        result = handle_file_operation(request)
        assert "deleted file" in result.lower()
        
        # Verify file was deleted
        assert not file_path.exists()
    
    def test_handle_file_operation_search(self):
        """Test file search operation."""
        # Create some test files
        (self.test_dir / 'test1.txt').write_text('Hello')
        (self.test_dir / 'test2.txt').write_text('World')
        
        request = {
            'operation': 'search',
            'pattern': 'test',
            'directory': str(self.test_dir)
        }
        result = handle_file_operation(request)
        assert 'test1.txt' in result
        assert 'test2.txt' in result
    
    def test_handle_file_operation_list(self):
        """Test directory listing operation."""
        # Create some test files
        (self.test_dir / 'test1.txt').write_text('Hello')
        (self.test_dir / 'test2.txt').write_text('World')
        
        request = {
            'operation': 'list',
            'directory': str(self.test_dir)
        }
        result = handle_file_operation(request)
        assert 'test1.txt' in result
        assert 'test2.txt' in result
    
    def test_process_file_flag_request(self):
        """Test the main processor for file flag requests."""
        # Ensure file does not exist before test
        file_path = self.test_dir / 'test.txt'
        if file_path.exists():
            file_path.unlink()
        # Test create operation
        request = f"create file test.txt in folder {self.test_dir} with content 'Hello'"
        result = process_file_flag_request(request)
        assert "successfully created" in result.lower() or "created file" in result.lower()
        
        # Test read operation
        request = f"read file test.txt in folder {self.test_dir}"
        result = process_file_flag_request(request)
        assert 'hello' in result.lower()

    def test_create_file(self, file_ops, test_dir):
        """Test file creation."""
        file_path = os.path.join(test_dir, "test.txt")
        content = "Test content"
        
        result = file_ops.create_file(file_path, content)
        assert result is True
        assert os.path.exists(file_path)
        
        with open(file_path, 'r') as f:
            assert f.read() == content

    def test_read_file(self, file_ops, test_dir):
        """Test file reading."""
        file_path = os.path.join(test_dir, "test.txt")
        content = "Test content"
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        result = file_ops.read_file(file_path)
        assert result == content

    def test_delete_file(self, file_ops, test_dir):
        """Test file deletion."""
        file_path = os.path.join(test_dir, "test.txt")
        content = "Test content"
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        result = file_ops.delete_file(file_path)
        assert result is True
        assert not os.path.exists(file_path)

    def test_file_not_found(self, file_ops, test_dir):
        """Test handling of non-existent file."""
        file_path = os.path.join(test_dir, "nonexistent.txt")
        
        result = file_ops.read_file(file_path)
        assert result is None

    def test_create_directory(self, file_ops, test_dir):
        """Test directory creation."""
        dir_path = os.path.join(test_dir, "test_dir")
        
        result = file_ops.create_directory(dir_path)
        assert result is True
        assert os.path.isdir(dir_path)

    def test_list_directory(self, file_ops, test_dir):
        """Test directory listing."""
        # Create test files
        files = ["file1.txt", "file2.txt", "file3.txt"]
        for file in files:
            with open(os.path.join(test_dir, file), 'w') as f:
                f.write("Test content")
                
        result = file_ops.list_directory(test_dir)
        assert len(result) == len(files)
        for file in files:
            assert file in result

    def test_file_permissions(self, file_ops, test_dir):
        """Test file permissions."""
        file_path = os.path.join(test_dir, "test.txt")
        content = "Test content"
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        # Test read permission
        assert file_ops.check_read_permission(file_path) is True
        
        # Test write permission
        assert file_ops.check_write_permission(file_path) is True

    def test_file_operations_with_special_chars(self, file_ops, test_dir):
        """Test file operations with special characters in filenames."""
        file_name = "test file with spaces & special chars!.txt"
        file_path = os.path.join(test_dir, file_name)
        content = "Test content"
        
        # Test creation
        result = file_ops.create_file(file_path, content)
        assert result is True
        assert os.path.exists(file_path)
        
        # Test reading
        result = file_ops.read_file(file_path)
        assert result == content
        
        # Test deletion
        result = file_ops.delete_file(file_path)
        assert result is True
        assert not os.path.exists(file_path)

    @pytest.mark.parametrize("content,expected", [
        ("Simple content", "Simple content"),
        ("", ""),
        ("Content with\nnewlines", "Content with\nnewlines"),
        ("Content with\t tabs", "Content with\t tabs"),
    ])
    def test_file_content_variations(self, file_ops, test_dir, content, expected):
        """Test file operations with various content types."""
        file_path = os.path.join(test_dir, "test.txt")
        
        # Test creation
        result = file_ops.create_file(file_path, content)
        assert result is True
        
        # Test reading
        result = file_ops.read_file(file_path)
        assert result == expected

    def test_concurrent_file_operations(self, file_ops, test_dir):
        """Test concurrent file operations."""
        import threading
        
        def write_file(file_num):
            file_path = os.path.join(test_dir, f"test{file_num}.txt")
            content = f"Content for file {file_num}"
            file_ops.create_file(file_path, content)
            
        # Create multiple files concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_file, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Verify all files were created
        for i in range(5):
            file_path = os.path.join(test_dir, f"test{i}.txt")
            assert os.path.exists(file_path)
            content = file_ops.read_file(file_path)
            assert content == f"Content for file {i}" 