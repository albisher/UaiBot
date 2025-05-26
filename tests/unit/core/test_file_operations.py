import pytest
import os
import tempfile
from labeeb.core.file_operations import FileOperations

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def file_ops(temp_dir):
    """Provide a FileOperations instance with a temporary directory."""
    ops = FileOperations()
    ops.work_dir = temp_dir
    return ops

def test_file_operations_initialization(file_ops):
    """Test that FileOperations initializes correctly."""
    assert file_ops is not None
    assert hasattr(file_ops, 'work_dir')

def test_create_file(file_ops):
    """Test file creation."""
    test_file = "test.txt"
    content = "Hello, World!"
    
    file_ops.create_file(test_file, content)
    assert os.path.exists(os.path.join(file_ops.work_dir, test_file))
    
    with open(os.path.join(file_ops.work_dir, test_file), 'r') as f:
        assert f.read() == content

def test_delete_file(file_ops):
    """Test file deletion."""
    test_file = "test.txt"
    content = "Hello, World!"
    
    file_ops.create_file(test_file, content)
    assert os.path.exists(os.path.join(file_ops.work_dir, test_file))
    
    file_ops.delete_file(test_file)
    assert not os.path.exists(os.path.join(file_ops.work_dir, test_file)) 