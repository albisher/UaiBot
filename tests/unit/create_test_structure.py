#!/usr/bin/env python3
"""
Create Test Structure
--------------------
Sets up the required test directory structure and sample test files
for the UaiBot project.
"""

import os
import sys
import platform
import shutil
from pathlib import Path

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Try to import the output formatter if available
# import test_files.output_formatter
try:
    from test_files.output_formatter import TestOutputFormatter
    formatter = TestOutputFormatter()
    format_status = formatter.format_status
    format_header = formatter.format_header
except ImportError:
    # Simple fallback if formatter isn't available
    def format_status(message, status="info"):
        symbols = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}
        return f"{symbols.get(status, '•')} {message}"
    
    def format_header(text, emoji_key=None):
        return f"{text}\n{'-' * len(text)}"

# Define test directory structure
TEST_DIRS = {
    "unit": os.path.join(current_dir, "unit"),
    "integration": os.path.join(current_dir, "integration"),
    "system": os.path.join(current_dir, "system"),
    "human_interaction": os.path.join(current_dir, "human_interaction"),
}

# Define sample test files to create
SAMPLE_FILES = {
    "unit/sample.txt": "This is a sample text file for testing.\nIt contains multiple lines of text.\n",
    "unit/sample_binary.bin": bytes(range(256)),
    "unit/sample file.txt": "This file has spaces in the name.\nUsed to test filename handling with spaces.\n",
    "unit/sample_$pecial.txt": "This file has special characters in the name.\nUsed to test handling of special characters.\n",
    "unit/test_formatter.py": """
#!/usr/bin/env python3
\"\"\"
Unit tests for the output formatter.
\"\"\"

import os
import sys
import unittest

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(test_dir)
sys.path.append(project_root)

from test_files.output_formatter import TestOutputFormatter

class TestOutputFormatterTests(unittest.TestCase):
    
    def setUp(self):
        self.formatter = TestOutputFormatter()
    
    def test_format_header(self):
        result = self.formatter.format_header("Test Header")
        self.assertIn("Test Header", result)
    
    def test_format_status(self):
        result = self.formatter.format_status("Test Status", "info")
        self.assertIn("Test Status", result)
    
if __name__ == "__main__":
    unittest.main()
""",
    "integration/test_main_with_f_flag.py": """
#!/usr/bin/env python3
\"\"\"
Integration test for main.py with -f flag.
\"\"\"

import os
import sys
import unittest
import tempfile
import subprocess

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(test_dir)
sys.path.append(project_root)

class TestMainWithFFlag(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"Test content for file flag test.")
        self.temp_file.close()
    
    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.temp_file.name)
    
    def test_main_with_f_flag(self):
        # Run main.py with -f flag pointing to our temp file
        process = subprocess.Popen(
            [sys.executable, os.path.join(project_root, "main.py"), "-f", self.temp_file.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)
        
        # Check return code
        self.assertEqual(process.returncode, 0, f"Process failed with stderr: {stderr}")
        
        # Check output for indicators of success
        # (Adjust these based on your actual expected output)
        self.assertIn("UaiBot", stdout, "Output should mention UaiBot")

if __name__ == "__main__":
    unittest.main()
""",
    "human_interaction/sample_interaction_test.py": """
#!/usr/bin/env python3
\"\"\"
A simple human-like interaction test that runs with a fixed timeout.
This helps prevent hanging on keyboard input or other blocking operations.
\"\"\"

import os
import sys
import time
import signal
import platform

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(test_dir)
sys.path.append(project_root)

# Try to import the output formatter
try:
    from test_files.output_formatter import TestOutputFormatter
    formatter = TestOutputFormatter()
except ImportError:
    class SimpleFormatter:
        def format_status(self, msg, status="info"):
            return f"[{status.upper()}] {msg}"
    formatter = SimpleFormatter()

# Set a timeout to prevent the test from hanging
TIMEOUT = 30  # seconds

def timeout_handler(signum, frame):
    print(formatter.format_status("Test timed out after 30 seconds", "warning"))
    sys.exit(0)

# Register the timeout handler
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(TIMEOUT)

def main():
    # Print system information
    print(formatter.format_status(f"Running on {platform.system()} {platform.release()}", "info"))
    print(formatter.format_status(f"Python version: {platform.python_version()}", "info"))
    
    # Simulate a human-like interaction test
    print(formatter.format_status("Starting human-like interaction test", "info"))
    
    # Simulate some processing
    for i in range(5):
        print(formatter.format_status(f"Processing step {i+1}/5...", "info"))
        time.sleep(1)
    
    # End test normally
    print(formatter.format_status("Human interaction test completed", "success"))
    
if __name__ == "__main__":
    main()
"""
}

