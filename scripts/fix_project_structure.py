#!/usr/bin/env python3
"""
Script to fix project structure and update imports.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the necessary directory structure."""
    directories = [
        'uaibot/core',
        'uaibot/utils',
        'uaibot/gui',
        'uaibot/data',
        'tests/unit',
        'tests/integration',
        'tests/system',
        'tests/multilingual'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py in each directory
        init_file = Path(directory) / '__init__.py'
        init_file.touch()

def move_files():
    """Move files to their correct locations."""
    # Move core files
    core_files = {
        'src/core/ai_command_interpreter.py': 'uaibot/core/ai_command_interpreter.py',
        'src/core/ai_handler.py': 'uaibot/core/ai_handler.py',
        'src/core/command_processor.py': 'uaibot/core/command_processor.py',
        'src/core/file_operations.py': 'uaibot/core/file_operations.py',
        'src/core/browser_controller.py': 'uaibot/core/browser_controller.py'
    }
    
    for src, dst in core_files.items():
        if os.path.exists(src):
            shutil.move(src, dst)
    
    # Move utility files
    util_files = {
        'src/utils/': 'uaibot/utils/',
        'src/gui/': 'uaibot/gui/'
    }
    
    for src, dst in util_files.items():
        if os.path.exists(src):
            for file in os.listdir(src):
                shutil.move(os.path.join(src, file), dst)
    
    # Move test files
    test_files = {
        'tests/test_ai_command_interpreter.py': 'tests/unit/test_ai_command_interpreter.py',
        'tests/test_ai_handler.py': 'tests/unit/test_ai_handler.py',
        'tests/test_command_processor.py': 'tests/unit/test_command_processor.py',
        'tests/test_file_operations.py': 'tests/unit/test_file_operations.py',
        'tests/test_browser_automation.py': 'tests/integration/test_browser_automation.py'
    }
    
    for src, dst in test_files.items():
        if os.path.exists(src):
            shutil.move(src, dst)

def create_main_py():
    """Create the main.py file in the root directory."""
    main_content = """#!/usr/bin/env python3
\"\"\"
UaiBot - AI-powered command interpreter and automation tool.
\"\"\"

import sys
import argparse
from uaibot.core.ai_command_interpreter import AICommandInterpreter
from uaibot.core.command_processor import CommandProcessor
from uaibot.core.file_operations import FileOperations
from uaibot.core.browser_controller import BrowserController

def main():
    parser = argparse.ArgumentParser(description='UaiBot - AI-powered command interpreter')
    parser.add_argument('-c', '--command', help='Command to execute')
    parser.add_argument('--no-safe-mode', action='store_true', help='Disable safe mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize components
        interpreter = AICommandInterpreter()
        processor = CommandProcessor()
        file_ops = FileOperations()
        browser = BrowserController()
        
        # Process command
        result = interpreter.interpret_command(args.command)
        if result:
            print(result)
        else:
            print("Command interpretation failed")
            sys.exit(1)
            
    except Exception as e:
        if args.debug:
            print(f"Error: {str(e)}")
        else:
            print("An error occurred while processing the command")
        sys.exit(1)

if __name__ == '__main__':
    main()
"""
    
    with open('main.py', 'w') as f:
        f.write(main_content)
    
    # Make it executable
    os.chmod('main.py', 0o755)

def main():
    """Main function to fix project structure."""
    print("Creating directory structure...")
    create_directory_structure()
    
    print("Moving files to correct locations...")
    move_files()
    
    print("Creating main.py...")
    create_main_py()
    
    print("Project structure has been fixed!")

if __name__ == '__main__':
    main() 