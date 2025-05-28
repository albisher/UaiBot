#!/usr/bin/env python3
"""
Labeeb Architecture Audit Tool
Validates project structure against master architecture specifications.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArchitectureAuditor:
    """Validates project structure against master architecture specifications."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations: List[Dict] = []
        self.required_dirs = {
            'src/labeeb': {
                'required_files': ['__init__.py', '__main__.py'],
                'required_dirs': ['ai', 'awareness', 'command_processing', 'config_loader',
                                'constants', 'core', 'data_models', 'exceptions',
                                'platform_services', 'services', 'tools', 'ui', 'utils']
            },
            'tests': {
                'required_files': ['__init__.py', 'conftest.py'],
                'required_dirs': ['fixtures', 'integration', 'unit', 'e2e', 'test_files']
            },
            'docs': {
                'required_dirs': ['agents_tools', 'architecture', 'features', 'research']
            },
            'config': {
                'required_files': ['settings.json']
            },
            'locales': {
                'required_dirs': ['ar/LC_MESSAGES', 'en/LC_MESSAGES']
            }
        }
        
        self.ignored_patterns = {
            '*.pyc', '*.pyo', '*.pyd', '__pycache__', '*.so',
            '.coverage', 'coverage.xml', 'htmlcov',
            '.pytest_cache', '.cache',
            '*.egg-info', 'dist', 'build', '*.egg',
            '.venv', 'venv',
            '*.log', 'nohup.out',
            '.vscode', '.idea',
            '*.bak'
        }

    def audit(self) -> Tuple[bool, List[Dict]]:
        """
        Perform full architecture audit.
        
        Returns:
            Tuple[bool, List[Dict]]: (success, violations)
        """
        logger.info("Starting architecture audit...")
        
        # Check required directories and files
        self._check_required_structure()
        
        # Check for backup files and directories
        self._check_backups()
        
        # Check for files in incorrect locations
        self._check_file_locations()
        
        # Check for proper gitignore patterns
        self._check_gitignore()
        
        success = len(self.violations) == 0
        if success:
            logger.info("Architecture audit passed successfully!")
        else:
            logger.warning(f"Architecture audit found {len(self.violations)} violations")
            
        return success, self.violations

    def _check_required_structure(self) -> None:
        """Check for required directories and files."""
        for dir_path, requirements in self.required_dirs.items():
            full_path = self.project_root / dir_path
            
            if not full_path.exists():
                self.violations.append({
                    'type': 'missing_directory',
                    'path': dir_path,
                    'message': f"Required directory '{dir_path}' does not exist"
                })
                continue
                
            # Check required files
            for file_name in requirements.get('required_files', []):
                file_path = full_path / file_name
                if not file_path.exists():
                    self.violations.append({
                        'type': 'missing_file',
                        'path': str(file_path.relative_to(self.project_root)),
                        'message': f"Required file '{file_name}' missing in '{dir_path}'"
                    })
            
            # Check required subdirectories
            for subdir in requirements.get('required_dirs', []):
                subdir_path = full_path / subdir
                if not subdir_path.exists():
                    self.violations.append({
                        'type': 'missing_directory',
                        'path': str(subdir_path.relative_to(self.project_root)),
                        'message': f"Required subdirectory '{subdir}' missing in '{dir_path}'"
                    })

    def _check_backups(self) -> None:
        """Check for backup files and directories."""
        for root, dirs, files in os.walk(self.project_root):
            # Check for backup directories
            if '.backup' in dirs:
                self.violations.append({
                    'type': 'backup_directory',
                    'path': str(Path(root).relative_to(self.project_root) / '.backup'),
                    'message': "Backup directory found - use version control instead"
                })
            
            # Check for backup files
            for file in files:
                if file.endswith('.bak'):
                    self.violations.append({
                        'type': 'backup_file',
                        'path': str(Path(root).relative_to(self.project_root) / file),
                        'message': "Backup file found - use version control instead"
                    })

    def _check_file_locations(self) -> None:
        """Check for files in incorrect locations."""
        # Check for tests in src directory
        src_tests = self.project_root / 'src' / 'tests'
        if src_tests.exists():
            self.violations.append({
                'type': 'incorrect_location',
                'path': str(src_tests.relative_to(self.project_root)),
                'message': "Tests found in src directory - should be in top-level tests/"
            })
        
        # Check for logs in src directory
        src_logs = self.project_root / 'src' / 'logs'
        if src_logs.exists():
            self.violations.append({
                'type': 'incorrect_location',
                'path': str(src_logs.relative_to(self.project_root)),
                'message': "Logs found in src directory - should be in top-level logs/"
            })

    def _check_gitignore(self) -> None:
        """Check for proper gitignore patterns."""
        gitignore_path = self.project_root / '.gitignore'
        if not gitignore_path.exists():
            self.violations.append({
                'type': 'missing_file',
                'path': '.gitignore',
                'message': "Missing .gitignore file"
            })
            return
            
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            
        for pattern in self.ignored_patterns:
            if pattern not in gitignore_content:
                self.violations.append({
                    'type': 'gitignore_pattern',
                    'pattern': pattern,
                    'message': f"Missing gitignore pattern: {pattern}"
                })

def main():
    """Main entry point for the architecture audit tool."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    auditor = ArchitectureAuditor(project_root)
    
    success, violations = auditor.audit()
    
    # Generate audit report
    report = {
        'timestamp': datetime.now().isoformat(),
        'success': success,
        'violations': violations
    }
    
    # Save report to tests/results
    results_dir = Path(project_root) / 'tests' / 'results'
    results_dir.mkdir(exist_ok=True)
    
    report_path = results_dir / 'architecture_audit.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    # Update TODO.md with audit results
    todo_path = Path(project_root) / 'docs' / 'development' / 'todo' / 'TODO.md'
    if todo_path.exists():
        with open(todo_path, 'r') as f:
            todo_content = f.read()
            
        # Add or update audit section
        audit_section = f"""
## Architecture Audit Results
Last audit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {'✅ Passed' if success else '❌ Failed'}
Violations: {len(violations)}
"""
        
        if '## Architecture Audit Results' in todo_content:
            # Update existing section
            import re
            todo_content = re.sub(
                r'## Architecture Audit Results.*?(?=##|$)',
                audit_section,
                todo_content,
                flags=re.DOTALL
            )
        else:
            # Add new section
            todo_content += f"\n{audit_section}"
            
        with open(todo_path, 'w') as f:
            f.write(todo_content)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 