"""
Test script for UaiBot system.

This script performs comprehensive testing of the UaiBot system,
including initialization, health checks, and basic functionality tests.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.ai_handler import AIHandler
from uaibot.core.command_processor.command_processor import CommandProcessor
from uaibot.core.command_processor.command_processor_monitor import CommandProcessorMonitor
from uaibot.core.command_processor.command_processor_metrics import CommandProcessorMetrics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_system() -> Dict[str, Any]:
    """Initialize the UaiBot system components."""
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        logger.info("Configuration manager initialized")

        # Initialize model manager
        model_manager = ModelManager(config_manager)
        logger.info("Model manager initialized")

        # Initialize AI handler
        ai_handler = AIHandler(model_manager)
        logger.info("AI handler initialized")

        # Initialize command processor
        command_processor = CommandProcessor(ai_handler)
        logger.info("Command processor initialized")

        # Initialize monitor
        monitor = CommandProcessorMonitor()
        logger.info("System monitor initialized")

        # Initialize metrics
        metrics = CommandProcessorMetrics()
        logger.info("Metrics collector initialized")

        return {
            "config_manager": config_manager,
            "model_manager": model_manager,
            "ai_handler": ai_handler,
            "command_processor": command_processor,
            "monitor": monitor,
            "metrics": metrics
        }

    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        raise

def run_health_checks(components: Dict[str, Any]) -> bool:
    """Run health checks on system components."""
    try:
        # Check command processor health
        processor_health = components["monitor"].check_health("command_processor")
        logger.info(f"Command processor health: {processor_health}")

        # Check model manager health
        model_health = components["monitor"].check_health("model_manager")
        logger.info(f"Model manager health: {model_health}")

        # Check AI handler health
        ai_health = components["monitor"].check_health("ai_handler")
        logger.info(f"AI handler health: {ai_health}")

        # Collect system metrics
        metrics = components["metrics"].collect_metrics()
        logger.info(f"System metrics: {metrics}")

        return all([
            processor_health.status == "healthy",
            model_health.status == "healthy",
            ai_health.status == "healthy"
        ])

    except Exception as e:
        logger.error(f"Error running health checks: {e}")
        return False

def test_basic_functionality(components: Dict[str, Any]) -> bool:
    """Test basic system functionality."""
    try:
        # Test simple command
        result = components["command_processor"].process_command("What is the current time?")
        logger.info(f"Command result: {result}")

        # Test command with parameters
        result = components["command_processor"].process_command("Show system information")
        logger.info(f"Command result: {result}")

        return result.success

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