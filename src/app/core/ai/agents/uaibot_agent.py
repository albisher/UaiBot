import logging
from typing import Dict, Any, List
from app.platform_core.platform_manager import PlatformManager
from app.core.ai.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class UaiBotAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()

    def initialize(self) -> None:
        """Initialize the agent with platform-specific settings"""
        try:
            # Initialize platform-specific handlers
            for handler_name, handler in self.handlers.items():
                try:
                    handler.initialize()
                    logger.info(f"Initialized {handler_name} handler")
                except Exception as e:
                    logger.error(f"Error initializing {handler_name} handler: {str(e)}")
                    raise

            # Set up agent configuration based on platform
            self.config.update({
                'platform': self.platform_info['name'],
                'version': self.platform_info['version'],
                'features': self.platform_info['features'],
                'paths': self.platform_info['paths']
            })

            logger.info(f"Initialized UaiBot agent for {self.platform_info['name']}")

        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}")
            raise

    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a command using platform-specific handlers"""
        try:
            result = {
                'status': 'success',
                'platform': self.platform_info['name'],
                'command': command,
                'output': None
            }

            # Use platform-specific handlers to process the command
            for handler_name, handler in self.handlers.items():
                try:
                    handler_result = handler.process_command(command)
                    if handler_result['status'] == 'success':
                        result['output'] = handler_result['output']
                        break
                except Exception as e:
                    logger.error(f"Error processing command with {handler_name}: {str(e)}")
                    continue

            if result['output'] is None:
                result['status'] = 'error'
                result['error'] = 'No handler could process the command'

            return result

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                'status': 'error',
                'platform': self.platform_info['name'],
                'command': command,
                'error': str(e)
            }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get detailed agent information"""
        return {
            'name': 'UaiBot',
            'platform': self.platform_info['name'],
            'version': self.platform_info['version'],
            'features': self.platform_info['features'],
            'handlers': list(self.handlers.keys())
        } 