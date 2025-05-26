#!/usr/bin/env python3
"""
Project Renaming Script
This script systematically renames project references from the old name to 'Labeeb'.
"""
import os
import re
import logging
from pathlib import Path
from typing import List, Set, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directories to exclude from processing
EXCLUDE_DIRS = {
    '.git',
    '__pycache__',
    'venv',
    'env',
    'node_modules',
    'build',
    'dist',
    'htmlcov',
    '.pytest_cache',
    '.coverage',
    '.idea',
    '.vscode'
}

# File extensions to process
TEXT_EXTENSIONS = {
    '.py', '.md', '.json', '.yaml', '.yml', '.ini', '.cfg',
    '.html', '.css', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
    '.sh', '.bash', '.zsh', '.fish', '.csh', '.tcsh', '.ksh',
    '.rst', '.tex', '.latex', '.bib', '.sty', '.cls',
    '.sql', '.pl', '.rb', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.swift', '.kt', '.kts', '.scala',
    '.php', '.rb', '.pl', '.pm', '.t', '.pod', '.podspec',
    '.gradle', '.properties', '.xml', '.toml', '.lock',
    '.env', '.env.example', '.env.local', '.env.development',
    '.env.test', '.env.production', '.env.staging',
    '.gitignore', '.dockerignore', '.editorconfig',
    '.prettierrc', '.eslintrc', '.stylelintrc',
    '.babelrc', '.browserslistrc', '.npmrc', '.yarnrc',
    '.travis.yml', '.circleci', '.github', '.gitlab',
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    'Makefile', 'CMakeLists.txt', 'package.json', 'package-lock.json',
    'yarn.lock', 'pnpm-lock.yaml', 'composer.json', 'composer.lock',
    'Gemfile', 'Gemfile.lock', 'Cargo.toml', 'Cargo.lock',
    'go.mod', 'go.sum', 'pom.xml', 'build.gradle', 'settings.gradle',
    'requirements.txt', 'setup.py', 'setup.cfg', 'pyproject.toml',
    'Pipfile', 'Pipfile.lock', 'poetry.lock', 'poetry.toml',
    'tox.ini', 'pytest.ini', '.coveragerc', '.flake8', '.pylintrc',
    'mypy.ini', 'bandit.yaml', 'safety.yaml', 'black.toml',
    'isort.cfg', 'pre-commit-config.yaml', '.pre-commit-config.yaml',
    'LICENSE', 'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md',
    'AUTHORS', 'NEWS', 'HISTORY', 'VERSION',
    'MANIFEST.in', 'PKG-INFO', 'setup.cfg', 'pyproject.toml',
    'conftest.py', 'pytest.ini', 'tox.ini', '.coveragerc',
    '.flake8', '.pylintrc', 'mypy.ini', 'bandit.yaml',
    'safety.yaml', 'black.toml', 'isort.cfg',
    'pre-commit-config.yaml', '.pre-commit-config.yaml',
    'LICENSE', 'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md',
    'AUTHORS', 'NEWS', 'HISTORY', 'VERSION',
    'MANIFEST.in', 'PKG-INFO'
}

# Files to preserve content
PRESERVE_FILES = {
    'TODO',
    'todo.txt',
    'notes.txt',
    '*.txt'  # Preserve all .txt files
}

def should_process_file(file_path: Path) -> bool:
    """Check if a file should be processed based on its extension and location."""
    # Skip files in excluded directories
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in file_path.parts:
            return False
    
    # Skip files that should be preserved
    for preserve_pattern in PRESERVE_FILES:
        if file_path.name == preserve_pattern or file_path.match(preserve_pattern):
            return False
    
    # Check file extension
    return file_path.suffix.lower() in TEXT_EXTENSIONS

def find_files_to_process(root_dir: Path) -> List[Path]:
    """Find all files that need to be processed."""
    files_to_process = []
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and should_process_file(file_path):
            files_to_process.append(file_path)
    
    return files_to_process

def process_file(file_path: Path, old_name: str, new_name: str) -> bool:
    """Process a single file, replacing old project name with new one."""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if file doesn't contain old name
        if old_name not in content:
            return False
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Replace old name with new name
        new_content = content.replace(old_name, new_name)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Updated {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    """Main entry point for the script."""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Get old and new project names
    old_name = input("Enter the old project name: ").strip()
    new_name = input("Enter the new project name: ").strip()
    
    if not old_name or not new_name:
        logger.error("Both old and new project names are required")
        return
    
    # Find files to process
    files_to_process = find_files_to_process(project_root)
    logger.info(f"Found {len(files_to_process)} files to process")
    
    # Process files
    updated_count = 0
    for file_path in files_to_process:
        if process_file(file_path, old_name, new_name):
            updated_count += 1
    
    logger.info(f"Updated {updated_count} files")
    logger.info("Backup files have been created with .bak extension. Please review the changes and remove backups if everything looks correct.")

if __name__ == "__main__":
    main() 