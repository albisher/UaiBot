#!/usr/bin/env python3
"""
Test cases for the OutputFormatter module.
Validates formatting functionality works as expected across platforms.
"""

import os
import sys
import unittest
from io import StringIO
from contextlib import redirect_stdout

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import the module to test
from test_files.output_formatter import (
    TestOutputFormatter, 
    format_header, 
    format_status, 
    format_box,
    format_file_operation,
    format_command_output
)

class TestOutputFormatterTests(unittest.TestCase):
    """Test cases for the TestOutputFormatter class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test formatter instance
        self.formatter = TestOutputFormatter(log_to_file=False)
        # Create a string buffer for capturing stdout
        self.buffer = StringIO()
        
    def test_format_header(self):
        """Test header formatting."""
        result = self.formatter.format_header("Test Header", "info")
        self.assertIn("Test Header", result)
        self.assertIn("-------", result)  # Should have underline
        
    def test_format_status(self):
        """Test status formatting with different status types."""
        statuses = ["success", "error", "warning", "info"]
        for status in statuses:
            result = self.formatter.format_status(f"This is a {status} message", status)
            self.assertIn(f"This is a {status} message", result)
            # Should contain emoji (though exact representation might vary by platform)
            self.assertTrue(len(result) > len(f"This is a {status} message"))
            
    def test_format_box(self):
        """Test box formatting."""
        content = "This is test content\nWith multiple lines"
        result = self.formatter.format_box(content, "Test Box")
        # Box should contain content and title
        self.assertIn("Test Box", result)
        self.assertIn("This is test content", result)
        self.assertIn("With multiple lines", result)
        # Should have box borders
        self.assertIn("┌", result)
        self.assertIn("┐", result)
        self.assertIn("└", result)
        self.assertIn("┘", result)
        
    def test_format_file_operation(self):
        """Test file operation result formatting."""
        # Success case
        success_result = self.formatter.format_file_operation_result(
            "Create", True, "File created successfully", "Details: test.txt created"
        )
        self.assertIn("Create", success_result)
        self.assertIn("File created successfully", success_result)
        self.assertIn("Details", success_result)
        
        # Error case
        error_result = self.formatter.format_file_operation_result(
            "Delete", False, "File not found", "Details: test.txt does not exist"
        )
        self.assertIn("Delete", error_result)
        self.assertIn("File not found", error_result)
        
    def test_format_command_output(self):
        """Test command output formatting."""
        command = "ls -la"
        stdout = "file1.txt\nfile2.txt"
        stderr = "Warning: some files are hidden"
        exit_code = 0
        
        result = self.formatter.format_command_output(command, stdout, stderr, exit_code)
        self.assertIn(command, result)
        self.assertIn(stdout, result)
        self.assertIn(stderr, result)
        self.assertIn(f"Exit code: {exit_code}", result)
        
    def test_thinking_box_output(self):
        """Test thinking box prints correctly."""
        message = "Processing file operations"
        
        with redirect_stdout(self.buffer):
            self.formatter.reset_output_status()
            self.formatter.print_thinking_box(message)
            
        output = self.buffer.getvalue()
        self.assertIn("🤔 Thinking...", output)
        self.assertIn(message, output)
        
    def test_result_output(self):
        """Test result message prints correctly."""
        with redirect_stdout(self.buffer):
            self.formatter.reset_output_status()
            self.formatter.print_result("success", "Operation completed successfully")
            
        output = self.buffer.getvalue()
        self.assertIn("Operation completed successfully", output)
        # Should contain emoji
        self.assertTrue(output.startswith("✅") or "✅" in output)
        
    def test_subsequent_output_suppression(self):
        """Test that subsequent outputs are suppressed until reset."""
        with redirect_stdout(self.buffer):
            self.formatter.reset_output_status()
            self.formatter.print_result("success", "First message")
            self.formatter.print_result("error", "Should not appear")
            
        output = self.buffer.getvalue()
        self.assertIn("First message", output)
        self.assertNotIn("Should not appear", output)
        
        # Reset and try again
        self.buffer = StringIO()  # New buffer
        with redirect_stdout(self.buffer):
            self.formatter.reset_output_status()
            self.formatter.print_result("error", "Now this should appear")
            
        output = self.buffer.getvalue()
        self.assertIn("Now this should appear", output)
        
    def test_convenience_functions(self):
        """Test the module-level convenience functions."""
        header = format_header("Test Header")
        self.assertIn("Test Header", header)
        
        status = format_status("Test Status", "warning")
        self.assertIn("Test Status", status)
        
        box = format_box("Test Content", "Test Title")
        self.assertIn("Test Content", box)
        self.assertIn("Test Title", box)
        
        file_op = format_file_operation("Read", True, "File read successfully")
        self.assertIn("Read", file_op)
        self.assertIn("File read successfully", file_op)
        
        cmd_out = format_command_output("echo test", "test", "", 0)
        self.assertIn("echo test", cmd_out)
        self.assertIn("test", cmd_out)


def run_manual_test():
    """Run a manual test with visual output to terminal."""
    print("\n===== MANUAL FORMATTER TEST =====\n")
    
    formatter = TestOutputFormatter()
    
    print(formatter.format_header("File Operations Test", "file"))
    print(formatter.format_status("Reading configuration file", "info"))
    print(formatter.format_status("Config loaded successfully", "success"))
    
    print("\nTesting box formatting:")
    content = "This is a test content\nWith multiple lines\nTo see how the box handles them"
    print(formatter.format_box(content, "Sample Output"))
    
    print("\nTesting file operation formatting:")
    print(formatter.format_file_operation_result(
        "Create", True, "Created directory /tmp/test", 
        "Path: /tmp/test\nPermissions: 755\nOwner: current_user"
    ))
    print(formatter.format_file_operation_result(
        "Delete", False, "Failed to delete file", 
        "Path: /tmp/nonexistent.txt\nError: No such file or directory"
    ))
    
    print("\nTesting command output formatting:")
    print(formatter.format_command_output(
        "find /tmp -name '*.log'",
        "/tmp/app.log\n/tmp/system.log",
        "",
        0
    ))
    
    print("\nTesting thinking box and results:")
    formatter.reset_output_status()
    formatter.print_thinking_box("Processing a complex operation\nThis might take a moment")
    formatter.print_result("success", "Operation completed successfully")
    

if __name__ == "__main__":
    # First run unit tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Then run manual visual test
    run_manual_test()
