import os
import sys
import tempfile
import shutil
from pathlib import Path

def setup_test_environment():
    """Set up the test environment."""
    # Add src directory to Python path
    src_path = str(Path(__file__).parent.parent / "src")
    sys.path.insert(0, src_path)
    # Additional setup steps can be added here

def teardown_test_environment():
    """Clean up the test environment."""
    # Cleanup steps can be added here
    pass 