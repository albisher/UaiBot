import argparse
import logging
import json
import os
from core.command_processor import CommandProcessor

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
    logging.basicConfig(
        level=getattr(logging, settings["log_level"]),
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
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    
    # Initialize command processor with settings
    processor = CommandProcessor(use_regex=settings["use_regex"])
    
    # Enable debug mode if requested
    if args.debug or settings["debug_mode"]:
        processor.utils.set_debug_mode(True)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    logger.info("UaiBot initialized")
    logger.info(f"Using {'AI-driven' if not settings['use_regex'] else 'regex-based'} command processing")
    
    try:
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
