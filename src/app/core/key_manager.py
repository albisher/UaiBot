"""
Secure key management for Labeeb.
"""
import os
import json
import base64
from pathlib import Path
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class KeyManager:
    """Manages secure storage and retrieval of API keys."""
    
    def __init__(self):
        """Initialize the key manager."""
        self.keys_dir = Path('config/keys')
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.keys_file = self.keys_dir / 'encrypted_keys.json'
        self._setup_encryption()
    
    def _setup_encryption(self):
        """Set up encryption using a derived key from the system."""
        # Use system-specific information to derive a key
        system_info = os.uname().sysname + os.uname().nodename
        salt = system_info.encode()
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(system_info.encode()))
        self.fernet = Fernet(key)
    
    def _encrypt(self, data: str) -> str:
        """Encrypt a string."""
        return self.fernet.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def get_key(self, key_name: str) -> str:
        """Get an API key."""
        if not self.keys_file.exists():
            return None
        
        try:
            with open(self.keys_file, 'r') as f:
                keys = json.load(f)
            encrypted_key = keys.get(key_name)
            if encrypted_key:
                return self._decrypt(encrypted_key)
        except Exception as e:
            print(f"Error retrieving key {key_name}: {e}")
        return None
    
    def set_key(self, key_name: str, key_value: str):
        """Set an API key."""
        try:
            # Load existing keys
            keys = {}
            if self.keys_file.exists():
                with open(self.keys_file, 'r') as f:
                    keys = json.load(f)
            
            # Add new key
            keys[key_name] = self._encrypt(key_value)
            
            # Save keys
            with open(self.keys_file, 'w') as f:
                json.dump(keys, f, indent=4)
            
            # Set secure permissions
            os.chmod(self.keys_file, 0o600)
            os.chmod(self.keys_dir, 0o700)
            
        except Exception as e:
            print(f"Error storing key {key_name}: {e}")
    
    def prompt_for_key(self, key_name: str, description: str = None) -> str:
        """Prompt user for an API key."""
        if description:
            print(f"\n{description}")
        key = getpass(f"Please enter your {key_name} (input will be hidden): ")
        if key:
            self.set_key(key_name, key)
            return key
        return None
    
    def ensure_key(self, key_name: str, description: str = None) -> str:
        """Ensure an API key exists, prompting if necessary."""
        key = self.get_key(key_name)
        if not key:
            key = self.prompt_for_key(key_name, description)
        return key 