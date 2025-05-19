#!/usr/bin/env python3
"""
UaiBot: AI-powered shell assistant.
Main entry point for the UaiBot application.
Supports both GUI and command-line interfaces.

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""
import json
import argparse
import os
import sys
import re
import subprocess
import platform
import warnings
import urllib3
import logging

# Disable httpx INFO level logging to prevent duplicate request logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("uaibot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress the urllib3 LibreSSL warning
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# Disable other urllib3 warnings
urllib3.disable_warnings()

# Import core components
from core.ai_handler import AIHandler
from core.shell_handler import ShellHandler
from core.utils import load_config, get_project_root

# Import modules
from device_manager import USBDetector
from screen_handler.screen_manager import ScreenManager

# Platform management for GUI
from platform_uai.platform_manager import PlatformManager

# Import license validation
from core.license_check import check_license

# Import command processing
from command_processor.command_processor_main import CommandProcessor

# GUI imports (only loaded if needed)
GUI_AVAILABLE = False
try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from gui.dual_window_emoji import UaiBotDualInterface
    GUI_AVAILABLE = True
except ImportError:
    pass  # GUI components not available or PyQt5 not installed

def main():
    """Main entry point for UaiBot."""
    # Parse command-line arguments first to check for license skip
    parser = argparse.ArgumentParser(description="UaiBot: AI-powered shell assistant.")
    parser.add_argument("-c", "--command", type=str, help="Execute a single command and exit.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode with minimal output")
    parser.add_argument("-g", "--gui", action="store_true", help="Launch the graphical user interface")
    parser.add_argument("--no-gui", action="store_true", help="Force command-line mode even if GUI is available")
    parser.add_argument("-i", "--interactive", action="store_true", help="Force interactive mode, regardless of config")
    parser.add_argument("--non-interactive", action="store_true", help="Disable interactive mode")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--fast", action="store_true", help="Fast mode - does not wait for user feedback on errors")
    parser.add_argument("--skip-license-check", action="store_true", help="Skip license validation (for development only)")
    args = parser.parse_args()

    # Set quiet mode and fast mode from command line args
    quiet_mode = args.quiet if hasattr(args, 'quiet') else False
    fast_mode = args.fast if hasattr(args, 'fast') else False
    # Set debug mode from command line args
    debug_mode = args.debug if hasattr(args, 'debug') else False
    
    # Check license status for potential commercial use unless skipped
    if not (hasattr(args, 'skip_license_check') and args.skip_license_check):
        license_valid = check_license()
        # We don't exit on invalid license, just warn - this could be changed if desired
    
    # Helper function for logging
    def log(message, force=False, debug_only=False, log_type="info"):
        """Log a message based on quiet and debug mode settings, with formatting.
        
        Args:
            message: The message to log
            force: If True, always print even in quiet mode
            debug_only: If True, only print when debug mode is enabled
            log_type: Type of log - "info", "debug", "warning", or "error"
        """
        if debug_only and not debug_mode:
            return  # Skip debug-only messages when debug mode is off
            
        # Define color codes for terminal output
        GRAY = "\033[90m"  # Mid-gray color
        YELLOW = "\033[93m"  # Light amber for warnings
        RED = "\033[91m"    # Red for errors
        RESET = "\033[0m"   # Reset to default color
        
        # Select emoji and color based on log type
        if log_type.lower() == "debug":
            prefix = f"{GRAY}🔍 [DEBUG] "
            suffix = RESET
        elif log_type.lower() == "warning":
            prefix = f"{YELLOW}⚠️ [WARNING] "
            suffix = RESET
        elif log_type.lower() == "error":
            prefix = f"{RED}🚫 [ERROR] "
            suffix = RESET
        else:  # Default to info
            prefix = f"{GRAY}📋 [INFO] "
            suffix = RESET
            
        # For user-facing non-debug logs, don't show the prefix in normal mode
        if not debug_mode and not debug_only and log_type.lower() == "info":
            # Regular user-facing messages shouldn't have log prefix
            if force or not quiet_mode:
                print(message)
        else:
            # Debug and other logs should have the formatted prefix
            if force or not quiet_mode:
                print(f"{prefix}{message}{suffix}")
                
        # Always log to file regardless of console output
        logger.log(
            logging.DEBUG if debug_only else logging.INFO,
            message
        )

    # Load configuration
    config_data = load_config()
    if not config_data:
        log("Error: Failed to load configuration.", force=True)
        exit(1)

    # --- Configuration Loading with Environment Variable Fallbacks ---
    ai_provider = config_data.get("default_ai_provider")
    if not ai_provider:
        log("Error: No default_ai_provider specified in config/settings.json.", force=True)
        log("Please set 'default_ai_provider' to either 'ollama' or 'google'.", force=True)
        exit(1)
        
    google_api_key = config_data.get("google_api_key")
    if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
        log("Google API key not in config or is placeholder, checking GOOGLE_API_KEY env var...", debug_only=True)
        env_key = os.getenv("GOOGLE_API_KEY")
        if env_key:
            google_api_key = env_key
            log("Using Google API key from GOOGLE_API_KEY environment variable.", debug_only=True)

    ollama_base_url = config_data.get("ollama_base_url")
    if not ollama_base_url:
        log("Ollama base URL not in config, checking OLLAMA_BASE_URL env var...", debug_only=True)
        env_ollama_url = os.getenv("OLLAMA_BASE_URL")
        if env_ollama_url:
            ollama_base_url = env_ollama_url
            log("Using Ollama base URL from OLLAMA_BASE_URL environment variable.", debug_only=True)
        else:
            ollama_base_url = "http://localhost:11434" # Default
            log(f"Using default Ollama base URL: {ollama_base_url}", debug_only=True)
    
    default_ollama_model = config_data.get("default_ollama_model")
    if not default_ollama_model:
        log("Default Ollama model not in config, checking DEFAULT_OLLAMA_MODEL env var...", debug_only=True)
        env_ollama_model = os.getenv("DEFAULT_OLLAMA_MODEL")
        if env_ollama_model:
            default_ollama_model = env_ollama_model
            log("Using default Ollama model from DEFAULT_OLLAMA_MODEL environment variable.", debug_only=True)
        
    default_google_model = config_data.get("default_google_model")
    if not default_google_model:
        log("Default Google model not in config, checking DEFAULT_GOOGLE_MODEL env var...", debug_only=True)
        env_google_model = os.getenv("DEFAULT_GOOGLE_MODEL")
        if env_google_model:
            default_google_model = env_google_model
            log("Using default Google model from DEFAULT_GOOGLE_MODEL environment variable.", debug_only=True)
        
    shell_safe_mode = config_data.get("shell_safe_mode", True)
    shell_dangerous_check = config_data.get("shell_dangerous_check", True)

    log(f"Using AI provider: {ai_provider}", debug_only=True)
    log(f"Shell safe_mode: {shell_safe_mode}, dangerous_command_check: {shell_dangerous_check}", debug_only=True)

    # Initialize AI handler with error handling and fallback
    ai_handler = None
    try:
        if ai_provider == "google":
            if not google_api_key or google_api_key == "YOUR_GOOGLE_API_KEY":
                log("Error: Google API key not configured. Please set it in config/settings.json or as GOOGLE_API_KEY environment variable.", force=True)
                exit(1)
            if not default_google_model:
                log("Error: No default_google_model specified. Please set it in config/settings.json or as DEFAULT_GOOGLE_MODEL environment variable.", force=True)
                exit(1)
            log(f"Initializing Google AI with model: {default_google_model}...", debug_only=True)
            ai_handler = AIHandler(model_type="google", api_key=google_api_key, google_model_name=default_google_model, quiet_mode=quiet_mode)
        elif ai_provider == "ollama":
            if not default_ollama_model:
                log("Error: No default_ollama_model specified. Please set it in config/settings.json or as DEFAULT_OLLAMA_MODEL environment variable.", force=True)
                exit(1)
            try:
                log(f"Initializing Ollama AI with model: {default_ollama_model}...", debug_only=True)
                ai_handler = AIHandler(model_type="ollama", ollama_base_url=ollama_base_url, quiet_mode=quiet_mode)
                ai_handler.set_ollama_model(default_ollama_model) 
            except ConnectionError as e:
                log(f"Error connecting to Ollama (URL: {ollama_base_url}): {e}", force=True)
                log("Ollama connection failed. Is Ollama installed and running?", force=True)
                
                if google_api_key and google_api_key != "YOUR_GOOGLE_API_KEY" and default_google_model:
                    log("Attempting to fall back to Google AI provider...", force=True)
                    try:
                        ai_handler = AIHandler(model_type="google", api_key=google_api_key, google_model_name=default_google_model, quiet_mode=quiet_mode)
                        log(f"Successfully connected to Google AI with model: {default_google_model} as fallback.", force=True)
                        ai_provider = "google" # Update the effective AI provider
                    except Exception as google_fallback_e:
                        log(f"Error initializing Google AI as fallback: {google_fallback_e}", force=True)
                else:
                    log("Google API key and/or default Google model not configured for fallback.", force=True)
                
                if not ai_handler:
                    log("ERROR: Could not connect to Ollama, and fallback to Google AI was not successful or not configured.", force=True)
                    log("Please either:", force=True)
                    log(f"1. Start Ollama (expected at {ollama_base_url}) by running 'ollama serve' in another terminal, OR", force=True)
                    log("2. Configure a valid Google API key and model in config/settings.json or environment variables.", force=True)
                    exit(1)
        else:
            log(f"Error: Unknown AI provider '{ai_provider}' in config/settings.json.", force=True)
            log("Please set 'default_ai_provider' to either 'ollama' or 'google'.", force=True)
            exit(1)

    except ImportError as e:
        log(f"Error initializing AI Handler: {e} - {e.__class__.__name__}", force=True)
        log("Please ensure the required libraries (google-generativeai or ollama) are installed.", force=True)
        log("Run: pip install google-generativeai ollama", force=True)
        exit(1)
    except ValueError as e:
        log(f"Configuration Error: {e} - {e.__class__.__name__}", force=True)
        exit(1)
    except ConnectionError as e:
        log(f"Connection Error: {e} - {e.__class__.__name__}", force=True)
        log("Please ensure Ollama is running. Try starting it with 'ollama serve' in another terminal.", force=True)
        exit(1)

    if not ai_handler:
        log("Fatal: AI Handler could not be initialized. Please check your configuration, AI provider status, and previous error messages.", force=True)
        exit(1)
    
    # Initialize components
    shell_handler = ShellHandler(safe_mode=shell_safe_mode, 
                                enable_dangerous_command_check=shell_dangerous_check, 
                                quiet_mode=quiet_mode,
                                fast_mode=fast_mode)
    
    # Initialize the command processor with our new implementation
    command_processor = CommandProcessor(ai_handler, shell_handler, quiet_mode=quiet_mode)
    
    # Debug log showing which command processor we're using
    if debug_mode:
        log(f"Using CommandProcessor from: {command_processor.__module__}")
    
    # Initialize screen manager
    screen_manager = ScreenManager(quiet_mode=quiet_mode)
    
    # Add the screen manager to the shell handler for sending commands to screen
    shell_handler.screen_manager = screen_manager

    # Determine if interactive mode is enabled in config (default: True)
    interactive_mode = config_data.get("interactive_mode", True)

        # Determine whether to use GUI or command line
    use_gui = False
    if args.gui:
        if not GUI_AVAILABLE:
            log("Error: GUI mode requested but PyQt5 or GUI components not available.", force=True)
            log("Please install PyQt5: pip install PyQt5", force=True)
            exit(1)
        use_gui = True
    elif args.no_gui:
        use_gui = False
    else:
        # Auto-detect based on config and environment
        use_gui = GUI_AVAILABLE and config_data.get("use_gui", False)
        # Don't use GUI if we're not in a graphical environment
        if use_gui and not os.environ.get('DISPLAY') and platform.system() != "Darwin":
            log("GUI mode not available: No display detected.", force=True)
            use_gui = False

    if args.command:  # If command is provided via CLI
        # Never use GUI for single commands
        result = command_processor.process_command(args.command)
        log(result)
        log("UaiBot single command execution finished.", debug_only=True)
    elif use_gui and GUI_AVAILABLE:  # Launch GUI mode
        try:
            log("Launching UaiBot GUI interface...")
            
            # Handle high DPI scaling on macOS
            if platform.system() == 'Darwin':
                os.environ['QT_MAC_WANTS_LAYER'] = '1'  # For macOS Retina displays
                
            # Create Qt application
            app = QApplication(sys.argv)
            
            # Set application metadata
            app.setApplicationName("UaiBot")
            app.setOrganizationName("UaiBot")
            app.setApplicationVersion("1.0.0")
            
            # Initialize platform components for GUI
            platform_manager = PlatformManager()
            if not platform_manager.platform_supported:
                log(f"Error: Unsupported platform for GUI: {platform.system()}", force=True)
                return 1
                
            platform_manager.initialize()
            audio_handler = platform_manager.get_audio_handler()
            usb_handler = platform_manager.get_usb_handler()
            
            # Create dual window interface
            interface = UaiBotDualInterface()
            
            # Set handlers including command_processor
            interface.set_handlers(ai_handler=ai_handler, shell_handler=shell_handler, 
                               command_processor=command_processor, quiet_mode=quiet_mode)
            
            # Note: No need to show welcome message here as it's already shown in the GUI class constructor
            
            # Show windows and run application
            interface.show()
            return app.exec_()
            
        except Exception as e:
            log(f"Error launching GUI: {str(e)}", force=True)
            log("Falling back to command-line mode.", force=True)
            # Fall through to interactive mode
    
    if interactive_mode:  # Enter interactive loop when enabled
        try:
            # Only show debug info in debug mode
            log("UaiBot started. Enter your commands or 'x' to quit.", debug_only=True)
            
            # Only show welcome message when NOT coming from a single command execution
            if not args.command:
                # Clean, simple welcome message for the user
                print("\nWelcome, I (UaiBot assistant) am ready to assist you.")
                print("Type your request please:")
            
            while True:
                # Get user input without showing "Request:" prompt
                user_input = input()
                if user_input.lower() in ['x', 'exit', 'quit']:
                    break
                result = command_processor.process_command(user_input)
                log(result)
                
                # Add a blank line and the prompt again after each response for better readability
                print("\nType your request please:")
        except KeyboardInterrupt:
            log("\nExiting UaiBot.")
        finally:
            log("UaiBot session ended.", debug_only=True)
    else:
        log("Interactive mode is disabled. Exiting.")

if __name__ == "__main__":
    main()
