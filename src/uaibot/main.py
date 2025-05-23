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
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from uaibot.logging_config import setup_logging, get_logger
from uaibot.core.exceptions import UaiBotError, AIError, ConfigurationError, CommandError
from uaibot.core.cache_manager import CacheManager
from uaibot.platform_uai.platform_manager import PlatformManager
from uaibot.core.command_processor.command_processor_main import CommandProcessor
from uaibot.core.shell_handler import ShellHandler
from uaibot.core.ai_handler import AIHandler
from uaibot.utils.output_facade import output
from uaibot.core.file_operations import process_file_flag_request
from uaibot.health_check.ollama_health_check import check_ollama_server, check_model_available
from uaibot.core.model_manager import ModelManager
from uaibot.core.config_manager import ConfigManager

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
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, debug: bool = False, mode: str = 'interactive', fast_mode: bool = False):
        """
        Initialize UaiBot with configuration.
        
        Args:
            config: Optional configuration dictionary
            debug: Boolean to enable debug output
            mode: The mode of operation (interactive, command, or file)
            fast_mode: Boolean to enable fast mode (minimal prompts, quick exit)
        """
        try:
            self.mode = mode
            self.fast_mode = fast_mode
            self.debug = debug
            # Initialize platform manager with mode awareness if needed
            self.platform_manager = PlatformManager(mode=mode, fast_mode=fast_mode) if 'mode' in PlatformManager.__init__.__code__.co_varnames else PlatformManager()
            if not self.platform_manager.is_platform_supported():
                raise ConfigurationError(f"Unsupported platform: {self.platform_manager.platform_name}")
            
            # Initialize platform components
            logger.info("Initializing platform components...")
            self.platform_manager.initialize(mode=mode, fast_mode=fast_mode) if 'mode' in self.platform_manager.initialize.__code__.co_varnames else self.platform_manager.initialize()
            
            # Load configuration from file if not provided
            if config is None:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'settings.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        self.config = json.load(f)
                else:
                    self.config = {}
            else:
                self.config = config
            
            # Configure output facade with verbosity settings
            output_verbosity = self.config.get('output_verbosity', 'normal')
            output.set_verbosity(output_verbosity)
            
            # Initialize shell handler and command processor
            self.shell_handler = ShellHandler(fast_mode=fast_mode)
            
            # Initialize AI handler with caching
            model_type = self.config.get('default_ai_provider', 'ollama')
            ollama_base_url = self.config.get('ollama_base_url', 'http://localhost:11434')
            
            # --- Automated Ollama model selection ---
            default_model = self.config.get('default_ollama_model', 'gemma:2b')
            selected_model = default_model
            if model_type == 'ollama':
                ok, tags_json = check_ollama_server()
                if ok:
                    ok, selected_model = check_model_available(tags_json, default_model)
                    if ok:
                        print(f"[UaiBot] Using Ollama model: {selected_model}")
                        # Update the config with the selected model
                        if self.update_config(selected_model):
                            self.config['default_ollama_model'] = selected_model
                        else:
                            print("[UaiBot] Warning: Failed to update configuration with selected model")
                    else:
                        print("[UaiBot] No available Ollama model found. Exiting.")
                        raise RuntimeError("No available Ollama model found.")
            else:
                selected_model = default_model
            # Initialize AIHandler with only supported arguments
            config_manager = ConfigManager()
            config_manager.set("default_ollama_model", selected_model)
            config_manager.set("ollama_base_url", ollama_base_url)
            self.ai_handler = AIHandler(
                model_manager=ModelManager(config_manager)
            )
            
            # Patch the model name for Ollama if needed
            if model_type == 'ollama':
                setattr(self.ai_handler, 'ollama_model_name', selected_model)
            
            self.command_processor = CommandProcessor(self.ai_handler)
            
            # Welcome message with platform info
            platform_info = self.platform_manager.get_platform_info()
            self.welcome_message = f"""
🤖 Welcome to UaiBot!
I'm your AI assistant, ready to help you with your tasks.
Running on: {platform_info['system']}
Type 'help' for available commands or just ask me anything!
"""
            logger.info("UaiBot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize UaiBot: {str(e)}")
            raise
    
    def start(self) -> None:
        """Start the UaiBot interactive session."""
        try:
            if not self.fast_mode:
                output.box(self.welcome_message, "Welcome")
            self._interactive_loop()
        except KeyboardInterrupt:
            if not self.fast_mode:
                output.info("👋 Session interrupted. Goodbye!")
        except Exception as e:
            logger.error(f"Error in interactive session: {str(e)}")
            if not self.fast_mode:
                output.error(f"An error occurred: {str(e)}")
            else:
                print(f"Error: {str(e)}")
        finally:
            self.cleanup()
    
    def _interactive_loop(self) -> None:
        """Main interactive loop for UaiBot."""
        model_switch_triggers = [
            'switch model',
            'change model',
            'set model',
            'use model',
            'change ai model',
            'set ai model',
            'switch ai model',
            'use ai model',
            'select model',
            'select ai model',
            'update model',
            'update ai model',
        ]
        while True:
            try:
                prompt = ">" if self.fast_mode else "\nYou: "
                user_input = input(prompt).strip()
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit', 'bye', 'x']:
                    if not self.fast_mode:
                        output.success("👋 Goodbye! Have a great day!")
                    break
                if user_input.lower() == 'help':
                    if not self.fast_mode:
                        self._show_help()
                    continue
                if user_input.lower() == 'clear':
                    self.ai_handler.clear_cache()
                    if not self.fast_mode:
                        output.success("Cache cleared successfully")
                    continue
                # Check for model switch triggers
                lowered = user_input.lower()
                if any(lowered.startswith(trigger) or trigger in lowered for trigger in model_switch_triggers):
                    self.switch_model()
                    continue
                response = self.command_processor.process_command(user_input)
                if not self.fast_mode:
                    output.info(response)
                else:
                    print(response)
            except KeyboardInterrupt:
                if not self.fast_mode:
                    output.info("👋 Session interrupted. Goodbye!")
                break
            except CommandError as e:
                if not self.fast_mode:
                    output.error(f"Command error: {str(e)}")
                else:
                    print(f"Error: {str(e)}")
            except AIError as e:
                if not self.fast_mode:
                    output.error(f"AI processing error: {str(e)}")
                else:
                    print(f"Error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                if not self.fast_mode:
                    output.error(f"An unexpected error occurred: {str(e)}")
                else:
                    print(f"Error: {str(e)}")
    
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

    def process_test_requests(self, file_path: str) -> None:
        """
        Process test requests from a file.
        
        Args:
            file_path: Path to the file containing test requests
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            requests = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
            for request in requests:
                output.box(f"🤖 Processing your request: '{request}'", "Request")
                response = self.command_processor.process_command(request)
                output.info(response)
        except Exception as e:
            logger.error(f"Error processing test requests: {str(e)}")
            raise

    def update_config(self, selected_model: str) -> bool:
        """
        Update the configuration with the selected model.
        
        Args:
            selected_model: The selected model name
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_dir = os.path.join(project_root, 'config')
            config_path = os.path.join(config_dir, 'settings.json')
            
            # Create config directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            
            # Load existing config or create new one
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update the model setting
            config['default_ollama_model'] = selected_model
            
            # Write the updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Updated configuration with model: {selected_model}")
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False

    def switch_model(self):
        """Interactively switch the AI model at runtime."""
        # Get available models for the selected provider
        if self.config['default_ai_provider'] == 'ollama':
            from uaibot.health_check.ollama_health_check import check_ollama_server
            ok, tags_json = check_ollama_server()
            if not ok:
                output.error("Could not connect to Ollama server. Please ensure it's running.")
                return
            
            if not tags_json or not isinstance(tags_json, list):
                output.error("No models available from Ollama server.")
                return
            
            if ok and tags_json and isinstance(tags_json, list):
                available_models = [m.get('name', '') for m in tags_json if m.get('name')]
            else:
                available_models = []
        else:
            output.error("Invalid provider selected.")
            return
                
        if not available_models:
            output.error("No models available for the selected provider.")
            return
            
        print("\nAvailable models:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model}")
            
        choice = input("Enter model number to switch to (or press Enter to abort): ").strip()
        if not choice or not choice.isdigit():
            output.info("Model switch aborted.")
            return
            
        idx = int(choice) - 1
        if 0 <= idx < len(available_models):
            selected_model = available_models[idx]
            # Update provider and model in config
            self.config['default_ai_provider'] = 'ollama'
            self.config['default_ollama_model'] = selected_model
                
            # Save config to file
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'settings.json')
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            # Re-initialize AI handler
            self.ai_handler = AIHandler(
                model_manager=ModelManager(config_manager=ConfigManager())
            )
            output.success(f"Switched to Ollama model: {selected_model}")
        else:
            output.error("Invalid model selection.")

