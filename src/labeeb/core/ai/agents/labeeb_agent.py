# This file is deprecated and should not be used. All logic is now in LabeebAgent.

"""
Labeeb Agent Implementation

This module implements the main Labeeb agent class.
"""

import logging
from typing import Dict, Any, List
from labeeb.platform_core.platform_manager import PlatformManager
from labeeb.core.ai.agents.base_agent import BaseAgent
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol

logger = logging.getLogger(__name__)

class LabeebAgent(BaseAgent, A2AProtocol, MCPProtocol, SmolAgentProtocol):
    """
    Main Labeeb agent implementation.
    Implements A2A, MCP, and SmolAgents protocols for enhanced agent communication.
    """
    
    def __init__(self, name: str = "Labeeb"):
        super().__init__()
        self.name = name
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.smol_protocol = SmolAgentProtocol()

    async def initialize(self) -> None:
        """Initialize the agent with platform-specific settings"""
        try:
            # Notify A2A protocol before initialization
            await self.a2a_protocol.notify_action("initialize", {"name": self.name})
            # Use MCP for initialization
            await self.mcp_protocol.execute_action("initialize", {"name": self.name})

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

            logger.info(f"Initialized Labeeb agent for {self.platform_info['name']}")
            
            # Notify SmolAgent protocol after initialization
            await self.smol_protocol.notify_completion("initialize", self.config)

        except Exception as e:
            error_msg = f"Error initializing agent: {str(e)}"
            await self.a2a_protocol.notify_error("initialize", error_msg)
            logger.error(error_msg)
            raise

    async def process_command(self, command: str) -> Dict[str, Any]:
        """Process a command using platform-specific handlers"""
        try:
            # Notify A2A protocol before command processing
            await self.a2a_protocol.notify_action("process_command", {"command": command})
            # Use MCP for command processing
            await self.mcp_protocol.execute_action("process_command", {"command": command})

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

            # Notify SmolAgent protocol after command processing
            await self.smol_protocol.notify_completion("process_command", result)
            return result

        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            await self.a2a_protocol.notify_error("process_command", error_msg)
            logger.error(error_msg)
            return {
                'status': 'error',
                'platform': self.platform_info['name'],
                'command': command,
                'error': str(e)
            }

    async def get_info(self) -> Dict[str, Any]:
        """Get detailed agent information"""
        try:
            # Notify A2A protocol before getting info
            await self.a2a_protocol.notify_action("get_info", {})
            # Use MCP for getting info
            await self.mcp_protocol.execute_action("get_info", {})

            result = {
                'name': self.name,
                'platform': self.platform_info['name'],
                'version': self.platform_info['version'],
                'capabilities': self.capabilities
            }

            # Notify SmolAgent protocol after getting info
            await self.smol_protocol.notify_completion("get_info", result)
            return result

        except Exception as e:
            error_msg = f"Error getting agent info: {str(e)}"
            await self.a2a_protocol.notify_error("get_info", error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    async def get_agent_info(self) -> Dict[str, Any]:
        """Get detailed agent information"""
        try:
            # Notify A2A protocol before getting agent info
            await self.a2a_protocol.notify_action("get_agent_info", {})
            # Use MCP for getting agent info
            await self.mcp_protocol.execute_action("get_agent_info", {})

            result = {
                'name': self.name,
                'platform': self.platform_info['name'],
                'version': self.platform_info['version'],
                'features': self.platform_info['features'],
                'handlers': list(self.handlers.keys())
            }

            # Notify SmolAgent protocol after getting agent info
            await self.smol_protocol.notify_completion("get_agent_info", result)
            return result

        except Exception as e:
            error_msg = f"Error getting agent info: {str(e)}"
            await self.a2a_protocol.notify_error("get_agent_info", error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    # A2A Protocol Methods
    async def register_agent(self, agent_id: str, capabilities: Dict[str, Any]) -> None:
        await self.a2a_protocol.register_agent(agent_id, capabilities)

    async def unregister_agent(self, agent_id: str) -> None:
        await self.a2a_protocol.unregister_agent(agent_id)

    # MCP Protocol Methods
    async def register_channel(self, channel_id: str, channel_type: str) -> None:
        await self.mcp_protocol.register_channel(channel_id, channel_type)

    async def unregister_channel(self, channel_id: str) -> None:
        await self.mcp_protocol.unregister_channel(channel_id)

    # SmolAgent Protocol Methods
    async def register_capability(self, capability: str, handler: callable) -> None:
        await self.smol_protocol.register_capability(capability, handler)

    async def unregister_capability(self, capability: str) -> None:
        await self.smol_protocol.unregister_capability(capability) 