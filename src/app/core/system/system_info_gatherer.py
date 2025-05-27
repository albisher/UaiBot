import logging
import psutil
from typing import Dict, Any
from labeeb.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class SystemInfoGatherer:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()

    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        try:
            system_info = {
                'platform': self.platform_info['name'],
                'version': self.platform_info['version'],
                'system': {}
            }

            # Get CPU information
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'usage_percent': psutil.cpu_percent(interval=1)
            }
            system_info['system']['cpu'] = cpu_info

            # Get memory information
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
            system_info['system']['memory'] = memory_info

            # Get disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
            system_info['system']['disk'] = disk_info

            # Get network information
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'error_in': network.errin,
                'error_out': network.errout,
                'drop_in': network.dropin,
                'drop_out': network.dropout
            }
            system_info['system']['network'] = network_info

            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            system_info['system']['processes'] = processes

            # Get platform-specific information
            if self.platform_info['name'] == 'mac':
                system_info['system']['mac_specific'] = self._get_mac_specific_info()
            elif self.platform_info['name'] == 'windows':
                system_info['system']['windows_specific'] = self._get_windows_specific_info()
            elif self.platform_info['name'] == 'ubuntu':
                system_info['system']['ubuntu_specific'] = self._get_ubuntu_specific_info()

            return system_info

        except Exception as e:
            logger.error(f"Error gathering system info: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'error': str(e)
            }

    def _get_mac_specific_info(self) -> Dict[str, Any]:
        """Get macOS-specific system information"""
        try:
            return {
                'kernel_version': self.platform_info['version'],
                'architecture': self.platform_info['architecture'],
                'python_version': self.platform_info['python_version']
            }
        except Exception as e:
            logger.error(f"Error getting macOS specific info: {str(e)}")
            return {'error': str(e)}

    def _get_windows_specific_info(self) -> Dict[str, Any]:
        """Get Windows-specific system information"""
        try:
            return {
                'kernel_version': self.platform_info['version'],
                'architecture': self.platform_info['architecture'],
                'python_version': self.platform_info['python_version']
            }
        except Exception as e:
            logger.error(f"Error getting Windows specific info: {str(e)}")
            return {'error': str(e)}

    def _get_ubuntu_specific_info(self) -> Dict[str, Any]:
        """Get Ubuntu-specific system information"""
        try:
            return {
                'kernel_version': self.platform_info['version'],
                'architecture': self.platform_info['architecture'],
                'python_version': self.platform_info['python_version']
            }
        except Exception as e:
            logger.error(f"Error getting Ubuntu specific info: {str(e)}")
            return {'error': str(e)} 