def main():
    """Main entry point for UaiBot."""
    parser = argparse.ArgumentParser(description='UaiBot: AI-powered shell assistant')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--fast', action='store_true', help='Enable fast mode')
    parser.add_argument('-f', '--file', help='Process requests from a file')
    parser.add_argument('--batch', type=str, help='Path to file with batch user inputs (one per line)')
    args = parser.parse_args()
    
    try:
        # Set up logging
        if args.debug:
            setup_logging(component="main", log_level=logging.DEBUG)
        else:
            setup_logging(component="main")
        
        # Initialize UaiBot
        uaibot = UaiBot(debug=args.debug, fast_mode=args.fast)
        
        if args.file:
            uaibot.process_test_requests(args.file)
        elif args.batch:
            # Batch mode: process each line in the file as a user input
            with open(args.batch, 'r') as f:
                for line in f:
                    user_input = line.strip()
                    if not user_input or user_input.startswith('#'):
                        continue  # skip empty lines and comments
                    print(f"\n[Batch] User: {user_input}")
                    try:
                        result = uaibot.process_single_command(user_input)
                        print(f"[Batch] Result: {result}\n")
                    except Exception as e:
                        print(f"[Batch] Error processing input: {e}\n")
            sys.exit(0)
        else:
            uaibot.start()
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Resources cleaned up successfully")

if __name__ == '__main__':
    main()
