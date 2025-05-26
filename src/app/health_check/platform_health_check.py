import sys
import logging
from typing import Dict, Any
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class PlatformHealthCheck:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()

    def check_platform_health(self) -> Dict[str, Any]:
        """Check platform-specific health status"""
        try:
            health_status = {
                'platform': self.platform_info['name'],
                'version': self.platform_info['version'],
                'status': 'healthy',
                'handlers': {}
            }

            # Check each handler's health
            for handler_name, handler in self.platform_manager.get_handlers().items():
                try:
                    handler_health = handler.check_health()
                    health_status['handlers'][handler_name] = handler_health
                except Exception as e:
                    logger.error(f"Error checking health for handler {handler_name}: {str(e)}")
                    health_status['handlers'][handler_name] = {
                        'status': 'error',
                        'error': str(e)
                    }

            return health_status

        except Exception as e:
            logger.error(f"Error checking platform health: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'status': 'error',
                'error': str(e)
            }

    def get_platform_info(self) -> Dict[str, Any]:
        """Get detailed platform information"""
        return self.platform_info

def check_platform_health():
    """Check platform-specific health status."""
    platform_manager = PlatformManager()
    platform_info = platform_manager.get_platform_info()
    
    print("--- Platform-Specific Health Check ---")
    print(f"Platform: {platform_info['name']}")
    print(f"System: {platform_info['system']}")
    print(f"Architecture: {platform_info['architecture']}")
    
    # Check platform-specific requirements
    if platform_info['name'] == 'mac':
        check_mac_requirements(platform_info)
    elif platform_info['name'] == 'windows':
        check_windows_requirements(platform_info)
    elif platform_info['name'] == 'ubuntu':
        check_ubuntu_requirements(platform_info)
    else:
        print("Unknown or unsupported platform.")

def check_mac_requirements(platform_info):
    """Check macOS-specific requirements."""
    print("\nChecking macOS requirements...")
    # Add macOS-specific checks here

def check_windows_requirements(platform_info):
    """Check Windows-specific requirements."""
    print("\nChecking Windows requirements...")
    # Add Windows-specific checks here

def check_ubuntu_requirements(platform_info):
    """Check Ubuntu-specific requirements."""
    print("\nChecking Ubuntu requirements...")
    # Add Ubuntu-specific checks here

if __name__ == "__main__":
    check_platform_health() 