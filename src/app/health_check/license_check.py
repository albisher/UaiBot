import logging
import json
import os
from typing import Dict, Any
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class LicenseHealthCheck:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.license_path = os.path.join(self.platform_info['paths']['config'], 'license.json')

    def check_license_health(self) -> Dict[str, Any]:
        """Check license health status"""
        try:
            health_status = {
                'platform': self.platform_info['name'],
                'status': 'healthy',
                'license_info': {}
            }

            if not os.path.exists(self.license_path):
                health_status['status'] = 'error'
                health_status['license_info'] = {
                    'error': 'License file not found'
                }
                return health_status

            with open(self.license_path, 'r') as f:
                license_data = json.load(f)

            # Validate license data
            required_fields = ['license_key', 'expiry_date', 'features']
            for field in required_fields:
                if field not in license_data:
                    health_status['status'] = 'error'
                    health_status['license_info'] = {
                        'error': f'Missing required field: {field}'
                    }
                    return health_status

            health_status['license_info'] = {
                'license_key': license_data['license_key'],
                'expiry_date': license_data['expiry_date'],
                'features': license_data['features']
            }

            return health_status

        except Exception as e:
            logger.error(f"Error checking license health: {str(e)}")
            return {
                'platform': self.platform_info['name'],
                'status': 'error',
                'error': str(e)
            }

    def get_license_info(self) -> Dict[str, Any]:
        """Get detailed license information"""
        return self.check_license_health()['license_info'] 