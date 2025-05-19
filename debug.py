#!/usr/bin/env python3
import sys
import os
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current directory: {os.getcwd()}")
print("\nDirectory structure:")
for dirpath, dirnames, filenames in os.walk('.', topdown=True):
    if '.git' in dirnames:
        dirnames.remove('.git')  # Don't show git directory
    if '__pycache__' in dirnames:
        dirnames.remove('__pycache__')  # Skip pycache
    if dirpath.startswith('./tests') or dirpath.startswith('./backup'):
        continue  # Skip tests and backup directories
    if len(dirpath) > 2:  # Skip root directory
        print(f"{dirpath}")
        for file in filenames:
            if file.endswith('.py'):
                print(f"  - {file}")
