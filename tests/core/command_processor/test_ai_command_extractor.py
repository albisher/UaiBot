"""
Test suite for AICommandExtractor class.

This module contains comprehensive tests for the AICommandExtractor class,
following Ubuntu test conventions and cursor rules.
"""

import unittest
import json
from uaibot.core.command_processor.ai_command_extractor import AICommandExtractor
import pytest

class TestAICommandExtractor(unittest.TestCase):
    """Test cases for AICommandExtractor class."""

    @pytest.fixture
    def extractor(self):
        return AICommandExtractor()

    def test_extract_command_json_plan(self):
        """Test extraction of commands from JSON plan format."""
        # Test case 1: Valid JSON plan
        valid_json = {
            "plan": [
                {
                    "step": "get_system_uptime",
                    "description": "Get system uptime",
                    "operation": "system_command",
                    "parameters": {"command": "uptime"},
                    "confidence": 0.95,
                    "conditions": None
                }
            ],
            "overall_confidence": 0.95,
            "language": "en"
        }
        success, plan, metadata = self.extractor.extract_command(json.dumps(valid_json))
        self.assertTrue(success)
        self.assertEqual(plan["plan"][0]["operation"], "system_command")
        self.assertEqual(metadata["source"], "plan_json")

        # Test case 2: Invalid JSON
        invalid_json = "not a json"
        success, plan, metadata = self.extractor.extract_command(invalid_json)
        self.assertFalse(success)
        self.assertIsNone(plan)
        self.assertTrue(metadata["is_error"])

    def test_extract_code_blocks(self):
        """Test extraction of commands from code blocks."""
        # Test case 1: Bash code block
        text = """
        Here's the command:
        ```bash
        ls -la
        ```
        """
        blocks = self.extractor._extract_code_blocks(text)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].strip(), "ls -la")

        # Test case 2: Multiple code blocks
        text = """
        First command:
        ```bash
        pwd
        ```
        Second command:
        ```shell
        echo "test"
        ```
        """
        blocks = self.extractor._extract_code_blocks(text)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].strip(), "pwd")
        self.assertEqual(blocks[1].strip(), 'echo "test"')

    def test_extract_arabic_command(self):
        """Test extraction of Arabic commands."""
        # Test case 1: Create file command
        text = "اكتب 'test content' في ملف test.txt"
        command = self.extractor._extract_arabic_command(text)
        self.assertEqual(command, "echo 'test content' > test.txt")

        # Test case 2: Read file command
        text = "اقرأ ملف test.txt"
        command = self.extractor._extract_arabic_command(text)
        self.assertEqual(command, "cat test.txt")

        # Test case 3: Delete file command
        text = "احذف ملف test.txt"
        command = self.extractor._extract_arabic_command(text)
        self.assertEqual(command, "rm test.txt")

    def test_detect_file_operation(self):
        """Test detection of file operations."""
        # Test case 1: Create file
        command = "echo 'test' > test.txt"
        metadata = {}
        result = self.extractor._detect_file_operation(command, metadata)
        self.assertEqual(result["file_operation"], "create")
        self.assertEqual(result["operation_params"]["filename"], "test.txt")

        # Test case 2: Read file
        command = "cat test.txt"
        metadata = {}
        result = self.extractor._detect_file_operation(command, metadata)
        self.assertEqual(result["file_operation"], "read")
        self.assertEqual(result["operation_params"]["filename"], "test.txt")

        # Test case 3: Delete file
        command = "rm test.txt"
        metadata = {}
        result = self.extractor._detect_file_operation(command, metadata)
        self.assertEqual(result["file_operation"], "delete")
        self.assertEqual(result["operation_params"]["filename"], "test.txt")

    def test_check_for_error(self):
        """Test error detection in AI responses."""
        # Test case 1: Error response
        text = "ERROR: Cannot execute this command safely"
        is_error, message = self.extractor._check_for_error(text)
        self.assertTrue(is_error)
        self.assertIsNotNone(message)

        # Test case 2: Safe response
        text = "Here's a safe command: ls -la"
        is_error, message = self.extractor._check_for_error(text)
        self.assertFalse(is_error)
        self.assertIsNone(message)

    def test_generate_command_from_file_operation(self):
        """Test generation of shell commands from file operations."""
        # Test case 1: Create file
        command = self.extractor._generate_command_from_file_operation(
            "create",
            {"filename": "test.txt", "content": "test content"}
        )
        self.assertEqual(command, "echo 'test content' > test.txt")

        # Test case 2: Read file
        command = self.extractor._generate_command_from_file_operation(
            "read",
            {"filename": "test.txt"}
        )
        self.assertEqual(command, "cat test.txt")

        # Test case 3: Delete file
        command = self.extractor._generate_command_from_file_operation(
            "delete",
            {"filename": "test.txt", "recursive": True, "force": True}
        )
        self.assertEqual(command, "rm -rf test.txt")

    def test_format_ai_prompt(self):
        """Test formatting of AI prompts."""
        user_input = "Show me the system uptime"
        system_info = {
            "system": "Linux",
            "version": "5.4.0"
        }
        prompt = self.extractor.format_ai_prompt(user_input, system_info)
        
        # Verify prompt contains required elements
        self.assertIn("You are an AI assistant", prompt)
        self.assertIn("Linux", prompt)
        self.assertIn("5.4.0", prompt)
        self.assertIn("Show me the system uptime", prompt)
        self.assertIn("STRICT INSTRUCTIONS", prompt)
        self.assertIn("plan", prompt)

    def test_extract_command_success(self, extractor):
        """Test successful command extraction."""
        ai_response = """
        Here's what I'll do:
        ```json
        {
            "command": "echo 'Hello World'",
            "type": "shell",
            "description": "Print hello world"
        }
        ```
        """
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is True
        assert plan["command"] == "echo 'Hello World'"
        assert plan["type"] == "shell"
        assert plan["description"] == "Print hello world"

    def test_extract_command_no_json(self, extractor):
        """Test command extraction without JSON."""
        ai_response = "Run this command: echo 'Hello World'"
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is True
        assert plan["command"] == "echo 'Hello World'"

    def test_extract_command_arabic(self, extractor):
        """Test command extraction with Arabic text."""
        ai_response = "قم بتنفيذ هذا الأمر: echo 'Hello World'"
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is True
        assert plan["command"] == "echo 'Hello World'"

    def test_extract_command_file_operation(self, extractor):
        """Test command extraction with file operation."""
        ai_response = """
        Create a file:
        ```json
        {
            "command": "touch test.txt",
            "type": "file",
            "operation": "create",
            "path": "test.txt"
        }
        ```
        """
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is True
        assert plan["command"] == "touch test.txt"
        assert plan["type"] == "file"
        assert plan["operation"] == "create"
        assert plan["path"] == "test.txt"

    def test_extract_command_invalid_json(self, extractor):
        """Test command extraction with invalid JSON."""
        ai_response = """
        ```json
        {
            "command": "echo 'Hello World'",
            "type": "shell",
            "description": "Print hello world",
        ```
        """
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is False
        assert plan is None

    def test_extract_command_empty_response(self, extractor):
        """Test command extraction with empty response."""
        ai_response = ""
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is False
        assert plan is None

    def test_extract_command_multiple_commands(self, extractor):
        """Test command extraction with multiple commands."""
        ai_response = """
        Here are the commands:
        ```json
        {
            "commands": [
                {
                    "command": "echo 'Hello'",
                    "type": "shell"
                },
                {
                    "command": "echo 'World'",
                    "type": "shell"
                }
            ]
        }
        ```
        """
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is True
        assert len(plan["commands"]) == 2
        assert plan["commands"][0]["command"] == "echo 'Hello'"
        assert plan["commands"][1]["command"] == "echo 'World'"

    def test_extract_command_with_metadata(self, extractor):
        """Test command extraction with metadata."""
        ai_response = """
        ```json
        {
            "command": "echo 'Hello World'",
            "type": "shell",
            "metadata": {
                "confidence": 0.95,
                "language": "en"
            }
        }
        ```
        """
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success is True
        assert plan["command"] == "echo 'Hello World'"
        assert metadata["confidence"] == 0.95
        assert metadata["language"] == "en"

    @pytest.mark.parametrize("ai_response,expected_success", [
        ("echo 'Hello World'", True),
        ("", False),
        ("Invalid command", False),
        ("```json\n{}\n```", False),
    ])
    def test_extract_command_various_inputs(self, extractor, ai_response, expected_success):
        """Test command extraction with various inputs."""
        success, plan, metadata = extractor.extract_command(ai_response)
        assert success == expected_success

if __name__ == '__main__':
    unittest.main() 