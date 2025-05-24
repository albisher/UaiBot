# core/ai_handler.py
import os
import json
import platform
import subprocess
import re
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from .model_manager import ModelManager
from .system_info_gatherer import SystemInfoGatherer
from .config_manager import ConfigManager
from uaibot.core.logging_config import get_logger
logger = get_logger(__name__)
from uaibot.core.cache_manager import CacheManager
from uaibot.core.exceptions import AIError, ConfigurationError
from uaibot.core.ai_performance_tracker import AIPerformanceTracker
from uaibot.core.model_config_manager import ModelConfigManager
from uaibot.core.key_manager import KeyManager
import psutil
from uaibot.typing import SystemInfo
from uaibot.core.command_processor.ai_command_extractor import AICommandExtractor

@dataclass
class PromptConfig:
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.95
    top_k: int = 40

@dataclass
class ResponseInfo:
    text: str
    raw_response: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class AIHandler:
    """
    Handles Ollama model interactions for UaiBot.
    Provides a unified interface for processing prompts and handling responses from Ollama.
    """
    def __init__(self, model_manager: ModelManager) -> None:
        self.model_manager = model_manager
        self.prompt_config = PromptConfig()
        self.command_extractor = AICommandExtractor()

    def process_prompt(self, prompt: str, extra_context: str = None) -> ResponseInfo:
        try:
            system_info = get_system_info()['platform']
            if extra_context:
                prompt = f"[Visual Context]: {extra_context}\n{prompt}"
            formatted_prompt = self.format_ai_prompt(prompt, system_info)
            logger.debug(f"Formatted AI prompt: {formatted_prompt}")
            response = self._get_model_response(formatted_prompt)
            logger.debug(f"Raw model response: {response}")
            success, plan, extraction_metadata = self.command_extractor.extract_command(response.get('response', ''))
            logger.debug(f"Extraction success: {success}, plan: {plan}, metadata: {extraction_metadata}")
            if not success or not plan:
                raise AIError(f"Failed to extract valid command from model response: {extraction_metadata.get('error_message')}")
            return ResponseInfo(
                text=json.dumps(plan, indent=2),
                raw_response=response,
                metadata=extraction_metadata
            )
        except Exception as e:
            logger.error(f"Error processing prompt: {str(e)}")
            raise

    def format_ai_prompt(self, prompt: str, system_info: str) -> str:
        """Format the prompt for the AI model with standardized instructions."""
        return f"""You are UaiBot, an AI assistant that helps users with tasks. Follow these guidelines:

1. Command Processing:
   - Focus on executing commands, not providing feedback
   - Break down complex commands into clear, sequential steps
   - Each step should have a clear description and operation
   - For system commands, provide the exact command to execute

2. Response Format:
   Always respond in this JSON format:
   {{
     "plan": [
       {{
         "step": "step_name",
         "description": "Clear description of what this step does",
         "operation": "system_command",
         "parameters": {{
           "command": "exact system command to execute"
         }},
         "confidence": 0.0-1.0,
         "conditions": null
       }}
     ]
   }}

3. System Information:
   Current system: {system_info}

User Command: {prompt}

Remember:
- Focus on executing commands, not providing feedback
- Use standardized response format
- Include confidence scores
- Break down complex commands into multiple steps
- Only include system commands that can be executed"""

    def _format_prompt(self, prompt: str) -> str:
        return f"User: {prompt}\nAssistant:"

    def _get_model_response(self, prompt: str) -> Dict[str, Any]:
        try:
            import ollama
            response = ollama.generate(
                model=self.model_manager.model_info.name,
                prompt=prompt,
                options={
                    "temperature": self.prompt_config.temperature,
                    "top_p": self.prompt_config.top_p,
                    "top_k": self.prompt_config.top_k,
                    "num_predict": self.prompt_config.max_tokens
                }
            )
            return response
        except Exception as e:
            logger.error(f"Error getting model response: {str(e)}")
            raise

    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        try:
            text = response.get("response", "")
            if not text:
                raise ValueError("Empty response from model")
            metadata = {
                "model": self.model_manager.model_info.name,
                "tokens": response.get("total_tokens", 0),
                "prompt_tokens": response.get("prompt_tokens", 0),
                "completion_tokens": response.get("completion_tokens", 0)
            }
            return {
                "text": text,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise

def get_system_info() -> SystemInfo:
    """Get system information.

    Returns:
        A dictionary containing system information
    """
    return {
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        },
        'cpu': {
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
            'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None,
            'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'cpu_usage_per_core': [x for x in psutil.cpu_percent(percpu=True, interval=1)],
            'total_cpu_usage': psutil.cpu_percent(interval=1),
        },
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'used': psutil.virtual_memory().used,
            'percentage': psutil.virtual_memory().percent,
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'used': psutil.disk_usage('/').used,
            'free': psutil.disk_usage('/').free,
            'percentage': psutil.disk_usage('/').percent,
        },
        'network': {
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_received': psutil.net_io_counters().bytes_recv,
            'packets_sent': psutil.net_io_counters().packets_sent,
            'packets_received': psutil.net_io_counters().packets_recv,
        },
    }

__all__ = ['get_system_info']
