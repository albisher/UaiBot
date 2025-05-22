#!/usr/bin/env python3
"""
Test suite for AI command interpreter.
Tests the functionality of AI-driven command interpretation.
"""
import pytest
from pathlib import Path
from app.core.ai_command_interpreter import AICommandInterpreter

class TestAICommandInterpreter:
    """Test suite for AI command interpreter."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for each test."""
        self.interpreter = AICommandInterpreter()
        yield
        # Cleanup after tests
        self.interpreter.clear_context()
    
    def test_interpret_command_basic(self):
        """Test basic command interpretation."""
        command = "create file test.txt with content 'Hello'"
        result = self.interpreter.interpret_command(command)
        
        assert isinstance(result, dict)
        assert 'operation' in result
        assert 'parameters' in result
        assert 'context' in result
        assert 'confidence' in result
    
    def test_process_command_file_operation(self):
        """Test processing a file operation command."""
        command = "create file test.txt with content 'Hello'"
        result = self.interpreter.process_command(command)
        
        assert isinstance(result, str)
        assert "created" in result.lower() or "success" in result.lower()
    
    def test_command_history(self):
        """Test command history tracking."""
        command = "create file test.txt with content 'Hello'"
        self.interpreter.process_command(command)
        
        history = self.interpreter.get_command_history()
        assert len(history) == 1
        assert history[0]['command'] == command
    
    def test_context_management(self):
        """Test context management functionality."""
        # Test saving and loading context
        test_context = {'test_key': 'test_value'}
        self.interpreter.context = test_context
        
        # Save context
        self.interpreter.save_context()
        
        # Clear context
        self.interpreter.clear_context()
        assert not self.interpreter.context
        
        # Load context
        self.interpreter.load_context()
        assert self.interpreter.context == test_context
    
    def test_multilingual_support(self):
        """Test multilingual command support."""
        # Test English command
        en_command = "create file test.txt with content 'Hello'"
        en_result = self.interpreter.process_command(en_command, 'en')
        assert isinstance(en_result, str)
        
        # Test Arabic command
        ar_command = "إنشاء ملف test.txt بالمحتوى 'مرحبا'"
        ar_result = self.interpreter.process_command(ar_command, 'ar')
        assert isinstance(ar_result, str)
    
    def test_error_handling(self):
        """Test error handling in command processing."""
        # Test with invalid command
        result = self.interpreter.process_command("")
        assert "error" in result.lower()
        
        # Test with invalid operation
        result = self.interpreter.process_command("invalid operation")
        assert "error" in result.lower() 