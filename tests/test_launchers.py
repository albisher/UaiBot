#!/usr/bin/env python3
"""
Labeeb Launcher Tests

This module contains tests for the Labeeb launcher implementations.
"""
import os
import sys
import pytest
import asyncio
from pathlib import Path
from tkinter import Tk

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from scripts.launch import LabeebCLI
from scripts.launch_gui import LabeebGUI, LabeebApp

@pytest.fixture
def cli_agent():
    """Create a CLI agent instance."""
    return LabeebCLI()

@pytest.fixture
def gui_agent():
    """Create a GUI agent instance."""
    return LabeebGUI()

@pytest.fixture
def root():
    """Create a tkinter root window."""
    root = Tk()
    yield root
    root.destroy()

@pytest.fixture
def app(root):
    """Create a LabeebApp instance."""
    return LabeebApp(root)

@pytest.mark.asyncio
async def test_cli_agent_execute_command(cli_agent):
    """Test CLI agent command execution."""
    result = await cli_agent.execute("execute_command", {"command": "echo 'test'"})
    assert result["success"]
    assert "test" in result["stdout"]

@pytest.mark.asyncio
async def test_cli_agent_process_input(cli_agent):
    """Test CLI agent input processing."""
    result = await cli_agent.execute("process_input", {"input": "test message"})
    assert "response" in result

@pytest.mark.asyncio
async def test_gui_agent_execute_command(gui_agent):
    """Test GUI agent command execution."""
    result = await gui_agent.execute("execute_command", {"command": "echo 'test'"})
    assert result["success"]
    assert "test" in result["stdout"]

@pytest.mark.asyncio
async def test_gui_agent_process_input(gui_agent):
    """Test GUI agent input processing."""
    result = await gui_agent.execute("process_input", {"input": "test message"})
    assert "response" in result

def test_gui_app_creation(app):
    """Test GUI app creation."""
    assert app.agent is not None
    assert app.output_text is not None
    assert app.input_field is not None
    assert app.send_button is not None
    assert app.status_label is not None

def test_gui_app_input_handling(app):
    """Test GUI app input handling."""
    # Set test input
    app.input_field.insert(0, "test message")
    
    # Trigger input handling
    app.on_input()
    
    # Verify input field is cleared
    assert app.input_field.get() == ""
    
    # Verify output contains user message
    output_text = app.output_text.get("1.0", tk.END)
    assert "You: test message" in output_text 

def create_cli():
    """Create a LabeebCLI instance."""
    return LabeebCLI()

def create_gui():
    """Create a LabeebGUI instance."""
    return LabeebGUI()

def create_app():
    """Create a LabeebApp instance."""
    root = Tk()
    return LabeebApp(root) 