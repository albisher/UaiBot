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
    
    def process_command(self, command: str, extra_context: str = None) -> CommandResult:
        """
        Process a command using the AI model.
        
        Args:
            command (str): The command to process
            extra_context (str, optional): Extra context (e.g., vision result) to pass to the AI model
        Returns:
            CommandResult: The result of the command execution
        """
        start_time = datetime.now()
        try:
            self.stats.total_commands += 1
            if not self._validate_command(command):
                print("[DEBUG] Invalid command format.")
                return CommandResult(success=False, output="", error="Invalid command format")
            if not self._check_command_safety(command):
                print("[DEBUG] Command failed safety check.")
                return CommandResult(success=False, output="", error="Command failed safety check")
            print(f"[USER COMMAND]: {command}")
            # Pass extra_context to AI handler if present
            response = self.ai_handler.process_prompt(command, extra_context=extra_context) if extra_context else self.ai_handler.process_prompt(command)
            import json, subprocess
            user_messages = []
            incomplete_plan = False
            try:
                plan_obj = json.loads(response.text)
                print("\n[AI PLAN JSON]\n", json.dumps(plan_obj, indent=2))
                if "plan" in plan_obj and isinstance(plan_obj["plan"], list):
                    for step in plan_obj["plan"]:
                        print("[AI PLAN STEP]", json.dumps(step, indent=2))
                        desc = step.get("description", "")
                        op = step.get("operation", "")
                        params = step.get("parameters", {})
                        msg = desc
                        if op == "system_command":
                            cmd = params.get("command")
                            if cmd:
                                print(f"[EXECUTING SYSTEM COMMAND]: {cmd}")
                                try:
                                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                                    if result.returncode == 0:
                                        print("[SYSTEM OUTPUT]:\n", result.stdout.strip())
                                        msg += f"\n[System Output]:\n{result.stdout.strip()}"
                                        # After executing a system command, get user-friendly feedback
                                        feedback = self.get_system_command_feedback(cmd, result.stdout.strip())
                                        # Pass feedback to GUI/system output
                                    else:
                                        print("[SYSTEM ERROR]:\n", result.stderr.strip())
                                        msg += f"\n[System Error]:\n{result.stderr.strip()}"
                                except Exception as e:
                                    print(f"[EXECUTION ERROR]: {str(e)}")
                                    msg += f"\n[Execution Error]: {str(e)}"
                            else:
                                incomplete_plan = True
                                msg += "\n[ERROR: Missing required parameters for system command]"
                        user_messages.append(msg)
                else:
                    print("[DEBUG] No valid plan found in AI response.")
                    user_messages.append(response.text)
            except Exception as e:
                print(f"[DEBUG] Failed to parse or execute plan: {e}")
                user_messages.append(response.text)
            self._save_command_result(command, response)
            return CommandResult(
                success=True,
                output="\n\n".join(user_messages),
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
            
            # Prepare result data (only serializable fields)
            result_data = {
                "timestamp": timestamp,
                "command": command,
                "result": getattr(response, 'text', str(response)),
                "raw_response": str(getattr(response, 'raw_response', '')),
                "metadata": dict(getattr(response, 'metadata', {})),
            }
            
            # Save to file
            filepath = os.path.join(results_dir, filename)
            with open(filepath, "w") as f:
                json.dump(result_data, f, indent=2)
            
            logger.info(f"Saved command result to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving command result: {str(e)}")
            print(f"[ERROR] Error saving command result: {str(e)}")

    def get_system_command_feedback(self, command, output):
        if output and output.strip():
            return output.strip()
        if 'calculator' in command.lower():
            return "Calculator app opened on screen 1."
        if 'safari' in command.lower():
            return "Safari browser launched."
        if 'open' in command.lower() and 'http' in command.lower():
            return "Website opened in default browser."
        return "Command executed successfully, but no output was returned." 