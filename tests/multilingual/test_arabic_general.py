import os
import sys
import argparse
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.uaibot.core.command_processor.command_processor_main import CommandProcessor
from src.uaibot.core.ai_handler import AIHandler
from src.uaibot.core.model_manager import ModelManager
from src.uaibot.core.config_manager import ConfigManager


def load_arabic_commands(file_path):
    """Load Arabic commands from the specified file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"File content:\n{content}\n")  # Debug: Print file content
    # Extract commands from the list of tuples (Arabic command, English action)
    commands = []
    for line in content.split('\n'):
        if line.strip().startswith('(') and line.strip().endswith(')'):
            parts = line.strip()[1:-1].split(',', 1)
            if len(parts) >= 1:
                command = parts[0].strip().strip('"')
                commands.append(command)
    print(f"Extracted commands: {commands}\n")  # Debug: Print extracted commands
    return commands


def extract_commands(file_content):
    # Use regex to extract commands from markdown format, line by line
    command_pattern = r'^\s*\d+\.\s*"(.*?)"\s*=\s*.*$'
    commands = re.findall(command_pattern, file_content, re.MULTILINE)
    return commands  # List of Arabic commands only


def main():
    parser = argparse.ArgumentParser(description='Test Arabic commands from a specified file.')
    parser.add_argument('--file', type=str, default='todo/human_instructions/KuwaitiArabic.txt',
                        help='Path to the Arabic instruction file (default: todo/human_instructions/KuwaitiArabic.txt)')
    args = parser.parse_args()

    # Load Arabic commands
    commands = load_arabic_commands(args.file)
    if not commands:
        print("No commands found in the specified file.")
        return

    # Initialize components
    config_manager = ConfigManager()
    model_manager = ModelManager(config_manager)
    ai_handler = AIHandler(model_manager)
    processor = CommandProcessor(ai_handler)

    # Process each command
    for command in commands:
        print(f"Command: {command}")
        result = processor.process_command(command)
        print(f"Output: {result.output}")
        print("----------------------------------------")

    # Read file content
    file_path = Path(args.file)
    file_content = file_path.read_text(encoding='utf-8')
    print("File content read successfully:", file_content[:100])  # Print first 100 characters


if __name__ == "__main__":
    main() 