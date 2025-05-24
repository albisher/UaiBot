"""Tests for the capabilities management system."""

import pytest
from datetime import datetime
from pathlib import Path
import json
import tempfile
import os

from uaibot.core.capabilities import CapabilitiesManager, Capability

@pytest.fixture
def temp_capabilities_file():
    """Create a temporary capabilities file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        json.dump([], f)
    yield f.name
    os.unlink(f.name)

@pytest.fixture
def capabilities_manager(temp_capabilities_file):
    """Create a CapabilitiesManager instance with a temporary file."""
    return CapabilitiesManager(temp_capabilities_file)

def test_register_capability(capabilities_manager):
    """Test registering a new capability."""
    capabilities_manager.register_capability(
        name="mouse_control",
        description="Control mouse movements and clicks",
        category="input",
        implementation_path="uaibot.core.input.mouse",
        dependencies=["screen_reading"],
        status="experimental",
        version="0.1.0"
    )
    
    cap = capabilities_manager.get_capability("mouse_control")
    assert cap is not None
    assert cap.name == "mouse_control"
    assert cap.description == "Control mouse movements and clicks"
    assert cap.category == "input"
    assert cap.is_tested is False
    assert cap.test_coverage == 0.0
    assert cap.dependencies == ["screen_reading"]
    assert cap.status == "experimental"
    assert cap.version == "0.1.0"

def test_update_test_status(capabilities_manager):
    """Test updating a capability's test status."""
    capabilities_manager.register_capability(
        name="keyboard_input",
        description="Simulate keyboard input",
        category="input",
        implementation_path="uaibot.core.input.keyboard"
    )
    
    capabilities_manager.update_test_status(
        name="keyboard_input",
        is_tested=True,
        test_coverage=85.5,
        status="active"
    )
    
    cap = capabilities_manager.get_capability("keyboard_input")
    assert cap.is_tested is True
    assert cap.test_coverage == 85.5
    assert cap.status == "active"

def test_list_capabilities(capabilities_manager):
    """Test listing capabilities with filters."""
    # Register multiple capabilities
    capabilities_manager.register_capability(
        name="mouse_control",
        description="Mouse control",
        category="input",
        implementation_path="uaibot.core.input.mouse"
    )
    
    capabilities_manager.register_capability(
        name="screen_reading",
        description="Screen reading",
        category="input",
        implementation_path="uaibot.core.input.screen"
    )
    
    capabilities_manager.register_capability(
        name="text_to_speech",
        description="Text to speech",
        category="output",
        implementation_path="uaibot.core.output.speech"
    )
    
    # Test filtering by category
    input_caps = capabilities_manager.list_capabilities(category="input")
    assert len(input_caps) == 2
    assert all(cap.category == "input" for cap in input_caps)
    
    # Test filtering by status
    capabilities_manager.update_test_status(
        name="mouse_control",
        is_tested=True,
        test_coverage=90.0,
        status="active"
    )
    
    active_caps = capabilities_manager.list_capabilities(status="active")
    assert len(active_caps) == 1
    assert active_caps[0].name == "mouse_control"
    
    # Test filtering by test status
    tested_caps = capabilities_manager.list_capabilities(is_tested=True)
    assert len(tested_caps) == 1
    assert tested_caps[0].name == "mouse_control"

def test_check_dependencies(capabilities_manager):
    """Test dependency checking."""
    # Register capabilities with dependencies
    capabilities_manager.register_capability(
        name="screen_reading",
        description="Screen reading",
        category="input",
        implementation_path="uaibot.core.input.screen"
    )
    
    capabilities_manager.register_capability(
        name="mouse_control",
        description="Mouse control",
        category="input",
        implementation_path="uaibot.core.input.mouse",
        dependencies=["screen_reading"]
    )
    
    # Test missing dependency
    capabilities_manager.register_capability(
        name="advanced_mouse",
        description="Advanced mouse control",
        category="input",
        implementation_path="uaibot.core.input.advanced_mouse",
        dependencies=["mouse_control", "nonexistent_capability"]
    )
    
    missing_deps = capabilities_manager.check_dependencies("advanced_mouse")
    assert "nonexistent_capability" in missing_deps
    assert "mouse_control (untested)" in missing_deps

def test_get_capability_status(capabilities_manager):
    """Test getting detailed capability status."""
    capabilities_manager.register_capability(
        name="mouse_control",
        description="Mouse control",
        category="input",
        implementation_path="uaibot.core.input.mouse",
        dependencies=["screen_reading"]
    )
    
    status = capabilities_manager.get_capability_status("mouse_control")
    assert status["name"] == "mouse_control"
    assert status["is_tested"] is False
    assert status["test_coverage"] == 0.0
    assert "screen_reading" in status["missing_dependencies"]
    assert status["is_ready"] is False
    
    # Update test status and check again
    capabilities_manager.update_test_status(
        name="mouse_control",
        is_tested=True,
        test_coverage=95.0,
        status="active"
    )
    
    status = capabilities_manager.get_capability_status("mouse_control")
    assert status["is_tested"] is True
    assert status["test_coverage"] == 95.0
    assert status["status"] == "active"
    assert not status["is_ready"]  # Still not ready due to missing dependency

def test_persistence(temp_capabilities_file):
    """Test that capabilities are properly persisted to and loaded from file."""
    # Create first manager and register a capability
    manager1 = CapabilitiesManager(temp_capabilities_file)
    manager1.register_capability(
        name="test_capability",
        description="Test capability",
        category="test",
        implementation_path="test.path"
    )
    
    # Create second manager and verify capability was loaded
    manager2 = CapabilitiesManager(temp_capabilities_file)
    cap = manager2.get_capability("test_capability")
    assert cap is not None
    assert cap.name == "test_capability"
    assert cap.description == "Test capability" 