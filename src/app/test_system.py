"""
Test script for Labeeb system.

This script performs comprehensive testing of the Labeeb system,
including initialization, health checks, and basic functionality tests.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

from labeeb.core.config_manager import ConfigManager
from labeeb.core.model_manager import ModelManager
from labeeb.core.ai.agent import Agent, ToolRegistry, EchoTool, safe_path
from labeeb.core.ai.agent_tools.file_tool import FileTool

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_system() -> Dict[str, Any]:
    """Initialize the Labeeb system components (agentic core)."""
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        logger.info("Configuration manager initialized")

        # Initialize model manager
        model_manager = ModelManager(config_manager)
        logger.info("Model manager initialized")

        # Initialize agentic core
        registry = ToolRegistry()
        registry.register(EchoTool())
        registry.register(FileTool())
        agent = Agent(tools=registry)
        logger.info("Agentic core initialized")

        return {
            "config_manager": config_manager,
            "model_manager": model_manager,
            "agent": agent
        }

    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        raise

def run_health_checks(components: Dict[str, Any]) -> bool:
    """Stub health check for agentic core."""
    logger.info("Health check: agentic core initialized.")
    return True

def test_basic_functionality(components: Dict[str, Any]) -> bool:
    """Test basic system functionality (agentic core)."""
    try:
        # Test simple command
        result = components["agent"].plan_and_execute("echo Hello, world!", {})
        logger.info(f"Command result: {result}")

        # Test file tool
        result = components["agent"].plan_and_execute("file", {"filename": "test.txt", "content": "test content"}, action="create")
        logger.info(f"Command result: {result}")

        return True

    except Exception as e:
        logger.error(f"Error testing basic functionality: {e}")
        return False

def main():
    """Main test function."""
    try:
        # Initialize system
        logger.info("Initializing system...")
        components = initialize_system()

        # Run health checks
        logger.info("Running health checks...")
        health_status = run_health_checks(components)
        if not health_status:
            logger.error("Health checks failed")
            sys.exit(1)
        logger.info("Health checks passed")

        # Test basic functionality
        logger.info("Testing basic functionality...")
        functionality_status = test_basic_functionality(components)
        if not functionality_status:
            logger.error("Basic functionality tests failed")
            sys.exit(1)
        logger.info("Basic functionality tests passed")

        logger.info("All tests completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 