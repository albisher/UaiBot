"""
Command Processor module for UaiBot.

This module handles the processing and execution of commands using AI models.
It includes command validation, safety checks, and response handling.

The module includes:
- Command processing and validation
- Safety checks and filtering
- Response handling and formatting
- Error handling and logging

Example:
    >>> config = ConfigManager()
    >>> model_manager = ModelManager(config)
    >>> ai_handler = AIHandler(model_manager)
    >>> processor = CommandProcessor(ai_handler)
    >>> result = processor.process_command("What is the weather?")
"""
import logging
import json
import os
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from ..ai_handler import AIHandler

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for command responses
T = TypeVar('T')
CommandResponse = TypeVar('CommandResponse')

@dataclass
class CommandConfig:
    """Configuration for command processing."""
    max_retries: int = 3
    timeout: int = 30
    safety_level: str = "strict"

@dataclass
class CommandResult:
    """Result of a command execution."""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CommandProcessor:
    """
    A class to process and execute commands using AI models.
    
    This class provides a unified interface for processing commands,
    including validation, safety checks, and response handling.
    
    Attributes:
        ai_handler (AIHandler): AI handler instance
        config (CommandConfig): Configuration for command processing
    """
    
    def __init__(self, ai_handler: AIHandler) -> None:
        """
        Initialize the CommandProcessor.
        
        Args:
            ai_handler (AIHandler): AI handler instance
        """
        self.ai_handler = ai_handler
        self.config = CommandConfig()
        # Initialize stats to avoid attribute errors
        self.stats = type('Stats', (), {'total_commands': 0})()
    
    def process_command(self, command: str) -> CommandResult:
        """
        Process a command using the AI model.
        
        Args:
            command (str): The command to process
            
        Returns:
            CommandResult: The result of the command execution
            
        Raises:
            Exception: If there's an error processing the command
        """
        start_time = datetime.now()
        try:
            # Update stats
            self.stats.total_commands += 1
            # Validate command
            if not self._validate_command(command):
                print("[DEBUG] Invalid command format.")
                return CommandResult(success=False, output="", error="Invalid command format")
            # Check command safety
            if not self._check_command_safety(command):
                print("[DEBUG] Command failed safety check.")
                return CommandResult(success=False, output="", error="Command failed safety check")
            # Process command with AI
            response = self.ai_handler.process_prompt(command)
            # Try to interpret the plan from the AI response (JSON)
            import json, subprocess
            user_message = None
            try:
                plan_obj = json.loads(response.text)
                print("\n[AI PLAN JSON]\n", json.dumps(plan_obj, indent=2))
                if "plan" in plan_obj and isinstance(plan_obj["plan"], list):
                    step = plan_obj["plan"][0] if plan_obj["plan"] else None
                    if step:
                        print("[AI PLAN STEP]", json.dumps(step, indent=2))
                        # Show the description as the user-friendly message
                        user_message = step.get("description")
                        # If it's a system command, try to execute it
                        if step.get("operation") == "system_command":
                            cmd = step.get("parameters", {}).get("command")
                            if cmd:
                                print(f"[EXECUTING SYSTEM COMMAND]: {cmd}")
                                try:
                                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                                    if result.returncode == 0:
                                        print("[SYSTEM OUTPUT]:\n", result.stdout.strip())
                                        user_message += f"\n[System Output]:\n{result.stdout.strip()}"
                                    else:
                                        print("[SYSTEM ERROR]:\n", result.stderr.strip())
                                        user_message += f"\n[System Error]:\n{result.stderr.strip()}"
                                except Exception as e:
                                    print(f"[EXECUTION ERROR]: {str(e)}")
                                    user_message += f"\n[Execution Error]: {str(e)}"
                else:
                    print("[DEBUG] No valid plan found in AI response.")
                    user_message = response.text
            except Exception as e:
                print(f"[DEBUG] Failed to parse or execute plan: {e}")
                user_message = response.text
            # Save result
            self._save_command_result(command, response)
            return CommandResult(
                success=True,
                output=user_message,
                metadata=response.metadata
            )
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            print(f"[ERROR] {str(e)}")
            return CommandResult(success=False, output="", error=str(e))
    
    def _validate_command(self, command: str) -> bool:
        """
        Validate the command format.
        
        Args:
            command (str): The command to validate
            
        Returns:
            bool: True if the command is valid, False otherwise
        """
        # Basic validation
        if not command or not isinstance(command, str):
            return False
        
        # Add more validation rules as needed
        return True
    
    def _check_command_safety(self, command: str) -> bool:
        """
        Check if the command is safe to execute.
        
        Args:
            command (str): The command to check
            
        Returns:
            bool: True if the command is safe, False otherwise
        """
        # Add safety checks based on config.safety_level
        if self.config.safety_level == "strict":
            # Implement strict safety checks
            pass
        elif self.config.safety_level == "moderate":
            # Implement moderate safety checks
            pass
        else:
            # Implement basic safety checks
            pass
        
        return True
    
    def _save_command_result(self, command: str, response: Any) -> None:
        """
        Save the command result to a file.
        
        Args:
            command (str): The original command
            response (Any): The AI response
        """
        try:
            # Create results directory if it doesn't exist
            results_dir = os.path.join("results", "command_results")
            os.makedirs(results_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sanitized_command = "".join(c if c.isalnum() else "_" for c in command[:50])
            filename = f"{timestamp}_{sanitized_command}.json"
            
            # Prepare result data
            result_data = {
                "timestamp": timestamp,
                "command": command,
                "result": response.text,
                "raw_response": response.raw_response,
                "metadata": {
                    "model": response.metadata.get("model"),
                    "tokens": response.metadata.get("tokens"),
                    "processing_time": response.metadata.get("processing_time")
                }
            }
            
            # Save to file
            filepath = os.path.join(results_dir, filename)
            with open(filepath, "w") as f:
                json.dump(result_data, f, indent=2)
            
            logger.info(f"Saved command result to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving command result: {str(e)}") 