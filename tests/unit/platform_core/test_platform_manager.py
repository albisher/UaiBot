"""
Tests for platform manager functionality.
"""
import pytest
import os
import platform
from src.app.platform_core.platform_manager import (
    PlatformManager,
    get_platform_system_info_gatherer
)
from src.app.platform_core.common.system_info import BaseSystemInfoGatherer
from src.app.platform_core.mac.system_info import MacSystemInfoGatherer
from src.app.platform_core.windows.system_info import WindowsSystemInfoGatherer
from src.app.platform_core.ubuntu.system_info import UbuntuSystemInfoGatherer

@pytest.fixture
def platform_manager():
    """Create a platform manager instance for testing."""
    return PlatformManager()

def test_platform_detection(platform_manager):
    """Test platform detection functionality."""
    # Test platform detection
    platform_name = platform_manager.get_platform()
    assert platform_name in ['macos', 'ubuntu', 'windows', 'unknown']
    
    # Test platform support check
    assert platform_manager.is_platform_supported() == (platform_name != 'unknown')

def test_system_info_gatherer():
    """Test system info gatherer factory method."""
    # Get the appropriate gatherer for current platform
    gatherer = get_platform_system_info_gatherer()
    
    # Check that we got the right type of gatherer
    if platform.system() == 'Darwin':
        assert isinstance(gatherer, MacSystemInfoGatherer)
    elif platform.system() == 'Windows':
        assert isinstance(gatherer, WindowsSystemInfoGatherer)
    elif platform.system() == 'Linux':
        assert isinstance(gatherer, UbuntuSystemInfoGatherer)
    else:
        pytest.skip("Unsupported platform for testing")
    
    # Check that it's a valid system info gatherer
    assert isinstance(gatherer, BaseSystemInfoGatherer)

def test_system_info_retrieval():
    """Test system information retrieval."""
    # Get system info
    info = PlatformManager.get_system_info()
    
    # Check that we got a dictionary
    assert isinstance(info, dict)
    
    # Check that it contains expected keys
    assert 'platform' in info
    assert 'cpu' in info
    assert 'memory' in info
    assert 'disk' in info
    assert 'network' in info
    
    # Check platform info
    platform_info = info['platform']
    assert 'system' in platform_info
    assert 'release' in platform_info
    assert 'version' in platform_info
    assert 'machine' in platform_info
    assert 'processor' in platform_info
    
    # Check CPU info
    cpu_info = info['cpu']
    assert 'physical_cores' in cpu_info
    assert 'total_cores' in cpu_info
    assert 'max_frequency' in cpu_info
    assert 'min_frequency' in cpu_info
    assert 'current_frequency' in cpu_info
    assert 'cpu_usage_per_core' in cpu_info
    assert 'total_cpu_usage' in cpu_info
    
    # Check memory info
    memory_info = info['memory']
    assert 'total' in memory_info
    assert 'available' in memory_info
    assert 'used' in memory_info
    assert 'percentage' in memory_info
    
    # Check disk info
    disk_info = info['disk']
    assert 'total' in disk_info
    assert 'used' in disk_info
    assert 'free' in disk_info
    assert 'percentage' in disk_info
    
    # Check network info
    network_info = info['network']
    assert 'bytes_sent' in network_info
    assert 'bytes_received' in network_info
    assert 'packets_sent' in network_info
    assert 'packets_received' in network_info

def test_localized_system_info():
    """Test localized system information retrieval."""
    # Test with English
    en_info = PlatformManager.get_system_info('en')
    assert isinstance(en_info, dict)
    
    # Test with Arabic
    ar_info = PlatformManager.get_system_info('ar')
    assert isinstance(ar_info, dict)
    
    # Test with Saudi Arabic
    ar_sa_info = PlatformManager.get_system_info('ar-SA')
    assert isinstance(ar_sa_info, dict)
    
    # Test with unsupported language (should fallback to English)
    fallback_info = PlatformManager.get_system_info('xx')
    assert isinstance(fallback_info, dict)

def test_platform_info(platform_manager):
    """Test platform information retrieval."""
    info = platform_manager.get_platform_info()
    
    # Check that we got a dictionary
    assert isinstance(info, dict)
    
    # Check that it contains expected keys
    assert 'name' in info
    assert 'system' in info
    assert 'release' in info
    assert 'version' in info
    assert 'machine' in info
    assert 'processor' in info
    assert 'python_version' in info
    assert 'handlers' in info
    
    # Check platform-specific information
    if platform_manager.get_platform() == 'macos':
        assert 'mac_version' in info
    elif platform_manager.get_platform() == 'windows':
        assert 'windows_edition' in info

def test_config_management(platform_manager, tmp_path):
    """Test platform configuration management."""
    # Test initial config
    initial_config = platform_manager.get_config()
    assert isinstance(initial_config, dict)
    
    # Test config update
    new_config = {
        'test_key': 'test_value',
        'nested': {
            'key': 'value'
        }
    }
    assert platform_manager.update_config(new_config)
    
    # Verify config was updated
    updated_config = platform_manager.get_config()
    assert updated_config['test_key'] == 'test_value'
    assert updated_config['nested']['key'] == 'value'

def test_handler_management(platform_manager):
    """Test platform handler management."""
    # Get available handlers
    handlers = platform_manager.get_available_handlers()
    assert isinstance(handlers, list)
    
    # Test handler availability check
    for handler_type in handlers:
        assert platform_manager.is_handler_available(handler_type)
    
    # Test getting a handler
    if handlers:
        handler = platform_manager.get_handler(handlers[0])
        assert handler is not None
        assert handler.is_available()
    
    # Test getting non-existent handler
    assert platform_manager.get_handler('non_existent_handler') is None 