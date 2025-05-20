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
from utils.output_formatter import get_terminal_width

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

# Import the OutputFacade singleton
from utils.output_facade import output

# Alias for backward compatibility
def format_uaibot_output(message, msg_type="info"):
    """
    Format output using the output facade.
    This is a legacy function maintained for backward compatibility.
    Uses the new OutputFacade internally.
    """
    # Convert legacy message types to appropriate OutputFacade method calls
    if msg_type == "info":
        return output.box(message, "Information")
    elif msg_type == "success":
        output.success(message)
        return message
    elif msg_type == "error":
        output.error(message)
        return message
    elif msg_type == "warning":
        output.warning(message)
        return message
    elif msg_type == "robot":
        return output.box(message, "UaiBot")
    elif msg_type == "tip":
        output.info(message) 
        return message
    else:
        output.info(message)
        return message

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
            output.error(f"Unsupported platform: {self.platform_manager.platform_name}")
            sys.exit(1)
            
        # Initialize platform components
        logger.info("Initializing platform components...")
        self.platform_manager.initialize()
        
        # Load configuration
        config = load_config() or {}
        
        # Configure output facade with verbosity settings
        output_verbosity = config.get('output_verbosity', 'normal')
        
        # Initialize shell handler and command processor
        self.shell_handler = ShellHandler()
        from core.ai_handler import AIHandler
        
        model_type = config.get('default_ai_provider', 'ollama')
        ollama_base_url = config.get('ollama_base_url', 'http://localhost:11434')
        google_api_key = config.get('google_api_key')
        google_model_name = config.get('default_google_model', 'gemini-pro')
        if model_type == 'google':
            self.ai_handler = AIHandler(model_type='google', api_key=google_api_key, google_model_name=google_model_name)
        else:
            self.ai_handler = AIHandler(model_type='ollama', ollama_base_url=ollama_base_url)
        self.command_processor = CommandProcessor(self.ai_handler, self.shell_handler)
        
        # Welcome message with platform info
        platform_info = self.platform_manager.get_platform_info()
        self.welcome_message = f"""
🤖 Welcome to UaiBot!
I'm your AI assistant.
Type commands or questions for help.
Running on: {platform_info['name']}
"""
        # Set output verbosity based on config
        self.output_verbosity = output_verbosity
    
    def start(self):
        """Start the UaiBot interactive session."""
        print(format_uaibot_output(self.welcome_message, "robot"))
        self._interactive_loop()
    
    def _interactive_loop(self):
        """Main interactive loop for UaiBot."""
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(format_uaibot_output("👋 Goodbye! Have a great day!", "success"))
                    
                    # Clean up platform resources
                    self.platform_manager.cleanup()
                    break
                
                response = self.command_processor.process_command(user_input)
                print(format_uaibot_output(response, "info"))
                
            except KeyboardInterrupt:
                print(format_uaibot_output("👋 Session interrupted. Goodbye!", "warning"))
                
                # Clean up platform resources
                self.platform_manager.cleanup()
                break
            except Exception as e:
                print(format_uaibot_output(f"❌ An error occurred: {str(e)}", "error"))
                print(format_uaibot_output("🔄 Let's continue. What else can I help you with?", "tip"))
                logger.error(f"Error in interactive loop: {str(e)}", exc_info=True)
    
    def process_single_command(self, command):
        """Process a single command and return the result."""
        try:
            result = self.command_processor.process_command(command)
            print(format_uaibot_output(result, "info"))
            return result
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
