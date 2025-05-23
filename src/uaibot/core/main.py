import argparse
import logging
import json
import os
from uaibot.core.command_processor.command_processor import CommandProcessor
from uaibot.core.logging_config import setup_logging, get_logger
from uaibot.core.exceptions import UaiBotError, AIError, ConfigurationError, CommandError
from uaibot.core.cache_manager import CacheManager
from uaibot.core.ai_handler import AIHandler
from uaibot.utils.output_facade import output
from uaibot.core.file_operations import process_file_flag_request

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UaiBot:
    """Main class for UaiBot."""
    
    def __init__(self):
        self.processor = CommandProcessor()
    
    def initialize(self):
        """Initialize UaiBot."""
        logger.info("UaiBot initialized")
    
    def process_command(self, command: str) -> dict:
        """Process a command."""
        return self.processor.execute_command(command)

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
            logging.FileHandler('app.log')
        ]
    )

def main():
    """Main entry point for UaiBot."""
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='UaiBot - AI-powered command processor')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--fast', action='store_true', help='Enable fast mode')
    parser.add_argument('command', nargs='*', help='Command to execute')
    args = parser.parse_args()

    try:
        # Initialize UaiBot
        uaibot = UaiBot()
        uaibot.initialize()

        # If a command is provided as an argument, process it and exit
        if args.command:
            command_str = ' '.join(args.command)
            result = uaibot.process_command(command_str)
            logger.debug(f"Result dictionary: {result}")
            if 'message' not in result:
                logger.warning("Result dictionary missing 'message' key, using default message.")
                result['message'] = "An error occurred"
            print(result['message'])
            return

        # Otherwise, enter interactive mode
        while True:
            try:
                user_input = input("Enter command: ")
                result = uaibot.process_command(user_input)
                logger.debug(f"Result dictionary: {result}")
                if 'message' not in result:
                    logger.warning("Result dictionary missing 'message' key, using default message.")
                    result['message'] = "An error occurred"
                print(result['message'])
            except KeyboardInterrupt:
                logger.info("UaiBot shutting down")
                break
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                print("An error occurred")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print("An error occurred")

if __name__ == "__main__":
    main()
