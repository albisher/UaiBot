"""Tests for mouse control capabilities."""

import pytest
from unittest.mock import MagicMock, patch
import time
from typing import Tuple, List

from uaibot.core.bot import UaiBot
from uaibot.core.capabilities import CapabilitiesManager

@pytest.fixture
def uaibot():
    """Create a UaiBot instance for testing."""
    return UaiBot()

class TestMouseControl:
    """Test suite for mouse control capabilities."""
    
    def test_basic_mouse_movement(self, uaibot):
        """Test basic mouse movement capabilities."""
        # Test absolute positioning
        result = uaibot.process_command("move mouse to coordinates (100, 200)")
        assert result["status"] == "success"
        assert "mouse_control" in result["result"]["used_capabilities"]
        
        # Test relative movement
        result = uaibot.process_command("move mouse 50 pixels right")
        assert result["status"] == "success"
        
        # Test movement to screen edges
        result = uaibot.process_command("move mouse to top left corner")
        assert result["status"] == "success"
        
        result = uaibot.process_command("move mouse to bottom right corner")
        assert result["status"] == "success"
    
    def test_click_operations(self, uaibot):
        """Test various click operations."""
        # Test left click
        result = uaibot.process_command("click at current position")
        assert result["status"] == "success"
        
        # Test right click
        result = uaibot.process_command("right-click at coordinates (150, 150)")
        assert result["status"] == "success"
        
        # Test double click
        result = uaibot.process_command("double-click the button")
        assert result["status"] == "success"
        
        # Test middle click
        result = uaibot.process_command("middle-click at current position")
        assert result["status"] == "success"
    
    def test_drag_operations(self, uaibot):
        """Test drag and drop operations."""
        # Test simple drag
        result = uaibot.process_command("drag from (100, 100) to (200, 200)")
        assert result["status"] == "success"
        
        # Test drag with hold
        result = uaibot.process_command("drag and hold from (100, 100) to (200, 200)")
        assert result["status"] == "success"
        
        # Test drag with release
        result = uaibot.process_command("release mouse at (200, 200)")
        assert result["status"] == "success"
    
    def test_scroll_operations(self, uaibot):
        """Test scroll operations."""
        # Test vertical scroll
        result = uaibot.process_command("scroll down 100 pixels")
        assert result["status"] == "success"
        
        result = uaibot.process_command("scroll up 50 pixels")
        assert result["status"] == "success"
        
        # Test horizontal scroll
        result = uaibot.process_command("scroll right 100 pixels")
        assert result["status"] == "success"
        
        result = uaibot.process_command("scroll left 50 pixels")
        assert result["status"] == "success"
        
        # Test scroll with speed
        result = uaibot.process_command("scroll down slowly")
        assert result["status"] == "success"
        
        result = uaibot.process_command("scroll up quickly")
        assert result["status"] == "success"
    
    def test_gesture_operations(self, uaibot):
        """Test mouse gesture operations."""
        # Test simple gestures
        result = uaibot.process_command("draw circle with mouse")
        assert result["status"] == "success"
        
        result = uaibot.process_command("draw square with mouse")
        assert result["status"] == "success"
        
        # Test complex gestures
        result = uaibot.process_command("draw figure eight with mouse")
        assert result["status"] == "success"
    
    def test_speed_control(self, uaibot):
        """Test mouse movement speed control."""
        # Test different speeds
        result = uaibot.process_command("move mouse slowly to (100, 100)")
        assert result["status"] == "success"
        
        result = uaibot.process_command("move mouse quickly to (200, 200)")
        assert result["status"] == "success"
        
        # Test acceleration
        result = uaibot.process_command("move mouse with acceleration to (300, 300)")
        assert result["status"] == "success"
    
    def test_precision_control(self, uaibot):
        """Test precision mouse control."""
        # Test pixel-perfect movement
        result = uaibot.process_command("move mouse precisely to (150, 150)")
        assert result["status"] == "success"
        
        # Test small movements
        result = uaibot.process_command("move mouse 1 pixel right")
        assert result["status"] == "success"
        
        # Test precise clicking
        result = uaibot.process_command("click precisely at (175, 175)")
        assert result["status"] == "success"
    
    def test_combination_operations(self, uaibot):
        """Test combination of mouse operations."""
        # Test drag and click
        result = uaibot.process_command("drag from (100, 100) to (200, 200) and click")
        assert result["status"] == "success"
        
        # Test move and scroll
        result = uaibot.process_command("move to (150, 150) and scroll down")
        assert result["status"] == "success"
        
        # Test complex sequence
        result = uaibot.process_command("move to (100, 100), click, drag to (200, 200), and release")
        assert result["status"] == "success"
    
    def test_error_handling(self, uaibot):
        """Test error handling in mouse operations."""
        # Test invalid coordinates
        result = uaibot.process_command("move mouse to (-100, -100)")
        assert result["status"] == "error"
        
        # Test invalid movement
        result = uaibot.process_command("move mouse 999999 pixels right")
        assert result["status"] == "error"
        
        # Test invalid click
        result = uaibot.process_command("click at invalid position")
        assert result["status"] == "error"
    
    def test_boundary_conditions(self, uaibot):
        """Test boundary conditions for mouse operations."""
        # Test screen boundaries
        result = uaibot.process_command("move mouse to screen edge")
        assert result["status"] == "success"
        
        # Test maximum scroll
        result = uaibot.process_command("scroll to bottom of page")
        assert result["status"] == "success"
        
        # Test minimum movement
        result = uaibot.process_command("move mouse 0.1 pixels right")
        assert result["status"] == "success"
    
    def test_capability_status(self, uaibot):
        """Test that mouse control capability is properly registered and tested."""
        status = uaibot.capabilities.get_capability_status("mouse_control")
        assert status["is_tested"] is True
        assert status["test_coverage"] >= 95.0
        assert status["status"] == "active"
        assert status["is_ready"] is True 