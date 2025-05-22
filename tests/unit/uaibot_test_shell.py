#!/usr/bin/env python3
"""
Directly interact with UaiBot
"""

import os
import sys
import cmd
import readline

# Add parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.shell_handler import ShellHandler

class UaiBotTestShell(cmd.Cmd):
    intro = "UaiBot Test Shell. Type help or ? to list commands.\n"
    prompt = "UaiBotTest> "
    
    def __init__(self):
        super().__init__()
        self.shell_handler = ShellHandler(safe_mode=False, quiet_mode=False)
    
    def do_find_folders(self, arg):
        """Find folders: find_folders <name> [include_cloud=True/False]"""
        args = arg.split()
        if not args:
            print("Usage: find_folders <folder_name> [include_cloud=True/False]")
            return
            
        folder_name = args[0]
        include_cloud = True  # Default
        
        if len(args) > 1:
            if args[1].lower() == "false":
                include_cloud = False
            elif args[1].lower() == "true":
                include_cloud = True
        
        print(f"Searching for folders matching '{folder_name}' with include_cloud={include_cloud}...")
        try:
            result = self.shell_handler.find_folders(folder_name, include_cloud=include_cloud)
            print("\nResult:")
            print(result)
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def do_test_notes(self, arg):
        """Test finding notes folders with debugging"""
        try:
            print("Testing with 'notes' and include_cloud=True...")
            result = self.shell_handler.find_folders("notes", include_cloud=True)
            print("\nResult:")
            print(result)
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def do_exit(self, arg):
        """Exit the shell"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Alias for exit"""
        return self.do_exit(arg)

if __name__ == "__main__":
    UaiBotTestShell().cmdloop()
