#!/usr/bin/env python3

"""
Fix syntax errors in the AI Command Extractor file.
"""

import os
import re

def fix_file(file_path):
    print(f"Fixing file: {file_path}")
    
    # Read the original file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Keep a backup
    backup_path = file_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Remove problematic docstring sections
    content = re.sub(r'("""[\s\S]*?)FORMAT [0-9][\s\S]*?"""', r'\1"""', content)
    
    # Write the fixed content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed file saved to: {file_path}")
    print(f"Original file backed up to: {backup_path}")

if __name__ == "__main__":
    fix_file("/home/a/Documents/Projects/UaiBot/command_processor/ai_command_extractor.py")
