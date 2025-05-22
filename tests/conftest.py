import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from app.config.output_paths import (
    TEST_OUTPUTS_DIR,
    TEST_COVERAGE_DIR,
    TEST_LOGS_DIR,
    get_test_output_path,
    get_coverage_file_path
)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory."""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture(scope="session")
def test_config():
    """Return test configuration settings."""
    return {
        'timeout': 30,
        'retries': 3,
        'coverage_threshold': 80,
        'test_data_path': os.path.join(os.path.dirname(__file__), 'data')
    }

@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = os.path.join(temp_dir, 'sample.txt')
    with open(file_path, 'w') as f:
        f.write('Test content')
    return file_path

@pytest.fixture(scope="function")
def mock_ai_response():
    """Return a mock AI response for testing."""
    return {
        'success': True,
        'command': 'echo "Hello World"',
        'metadata': {
            'confidence': 0.95,
            'language': 'en'
        }
    }

@pytest.fixture(scope="function")
def mock_file_operations():
    """Mock file operations for testing."""
    class MockFileOps:
        def __init__(self):
            self.files = {}
            self.operations = []

        def create_file(self, path, content):
            self.files[path] = content
            self.operations.append(('create', path))
            return True

        def read_file(self, path):
            return self.files.get(path)

        def delete_file(self, path):
            if path in self.files:
                del self.files[path]
                self.operations.append(('delete', path))
                return True
            return False

    return MockFileOps()

@pytest.fixture(scope="function")
def mock_command_processor():
    """Mock command processor for testing."""
    class MockCommandProcessor:
        def __init__(self):
            self.commands = []
            self.results = {}

        def process_command(self, command):
            self.commands.append(command)
            return self.results.get(command, {'success': True})

        def set_result(self, command, result):
            self.results[command] = result

    return MockCommandProcessor()

@pytest.fixture(scope="session")
def temp_log_dir(tmp_path_factory):
    """Create a temporary directory for test logs."""
    log_dir = tmp_path_factory.mktemp("logs")
    return log_dir

@pytest.fixture(scope="function")
def mock_platform_manager(monkeypatch):
    """Mock platform manager for testing."""
    class MockPlatformManager:
        def __init__(self):
            self.platform_supported = True
            self.platform_name = "test_platform"
        
        def initialize(self):
            pass
        
        def cleanup(self):
            pass
        
        def get_platform_info(self):
            return {
                "name": "test_platform",
                "version": "1.0.0",
                "capabilities": ["test"]
            }
    
    monkeypatch.setattr("platform_uai.platform_manager.PlatformManager", MockPlatformManager)
    return MockPlatformManager()

@pytest.fixture(scope="session")
def test_output_dir():
    """Create and return a test output directory for the current test session."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = TEST_OUTPUTS_DIR / f"test_session_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture(scope="function")
def test_case_dir(test_output_dir, request):
    """Create and return a directory for the current test case."""
    test_name = request.node.name
    case_dir = test_output_dir / test_name
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Set up coverage file path
    config.option.cov_output = str(get_coverage_file_path())
    
    # Set up test log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = TEST_LOGS_DIR / f"test_run_{timestamp}.log"
    config.option.log_file = str(log_file)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":  # Only process the actual test call
        test_dir = item.funcargs.get("test_case_dir")
        if test_dir:
            # Save test output if available
            if hasattr(report, "stdout"):
                with open(test_dir / "stdout.txt", "w") as f:
                    f.write(report.stdout)
            if hasattr(report, "stderr"):
                with open(test_dir / "stderr.txt", "w") as f:
                    f.write(report.stderr)
            # Save test result
            with open(test_dir / "result.txt", "w") as f:
                f.write(f"Test: {item.name}\n")
                f.write(f"Outcome: {report.outcome}\n")
                if report.outcome == "failed":
                    f.write(f"Error: {report.longrepr}\n") 