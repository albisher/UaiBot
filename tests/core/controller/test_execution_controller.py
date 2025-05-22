"""
Test suite for the execution controller.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import json
import os

from app.core.controller.execution_controller import ExecutionController

@pytest.fixture
def mock_shell_handler():
    """Create a mock shell handler."""
    handler = Mock()
    handler.execute_command.return_value = "Command executed successfully"
    return handler

@pytest.fixture
def mock_ai_handler():
    """Create a mock AI handler."""
    handler = Mock()
    handler.process_prompt.return_value = "AI processed successfully"
    return handler

@pytest.fixture
def execution_controller(mock_shell_handler, mock_ai_handler):
    """Create an execution controller instance."""
    return ExecutionController(mock_shell_handler, mock_ai_handler)

def test_execute_plan_success(execution_controller, tmp_path):
    """Test successful plan execution."""
    # Create a test plan
    plan = {
        "plan": [
            {
                "step": 1,
                "description": "Create a test file",
                "operation": "file.create",
                "parameters": {
                    "filename": str(tmp_path / "test.txt"),
                    "content": "Hello, World!"
                },
                "confidence": 0.98,
                "condition": None,
                "on_success": [2],
                "on_failure": [],
                "explanation": "Creates a test file"
            },
            {
                "step": 2,
                "description": "Read the test file",
                "operation": "file.read",
                "parameters": {
                    "filename": str(tmp_path / "test.txt")
                },
                "confidence": 0.95,
                "condition": None,
                "on_success": [],
                "on_failure": [],
                "explanation": "Reads the test file"
            }
        ],
        "overall_confidence": 0.96,
        "alternatives": [],
        "language": "en"
    }
    
    # Execute the plan
    result = execution_controller.execute_plan(plan)
    
    # Verify results
    assert result["status"] == "success"
    assert len(result["results"]) == 2
    assert result["results"][0]["status"] == "success"
    assert result["results"][1]["status"] == "success"
    assert result["results"][1]["output"] == "Hello, World!"
    
    # Verify state
    state = execution_controller.get_execution_state()
    assert state["completed_steps"] == [1, 2]
    assert state["failed_steps"] == []
    assert state["start_time"] is not None
    assert state["end_time"] is not None

def test_execute_plan_with_failure(execution_controller, tmp_path):
    """Test plan execution with a failing step."""
    # Create a test plan with a failing step
    plan = {
        "plan": [
            {
                "step": 1,
                "description": "Create a test file",
                "operation": "file.create",
                "parameters": {
                    "filename": str(tmp_path / "test.txt"),
                    "content": "Hello, World!"
                },
                "confidence": 0.98,
                "condition": None,
                "on_success": [2],
                "on_failure": [3],
                "explanation": "Creates a test file"
            },
            {
                "step": 2,
                "description": "Read non-existent file",
                "operation": "file.read",
                "parameters": {
                    "filename": str(tmp_path / "nonexistent.txt")
                },
                "confidence": 0.95,
                "condition": None,
                "on_success": [],
                "on_failure": [],
                "explanation": "Reads a non-existent file"
            },
            {
                "step": 3,
                "description": "Execute shell command",
                "operation": "shell.execute",
                "parameters": {
                    "command": "echo 'Recovery step'"
                },
                "confidence": 0.95,
                "condition": None,
                "on_success": [],
                "on_failure": [],
                "explanation": "Executes a recovery command"
            }
        ],
        "overall_confidence": 0.96,
        "alternatives": [],
        "language": "en"
    }
    
    # Execute the plan
    result = execution_controller.execute_plan(plan)
    
    # Verify results
    assert result["status"] == "partial_success"
    assert len(result["results"]) == 3
    assert result["results"][0]["status"] == "success"
    assert result["results"][1]["status"] == "error"
    assert result["results"][2]["status"] == "success"
    
    # Verify state
    state = execution_controller.get_execution_state()
    assert state["completed_steps"] == [1, 3]
    assert state["failed_steps"] == [2]

def test_state_persistence(execution_controller, tmp_path):
    """Test state persistence functionality."""
    # Create a test plan
    plan = {
        "plan": [
            {
                "step": 1,
                "description": "Create a test file",
                "operation": "file.create",
                "parameters": {
                    "filename": str(tmp_path / "test.txt"),
                    "content": "Hello, World!"
                },
                "confidence": 0.98,
                "condition": None,
                "on_success": [],
                "on_failure": [],
                "explanation": "Creates a test file"
            }
        ],
        "overall_confidence": 0.96,
        "alternatives": [],
        "language": "en"
    }
    
    # Execute the plan
    execution_controller.execute_plan(plan)
    
    # Create a new controller instance
    new_controller = ExecutionController(Mock(), Mock())
    
    # Verify state was loaded
    state = new_controller.get_execution_state()
    assert state["completed_steps"] == [1]
    assert state["failed_steps"] == []
    assert state["start_time"] is not None
    assert state["end_time"] is not None

def test_clear_state(execution_controller, tmp_path):
    """Test state clearing functionality."""
    # Create and execute a test plan
    plan = {
        "plan": [
            {
                "step": 1,
                "description": "Create a test file",
                "operation": "file.create",
                "parameters": {
                    "filename": str(tmp_path / "test.txt"),
                    "content": "Hello, World!"
                },
                "confidence": 0.98,
                "condition": None,
                "on_success": [],
                "on_failure": [],
                "explanation": "Creates a test file"
            }
        ],
        "overall_confidence": 0.96,
        "alternatives": [],
        "language": "en"
    }
    
    execution_controller.execute_plan(plan)
    
    # Clear state
    execution_controller.clear_state()
    
    # Verify state was cleared
    state = execution_controller.get_execution_state()
    assert state["completed_steps"] == []
    assert state["failed_steps"] == []
    assert state["start_time"] is None
    assert state["end_time"] is None
    assert state["state_variables"] == {}

def test_state_variables(execution_controller, tmp_path):
    """Test state variable handling."""
    # Create a test plan with state variables
    plan = {
        "plan": [
            {
                "step": 1,
                "description": "Create a test file",
                "operation": "file.create",
                "parameters": {
                    "filename": str(tmp_path / "test.txt"),
                    "content": "Hello, World!",
                    "$file_path": str(tmp_path / "test.txt")
                },
                "confidence": 0.98,
                "condition": None,
                "on_success": [2],
                "on_failure": [],
                "explanation": "Creates a test file"
            },
            {
                "step": 2,
                "description": "Read the test file",
                "operation": "file.read",
                "parameters": {
                    "filename": "$file_path"
                },
                "confidence": 0.95,
                "condition": None,
                "on_success": [],
                "on_failure": [],
                "explanation": "Reads the test file"
            }
        ],
        "overall_confidence": 0.96,
        "alternatives": [],
        "language": "en"
    }
    
    # Execute the plan
    result = execution_controller.execute_plan(plan)
    
    # Verify state variables
    state = execution_controller.get_execution_state()
    assert state["state_variables"]["file_path"] == str(tmp_path / "test.txt")
    
    # Verify results
    assert result["status"] == "success"
    assert len(result["results"]) == 2
    assert result["results"][0]["status"] == "success"
    assert result["results"][1]["status"] == "success"
    assert result["results"][1]["output"] == "Hello, World!" 