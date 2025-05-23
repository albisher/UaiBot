#!/usr/bin/env python3
"""
Script to run all random tasks from random_tasks.txt through the main UaiBot interface.
"""

from pathlib import Path
import logging
import sys

# Ensure src is in the import path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uaibot.main import UaiBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    tasks_file = Path("random_tasks.txt")
    if not tasks_file.exists():
        logger.error(f"File not found: {tasks_file}")
        return

    # Initialize UaiBot (adjust parameters as needed)
    bot = UaiBot(debug=True, mode='command', fast_mode=True)

    with tasks_file.open("r") as f:
        tasks = [line.strip() for line in f if line.strip()]

    logger.info(f"Loaded {len(tasks)} tasks from {tasks_file}")

    for i, task in enumerate(tasks, 1):
        print(f"\nTask {i}: {task}")
        try:
            response = bot.process_single_command(task)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 