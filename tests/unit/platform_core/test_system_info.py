"""
Tests for platform-specific system information gatherers.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.app.platform_core.common.system_info import BaseSystemInfoGatherer
from src.app.platform_core.mac.system_info import MacSystemInfoGatherer
from src.app.platform_core.windows.system_info import WindowsSystemInfoGatherer
from src.app.platform_core.ubuntu.system_info import UbuntuSystemInfoGatherer
import platform
import psutil

@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for testing."""
    with patch('subprocess.run') as mock:
        yield mock

class TestBaseSystemInfoGatherer:
    """Tests for the base system information gatherer."""
    
    def test_get_common_info(self):
        """Test that common info contains all expected fields."""
        gatherer = BaseSystemInfoGatherer()
        info = gatherer.get_common_info()
        
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

class TestMacSystemInfoGatherer:
    """Tests for the macOS system information gatherer."""
    
    def test_get_system_info(self, mock_subprocess):
        """Test getting macOS system information."""
        # Mock subprocess responses
        mock_subprocess.side_effect = [
            MagicMock(stdout="10.15.7\n", returncode=0),  # sw_vers
            MagicMock(stdout="19.6.0\n", returncode=0),   # uname
            MagicMock(stdout="1234567890\n", returncode=0), # sysctl
            MagicMock(stdout="macbook-pro\n", returncode=0)  # hostname
        ]
        
        gatherer = MacSystemInfoGatherer()
        info = gatherer.get_system_info()
        
        # Check platform-specific info
        platform_info = info['platform']
        assert platform_info['macos_version'] == "10.15.7"
        assert platform_info['kernel_version'] == "19.6.0"
        assert platform_info['boot_time'] == "1234567890"
        assert platform_info['hostname'] == "macbook-pro"
        
        # Verify subprocess calls
        mock_subprocess.assert_any_call(['sw_vers', '-productVersion'], 
                                      capture_output=True, text=True, check=True)
        mock_subprocess.assert_any_call(['uname', '-r'], 
                                      capture_output=True, text=True, check=True)
        mock_subprocess.assert_any_call(['sysctl', '-n', 'kern.boottime'], 
                                      capture_output=True, text=True, check=True)
        mock_subprocess.assert_any_call(['hostname'], 
                                      capture_output=True, text=True, check=True)

class TestWindowsSystemInfoGatherer:
    """Tests for the Windows system information gatherer."""
    
    def test_get_system_info(self, mock_subprocess):
        """Test getting Windows system information."""
        # Mock subprocess responses
        mock_subprocess.side_effect = [
            MagicMock(stdout="REG_SZ    Windows 10 Pro\n", returncode=0),  # reg query ProductName
            MagicMock(stdout="REG_SZ    Professional\n", returncode=0),     # reg query EditionID
            MagicMock(stdout="REG_SZ    19045\n", returncode=0),           # reg query CurrentBuildNumber
            MagicMock(stdout="windows-pc\n", returncode=0)                 # hostname
        ]
        
        gatherer = WindowsSystemInfoGatherer()
        info = gatherer.get_system_info()
        
        # Check platform-specific info
        platform_info = info['platform']
        assert platform_info['windows_version'] == "Windows 10 Pro"
        assert platform_info['edition'] == "Professional"
        assert platform_info['build_number'] == "19045"
        assert platform_info['hostname'] == "windows-pc"
        
        # Verify subprocess calls
        mock_subprocess.assert_any_call(
            ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'ProductName'],
            capture_output=True, text=True, check=True
        )
        mock_subprocess.assert_any_call(
            ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'EditionID'],
            capture_output=True, text=True, check=True
        )
        mock_subprocess.assert_any_call(
            ['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion', '/v', 'CurrentBuildNumber'],
            capture_output=True, text=True, check=True
        )
        mock_subprocess.assert_any_call(['hostname'], 
                                      capture_output=True, text=True, check=True)

class TestUbuntuSystemInfoGatherer:
    """Tests for the Ubuntu system information gatherer."""
    
    def test_get_system_info(self, mock_subprocess):
        """Test getting Ubuntu system information."""
        # Mock subprocess responses
        mock_subprocess.side_effect = [
            MagicMock(stdout="Description:    Ubuntu 22.04.1 LTS\n", returncode=0),  # lsb_release
            MagicMock(stdout="5.15.0-56-generic\n", returncode=0),                  # uname
            MagicMock(stdout="2023-01-01 00:00:00\n", returncode=0),               # uptime
            MagicMock(stdout="ubuntu-pc\n", returncode=0)                           # hostname
        ]
        
        gatherer = UbuntuSystemInfoGatherer()
        info = gatherer.get_system_info()
        
        # Check platform-specific info
        platform_info = info['platform']
        assert platform_info['ubuntu_version'] == "Ubuntu 22.04.1 LTS"
        assert platform_info['kernel_version'] == "5.15.0-56-generic"
        assert platform_info['boot_time'] == "2023-01-01 00:00:00"
        assert platform_info['hostname'] == "ubuntu-pc"
        
        # Verify subprocess calls
        mock_subprocess.assert_any_call(['lsb_release', '-d'], 
                                      capture_output=True, text=True, check=True)
        mock_subprocess.assert_any_call(['uname', '-r'], 
                                      capture_output=True, text=True, check=True)
        mock_subprocess.assert_any_call(['uptime', '-s'], 
                                      capture_output=True, text=True, check=True)
        mock_subprocess.assert_any_call(['hostname'], 
                                      capture_output=True, text=True, check=True)

