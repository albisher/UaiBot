#!/usr/bin/env python3
"""
Browser Search Command for UaiBot
Integrates the browser search demo with the main UaiBot interface.
"""
import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from app.core.logging_config import get_logger
from demo.browser_search_demo import demo_browser_search

logger = get_logger(__name__)

def execute_browser_search():
    """Execute the browser search demo."""
    try:
        demo_browser_search()
        return "Browser search demo completed successfully!"
    except Exception as e:
        logger.error(f"Error in browser search demo: {str(e)}")
        return f"Error during browser search demo: {str(e)}"

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Run the demo
    result = execute_browser_search()
    print(result) 