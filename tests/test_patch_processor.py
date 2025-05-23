"""
Tests for processing patch files and generating readable reports.
"""
import os
import json
import pytest
from src.datetime import datetime
from src.typing import Dict, List, Any
from app.core.ai_handler import AIHandler
from app.core.model_config_manager import ModelConfigManager

def verify_file_organization(filepath: str) -> None:
    """
    Verify that a file is in the correct directory according to project rules.
    
    Args:
        filepath: Path to the file to verify
        
    Raises:
        ValueError: If file is not in the correct directory
    """
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Define allowed directories and their purposes
    allowed_dirs = {
        'app': 'Source code',
        'tests': 'Test files',
        'scripts': 'Executable scripts',
        'config': 'Configuration files',
        'docs': 'Documentation',
        'reports': 'Generated reports'
    }
    
    # Get the relative path from project root
    rel_path = os.path.relpath(filepath, project_root)
    dir_name = rel_path.split(os.sep)[0]
    
    # Verify the file is in an allowed directory
    if dir_name not in allowed_dirs:
        raise ValueError(
            f"File '{rel_path}' is not in an allowed directory. "
            f"Allowed directories: {', '.join(allowed_dirs.keys())}"
        )

class PatchProcessor:
    """Processes patch files and generates readable reports."""
    
    def __init__(self, ai_handler: AIHandler):
        """
        Initialize the patch processor.
        
        Args:
            ai_handler: AIHandler instance for processing commands
        """
        self.ai_handler = ai_handler
        self.results: Dict[str, List[Dict[str, Any]]] = {}
    
    def process_patch_file(self, filepath: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process a patch file and generate results.
        
        Args:
            filepath: Path to the patch file
            
        Returns:
            Dictionary containing processed results by category
            
        Raises:
            ValueError: If file is not in the correct directory
        """
        # Verify file organization
        verify_file_organization(filepath)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Split content into categories
        categories = self._split_into_categories(content)
        
        # Process each category
        for category, commands in categories.items():
            self.results[category] = []
            for command in commands:
                if command.strip():
                    result = self._process_command(command.strip())
                    self.results[category].append({
                        'command': command.strip(),
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
        
        return self.results
    
    def _split_into_categories(self, content: str) -> Dict[str, List[str]]:
        """
        Split patch file content into categories.
        
        Args:
            content: Content of the patch file
            
        Returns:
            Dictionary mapping categories to lists of commands
        """
        categories = {}
        current_category = None
        
        for line in content.split('\n'):
            if line.startswith('# '):
                current_category = line[2:].strip()
                categories[current_category] = []
            elif current_category and line.strip():
                categories[current_category].append(line)
        
        return categories
    
    def _process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a single command using the AI handler.
        
        Args:
            command: Command to process
            
        Returns:
            Dictionary containing the processing result
        """
        try:
            return self.ai_handler.process_command(command)
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def generate_report(self, output_file: str) -> None:
        """
        Generate a readable report from the processed results.
        
        Args:
            output_file: Path to save the report
            
        Raises:
            ValueError: If file is not in the correct directory
        """
        # Verify file organization
        verify_file_organization(output_file)
        
        report = []
        
        for category, commands in self.results.items():
            report.append(f"\n{'='*80}\n{category}\n{'='*80}\n")
            
            for cmd_result in commands:
                report.append(f"\nCommand: {cmd_result['command']}")
                report.append(f"Timestamp: {cmd_result['timestamp']}")
                
                if 'error' in cmd_result['result']:
                    report.append(f"Status: Failed")
                    report.append(f"Error: {cmd_result['result']['error']}")
                else:
                    report.append(f"Status: Success")
                    report.append(f"Model: {cmd_result['result'].get('model', 'Unknown')}")
                    report.append(f"Confidence: {cmd_result['result'].get('confidence', 'N/A')}")
                    report.append(f"Response: {cmd_result['result'].get('command', '')}")
                    if 'explanation' in cmd_result['result']:
                        report.append(f"Explanation: {cmd_result['result']['explanation']}")
                
                report.append("-" * 80)
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))

