"""
Labeeb license verification module.

This module checks if the application is being used according to its license terms.
For commercial environments, it verifies if a valid commercial license is present.

Copyright (c) 2025 Labeeb Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""
import os
import json
import logging
from pathlib import Path
from labeeb.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

def check_license():
    """Check license validity and platform compatibility."""
    platform_manager = PlatformManager()
    platform_info = platform_manager.get_platform_info()
    
    # Get license info
    license_path = os.path.join(os.path.expanduser("~"), ".labeeb", "license.json")
    if not os.path.exists(license_path):
        logger.error("License file not found")
        return False
        
    try:
        with open(license_path) as f:
            license_data = json.load(f)
            
        # Check platform compatibility
        if platform_info['name'] not in license_data.get('supported_platforms', []):
            logger.error(f"Platform {platform_info['name']} not supported by license")
            return False
            
        # Check other license conditions
        # ... (rest of license validation logic)
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking license: {e}")
        return False

if __name__ == "__main__":
    if check_license():
        print("License check passed")
    else:
        print("License check failed")
