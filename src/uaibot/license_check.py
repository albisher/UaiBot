"""
UaiBot license verification module.

This module checks if the application is being used according to its license terms.
For commercial environments, it verifies if a valid commercial license is present.

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""
import os
import socket
import platform
import datetime
import getpass
import uuid
import json
from .pathlib import Path
from uaibot.utils import get_project_root

def is_commercial_environment():
    """
    Try to detect if the application is running in what appears to be a commercial environment.
    This is a best-effort check and may have false positives/negatives.
    """
    commercial_indicators = 0
    
    # Check for domain name patterns that suggest corporate environments
    hostname = socket.gethostname().lower()
    domain_patterns = ['.corp.', '.inc.', '.ltd.', '.com', '-corp', 'enterprise', 'business']
    if any(pattern in hostname for pattern in domain_patterns):
        commercial_indicators += 1
    
    # Check for enterprise OS editions
    os_info = platform.platform().lower()
    enterprise_os = ['enterprise', 'professional', 'business', 'server']
    if any(edition in os_info for edition in enterprise_os):
        commercial_indicators += 1
    
    # Check for large number of users (possible server)
    try:
        import psutil
        user_count = len(set(p.username() for p in psutil.users()))
        if user_count > 5:  # Arbitrary threshold
            commercial_indicators += 1
    except (ImportError, AttributeError):
        pass
    
    # Return True if multiple indicators suggest commercial use
    return commercial_indicators >= 2

def has_valid_license():
    """
    Check if a valid commercial license file exists.
    """
    # Get the project root directory
    try:
        root_dir = get_project_root()
    except ImportError:
        # Fallback if import fails
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    license_file = os.path.join(root_dir, 'license_key.json')
    
    if not os.path.exists(license_file):
        return False
    
    try:
        with open(license_file, 'r') as f:
            license_data = json.load(f)
            
        # Check license key against expected format
        license_key = license_data.get('license_key', '')
        expiry_date = license_data.get('expiry_date', '')
        
        if not license_key or not expiry_date:
            return False
            
        # Check if license has expired
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if expiry_date < today:
            return False
            
        # Add additional validation as needed
        return True
    
    except (json.JSONDecodeError, KeyError, ValueError):
        return False

def check_license():
    """
    Check license status and display appropriate messages.
    """
    if is_commercial_environment():
        if has_valid_license():
            print("Commercial license detected and valid.")
            return True
        else:
            print("""
╔════════════════════════════════════════════════════════════════╗
║  COMMERCIAL LICENSE REQUIRED                                   ║
║                                                                ║
║  It appears you may be using UaiBot in a commercial setting.   ║
║  UaiBot requires a commercial license for business use.        ║
║                                                                ║
║  Please contact [YOUR_CONTACT_INFORMATION]                     ║
║  to purchase a commercial license.                             ║
║                                                                ║
║  Use of UaiBot without a proper license in a commercial        ║
║  environment is not permitted.                                 ║
╚════════════════════════════════════════════════════════════════╝
""")
            return False
    return True  # Non-commercial use is allowed

if __name__ == "__main__":
    # Simple test of the license check
    print(f"Commercial environment: {is_commercial_environment()}")
    print(f"Valid license: {has_valid_license()}")
    check_license()
