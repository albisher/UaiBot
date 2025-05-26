import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

# Add src to Python path
src_path = Path(__file__).parent.parent.parent
sys.path.append(str(src_path))

from labeeb.core.tools.system_tools import SystemTools
from labeeb.platform_core.platform_utils import get_input_handler
from labeeb.core.tools.json_tools import JSONTool

class LabeebAgent:
    """Master agent that coordinates tasks and tools for Labeeb."""
    
    def __init__(self):
        self.tools = SystemTools()
        self.json_tool = JSONTool()
        self.input_handler = get_input_handler()
        self.memory = {}  # Simple memory for now
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger('LabeebAgent')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / f'Labeeb_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process natural language input and execute appropriate actions."""
        try:
            self.logger.info(f"Processing input: {user_input}")
            
            # For now, use simple keyword matching
            # TODO: Replace with proper NLP/LLM processing
            if "weather" in user_input.lower():
                return self._handle_weather_request()
            elif "system" in user_input.lower() and "info" in user_input.lower():
                return self._handle_system_info_request()
            elif "screenshot" in user_input.lower():
                return self._handle_screenshot_request()
            elif "execute" in user_input.lower() or "run" in user_input.lower():
                return self._handle_command_request(user_input)
            else:
                return {
                    "status": "error",
                    "message": "I don't understand that request. Try asking about weather, system info, or taking a screenshot."
                }
                
        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}")
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }
    
    def _handle_weather_request(self) -> Dict[str, Any]:
        """Handle weather information request."""
        self.logger.info("Handling weather request")
        return self.tools.get_weather_info()
    
    def _handle_system_info_request(self) -> Dict[str, Any]:
        """Handle system information request."""
        self.logger.info("Handling system info request")
        return self.tools.get_system_info()
    
    def _handle_screenshot_request(self) -> Dict[str, Any]:
        """Handle screenshot request."""
        self.logger.info("Handling screenshot request")
        result = self.tools.take_screenshot()
        if result["success"]:
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            result["image"].save(filename)
            result["filename"] = filename
        return result
    
    def _handle_command_request(self, user_input: str) -> Dict[str, Any]:
        """Handle command execution request."""
        self.logger.info("Handling command request")
        # Extract command from input
        # TODO: Improve command extraction
        command = user_input.split("execute", 1)[-1].split("run", 1)[-1].strip()
        return self.tools.execute_command(command)
    
    def execute_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a sequence of actions."""
        results = []
        for step in workflow:
            try:
                action = getattr(self, f"_handle_{step['action']}_request")
                result = action(**step.get("args", {}))
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error in workflow step {step}: {str(e)}")
                results.append({
                    "status": "error",
                    "message": str(e)
                })
        return {
            "status": "completed",
            "results": results
        } 