#!/usr/bin/env python3
# test_system_info.py

import sys
import os
import unittest
from unittest import mock
import platform

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from uaibot.core.ai_handler import get_system_info

class TestSystemInfo(unittest.TestCase):
    
    def test_actual_system_info(self):
        """Test the function with the actual system."""
        system_info = get_system_info()
        print(f"\nActual system info: {system_info}")
        # Basic validation - should contain system type and shell information
        self.assertIsInstance(system_info, str)
        self.assertTrue("shell" in system_info)
        
    @mock.patch('platform.system')
    @mock.patch('platform.platform')
    @mock.patch('platform.machine')
    @mock.patch('platform.processor')
    @mock.patch('platform.version')
    @mock.patch('os.environ.get')
    @mock.patch('platform.mac_ver')
    @mock.patch('subprocess.check_output')
    def test_macos(self, mock_check_output, mock_mac_ver, mock_environ_get, 
                  mock_version, mock_processor, mock_machine, mock_platform, mock_system):
        """Test macOS detection and formatting."""
        # Setup mocks
        mock_system.return_value = "Darwin"
        mock_platform.return_value = "Darwin-20.6.0-x86_64-i386-64bit"
        mock_machine.return_value = "x86_64"
        mock_processor.return_value = "i386"
        mock_version.return_value = "Darwin Kernel Version 20.6.0"
        mock_environ_get.return_value = "/bin/zsh"
        mock_mac_ver.return_value = ("12.0.1", ("", "", ""), "")
        mock_check_output.return_value = b"MacBookPro16,1"
        
        system_info = get_system_info()
        print(f"\nMocked macOS info: {system_info}")
        
        # Assertions
        self.assertIn("macOS", system_info)
        self.assertIn("Monterey", system_info)
        self.assertIn("MacBookPro16,1", system_info)
        self.assertIn("zsh", system_info)

    @mock.patch('platform.system')
    @mock.patch('platform.platform')
    @mock.patch('platform.machine')
    @mock.patch('platform.processor')
    @mock.patch('platform.version')
    @mock.patch('os.environ.get')
    @mock.patch('platform.win32_ver')
    @mock.patch('subprocess.check_output')
    def test_windows(self, mock_check_output, mock_win32_ver, mock_environ_get, 
                    mock_version, mock_processor, mock_machine, mock_platform, mock_system):
        """Test Windows detection and formatting."""
        # Setup mocks
        mock_system.return_value = "Windows"
        mock_platform.return_value = "Windows-10-10.0.19041-SP0"
        mock_machine.return_value = "AMD64"
        mock_processor.return_value = "Intel64 Family 6 Model 142 Stepping 12, GenuineIntel"
        mock_version.return_value = "10.0.19041"
        mock_environ_get.return_value = "cmd.exe"
        mock_win32_ver.return_value = ("10", "10.0.19041", "SP0", "")
        mock_check_output.return_value = b"Microsoft Windows 10 Pro\r\n"
        
        system_info = get_system_info()
        print(f"\nMocked Windows info: {system_info}")
        
        # Assertions
        self.assertIn("Windows", system_info)
        self.assertIn("10", system_info)
        self.assertIn("Pro", system_info)
        self.assertIn("cmd", system_info)

    @mock.patch('platform.system')
    @mock.patch('platform.platform')
    @mock.patch('platform.machine')
    @mock.patch('platform.processor')
    @mock.patch('platform.version')
    @mock.patch('os.environ.get')
    @mock.patch('os.path.exists')
    @mock.patch('builtins.open')
    @mock.patch('subprocess.run')
    def test_linux_ubuntu(self, mock_run, mock_open, mock_exists, mock_environ_get,
                         mock_version, mock_processor, mock_machine, mock_platform, mock_system):
        """Test Linux (Ubuntu) detection and formatting."""
        # Setup mocks
        mock_system.return_value = "Linux"
        mock_platform.return_value = "Linux-5.4.0-94-generic-x86_64-with-Ubuntu-20.04-focal"
        mock_machine.return_value = "x86_64"
        mock_processor.return_value = "x86_64"
        mock_version.return_value = "#106-Ubuntu SMP Thu Jan 20 12:02:19 UTC 2022"
        mock_environ_get.return_value = "/bin/bash"
        
        # Mock os.path.exists for /etc/os-release but not for Raspberry Pi
        mock_exists.side_effect = lambda path: path == '/etc/os-release'
        
        # Mock file reading for os-release
        mock_file = mock.MagicMock()
        mock_file.__enter__.return_value.read.return_value = 'PRETTY_NAME="Ubuntu 20.04.3 LTS"'
        mock_open.return_value = mock_file
        
        # Mock subprocess for Jetson check (negative)
        mock_run.return_value.returncode = 1
        
        system_info = get_system_info()
        print(f"\nMocked Linux (Ubuntu) info: {system_info}")
        
        # Assertions
        self.assertIn("Ubuntu 20.04.3 LTS", system_info)
        self.assertIn("x86_64", system_info)
        self.assertIn("bash", system_info)

    @mock.patch('platform.system')
    @mock.patch('platform.platform')
    @mock.patch('platform.machine')
    @mock.patch('platform.processor')
    @mock.patch('platform.version')
    @mock.patch('os.environ.get')
    @mock.patch('os.path.exists')
    @mock.patch('builtins.open')
    @mock.patch('subprocess.run')
    def test_raspberry_pi(self, mock_run, mock_open, mock_exists, mock_environ_get,
                         mock_version, mock_processor, mock_machine, mock_platform, mock_system):
        """Test Raspberry Pi detection and formatting."""
        # Setup mocks
        mock_system.return_value = "Linux"
        mock_platform.return_value = "Linux-5.10.103-v8-aarch64-with-debian-11.3"
        mock_machine.return_value = "aarch64"
        mock_processor.return_value = "aarch64"
        mock_version.return_value = "#1 SMP Debian 5.10.103-2"
        mock_environ_get.return_value = "/bin/bash"
        
        # Mock both os-release and device-tree/model exist
        mock_exists.side_effect = lambda path: path in ['/etc/os-release', '/proc/device-tree/model']
        
        # Mock file reading - implement a custom side_effect
        def mock_file_read(path):
            mock_f = mock.MagicMock()
            if path == '/etc/os-release':
                mock_f.__enter__.return_value.read.return_value = 'PRETTY_NAME="Raspberry Pi OS 11 (bullseye)"'
            elif path == '/proc/device-tree/model':
                mock_f.__enter__.return_value.read.return_value = 'Raspberry Pi 4 Model B Rev 1.2'
            return mock_f
        mock_open.side_effect = mock_file_read
        
        # Mock subprocess for Jetson check (negative)
        mock_run.return_value.returncode = 1
        
        system_info = get_system_info()
        print(f"\nMocked Raspberry Pi info: {system_info}")
        
        # Assertions
        self.assertIn("Raspberry Pi OS 11", system_info)
        self.assertIn("Raspberry Pi 4 Model B", system_info)
        self.assertIn("bash", system_info)

    @mock.patch('platform.system')
    @mock.patch('platform.platform')
    @mock.patch('platform.machine')
    @mock.patch('platform.processor')
    @mock.patch('platform.version')
    @mock.patch('os.environ.get')
    def test_unknown_system(self, mock_environ_get, mock_version, mock_processor, 
                           mock_machine, mock_platform, mock_system):
        """Test handling of unknown/unsupported systems."""
        # Setup mocks
        mock_system.return_value = "FreeBSD"
        mock_platform.return_value = "FreeBSD-13.1-RELEASE-amd64-64bit"
        mock_machine.return_value = "amd64"
        mock_processor.return_value = "amd64"
        mock_version.return_value = "FreeBSD 13.1-RELEASE releng"
        mock_environ_get.return_value = "/usr/local/bin/tcsh"
        
        system_info = get_system_info()
        print(f"\nMocked FreeBSD info: {system_info}")
        
        # Assertions
        self.assertIn("FreeBSD", system_info)
        self.assertIn("amd64", system_info)
        self.assertIn("tcsh", system_info)

if __name__ == '__main__':
    unittest.main()
