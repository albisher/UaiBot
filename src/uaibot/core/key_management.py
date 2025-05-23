"""
Key management utility for UaiBot.
"""
import os
import sys
import json
from pathlib import Path
from getpass import getpass
from typing import List, Optional

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.uaibot.core.key_manager import KeyManager

class KeyManagement:
    """Utility for managing API keys."""
    
    def __init__(self):
        """Initialize key management."""
        self.key_manager = KeyManager()
    
    def list_keys(self) -> List[str]:
        """List all stored keys."""
        try:
            if not self.key_manager.keys_file.exists():
                return []
            
            with open(self.key_manager.keys_file, 'r') as f:
                keys = json.load(f)
            return list(keys.keys())
        except Exception as e:
            print(f"Error listing keys: {e}")
            return []
    
    def show_key_info(self, key_name: str) -> None:
        """Show information about a specific key."""
        try:
            key = self.key_manager.get_key(key_name)
            if key:
                # Show masked version of the key
                masked_key = key[:4] + '*' * (len(key) - 8) + key[-4:]
                print(f"\nKey: {key_name}")
                print(f"Value: {masked_key}")
                print(f"Length: {len(key)} characters")
            else:
                print(f"No key found for: {key_name}")
        except Exception as e:
            print(f"Error showing key info: {e}")
    
    def add_key(self, key_name: str, description: Optional[str] = None) -> bool:
        """Add a new key."""
        try:
            if description:
                print(f"\n{description}")
            key = getpass(f"Enter value for {key_name} (input will be hidden): ")
            if key:
                self.key_manager.set_key(key_name, key)
                print(f"✓ Key {key_name} stored successfully")
                return True
            print("No key provided")
            return False
        except Exception as e:
            print(f"Error adding key: {e}")
            return False
    
    def delete_key(self, key_name: str) -> bool:
        """Delete a key."""
        try:
            if not self.key_manager.keys_file.exists():
                print("No keys file found")
                return False
            
            # Load existing keys
            with open(self.key_manager.keys_file, 'r') as f:
                keys = json.load(f)
            
            if key_name not in keys:
                print(f"Key {key_name} not found")
                return False
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete {key_name}? (y/N): ").lower()
            if confirm != 'y':
                print("Deletion cancelled")
                return False
            
            # Remove key
            del keys[key_name]
            
            # Save updated keys
            with open(self.key_manager.keys_file, 'w') as f:
                json.dump(keys, f, indent=4)
            
            print(f"✓ Key {key_name} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting key: {e}")
            return False
    
    def update_key(self, key_name: str) -> bool:
        """Update an existing key."""
        try:
            if not self.key_manager.get_key(key_name):
                print(f"Key {key_name} not found")
                return False
            
            print(f"\nUpdating key: {key_name}")
            return self.add_key(key_name)
        except Exception as e:
            print(f"Error updating key: {e}")
            return False

def main():
    """Run the key management interface."""
    km = KeyManagement()
    
    while True:
        print("\n=== UaiBot Key Management ===")
        print("1. List all keys")
        print("2. Show key info")
        print("3. Add new key")
        print("4. Update key")
        print("5. Delete key")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            keys = km.list_keys()
            if keys:
                print("\nStored keys:")
                for key in keys:
                    print(f"- {key}")
            else:
                print("\nNo keys stored")
        
        elif choice == '2':
            key_name = input("Enter key name: ").strip()
            km.show_key_info(key_name)
        
        elif choice == '3':
            key_name = input("Enter key name: ").strip()
            description = input("Enter description (optional): ").strip() or None
            km.add_key(key_name, description)
        
        elif choice == '4':
            key_name = input("Enter key name to update: ").strip()
            km.update_key(key_name)
        
        elif choice == '5':
            key_name = input("Enter key name to delete: ").strip()
            km.delete_key(key_name)
        
        elif choice == '6':
            print("\nExiting key management...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main() 