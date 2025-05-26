"""
Tests for platform-specific awareness handlers.

This module contains tests for the platform-specific awareness handlers,
following A2A (Agent-to-Agent), MCP (Multi-Context Protocol), and SmolAgents patterns.
"""
import os
import sys
import platform
import pytest
from typing import Dict, Any
from src.app.platform_core.common.awareness import (
    BaseAwarenessHandler,
    AwarenessContext,
    AwarenessHandlerFactory
)

def test_awareness_handler_factory():
    """Test the awareness handler factory."""
    # Test supported platforms
    supported_platforms = AwarenessHandlerFactory.get_supported_platforms()
    assert isinstance(supported_platforms, list)
    assert platform.system() in supported_platforms
    
    # Test handler creation
    config: Dict[str, Any] = {}
    handler = AwarenessHandlerFactory.create_handler(config)
    assert isinstance(handler, BaseAwarenessHandler)
    
    # Test handler methods
    system_info = handler.get_system_awareness()
    assert isinstance(system_info, dict)
    assert 'os' in system_info
    assert 'memory' in system_info
    assert 'cpu' in system_info
    
    user_info = handler.get_user_awareness()
    assert isinstance(user_info, dict)
    assert 'username' in user_info
    assert 'home_dir' in user_info
    
    environment_info = handler.get_environment_awareness()
    assert isinstance(environment_info, dict)
    assert 'python_version' in environment_info
    assert 'working_directory' in environment_info
    
    # Test context updates
    context = AwarenessContext(
        system_info=system_info,
        user_info=user_info,
        environment_info=environment_info,
        agent_state={}
    )
    handler.update_context(context)
    assert handler.get_context() == context

def test_awareness_context():
    """Test the awareness context."""
    context = AwarenessContext(
        system_info={'os': platform.system()},
        user_info={'username': os.getlogin()},
        environment_info={'python_version': sys.version},
        agent_state={'status': 'active'}
    )
    
    assert isinstance(context.system_info, dict)
    assert isinstance(context.user_info, dict)
    assert isinstance(context.environment_info, dict)
    assert isinstance(context.agent_state, dict)
    
    assert 'os' in context.system_info
    assert 'username' in context.user_info
    assert 'python_version' in context.environment_info
    assert 'status' in context.agent_state

def test_platform_specific_info():
    """Test platform-specific information."""
    config: Dict[str, Any] = {}
    handler = AwarenessHandlerFactory.create_handler(config)
    
    system_info = handler.get_system_awareness()
    if platform.system() == 'Windows':
        assert 'os_version' in system_info
        assert 'os_release' in system_info
    elif platform.system() == 'Linux':
        assert 'ubuntu_version' in system_info
        assert 'kernel_version' in system_info
    elif platform.system() == 'Darwin':
        assert 'macos_version' in system_info
        assert 'model' in system_info
    
    user_info = handler.get_user_awareness()
    if platform.system() == 'Windows':
        assert 'user_domain' in user_info
        assert 'user_profile' in user_info
    elif platform.system() in ('Linux', 'Darwin'):
        assert 'user_id' in user_info
        assert 'group_id' in user_info
        assert 'shell' in user_info
        assert 'groups' in user_info
    
    environment_info = handler.get_environment_awareness()
    assert 'python_version' in environment_info
    assert 'python_executable' in environment_info
    assert 'working_directory' in environment_info
    assert 'environment_variables' in environment_info
    assert 'path' in environment_info 