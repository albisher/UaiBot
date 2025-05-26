import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import json
import pyaudio
import wave
import tempfile
import whisper
import keyboard
import time
from labeeb.logging_config import setup_logging, get_logger
from labeeb.core.exceptions import LabeebError, AIError, ConfigurationError, CommandError
from labeeb.core.cache_manager import CacheManager
from labeeb.core.model_manager import ModelManager
from labeeb.core.config_manager import ConfigManager
from labeeb.core.ai.agent import Agent, ToolRegistry, EchoTool, safe_path
from labeeb.core.ai.agent_tools.file_tool import FileTool

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PROJECT_NAME = "Labeeb"
VERSION = "1.0.0"

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

class Labeeb:
    """Main class for Labeeb."""
    
    def __init__(self, debug=False):
        config_manager = ConfigManager()
        model_manager = ModelManager(config_manager)
        self.registry = ToolRegistry()
        self.registry.register(EchoTool())
        self.registry.register(FileTool())
        self.agent = Agent(tools=self.registry)
        self.debug = debug
    
    def initialize(self):
        """Initialize Labeeb."""
        logger.info("Labeeb initialized")
    
    def process_command(self, command: str) -> dict:
        """Process a command."""
        return self.agent.plan_and_execute(command, {})

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
                                result = self.process_command(transcribed_text)
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
    """Main entry point for Labeeb."""
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Labeeb - AI-powered command processor')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--fast', action='store_true', help='Enable fast mode')
    parser.add_argument('--mic', action='store_true', help='Enable microphone streaming mode')
    parser.add_argument('command', nargs='*', help='Command to execute')
    args = parser.parse_args()

    try:
        # Initialize Labeeb
        labeeb = Labeeb(debug=args.debug)
        labeeb.initialize()

        # If --mic flag is provided, start microphone mode and exit
        if args.mic:
            labeeb.start_microphone_mode()
            return

        # If a command is provided as an argument, process it and exit
        if args.command:
            command_str = ' '.join(args.command)
            result = labeeb.process_command(command_str)
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
                result = labeeb.process_command(user_input)
                logger.debug(f"Result dictionary: {result}")
                if 'message' not in result:
                    logger.warning("Result dictionary missing 'message' key, using default message.")
                    result['message'] = "An error occurred"
                print(result['message'])
            except KeyboardInterrupt:
                logger.info("Labeeb shutting down")
                break
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                print("An error occurred")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print("An error occurred")

if __name__ == "__main__":
    main()