@pytest.fixture
def ai_handler():
    """Create an AI handler instance for testing."""
    return AIHandler(
        model_type='ollama',
        debug=True
    )

@pytest.fixture
def patch_processor(ai_handler):
    """Create a patch processor instance for testing."""
    return PatchProcessor(ai_handler)

def test_patch_processor_initialization(patch_processor):
    """Test patch processor initialization."""
    assert patch_processor.ai_handler is not None
    assert isinstance(patch_processor.results, dict)
    assert len(patch_processor.results) == 0

def test_category_splitting(patch_processor):
    """Test splitting patch file content into categories."""
    content = """# Category 1
command1
command2

# Category 2
command3
command4"""
    
    categories = patch_processor._split_into_categories(content)
    assert len(categories) == 2
    assert 'Category 1' in categories
    assert 'Category 2' in categories
    assert len(categories['Category 1']) == 2
    assert len(categories['Category 2']) == 2

def test_command_processing(patch_processor):
    """Test processing individual commands."""
    command = "show me the system load"
    result = patch_processor._process_command(command)
    assert isinstance(result, dict)
    assert 'command' in result or 'error' in result

def test_patch_file_processing(patch_processor, tmp_path):
    """Test processing a complete patch file."""
    # Create a test patch file in the correct directory
    patch_file = tmp_path / "test_patch.txt"
    patch_file.write_text("""# System Information
show system load
check memory usage

# File Operations
list files
check permissions""")
    
    # Process the file
    results = patch_processor.process_patch_file(str(patch_file))
    assert len(results) == 2
    assert 'System Information' in results
    assert 'File Operations' in results

def test_report_generation(patch_processor, tmp_path):
    """Test generating a readable report."""
    # Create test results
    patch_processor.results = {
        'Test Category': [
            {
                'command': 'test command',
                'result': {
                    'command': 'test response',
                    'confidence': 0.95,
                    'model': 'test-model'
                },
                'timestamp': datetime.now().isoformat()
            }
        ]
    }
    
    # Generate report in the correct directory
    report_file = tmp_path / "test_report.txt"
    patch_processor.generate_report(str(report_file))
    
    # Verify report content
    assert report_file.exists()
    content = report_file.read_text()
    assert 'Test Category' in content
    assert 'test command' in content
    assert 'test response' in content

def test_error_handling(patch_processor):
    """Test handling of command processing errors."""
    # Test with an invalid command
    result = patch_processor._process_command("invalid command that should fail")
    assert 'error' in result
    assert result['status'] == 'failed'

def test_file_organization_verification():
    """Test file organization verification."""
    # Test valid file paths
    valid_paths = [
        'app/core/test.py',
        'tests/unit/test_file.py',
        'scripts/process_patch.py',
        'config/settings.json',
        'docs/README.md',
        'reports/patch_report.txt'
    ]
    
    for path in valid_paths:
        verify_file_organization(path)
    
    # Test invalid file paths
    invalid_paths = [
        'test.py',  # Root directory
        'invalid/test.py',  # Invalid directory
        'src/test.py'  # Non-standard directory
    ]
    
    for path in invalid_paths:
        with pytest.raises(ValueError):
            verify_file_organization(path)

def test_full_patch_processing(patch_processor, tmp_path):
    """Test processing the actual patch1.txt file."""
    # Get the path to patch1.txt
    patch_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'master', 'patch1.txt')
    
    # Process the file
    results = patch_processor.process_patch_file(patch_file)
    
    # Generate report in the correct directory
    report_file = tmp_path / "patch1_report.txt"
    patch_processor.generate_report(str(report_file))
    
    # Verify report
    assert report_file.exists()
    content = report_file.read_text()
    
    # Check for expected categories
    expected_categories = [
        'System Information and Status',
        'File System Operations',
        'Application Management',
        'Network and Connectivity'
    ]
    
    for category in expected_categories:
        assert category in content
    
    # Verify command results are present
    assert 'Command:' in content
    assert 'Status:' in content
    assert 'Response:' in content or 'Error:' in content 