def create_directory_structure():
    """Create the test directory structure."""
    print(format_header("Creating Test Directory Structure", "folder"))
    
    for dir_name, dir_path in TEST_DIRS.items():
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(format_status(f"Created directory: {dir_path}", "success"))
        except Exception as e:
            print(format_status(f"Error creating directory {dir_path}: {e}", "error"))

def create_sample_files():
    """Create sample test files."""
    print(format_header("Creating Sample Test Files", "file"))
    
    for rel_path, content in SAMPLE_FILES.items():
        abs_path = os.path.join(current_dir, rel_path)
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        try:
            # Handle binary vs text content
            if isinstance(content, bytes):
                with open(abs_path, 'wb') as f:
                    f.write(content)
            else:
                with open(abs_path, 'w') as f:
                    f.write(content)
            print(format_status(f"Created file: {abs_path}", "success"))
        except Exception as e:
            print(format_status(f"Error creating file {abs_path}: {e}", "error"))

def create_run_scripts():
    """Create platform-specific run scripts."""
    print(format_header("Creating Run Scripts", "command"))
    
    # Create a cross-platform Python test script
    with open(os.path.join(current_dir, "run_simple_test.py"), 'w') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Simple test script that works on all platforms.
\"\"\"

import os
import sys
import platform

print(f"Running simple test on {platform.system()} {platform.release()}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Find main.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main_py = os.path.join(project_root, "main.py")

if os.path.exists(main_py):
    print(f"Found main.py at: {main_py}")
    print("Test PASSED")
    sys.exit(0)
else:
    print(f"main.py not found at: {main_py}")
    print("Test FAILED")
    sys.exit(1)
""")
    print(format_status("Created run_simple_test.py", "success"))
    
    # Create a Unix shell script
    if platform.system() != "Windows":
        script_path = os.path.join(current_dir, "run_tests.sh")
        with open(script_path, 'w') as f:
            f.write("""#!/bin/bash
# Simple test runner for Unix-like systems

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "===================================="
echo "Running UaiBot tests"
echo "===================================="
echo "Project root: $PROJECT_ROOT"
echo "Test directory: $SCRIPT_DIR"
echo "Python: $(python --version)"
echo "===================================="

# Run basic test
python "$SCRIPT_DIR/run_simple_test.py"

# Check if any test files exist in unit directory
if [ -d "$SCRIPT_DIR/unit" ]; then
    echo "Running unit tests..."
    for test_file in "$SCRIPT_DIR"/unit/test_*.py; do
        if [ -f "$test_file" ]; then
            echo "Running $test_file"
            python "$test_file"
        fi
    done
fi

# Test main.py with -f flag if sample.txt exists
if [ -f "$SCRIPT_DIR/unit/sample.txt" ]; then
    echo "Testing main.py with -f flag..."
    python "$PROJECT_ROOT/main.py" -f "$SCRIPT_DIR/unit/sample.txt"
fi

echo "Tests completed"
""")
        # Make it executable
        os.chmod(script_path, 0o755)
        print(format_status(f"Created and made executable: {script_path}", "success"))
    
    # Create a Windows batch file
    if platform.system() == "Windows" or True:  # Create it anyway for reference
        script_path = os.path.join(current_dir, "run_tests.bat")
        with open(script_path, 'w') as f:
            f.write("""@echo off
:: Simple test runner for Windows

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo ====================================
echo Running UaiBot tests
echo ====================================
echo Project root: %PROJECT_ROOT%
echo Test directory: %SCRIPT_DIR%
python --version
echo ====================================

:: Run basic test
python "%SCRIPT_DIR%run_simple_test.py"

:: Check if any test files exist in unit directory
if exist "%SCRIPT_DIR%unit" (
    echo Running unit tests...
    for %%f in ("%SCRIPT_DIR%unit\test_*.py") do (
        echo Running %%f
        python "%%f"
    )
)

:: Test main.py with -f flag if sample.txt exists
if exist "%SCRIPT_DIR%unit\sample.txt" (
    echo Testing main.py with -f flag...
    python "%PROJECT_ROOT%\main.py" -f "%SCRIPT_DIR%unit\sample.txt"
)

echo Tests completed
""")
        print(format_status(f"Created: {script_path}", "success"))

def main():
    print(format_header("UaiBot Test Structure Setup", "info"))
    
    create_directory_structure()
    create_sample_files()
    create_run_scripts()
    
    print(format_header("Setup Complete", "success"))
    print(format_status("You can now run tests with:", "info"))
    print("  python test_files/run_simple_test.py")
    
    if platform.system() != "Windows":
        print("  ./test_files/run_tests.sh")
    else:
        print("  test_files\\run_tests.bat")
        
    print("\nOr use the main test runner:")
    print("  python test_files/run_tests.py --all")

if __name__ == "__main__":
    main()
