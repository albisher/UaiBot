import logging
import psutil
from typing import Dict, Any
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class SystemInfoHealthCheck:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()

    def check_system_health(self) -> Dict[str, Any]:
        """Check system health status"""
        try:
            health_status = {
                'platform': self.platform_info['name'],
                'version': self.platform_info['version'],
                'status': 'healthy',
                'system_info': {}
            }

            # Get CPU information
            cpu_info = {
                'usage_percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
            health_status['system_info']['cpu'] = cpu_info

            # Get memory information
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
            health_status['system_info']['memory'] = memory_info

            # Get disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            }
            health_status['system_info']['disk'] = disk_info

            # Get network information
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            health_status['system_info']['network'] = network_info

            return health_status

        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'status': 'error',
                'error': str(e)
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        return self.check_system_health()['system_info']

def check_system_health():
    """Check overall system health."""
    system_info = get_system_info()
    print("\n--- System Health Check ---")
    print(f"Operating System: {system_info['os']}")
    print(f"Platform: {system_info['platform']}")
    print(f"Architecture: {system_info['architecture']}")
    print(f"Python Version: {system_info['python_version']}")
    
    # Check available features
    print("\nAvailable Features:")
    for feature, status in system_info['features'].items():
        print(f"- {feature}: {'Enabled' if status.get('enabled', False) else 'Disabled'}")
    
    # Check paths
    print("\nSystem Paths:")
    for path_type, path in system_info['paths'].items():
        print(f"- {path_type}: {path}")

if __name__ == "__main__":
    check_system_health() 