#!/usr/bin/env python3
"""
Labeeb Launcher Script
This script automatically chooses the best way to start Labeeb based on your environment.
"""
import os
import sys
import logging
from pathlib import Path
from app.platform_core.platform_manager import PlatformManager
from app.health_check.platform_health_check import PlatformHealthCheck
from app.health_check.system_info_health_check import SystemInfoHealthCheck
from app.health_check.license_check import LicenseHealthCheck
from app.health_check.update_find_folders import UpdateFolderHealthCheck

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

try:
    from app.utils import load_config, get_platform_name
except ImportError as e:
    print(f"Error importing Labeeb modules: {e}")
    print(f"Make sure you're running from the project root directory.")
    sys.exit(1)

def check_gui_available():
    """Check if GUI components are available"""
    try:
        import PyQt5
        return True
    except ImportError:
        return False

def main():
    """Main entry point for the application"""
    try:
        # Initialize platform manager
        platform_manager = PlatformManager()
        platform_info = platform_manager.get_platform_info()
        
        logger.info(f"Starting Labeeb on {platform_info['name']} {platform_info['version']}")
        
        # Run health checks
        health_checks = [
            PlatformHealthCheck(),
            SystemInfoHealthCheck(),
            LicenseHealthCheck(),
            UpdateFolderHealthCheck()
        ]
        
        for check in health_checks:
            try:
                health_status = check.check_health()
                if health_status['status'] != 'healthy':
                    logger.error(f"Health check failed: {health_status}")
                    sys.exit(1)
            except Exception as e:
                logger.error(f"Error running health check: {str(e)}")
                sys.exit(1)
        
        # Initialize platform-specific handlers
        handlers = platform_manager.get_handlers()
        for handler_name, handler in handlers.items():
            try:
                handler.initialize()
                logger.info(f"Initialized {handler_name} handler")
            except Exception as e:
                logger.error(f"Error initializing {handler_name} handler: {str(e)}")
                sys.exit(1)
        
        # Start the application
        logger.info("All health checks passed, starting application...")
        # TODO: Start the main application
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
