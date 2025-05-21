import argparse
import logging
import json
import os
from uaibot.core.command_processor import CommandProcessor
from uaibot.core.logging_config import setup_logging, get_logger
from uaibot.core.exceptions import UaiBotError, AIError, ConfigurationError, CommandError
from uaibot.core.cache_manager import CacheManager
from uaibot.core.ai_handler import AIHandler
from uaibot.utils.output_facade import output
from uaibot.core.file_operations import process_file_flag_request

def load_settings():
    """Load settings from JSON file."""
    settings_path = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "use_regex": False,
            "default_language": "en",
            "supported_languages": ["en", "ar"],
            "debug_mode": False,
            "log_level": "INFO"
        }

def setup_logging(settings):
    """Set up logging configuration."""
    log_level = settings.get("log_level", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('uaibot.log')
        ]
    )

def main():
    """Main entry point for the application."""
    # Load settings
    settings = load_settings()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='UaiBot - AI-powered command processor')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('-f', '--fast', action='store_true', help='Enable fast mode')
    parser.add_argument('command', nargs='?', help='Command to execute')
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    
    # Initialize command processor with settings
    processor = CommandProcessor(use_regex=settings.get("use_regex", False), fast_mode=args.fast)
    
    # Enable debug mode if requested
    if args.debug or settings.get("debug_mode", False):
        processor.utils.set_debug_mode(True)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    if args.fast:
        logger.info("Fast mode enabled")
    
    logger.info("UaiBot initialized")
    logger.info(f"Using {'AI-driven' if not settings.get('use_regex', False) else 'regex-based'} command processing")
    
    try:
        if args.command:
            # Execute single command
            result = processor.execute_command(args.command)
            
            # Print result
            if result["status"] == "success":
                if "message" in result:
                    print(result["message"])
                if "content" in result:
                    print(result["content"])
                if "files" in result:
                    print("\n".join(result["files"]))
                if "help" in result:
                    for category, commands in result["help"].items():
                        print(f"\n{category}:")
                        for cmd in commands:
                            print(f"  {cmd}")
            else:
                print(f"Error: {result['message']}")
        else:
            # Interactive mode
            while True:
                # Get command from user
                command = input("UaiBot> ").strip()
                
                # Exit if user types 'exit' or 'quit'
                if command.lower() in ['exit', 'quit']:
                    break
                    
                # Execute command
                result = processor.execute_command(command)
                
                # Print result
                if result["status"] == "success":
                    if "message" in result:
                        print(result["message"])
                    if "content" in result:
                        print(result["content"])
                    if "files" in result:
                        print("\n".join(result["files"]))
                    if "help" in result:
                        for category, commands in result["help"].items():
                            print(f"\n{category}:")
                            for cmd in commands:
                                print(f"  {cmd}")
                else:
                    print(f"Error: {result['message']}")
                    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        logger.info("UaiBot shutting down")

if __name__ == "__main__":
    main()
