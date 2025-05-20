#!/usr/bin/env python3
"""
UaiBot: AI-powered shell assistant.
Main entry point for the UaiBot application.
Supports both GUI and command-line interfaces.

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""
import os
import sys
import logging
import warnings
import urllib3
from core.logging_config import setup_logging
from pathlib import Path
from core.file_utils import search_files, expand_path, find_cv_files
from datetime import datetime
from platform_uai.platform_manager import PlatformManager

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

# Import the output handler to prevent duplicate outputs
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'test_files'))
    from test_files.output_handler import OutputHandler
    # Create a global output handler instance
    output_handler = OutputHandler()
except ImportError:
    # Output handler is optional, not critical if missing
    output_handler = None

# Disable httpx INFO level logging to prevent duplicate request logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set up logging with proper configuration to prevent duplicate messages
setup_logging(log_level=logging.INFO, log_file="logs/uaibot.log")
logger = logging.getLogger(__name__)

# Suppress all urllib3 warnings
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)

# Disable other urllib3 warnings
urllib3.disable_warnings()

# Import core components
from core.utils import load_config
from command_processor import CommandProcessor, ShellHandler

class UaiBot:
    """Main UaiBot class that handles user interaction."""
    
    def __init__(self):
        # Initialize platform manager
        self.platform_manager = PlatformManager()
        if not self.platform_manager.platform_supported:
            logger.error(f"Unsupported platform: {self.platform_manager.platform_name}")
            print(f"ERROR: Unsupported platform: {self.platform_manager.platform_name}")
            sys.exit(1)
            
        # Initialize platform components
        logger.info("Initializing platform components...")
        self.platform_manager.initialize()
        
        # Initialize shell handler and command processor
        self.shell_handler = ShellHandler()
        self.command_processor = CommandProcessor(self.shell_handler)
        
        # Welcome message with platform info
        platform_info = self.platform_manager.get_platform_info()
        self.welcome_message = f"""
🤖 Welcome to UaiBot!
I'm your AI assistant.
Type commands or questions for help.
Running on: {platform_info['name']}
"""
    
    def start(self):
        """Start the UaiBot interactive session."""
        print(self.welcome_message)
        self._interactive_loop()
    
    def _interactive_loop(self):
        """Main interactive loop for UaiBot."""
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("UaiBot: 👋 Goodbye! Have a great day!")
                    
                    # Clean up platform resources
                    self.platform_manager.cleanup()
                    break
                
                response = self.command_processor.process_command(user_input)
                print(f"\nUaiBot: {response}")
                
            except KeyboardInterrupt:
                print("\nUaiBot: 👋 Session interrupted. Goodbye!")
                
                # Clean up platform resources
                self.platform_manager.cleanup()
                break
            except Exception as e:
                print(f"\nUaiBot: ❌ An error occurred: {str(e)}")
                print("UaiBot: 🔄 Let's continue. What else can I help you with?")
                logger.error(f"Error in interactive loop: {str(e)}", exc_info=True)
    
    def process_single_command(self, command):
        """Process a single command and return the result."""
        try:
            return self.command_processor.process_command(command)
        finally:
            # Clean up platform resources even after a single command
            self.platform_manager.cleanup()


if __name__ == "__main__":
    # Parse command-line arguments
    args = sys.argv[1:]
    
    # Check if GUI mode is requested
    if "--gui" in args or "-g" in args:
        print("GUI mode requested. Please use 'python start_uaibot.py --gui' instead.")
        sys.exit(1)
        
    bot = UaiBot()
    
    if len(args) > 0 and not args[0].startswith("-"):
        # If command line arguments are provided, process them as a single command
        command = " ".join(args)
        result = bot.process_single_command(command)
        print(f"UaiBot: {result}")
    else:
        # Otherwise start interactive mode
        bot.start()
