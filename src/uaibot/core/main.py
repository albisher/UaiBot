import argparse
import logging
import json
import os
import pyaudio
import wave
import tempfile
import whisper
import keyboard
import time
from uaibot.core.command_processor.command_processor import CommandProcessor
from uaibot.core.logging_config import setup_logging, get_logger
from uaibot.core.exceptions import UaiBotError, AIError, ConfigurationError, CommandError
from uaibot.core.cache_manager import CacheManager
from uaibot.core.ai_handler import AIHandler
from uaibot.utils.output_facade import output
from uaibot.core.file_operations import process_file_flag_request
from uaibot.core.model_manager import ModelManager
from uaibot.core.config_manager import ConfigManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UaiBot:
    """Main class for UaiBot."""
    
    def __init__(self, debug=False):
        config_manager = ConfigManager()
        model_manager = ModelManager(config_manager)
        ai_handler = AIHandler(model_manager)
        self.processor = CommandProcessor(ai_handler)
        self.debug = debug
    
    def initialize(self):
        """Initialize UaiBot."""
        logger.info("UaiBot initialized")
    
    def process_command(self, command: str) -> dict:
        """Process a command."""
        return self.processor.execute_command(command)

    def start_microphone_mode(self):
        """Start microphone streaming mode with push-to-talk (space bar)."""
        logger.info("Starting microphone streaming mode (push-to-talk: hold space bar)...")
        print("Hold the space bar to record. Release to transcribe and process.")
        audio = pyaudio.PyAudio()
        stream = None
        frames = []
        recording = False
        try:
            while True:
                if keyboard.is_pressed('space'):
                    if not recording:
                        logger.info("Recording started (space bar held down)...")
                        print("Recording...")
                        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
                        frames = []
                        recording = True
                    data = stream.read(1024)
                    frames.append(data)
                else:
                    if recording:
                        logger.info("Recording stopped (space bar released).")
                        print("Processing...")
                        stream.stop_stream()
                        stream.close()
                        recording = False
                        # Save the recorded audio to a temporary file
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                            temp_path = temp_file.name
                            with wave.open(temp_path, 'wb') as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                                wf.setframerate(16000)
                                wf.writeframes(b''.join(frames))
                            logger.debug(f"Audio saved to temporary file: {temp_path}")
                        # Transcribe the audio file using whisper
                        try:
                            model = whisper.load_model("base")
                            logger.debug("Whisper model loaded.")
                            result = model.transcribe(temp_path)
                            logger.debug(f"Whisper transcription result: {result}")
                            transcribed_text = result.get("text", "")
                            logger.info(f"Transcribed text: {transcribed_text}")
                        except Exception as e:
                            logger.error(f"Error during transcription: {str(e)}")
                            transcribed_text = ""
                        # Process the transcribed text as a command
                        if transcribed_text.strip():
                            logger.debug(f"Processing transcribed command: {transcribed_text}")
                            try:
                                result = self.processor.process_command(transcribed_text)
                                logger.debug(f"Command processor result: {result}")
                                # Print the output to the user
                                output_str = None
                                # Handle CommandResult dataclass or dict
                                if hasattr(result, 'output'):
                                    output_str = result.output
                                elif isinstance(result, dict) and 'output' in result:
                                    output_str = result['output']
                                elif isinstance(result, dict) and 'message' in result:
                                    output_str = result['message']
                                if output_str:
                                    print(f"\n=== Result ===\n{output_str}\n")
                                else:
                                    print("\n=== No output from command ===\n")
                                # If the result includes an action, perform it (example: open app)
                                if hasattr(result, 'action') and callable(result.action):
                                    logger.info("Performing action from command result...")
                                    result.action()
                                elif isinstance(result, dict) and 'action' in result and callable(result['action']):
                                    logger.info("Performing action from command result (dict)...")
                                    result['action']()
                            except Exception as e:
                                logger.error(f"Error during command processing: {str(e)}")
                        else:
                            logger.warning("No transcribed text to process.")
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_path)
                            logger.debug(f"Temporary file deleted: {temp_path}")
                        except Exception as e:
                            logger.error(f"Error deleting temporary file: {str(e)}")
                        print("Ready. Hold space bar to record again.")
                # Small sleep to prevent high CPU usage
                time.sleep(0.05)
        except KeyboardInterrupt:
            logger.info("Microphone mode stopped by user.")
            print("Microphone mode stopped.")
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            audio.terminate()

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
    parser.add_argument('--mic', action='store_true', help='Enable microphone streaming mode')
    parser.add_argument('command', nargs='*', help='Command to execute')
    args = parser.parse_args()

    try:
        # Initialize UaiBot
        uaibot = UaiBot(debug=args.debug)
        uaibot.initialize()

        # If --mic flag is provided, start microphone mode and exit
        if args.mic:
            uaibot.start_microphone_mode()
            return

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
