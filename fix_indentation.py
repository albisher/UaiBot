#!/usr/bin/env python3
"""
Fix the indentation issue in shell_handler.py
"""

import re

def main():
    print("Reading shell_handler.py...")
    with open('core/shell_handler.py', 'r') as f:
        content = f.read()
        
    # Find the find_folders function that's outside the class
    pattern = r'def find_folders\(self,'
    matches = re.search(pattern, content)
    
    if not matches:
        print("Could not find the find_folders function.")
        return
        
    print("Found find_folders function with incorrect indentation.")
    
    # Replace the function signature with the properly indented one
    fixed_content = content.replace('def find_folders(self,', '    def find_folders(self,')
    
    # Create backup
    print("Creating backup...")
    with open('core/shell_handler.py.bak_indentation', 'w') as f:
        f.write(content)
    
    # Write fixed content
    print("Writing fixed content...")
    with open('core/shell_handler.py', 'w') as f:
        f.write(fixed_content)
    
    print("Done!")

if __name__ == "__main__":
    main()