class MockSystemInfoGatherer(BaseSystemInfoGatherer):
    """Mock system info gatherer for testing."""
    
    def get_system_info(self, language=None):
        """Get mock system information."""
        return {
            'platform': {
                'system': 'TestOS',
                'release': '1.0',
                'version': 'Test Version',
                'machine': 'test-machine',
                'processor': 'test-processor'
            }
        }

@pytest.fixture
def mock_gatherer():
    """Create a mock system info gatherer for testing."""
    return MockSystemInfoGatherer()

def test_base_system_info_gatherer():
    """Test base system info gatherer functionality."""
    # Test that base class is abstract
    with pytest.raises(TypeError):
        BaseSystemInfoGatherer()
    
    # Test that mock implementation works
    gatherer = MockSystemInfoGatherer()
    info = gatherer.get_system_info()
    assert isinstance(info, dict)
    assert 'platform' in info

def test_common_info_retrieval(mock_gatherer):
    """Test common system information retrieval."""
    # Get common info
    info = mock_gatherer.get_common_info()
    
    # Check that we got a dictionary
    assert isinstance(info, dict)
    
    # Check platform info
    platform_info = info['platform']
    assert 'system' in platform_info
    assert 'release' in platform_info
    assert 'version' in platform_info
    assert 'machine' in platform_info
    assert 'processor' in platform_info
    
    # Verify platform info matches system
    assert platform_info['system'] == platform.system()
    assert platform_info['release'] == platform.release()
    assert platform_info['version'] == platform.version()
    assert platform_info['machine'] == platform.machine()
    assert platform_info['processor'] == platform.processor()
    
    # Check CPU info
    cpu_info = info['cpu']
    assert 'physical_cores' in cpu_info
    assert 'total_cores' in cpu_info
    assert 'max_frequency' in cpu_info
    assert 'min_frequency' in cpu_info
    assert 'current_frequency' in cpu_info
    assert 'cpu_usage_per_core' in cpu_info
    assert 'total_cpu_usage' in cpu_info
    
    # Verify CPU info
    assert isinstance(cpu_info['physical_cores'], int)
    assert isinstance(cpu_info['total_cores'], int)
    assert cpu_info['physical_cores'] <= cpu_info['total_cores']
    
    # Check memory info
    memory_info = info['memory']
    assert 'total' in memory_info
    assert 'available' in memory_info
    assert 'used' in memory_info
    assert 'percentage' in memory_info
    
    # Verify memory info
    assert isinstance(memory_info['total'], int)
    assert isinstance(memory_info['available'], int)
    assert isinstance(memory_info['used'], int)
    assert isinstance(memory_info['percentage'], float)
    assert 0 <= memory_info['percentage'] <= 100
    
    # Check disk info
    disk_info = info['disk']
    assert 'total' in disk_info
    assert 'used' in disk_info
    assert 'free' in disk_info
    assert 'percentage' in disk_info
    
    # Verify disk info
    assert isinstance(disk_info['total'], int)
    assert isinstance(disk_info['used'], int)
    assert isinstance(disk_info['free'], int)
    assert isinstance(disk_info['percentage'], float)
    assert 0 <= disk_info['percentage'] <= 100
    
    # Check network info
    network_info = info['network']
    assert 'bytes_sent' in network_info
    assert 'bytes_received' in network_info
    assert 'packets_sent' in network_info
    assert 'packets_received' in network_info
    
    # Verify network info
    assert isinstance(network_info['bytes_sent'], int)
    assert isinstance(network_info['bytes_received'], int)
    assert isinstance(network_info['packets_sent'], int)
    assert isinstance(network_info['packets_received'], int)

def test_localized_system_info(mock_gatherer):
    """Test localized system information retrieval."""
    # Test with English
    en_info = mock_gatherer.get_localized_system_info('en')
    assert isinstance(en_info, dict)
    
    # Test with Arabic
    ar_info = mock_gatherer.get_localized_system_info('ar')
    assert isinstance(ar_info, dict)
    
    # Test with Saudi Arabic
    ar_sa_info = mock_gatherer.get_localized_system_info('ar-SA')
    assert isinstance(ar_sa_info, dict)
    
    # Test with unsupported language (should fallback to English)
    fallback_info = mock_gatherer.get_localized_system_info('xx')
    assert isinstance(fallback_info, dict)

def test_platform_specific_gatherers():
    """Test platform-specific system info gatherers."""
    # Get the appropriate gatherer for current platform
    if platform.system() == 'Darwin':
        gatherer = MacSystemInfoGatherer()
    elif platform.system() == 'Windows':
        gatherer = WindowsSystemInfoGatherer()
    elif platform.system() == 'Linux':
        gatherer = UbuntuSystemInfoGatherer()
    else:
        pytest.skip("Unsupported platform for testing")
    
    # Test system info retrieval
    info = gatherer.get_system_info()
    assert isinstance(info, dict)
    
    # Test platform-specific info
    if platform.system() == 'Darwin':
        assert 'macos_version' in info
        assert 'kernel_version' in info
        assert 'boot_time' in info
        assert 'hostname' in info
    elif platform.system() == 'Windows':
        assert 'windows_version' in info
        assert 'edition' in info
        assert 'build_number' in info
        assert 'hostname' in info
    elif platform.system() == 'Linux':
        assert 'ubuntu_version' in info
        assert 'kernel_version' in info
        assert 'boot_time' in info
        assert 'hostname' in info 