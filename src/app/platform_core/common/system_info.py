from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import psutil
import platform
from ..i18n import gettext as _

class BaseSystemInfoGatherer(ABC):
    """Base class for gathering system information across platforms."""
    
    @abstractmethod
    def get_system_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get system information for the current platform.
        
        Args:
            language: Optional language code for localized labels
            
        Returns:
            Dict[str, Any]: Dictionary containing system information
        """
        pass
    
    def get_common_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get common system information available on all platforms.
        
        Args:
            language: Optional language code for localized labels
            
        Returns:
            Dict[str, Any]: Dictionary containing common system information
        """
        return {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
            },
            'cpu': {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                'cpu_usage_per_core': [x for x in psutil.cpu_percent(percpu=True, interval=1)],
                'total_cpu_usage': psutil.cpu_percent(interval=1),
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used,
                'percentage': psutil.virtual_memory().percent,
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percentage': psutil.disk_usage('/').percent,
            },
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_received': psutil.net_io_counters().bytes_recv,
                'packets_sent': psutil.net_io_counters().packets_sent,
                'packets_received': psutil.net_io_counters().packets_recv,
            },
        }
    
    def get_localized_system_info(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get system information with localized labels.
        
        Args:
            language: Optional language code for localized labels
            
        Returns:
            Dict[str, Any]: Dictionary containing system information with localized labels
        """
        info = self.get_system_info(language)
        return {
            _('platform_info', language): info['platform'],
            _('cpu_info', language): info['cpu'],
            _('memory_info', language): info['memory'],
            _('disk_info', language): info['disk'],
            _('network_info', language): info['network'],
        } 