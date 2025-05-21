#!/usr/bin/env python3
# filepath: /Users/amac/Documents/code/UaiBot/test_command_processing_enhanced.py
"""
Comprehensive test suite for UaiBot's command processing system.
This script tests the following aspects:
1. Direct command mapping
2. AI command extraction
3. Command execution
4. Unknown command handling
5. Implementation request logging
"""

import sys
import os
import json
import time
import shutil
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from command_processor import CommandProcessor
from uaibot.core.shell_handler import ShellHandler


class MockAIHandler:
    """Mock AI handler for testing various AI response scenarios."""
    
    def __init__(self, response_type="success"):
        self.response_type = response_type
        self.prompt_history = []
    
    def get_ai_response(self, prompt):
        """Return different responses based on the response type."""
        self.prompt_history.append(prompt)
        
        if self.response_type == "success":
            return """I'll help you with that!

```shell
echo "Command executed successfully"
```

This will display a success message."""
        
        elif self.response_type == "error":
            return """I'm sorry, I cannot generate an executable command for this request.

ERROR: This operation requires administrator privileges and cannot be safely performed with a single command.
"""
        
        elif self.response_type == "implicit_error":
            return """I apologize, but I'm unable to create a command for this request. 
This type of system optimization requires multiple steps and configuration changes that 
would need to be carefully applied based on your specific hardware and software environment."""
        
        elif self.response_type == "malformed":
            return """Here's a command that might help:

```
echo "This is not properly formatted as a shell command block"
```

Hope this works for you!"""
        
        elif self.response_type == "empty":
            return ""
        
        else:
            return "I don't understand that request."
    
    def query_ai(self, prompt):
        return self.get_ai_response(prompt)


class TestCommandProcessing(unittest.TestCase):
    """Test suite for command processing functionality."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create test logs directory
        self.test_logs_dir = Path("/Users/amac/Documents/code/UaiBot/test_logs")
        self.test_logs_dir.mkdir(exist_ok=True)
        
        # Create a test config
        self.test_config = {
            "log_directory": str(self.test_logs_dir),
            "command_extraction": {
                "max_retries": 1,
                "verify_commands": True
            },
            "fallbacks": {
                "enable_direct_console_logging": True,
                "log_unknown_commands": True
            }
        }
        
        # Save test config
        self.test_config_path = Path("/Users/amac/Documents/code/UaiBot/test_config.json")
        with open(self.test_config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        # Create shell handler
        self.shell_handler = ShellHandler()
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up test logs directory
        if self.test_logs_dir.exists():
            shutil.rmtree(self.test_logs_dir)
        
        # Clean up test config
        if self.test_config_path.exists():
            self.test_config_path.unlink()
    
    def test_successful_command_extraction(self):
        """Test successful command extraction from AI response."""
        ai_handler = MockAIHandler("success")
        cmd_processor = CommandProcessor(ai_handler, self.shell_handler, quiet_mode=True)
        
        result = cmd_processor.process_command("optimize my system")
        self.assertIn("Command executed successfully", result)
    
    def test_error_detection_in_ai_response(self):
        """Test detection of explicit error messages in AI response."""
        ai_handler = MockAIHandler("error")
        cmd_processor = CommandProcessor(ai_handler, self.shell_handler, quiet_mode=True)
        
        result = cmd_processor.process_command("make my system faster")
        self.assertIn("logged for future implementation", result)
        self.assertIn("requires administrator privileges", result)
    
    def test_implicit_error_detection(self):
        """Test detection of implicit error messages in AI response."""
        ai_handler = MockAIHandler("implicit_error") 
        cmd_processor = CommandProcessor(ai_handler, self.shell_handler, quiet_mode=True)
        
        result = cmd_processor.process_command("configure my system for gaming")
        self.assertIn("logged for future implementation", result)
    
    def test_malformed_command_format(self):
        """Test handling of malformed command format in AI response."""
        ai_handler = MockAIHandler("malformed")
        cmd_processor = CommandProcessor(ai_handler, self.shell_handler, quiet_mode=True)
        
        result = cmd_processor.process_command("do something weird")
        # Even though malformed, it should extract the command if possible
        self.assertTrue(
            "Command executed successfully" in result or 
            "logged for future implementation" in result
        )
    
    def test_implementation_logging(self):
        """Test that unknown commands are properly logged for implementation."""
        # Create a command processor with a failing AI handler
        ai_handler = MockAIHandler("error")
        cmd_processor = CommandProcessor(ai_handler, self.shell_handler, quiet_mode=True)
        
        # Process a command that should fail and be logged
        cmd_processor.process_command("make my computer fly")
        
        # Check that the implementation log exists
        impl_log = self.test_logs_dir / "implementation_needed.log"
        self.assertTrue(impl_log.exists(), f"Implementation log not created at {impl_log}")
        
        # Check log contents
        with open(impl_log, 'r') as f:
            log_content = f.read()
            self.assertIn("make my computer fly", log_content)
    
    def test_direct_command_recognition(self):
        """Test direct command recognition and execution."""
        ai_handler = MockAIHandler()
        cmd_processor = CommandProcessor(ai_handler, self.shell_handler, quiet_mode=True)
        
        # Patch the _try_direct_execution method to avoid actual command execution
        with patch.object(cmd_processor, '_try_direct_execution') as mock_execute:
            mock_execute.return_value = "Command executed: ls -la"
            
            result = cmd_processor.process_command("ls -la")
            mock_execute.assert_called_once()
            self.assertIn("Command executed", result)
    
    def test_multiple_fallback_paths(self):
        """Test multiple fallback paths for logging."""
        # Create a command processor with invalid log directory
        ai_handler = MockAIHandler("error")
        
        # Modify the config to use a non-existent directory
        with open(self.test_config_path, 'w') as f:
            json.dump({"log_directory": "/nonexistent/directory"}, f)
        
        cmd_processor = CommandProcessor(ai_handler, self.shell_handler, quiet_mode=True)
        
        # Process a command that should be logged
        cmd_processor.process_command("do something impossible")
        
        # Check logs in fallback directories
        possible_logs = [
            Path("/Users/amac/Documents/code/UaiBot/logs/implementation_needed.log"),
            Path(os.path.expanduser("~/.uaibot/logs/implementation_needed.log")),
            Path("/tmp/uaibot_logs/implementation_needed.log")
        ]
        
        found_log = False
        for log_path in possible_logs:
            if log_path.exists():
                with open(log_path, 'r') as f:
                    if "do something impossible" in f.read():
                        found_log = True
                        break
        
        self.assertTrue(found_log, "Implementation log not found in any fallback location")


if __name__ == "__main__":
    unittest.main()
