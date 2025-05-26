#!/usr/bin/env python3
"""
Script to reorganize the Labeeb codebase according to the new architecture.
This script will:
1. Create necessary directories
2. Move files to their correct locations
3. Update import statements
4. Create missing __init__.py files
5. Support dry-run mode
6. Provide rollback capability
"""

import os
import shutil
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime

class CodebaseReorganizer:
    def __init__(self, root_dir: str = "labeeb", dry_run: bool = False):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.moved_files: Set[str] = set()
        self.created_dirs: Set[str] = set()
        self.backup_dir: Optional[Path] = None
        
        # Define the new directory structure
        self.new_structure = {
            "core": {
                "input": [
                    "input_handler.py",
                    "text_input_handler.py",
                    "voice_input_handler.py",
                    "image_input_handler.py",
                    "video_input_handler.py"
                ],
                "ai": [
                    "ai_handler.py",
                    "ai_command_interpreter.py",
                    "ai_response_cache.py",
                    "model_manager.py",
                    "ai_driven_processor.py",
                    "browser_search.py"
                ],
                "command_processor": [
                    "command_processor_main.py",
                    "command_registry.py",
                    "command_executor.py",
                    "ai_command_extractor.py",
                    "error_handler.py",
                    "direct_execution_handler.py",
                    "file_operations_handler.py",
                    "folder_search_handler.py",
                    "screen_session_manager.py",
                    "usb_query_handler.py",
                    "user_interaction_history.py"
                ],
                "output": [
                    "output_handler.py",
                    "text_output_handler.py",
                    "voice_output_handler.py",
                    "visual_output_handler.py",
                    "output_validator.py"
                ],
                "utils": [
                    "logging_config.py",
                    "logging_manager.py",
                    "memory_handler.py",
                    "query_processor.py",
                    "system_commands.py",
                    "system_info_gatherer.py"
                ]
            },
            "platform_uai": {
                "mac": [
                    "__init__.py",
                    "audio_handler.py",
                    "usb_handler.py",
                    "input_control/__init__.py",
                    "input_control/mac_input_handler.py",
                    "input_control/mac_voice_handler.py",
                    "input_control/mac_image_handler.py",
                    "input_control/mac_video_handler.py"
                ],
                "windows": [
                    "__init__.py",
                    "audio_handler.py",
                    "usb_handler.py",
                    "input_control/__init__.py",
                    "input_control/windows_input_handler.py",
                    "input_control/windows_voice_handler.py",
                    "input_control/windows_image_handler.py",
                    "input_control/windows_video_handler.py"
                ],
                "linux": [
                    "__init__.py",
                    "audio_handler.py",
                    "usb_handler.py",
                    "input_control/__init__.py",
                    "input_control/ubuntu_input_handler.py",
                    "input_control/ubuntu_voice_handler.py",
                    "input_control/ubuntu_image_handler.py",
                    "input_control/ubuntu_video_handler.py"
                ],
                "jetson": [
                    "__init__.py",
                    "audio_handler.py",
                    "usb_handler.py",
                    "input_control/__init__.py",
                    "input_control/jetson_input_handler.py",
                    "input_control/jetson_voice_handler.py",
                    "input_control/jetson_image_handler.py",
                    "input_control/jetson_video_handler.py"
                ]
            },
            "utils": [
                "file_utils.py",
                "parallel_utils.py",
                "system_health_check.py"
            ],
            "config": [
                "settings.json",
                "command_patterns.json",
                "output_styles.json",
                "output_paths.py",
                "config.json",
                "user_settings.json",
                "input_config.json",
                "output_config.json"
            ],
            "research": {
                "browser_automation": [
                    "browser_control.md",
                    "mouse_control.md",
                    "context_awareness.md",
                    "input_handling.md",
                    "implementation_guide.md"
                ],
                "multilingual": [
                    "language_detection.md",
                    "command_translation.md",
                    "response_localization.md",
                    "implementation_guide.md"
                ],
                "context_management": [
                    "context_persistence.md",
                    "context_validation.md",
                    "state_management.md",
                    "implementation_guide.md"
                ],
                "file_operations": [
                    "pattern_search.md",
                    "directory_management.md",
                    "file_flags.md",
                    "implementation_guide.md"
                ],
                "command_history": [
                    "history_tracking.md",
                    "history_persistence.md",
                    "history_search.md",
                    "implementation_guide.md"
                ],
                "error_handling": [
                    "error_recovery.md",
                    "user_feedback.md",
                    "validation_strategies.md",
                    "implementation_guide.md"
                ],
                "platform_specific": [
                    "platform_detection.md",
                    "cross_platform.md",
                    "os_specific.md",
                    "implementation_guide.md"
                ],
                "human_interaction": [
                    "user_feedback.md",
                    "interactive_commands.md",
                    "preferences.md",
                    "implementation_guide.md"
                ],
                "test_infrastructure": [
                    "test_configuration.md",
                    "test_execution.md",
                    "test_management.md",
                    "implementation_guide.md"
                ],
                "templates": [
                    "search_prompts.md",
                    "implementation_templates.md",
                    "test_templates.md",
                    "documentation_templates.md"
                ]
            }
        }
        
        # Define file mappings (old path -> new path)
        self.file_mappings = {
            # Input Components
            "core/input_handler.py": "core/input/input_handler.py",
            "core/text_input_handler.py": "core/input/text_input_handler.py",
            "core/voice_input_handler.py": "core/input/voice_input_handler.py",
            "core/image_input_handler.py": "core/input/image_input_handler.py",
            "core/video_input_handler.py": "core/input/video_input_handler.py",
            
            # AI Components
            "core/ai_handler.py": "core/ai/ai_handler.py",
            "core/ai_command_interpreter.py": "core/ai/ai_command_interpreter.py",
            "core/ai_response_cache.py": "core/ai/ai_response_cache.py",
            "core/model_manager.py": "core/ai/model_manager.py",
            "core/ai_driven_processor.py": "core/ai/ai_driven_processor.py",
            "core/browser_search.py": "core/ai/browser_search.py",
            
            # Command Processing
            "core/command_processor/command_processor_main.py": "core/command_processor/command_processor_main.py",
            "core/command_processor/command_registry.py": "core/command_processor/command_registry.py",
            "core/command_processor/command_executor.py": "core/command_processor/command_executor.py",
            "core/command_processor/ai_command_extractor.py": "core/command_processor/ai_command_extractor.py",
            "core/command_processor/error_handler.py": "core/command_processor/error_handler.py",
            "core/command_processor/direct_execution_handler.py": "core/command_processor/direct_execution_handler.py",
            "core/command_processor/file_operations_handler.py": "core/command_processor/file_operations_handler.py",
            "core/command_processor/folder_search_handler.py": "core/command_processor/folder_search_handler.py",
            "core/command_processor/screen_session_manager.py": "core/command_processor/screen_session_manager.py",
            "core/command_processor/usb_query_handler.py": "core/command_processor/usb_query_handler.py",
            "core/command_processor/user_interaction_history.py": "core/command_processor/user_interaction_history.py",
            
            # Output Components
            "core/output_handler.py": "core/output/output_handler.py",
            "core/text_output_handler.py": "core/output/text_output_handler.py",
            "core/voice_output_handler.py": "core/output/voice_output_handler.py",
            "core/visual_output_handler.py": "core/output/visual_output_handler.py",
            "core/output_validator.py": "core/output/output_validator.py",
            
            # Core Utils
            "core/logging_config.py": "core/utils/logging_config.py",
            "core/logging_manager.py": "core/utils/logging_manager.py",
            "core/memory_handler.py": "core/utils/memory_handler.py",
            "core/query_processor.py": "core/utils/query_processor.py",
            "core/system_commands.py": "core/utils/system_commands.py",
            "core/system_info_gatherer.py": "core/utils/system_info_gatherer.py",
            
            # Utilities
            "utils/file_utils.py": "utils/file_utils.py",
            "utils/parallel_utils.py": "utils/parallel_utils.py",
            "utils/system_health_check.py": "utils/system_health_check.py",
            
            # Configuration
            "config/settings.json": "config/settings.json",
            "config/command_patterns.json": "config/command_patterns.json",
            "config/output_styles.json": "config/output_styles.json",
            "config/output_paths.py": "config/output_paths.py",
            "config/config.json": "config/config.json",
            "config/user_settings.json": "config/user_settings.json",
            "config/input_config.json": "config/input_config.json",
            "config/output_config.json": "config/output_config.json",
            
            # Research Templates
            "research/templates/search_prompts.md": "research/templates/search_prompts.md",
            "research/templates/implementation_templates.md": "research/templates/implementation_templates.md",
            "research/templates/test_templates.md": "research/templates/test_templates.md",
            "research/templates/documentation_templates.md": "research/templates/documentation_templates.md"
        }

        # Define templates for new files
        self.file_templates = {
            "core/input/input_handler.py": '''"""
Input Handler module for Labeeb.
Handles all types of input processing.
"""
from typing import Dict, Any, Optional

class InputHandler:
    def __init__(self):
        self.initialized = False
        
    def process_input(self, input_data: Any) -> Dict[str, Any]:
        """Process any type of input."""
        pass
        
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data."""
        pass
        
    def normalize_input(self, input_data: Any) -> Dict[str, Any]:
        """Normalize input to standard format."""
        pass
''',
            "core/output/output_handler.py": '''"""
Output Handler module for Labeeb.
Handles all types of output processing.
"""
from typing import Dict, Any, Optional

class OutputHandler:
    def __init__(self):
        self.initialized = False
        
    def process_output(self, output_data: Any) -> Dict[str, Any]:
        """Process output data."""
        pass
        
    def validate_output(self, output_data: Any) -> bool:
        """Validate output data."""
        pass
        
    def deliver_output(self, output_data: Any) -> None:
        """Deliver output to user."""
        pass
''',
            "research/templates/search_prompts.md": '''# Search Prompts Template

## Feature: [Feature Name]

### Search Prompt
```
[Main search prompt]
```

### Key Requirements
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

### Implementation Considerations
- [Consideration 1]
- [Consideration 2]
- [Consideration 3]

### Required Libraries
- [Library 1]
- [Library 2]
- [Library 3]

### Example Usage
```python
# Example code
```

### Expected Behavior
- [Behavior 1]
- [Behavior 2]
- [Behavior 3]
''',
            
            "research/templates/implementation_templates.md": '''# Implementation Template

## Feature: [Feature Name]

### Overview
[Brief description of the feature]

### Requirements
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

### Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Code Structure
```python
# Code structure
```

### Testing Strategy
- [Test 1]
- [Test 2]
- [Test 3]

### Documentation
- [Doc 1]
- [Doc 2]
- [Doc 3]
''',
            
            "research/templates/test_templates.md": '''# Test Template

## Feature: [Feature Name]

### Test Cases
1. [Test Case 1]
2. [Test Case 2]
3. [Test Case 3]

### Test Data
```python
# Test data
```

### Expected Results
- [Result 1]
- [Result 2]
- [Result 3]

### Edge Cases
- [Edge Case 1]
- [Edge Case 2]
- [Edge Case 3]
''',
            
            "research/templates/documentation_templates.md": '''# Documentation Template

## Feature: [Feature Name]

### Overview
[Brief description]

### Usage
```python
# Usage example
```

### API Reference
- [API 1]
- [API 2]
- [API 3]

### Examples
1. [Example 1]
2. [Example 2]
3. [Example 3]

### Notes
- [Note 1]
- [Note 2]
- [Note 3]
'''
        }

    def create_backup(self):
        """Create a backup of the current codebase."""
        if self.dry_run:
            print("Dry run: Would create backup")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.root_dir.parent / f"Labeeb_backup_{timestamp}"
        
        if self.root_dir.exists():
            shutil.copytree(self.root_dir, self.backup_dir)
            print(f"Created backup at: {self.backup_dir}")

    def rollback(self):
        """Rollback changes using the backup."""
        if not self.backup_dir or not self.backup_dir.exists():
            print("No backup found for rollback")
            return
            
        if self.dry_run:
            print(f"Dry run: Would rollback to {self.backup_dir}")
            return
            
        # Remove current directory
        if self.root_dir.exists():
            shutil.rmtree(self.root_dir)
            
        # Restore from backup
        shutil.copytree(self.backup_dir, self.root_dir)
        print(f"Rolled back to backup at: {self.backup_dir}")

    def create_directory_structure(self):
        """Create the new directory structure."""
        print("Creating directory structure...")
        
        def create_dirs(base_path: Path, structure: Dict):
            for dir_name, content in structure.items():
                dir_path = base_path / dir_name
                if not dir_path.exists():
                    if not self.dry_run:
                        dir_path.mkdir(parents=True)
                    self.created_dirs.add(str(dir_path))
                    print(f"{'Would create' if self.dry_run else 'Created'} directory: {dir_path}")
                
                if isinstance(content, dict):
                    create_dirs(dir_path, content)
                elif isinstance(content, list):
                    # Create __init__.py if it doesn't exist
                    init_file = dir_path / "__init__.py"
                    if not init_file.exists():
                        if not self.dry_run:
                            init_file.touch()
                        print(f"{'Would create' if self.dry_run else 'Created'} __init__.py: {init_file}")

        create_dirs(self.root_dir, self.new_structure)

    def move_files(self):
        """Move files to their new locations."""
        print("\nMoving files to new locations...")
        
        for old_path, new_path in self.file_mappings.items():
            old_file = self.root_dir / old_path
            new_file = self.root_dir / new_path
            
            if old_file.exists():
                # Create parent directory if it doesn't exist
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                if not self.dry_run:
                    # Move the file
                    shutil.move(str(old_file), str(new_file))
                self.moved_files.add(str(new_file))
                print(f"{'Would move' if self.dry_run else 'Moved'}: {old_file} -> {new_file}")

    def update_imports(self):
        """Update import statements in moved files."""
        print("\nUpdating import statements...")
        
        for file_path in self.moved_files:
            if not file_path.endswith('.py'):
                continue
                
            if not self.dry_run:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update imports based on new structure
                new_content = self._update_import_paths(content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            print(f"{'Would update' if self.dry_run else 'Updated'} imports in: {file_path}")

    def _update_import_paths(self, content: str) -> str:
        """Update import paths in file content."""
        # Define import path mappings
        import_mappings = {
            r'from labeeb\.core\.command_processor import': 'from app.core.command_processor import',
            r'from labeeb\.core\.ai import': 'from app.core.ai import',
            r'from labeeb\.core\.device_manager import': 'from app.core.device_manager import',
            r'from labeeb\.core\.screen_handler import': 'from app.core.screen_handler import',
            r'from labeeb\.utils import': 'from app.utils import',
            r'from labeeb\.core\.utils import': 'from app.core.utils import',
            r'from labeeb\.platform_uai import': 'from app.platform_uai import'
        }
        
        for old_pattern, new_pattern in import_mappings.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        return content

    def create_missing_files(self):
        """Create missing files with basic templates."""
        print("\nCreating missing files...")
        
        def create_file_if_missing(path: Path, template: str = ""):
            if not path.exists():
                if not self.dry_run:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(template)
                print(f"{'Would create' if self.dry_run else 'Created'} file: {path}")

        # Create missing core files
        for dir_name, files in self.new_structure["core"].items():
            if isinstance(files, list):
                for file_name in files:
                    file_path = self.root_dir / "core" / dir_name / file_name
                    template = self.file_templates.get(f"core/{dir_name}/{file_name}", "")
                    create_file_if_missing(file_path, template)

        # Create missing platform files
        for platform in self.new_structure["platform_uai"]:
            for file_name in self.new_structure["platform_uai"][platform]:
                file_path = self.root_dir / "platform_uai" / platform / file_name
                create_file_if_missing(file_path)

    def run(self):
        """Run the reorganization process."""
        print("Starting codebase reorganization...")
        if self.dry_run:
            print("Running in DRY RUN mode - no changes will be made")
        
        try:
            self.create_backup()
            self.create_directory_structure()
            self.move_files()
            self.update_imports()
            self.create_missing_files()
            
            print("\nReorganization completed successfully!")
            print(f"{'Would create' if self.dry_run else 'Created'} {len(self.created_dirs)} directories")
            print(f"{'Would move' if self.dry_run else 'Moved'} {len(self.moved_files)} files")
            
        except Exception as e:
            print(f"\nError during reorganization: {str(e)}")
            if not self.dry_run:
                print("Attempting rollback...")
                self.rollback()
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Reorganize Labeeb codebase")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without making them")
    parser.add_argument("--root-dir", default="labeeb", help="Root directory of the codebase")
    
    args = parser.parse_args()
    
    reorganizer = CodebaseReorganizer(root_dir=args.root_dir, dry_run=args.dry_run)
    reorganizer.run() 