#!/usr/bin/env python3
# comprehensive_system_test.py

"""
A comprehensive test script for the get_system_info() function.
Tests detection of various operating systems and edge cases.
"""

import sys
import os
import platform
import unittest
from unittest import mock

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the function to test
from uaibot.core.ai_handler import get_system_info

class TestSystemInfo(unittest.TestCase):
    """Test cases for the get_system_info function."""
    
    def test_actual_system(self):
        """Test with the actual system."""
        result = get_system_info()
        print(f"\nActual system: {result}")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 10)  # Basic sanity check
    
    @mock.patch('platform.system', return_value='Darwin')
    @mock.patch('platform.platform', return_value='Darwin-21.6.0-x86_64-i386-64bit')
    @mock.patch('platform.machine', return_value='x86_64')
    @mock.patch('platform.processor', return_value='i386')
    @mock.patch('platform.version', return_value='Darwin Kernel Version 21.6.0')
    @mock.patch('os.environ.get', return_value='/bin/zsh')
    @mock.patch('platform.mac_ver', return_value=('12.6', ('', '', ''), ''))
    @mock.patch('subprocess.check_output', return_value=b'MacBookPro18,3')
    def test_macos(self, *mocks):
        """Test macOS detection."""
        result = get_system_info()
        print(f"\nmacOS: {result}")
        self.assertIn("macOS", result)
        self.assertIn("Monterey", result)
        self.assertIn("MacBookPro18,3", result)
        self.assertIn("zsh", result)

    @mock.patch('platform.system', return_value='Windows')
    @mock.patch('platform.platform', return_value='Windows-10-10.0.19041-SP0')
    @mock.patch('platform.machine', return_value='AMD64')
    @mock.patch('platform.processor', return_value='Intel64 Family 6')
    @mock.patch('platform.version', return_value='10.0.19041')
    @mock.patch('os.environ.get', return_value=None)
    @mock.patch('os.environ.__contains__', return_value=True)
    @mock.patch('os.environ.__getitem__', return_value='C:\\Windows\\System32\\cmd.exe')
    @mock.patch('platform.win32_ver', return_value=('10', '10.0.19041', 'SP0', ''))
    def test_windows(self, *mocks):
        """Test Windows detection."""
        result = get_system_info()
        print(f"\nWindows: {result}")
        self.assertIn("Windows", result)

    @mock.patch('platform.system', return_value='Linux')
    @mock.patch('platform.platform', return_value='Linux-5.15.0-generic-x86_64-with-glibc2.35')
    @mock.patch('platform.machine', return_value='x86_64')
    @mock.patch('platform.processor', return_value='x86_64')
    @mock.patch('platform.version', return_value='#1 SMP PREEMPT Ubuntu 5.15.0')
    @mock.patch('os.environ.get', return_value='/bin/bash')
    @mock.patch('os.path.exists', return_value=True)
    def test_linux_ubuntu(self, *mocks):
        """Test Linux (Ubuntu) detection."""
        with mock.patch('builtins.open', mock.mock_open(read_data='PRETTY_NAME="Ubuntu 22.04.2 LTS"')):
            result = get_system_info()
            print(f"\nLinux (Ubuntu): {result}")
            self.assertIn("Ubuntu", result)
            self.assertIn("bash", result)

    @mock.patch('platform.system', return_value='Linux')
    @mock.patch('platform.platform', return_value='Linux-5.15.0-generic-x86_64-with-glibc2.35')
    @mock.patch('platform.machine', return_value='x86_64')
    @mock.patch('platform.processor', return_value='x86_64')
    @mock.patch('platform.version', return_value='#1 SMP PREEMPT 5.15.0')
    @mock.patch('os.environ.get', return_value='/bin/bash')
    def test_linux_wsl(self, *mocks):
        """Test Linux on WSL detection."""
        # Mock the file checks for WSL detection
        orig_exists = os.path.exists
        
        def mock_exists(path):
            if path == '/proc/version':
                return True
            return False
        
        with mock.patch('os.path.exists', side_effect=mock_exists):
            with mock.patch('builtins.open', mock.mock_open(read_data='Linux version 5.15.0 (Microsoft@Microsoft.com)')):
                result = get_system_info()
                print(f"\nWSL: {result}")
                self.assertIn("Windows Subsystem for Linux", result)

    @mock.patch('platform.system', return_value='Linux')
    @mock.patch('platform.platform', return_value='Linux-5.10.0-aarch64-with-glibc2.33')
    @mock.patch('platform.machine', return_value='aarch64')
    @mock.patch('platform.processor', return_value='aarch64')
    @mock.patch('platform.version', return_value='#1 SMP ChromeOS 5.10.0')
    @mock.patch('os.environ.get', return_value='/bin/bash')
    def test_chromeos(self, *mocks):
        """Test ChromeOS detection."""
        # Mock the file checks for ChromeOS detection
        def mock_exists(path):
            if path == '/etc/os-release':
                return True
            return False
        
        with mock.patch('os.path.exists', side_effect=mock_exists):
            with mock.patch('builtins.open', mock.mock_open(read_data='PRETTY_NAME="ChromeOS 100"\nID=chromeos')):
                result = get_system_info()
                print(f"\nChromeOS: {result}")
                self.assertIn("Chrome OS", result)

    @mock.patch('platform.system', return_value='FreeBSD')
    @mock.patch('platform.platform', return_value='FreeBSD-13.2-RELEASE-amd64-64bit')
    @mock.patch('platform.machine', return_value='amd64')
    @mock.patch('platform.processor', return_value='amd64')
    @mock.patch('platform.version', return_value='13.2-RELEASE')
    @mock.patch('os.environ.get', return_value='/bin/csh')
    def test_freebsd(self, *mocks):
        """Test FreeBSD detection."""
        result = get_system_info()
        print(f"\nFreeBSD: {result}")
        self.assertIn("FreeBSD", result)
        self.assertIn("13.2", result)

    @mock.patch('platform.system', return_value='SunOS')
    @mock.patch('platform.platform', return_value='SunOS-5.11-sunos5-sparc')
    @mock.patch('platform.machine', return_value='sun4')
    @mock.patch('platform.processor', return_value='sparc')
    @mock.patch('platform.version', return_value='5.11')
    @mock.patch('os.environ.get', return_value='/bin/ksh')
    def test_solaris(self, *mocks):
        """Test Solaris detection."""
        result = get_system_info()
        print(f"\nSolaris: {result}")
        self.assertIn("Solaris", result)
        self.assertIn("5.11", result)

    @mock.patch('platform.system', return_value='AIX')
    @mock.patch('platform.platform', return_value='AIX-7.2-powerpc')
    @mock.patch('platform.machine', return_value='powerpc')
    @mock.patch('platform.processor', return_value='powerpc')
    @mock.patch('platform.version', return_value='7')
    @mock.patch('platform.release', return_value='2')
    @mock.patch('os.environ.get', return_value='/bin/ksh')
    def test_aix(self, *mocks):
        """Test AIX detection."""
        result = get_system_info()
        print(f"\nAIX: {result}")
        self.assertIn("AIX", result)
        self.assertIn("ksh", result)

    @mock.patch('platform.system', side_effect=Exception('Simulated error'))
    def test_error_handling(self, mock_system):
        """Test error handling when platform detection fails."""
        result = get_system_info()
        print(f"\nError case: {result}")
        self.assertIn("Unknown system", result)
        self.assertIn("Error", result)

if __name__ == '__main__':
    print("Running comprehensive system info tests...\n")
    unittest.main()
