#!/usr/bin/env python3
import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

def move_file(src, dst):
    """Move file from src to dst."""
    if os.path.exists(src):
        shutil.move(src, dst)
        logger.info(f"Moved {src} to {dst}")

def copy_file(src, dst):
    """Copy file from src to dst."""
    if os.path.exists(src):
        shutil.copy2(src, dst)
        logger.info(f"Copied {src} to {dst}")

def main():
    # Root directory structure
    root_dirs = [
        'src',
        'tests',
        'docs',
        'config',
        'plugins',
        'scripts',
        'data',
        'logs',
        'research',
        'secret',
        'master'
    ]

    # Create root directories
    for dir_name in root_dirs:
        create_directory(dir_name)

    # AI-specific directories
    ai_dirs = [
        'src/app/core/ai/agents',
        'src/app/core/ai/tools',
        'src/app/core/ai/models',
        'src/app/core/ai/workflows',
        'src/app/core/ai/protocols',
        'src/app/core/ai/guides',
        'src/app/core/ai/examples',
        'src/app/core/ai/development',
        'src/app/core/ai/production',
        'src/app/core/ai/testing',
        'src/app/core/ai/core',
        'src/app/core/ai/extensions',
        'src/app/core/ai/integrations',
        'src/app/core/ai/setup',
        'src/app/core/ai/utils',
        'src/app/core/ai/training',
        'src/app/core/ai/cache',
        'src/app/core/ai/application',
        'src/app/core/ai/error',
        'src/app/core/ai/audit'
    ]

    # Create AI directories
    for dir_path in ai_dirs:
        create_directory(dir_path)

    # Integration test files
    integration_tests = [
        'tests/integration/test_end_to_end_task_completion.py',
        'tests/integration/test_cross_agent_tool_usage.py',
        'tests/integration/test_multi_pc_synchronization.py',
        'tests/integration/test_protocol_switching.py'
    ]

    # Create integration test files
    for test_file in integration_tests:
        if not os.path.exists(test_file):
            with open(test_file, 'w') as f:
                f.write('# Integration test file\n')
            logger.info(f"Created test file: {test_file}")

    # Move platform-specific code to platform_core
    platform_core = 'src/app/core/platform_core'
    create_directory(platform_core)

    # Move platform-specific files
    platform_files = [
        ('src/app/platform_core/macos', 'src/app/core/platform_core/macos'),
        ('src/app/platform_core/windows', 'src/app/core/platform_core/windows'),
        ('src/app/platform_core/ubuntu', 'src/app/core/platform_core/ubuntu'),
        ('src/app/platform_core/common', 'src/app/core/platform_core/common')
    ]

    for src, dst in platform_files:
        if os.path.exists(src):
            shutil.move(src, dst)
            logger.info(f"Moved {src} to {dst}")

    logger.info("Project reorganization completed successfully!")

if __name__ == '__main__':
    main() 