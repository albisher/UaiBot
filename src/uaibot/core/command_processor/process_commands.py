"""
Command Processing module for UaiBot.

This module handles the processing of multiple commands in sequence,
including command validation, execution, and result handling.

The module includes:
- Command sequence processing
- Result aggregation and formatting
- Error handling and logging
- Result saving and organization

Example:
    >>> config = ConfigManager()
    >>> model_manager = ModelManager(config)
    >>> ai_handler = AIHandler(model_manager)
    >>> processor = CommandProcessor(ai_handler)
    >>> results = process_commands(processor, ["What is the weather?", "Show system info"])
"""
import logging
import json
import os
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from .command_processor import CommandProcessor, CommandResult

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for command responses
T = TypeVar('T')
CommandResponse = TypeVar('CommandResponse')

@dataclass
class CommandSequence:
    """A sequence of commands to process."""
    commands: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessingResult:
    """Result of processing a command sequence."""
    success: bool
    results: List[CommandResult]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

def process_commands(processor: CommandProcessor, commands: List[str]) -> ProcessingResult:
    """
    Process a sequence of commands.
    
    Args:
        processor (CommandProcessor): Command processor instance
        commands (List[str]): List of commands to process
        
    Returns:
        ProcessingResult: The result of processing all commands
        
    Raises:
        Exception: If there's an error processing the commands
    """
    try:
        # Create command sequence
        sequence = CommandSequence(
            commands=commands,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "total_commands": len(commands)
            }
        )
        
        # Process each command
        results = []
        for command in sequence.commands:
            result = processor.process_command(command)
            results.append(result)
            
            # Stop if a command fails
            if not result.success:
                return ProcessingResult(
                    success=False,
                    results=results,
                    error=result.error,
                    metadata=sequence.metadata
                )
        
        return ProcessingResult(
            success=True,
            results=results,
            metadata=sequence.metadata
        )
        
    except Exception as e:
        logger.error(f"Error processing commands: {str(e)}")
        return ProcessingResult(
            success=False,
            results=[],
            error=str(e),
            metadata=sequence.metadata if 'sequence' in locals() else {}
        )

def save_processing_result(result: ProcessingResult, output_dir: str = "results/command_results") -> None:
    """
    Save the processing result to a file.
    
    Args:
        result (ProcessingResult): The processing result to save
        output_dir (str): Directory to save the result in
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"command_sequence_{timestamp}.json"
        
        # Prepare result data
        result_data = {
            "timestamp": timestamp,
            "success": result.success,
            "error": result.error,
            "metadata": result.metadata,
            "results": [
                {
                    "command": result.metadata.get("commands", [])[i] if i < len(result.metadata.get("commands", [])) else f"command_{i}",
                    "success": r.success,
                    "output": r.output,
                    "error": r.error,
                    "metadata": r.metadata
                }
                for i, r in enumerate(result.results)
            ]
        }
        
        # Save to file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            json.dump(result_data, f, indent=2)
        
        logger.info(f"Saved processing result to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving processing result: {str(e)}")

if __name__ == "__main__":
    # Example usage
    from ..config_manager import ConfigManager
    from ..model_manager import ModelManager
    from ..ai_handler import AIHandler
    
    # Initialize components
    config = ConfigManager()
    model_manager = ModelManager(config)
    ai_handler = AIHandler(model_manager)
    processor = CommandProcessor(ai_handler)
    
    # Process commands
    commands = [
        "What is the weather?",
        "Show system info",
        "List files in current directory"
    ]
    
    result = process_commands(processor, commands)
    save_processing_result(result) 