"""Update folder health check module.

This module checks the health and accessibility of update folders configured for the platform, ensuring paths exist, are directories, and have proper permissions.
"""

import logging
import os
from typing import Dict, Any, List
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class UpdateFolderHealthCheck:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()

    def check_update_folders(self) -> Dict[str, Any]:
        """Check update folders health status"""
        try:
            health_status = {
                'platform': self.platform_info['name'],
                'status': 'healthy',
                'update_folders': {}
            }

            # Get update paths from platform info
            update_paths = self.platform_info['paths'].get('updates', [])
            if not update_paths:
                health_status['status'] = 'error'
                health_status['update_folders'] = {
                    'error': 'No update paths configured'
                }
                return health_status

            # Check each update path
            for path in update_paths:
                if not os.path.exists(path):
                    health_status['update_folders'][path] = {
                        'status': 'error',
                        'error': 'Path does not exist'
                    }
                    continue

                if not os.path.isdir(path):
                    health_status['update_folders'][path] = {
                        'status': 'error',
                        'error': 'Path is not a directory'
                    }
                    continue

                # Check directory permissions
                if not os.access(path, os.R_OK | os.W_OK):
                    health_status['update_folders'][path] = {
                        'status': 'error',
                        'error': 'Insufficient permissions'
                    }
                    continue

                # Get directory contents
                try:
                    contents = os.listdir(path)
                    health_status['update_folders'][path] = {
                        'status': 'healthy',
                        'contents': contents
                    }
                except Exception as e:
                    health_status['update_folders'][path] = {
                        'status': 'error',
                        'error': str(e)
                    }

            return health_status

        except Exception as e:
            logger.error(f"Error checking update folders: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'status': 'error',
                'error': str(e)
            }

    def get_update_folders(self) -> Dict[str, Any]:
        """Get detailed update folders information"""
        return self.check_update_folders()['update_folders'] 