"""
Labeeb - An intelligent agent framework for automation and assistance.

This module serves as the main entry point for starting the Labeeb agent.
It handles initialization, configuration loading, and agent startup.
"""

import logging
from app.core.ai.agents.labeeb_agent import LabeebAgent
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

def main():
    """Main entry point for starting Labeeb"""
    try:
        # Initialize platform manager
        platform_manager = PlatformManager()
        if not platform_manager.initialize():
            logger.error("Failed to initialize platform manager")
            return

        # Initialize agent
        agent = LabeebAgent()
        agent.initialize()

        logger.info("Labeeb agent started successfully")
        
        # Main event loop would go here
        # For now, just keep the process running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Shutting down Labeeb agent")
            agent.cleanup()
            platform_manager.cleanup()

    except Exception as e:
        logger.error(f"Error starting Labeeb: {str(e)}")
        raise

if __name__ == "__main__":
    main()
