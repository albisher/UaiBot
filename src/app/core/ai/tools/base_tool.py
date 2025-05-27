"""
Base class for all Labeeb agent tools. Provides the interface and shared logic for tool registration, execution, and documentation.

This module defines the base tool class for Labeeb's AI agent tools.
"""

class BaseAgentTool:
    """Base class for Labeeb agent tools."""
    
    def __init__(self):
        self.name = "Labeeb Tool"
        self.description = "A tool for Labeeb agents" 