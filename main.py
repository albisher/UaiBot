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
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

# Import core components
from core.logging_config import setup_logging, get_logger
from core.exceptions import UaiBotError, AIError, ConfigurationError, CommandError
from core.cache_manager import CacheManager
from platform_uai.platform_manager import PlatformManager
from command_processor import CommandProcessor, ShellHandler
from core.ai_handler import AIHandler
from utils.output_facade import output
from core.file_operations import process_file_flag_request

# Set up logging
logger = get_logger(__name__)

# Disable httpx INFO level logging to prevent duplicate request logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Suppress all urllib3 warnings
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)
urllib3.disable_warnings()

class UaiBot:
    """Main UaiBot class that handles user interaction."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, debug: bool = False):
        """
        Initialize UaiBot with configuration.
        
        Args:
            config: Optional configuration dictionary
            debug: Boolean to enable debug output
        """
        try:
            # Initialize platform manager
            self.platform_manager = PlatformManager()
            if not self.platform_manager.platform_supported:
                raise ConfigurationError(f"Unsupported platform: {self.platform_manager.platform_name}")
            
            # Initialize platform components
            logger.info("Initializing platform components...")
            self.platform_manager.initialize()
            
            # Load configuration
            self.config = config or {}
            
            # Configure output facade with verbosity settings
            output_verbosity = self.config.get('output_verbosity', 'normal')
            output.set_verbosity(output_verbosity)
            
            # Initialize shell handler and command processor
            self.shell_handler = ShellHandler()
            
            # Initialize AI handler with caching
            model_type = self.config.get('default_ai_provider', 'ollama')
            ollama_base_url = self.config.get('ollama_base_url', 'http://localhost:11434')
            google_api_key = self.config.get('google_api_key')
            google_model_name = self.config.get('default_google_model', 'gemini-pro')
            
            self.ai_handler = AIHandler(
                model_type=model_type,
                api_key=google_api_key,
                google_model_name=google_model_name,
                ollama_base_url=ollama_base_url,
                cache_ttl=self.config.get('cache_ttl', 3600),
                cache_size_mb=self.config.get('cache_size_mb', 100)
            )
            
            self.command_processor = CommandProcessor(self.ai_handler, self.shell_handler, debug=debug)
            
            # Welcome message with platform info
            platform_info = self.platform_manager.get_platform_info()
            self.welcome_message = f"""
🤖 Welcome to UaiBot!
I'm your AI assistant, ready to help you with your tasks.
Running on: {platform_info['name']}
Type 'help' for available commands or just ask me anything!
"""
            logger.info("UaiBot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize UaiBot: {str(e)}")
            raise
    
    def start(self) -> None:
        """Start the UaiBot interactive session."""
        try:
            output.box(self.welcome_message, "Welcome")
            self._interactive_loop()
        except KeyboardInterrupt:
            output.info("👋 Session interrupted. Goodbye!")
        except Exception as e:
            logger.error(f"Error in interactive session: {str(e)}")
            output.error(f"An error occurred: {str(e)}")
        finally:
            self.cleanup()
    
    def _interactive_loop(self) -> None:
        """Main interactive loop for UaiBot."""
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    output.success("👋 Goodbye! Have a great day!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'clear':
                    self.ai_handler.clear_cache()
                    output.success("Cache cleared successfully")
                    continue
                
                response = self.command_processor.process_command(user_input)
                output.info(response)
                
            except KeyboardInterrupt:
                raise
            except CommandError as e:
                output.error(f"Command error: {str(e)}")
            except AIError as e:
                output.error(f"AI processing error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                output.error(f"An unexpected error occurred: {str(e)}")
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
Available commands:
- help: Show this help message
- clear: Clear the AI response cache
- exit/quit/bye: Exit UaiBot

You can also:
- Ask me to execute shell commands
- Ask questions about your system
- Request file operations
- Get system information
"""
        output.box(help_text, "Help")
    
    def process_single_command(self, command: str) -> str:
        """
        Process a single command and return the result.
        
        Args:
            command: The command to process
            
        Returns:
            The command response
        """
        try:
            result = self.command_processor.process_command(command)
            return result
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.platform_manager.cleanup()
            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

def main():
    """Main entry point for UaiBot."""
    try:
        # Set up logging
        setup_logging(
            log_level=logging.INFO,
            log_file="logs/uaibot.log",
            max_bytes=10 * 1024 * 1024,  # 10MB
            backup_count=5
        )
        
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="UaiBot: AI-powered shell assistant")
        parser.add_argument("-f", "--file", type=str, help="Command to execute in file/automation mode")
        parser.add_argument("-c", "--command", type=str, help="Command to execute")
        parser.add_argument("--no-safe-mode", action="store_true", help="Disable safe mode for file operations")
        parser.add_argument("--gui", "-g", action="store_true", help="Start in GUI mode")
        parser.add_argument('--debug', action='store_true', help='Enable debug output for AI prompt/response/decision')
        args = parser.parse_args()
        
        # Check if GUI mode is requested
        if args.gui:
            output.info("GUI mode requested. Please use 'python start_uaibot.py --gui' instead.")
            sys.exit(1)
        
        # Initialize and start UaiBot
        bot = UaiBot(debug=args.debug)
        
        if args.file:
            # Process the command in file/automation mode (AI-driven)
            result = bot.process_single_command(args.file)
            output.info(result)
        elif args.command:
            result = bot.process_single_command(args.command)
            output.info(result)
        else:
            bot.start()
            
    except KeyboardInterrupt:
        output.info("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        output.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
