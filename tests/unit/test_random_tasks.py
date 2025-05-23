"""Test suite for random system tasks."""

import pytest
import logging
from pathlib import Path
from typing import Dict, List, Optional
import psutil
import os
import json
from datetime import datetime

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemTaskTester:
    """Test class for system-related tasks."""
    
    def __init__(self):
        """Initialize the system task tester."""
        self.results: Dict[str, bool] = {}
        self.error_log: List[str] = []
        
    def test_disk_operations(self) -> Dict[str, bool]:
        """Test disk-related operations."""
        results = {}
        try:
            # Test disk partitions
            partitions = psutil.disk_partitions()
            results["list_partitions"] = bool(partitions)
            
            # Test disk usage
            usage = psutil.disk_usage('/')
            results["check_usage"] = bool(usage)
            
            # Test temp files
            temp_dir = Path('/tmp')
            results["list_temp_files"] = temp_dir.exists()
            
        except Exception as e:
            logger.error(f"Disk operation test failed: {str(e)}")
            self.error_log.append(f"Disk operation error: {str(e)}")
            
        return results
    
    def test_memory_operations(self) -> Dict[str, bool]:
        """Test memory-related operations."""
        results = {}
        try:
            # Test memory info
            memory = psutil.virtual_memory()
            results["check_memory"] = bool(memory)
            
            # Test swap memory
            swap = psutil.swap_memory()
            results["check_swap"] = bool(swap)
            
        except Exception as e:
            logger.error(f"Memory operation test failed: {str(e)}")
            self.error_log.append(f"Memory operation error: {str(e)}")
            
        return results
    
    def test_process_operations(self) -> Dict[str, bool]:
        """Test process-related operations."""
        results = {}
        try:
            # Test process list
            processes = list(psutil.process_iter(['pid', 'name']))
            results["list_processes"] = bool(processes)
            
            # Test CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            results["check_cpu"] = isinstance(cpu_percent, float)
            
        except Exception as e:
            logger.error(f"Process operation test failed: {str(e)}")
            self.error_log.append(f"Process operation error: {str(e)}")
            
        return results
    
    def test_network_operations(self) -> Dict[str, bool]:
        """Test network-related operations."""
        results = {}
        try:
            # Test network interfaces
            net_if_addrs = psutil.net_if_addrs()
            results["list_interfaces"] = bool(net_if_addrs)
            
            # Test network connections
            net_connections = psutil.net_connections()
            results["list_connections"] = bool(net_connections)
            
        except Exception as e:
            logger.error(f"Network operation test failed: {str(e)}")
            self.error_log.append(f"Network operation error: {str(e)}")
            
        return results
    
    def test_file_operations(self) -> Dict[str, bool]:
        """Test file-related operations."""
        results = {}
        try:
            # Test file creation
            test_file = Path('test_file.txt')
            test_file.write_text('test')
            results["create_file"] = test_file.exists()
            
            # Test file reading
            content = test_file.read_text()
            results["read_file"] = content == 'test'
            
            # Cleanup
            test_file.unlink()
            results["delete_file"] = not test_file.exists()
            
        except Exception as e:
            logger.error(f"File operation test failed: {str(e)}")
            self.error_log.append(f"File operation error: {str(e)}")
            
        return results
    
    def run_all_tests(self) -> Dict[str, Dict[str, bool]]:
        """Run all system tests."""
        return {
            "disk": self.test_disk_operations(),
            "memory": self.test_memory_operations(),
            "process": self.test_process_operations(),
            "network": self.test_network_operations(),
            "file": self.test_file_operations()
        }

@pytest.fixture
def task_tester():
    """Create a system task tester instance."""
    return SystemTaskTester()

def test_disk_operations(task_tester):
    """Test disk operations."""
    results = task_tester.test_disk_operations()
    assert all(results.values()), "Some disk operations failed"
    
def test_memory_operations(task_tester):
    """Test memory operations."""
    results = task_tester.test_memory_operations()
    assert all(results.values()), "Some memory operations failed"
    
def test_process_operations(task_tester):
    """Test process operations."""
    results = task_tester.test_process_operations()
    assert all(results.values()), "Some process operations failed"
    
def test_network_operations(task_tester):
    """Test network operations."""
    results = task_tester.test_network_operations()
    assert all(results.values()), "Some network operations failed"
    
def test_file_operations(task_tester):
    """Test file operations."""
    results = task_tester.test_file_operations()
    assert all(results.values()), "Some file operations failed"
    
def test_all_operations(task_tester):
    """Test all system operations."""
    results = task_tester.run_all_tests()
    for category, category_results in results.items():
        assert all(category_results.values()), f"Some {category} operations failed" 