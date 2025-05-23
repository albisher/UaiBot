import pytest

def mock_ai_handler():
    """Return a mock AI handler for testing."""
    class MockAIHandler:
        def __init__(self):
            self.commands = []
            self.results = {}

        def process_command(self, command):
            self.commands.append(command)
            return self.results.get(command, {'success': True})

        def set_result(self, command, result):
            self.results[command] = result

    return MockAIHandler()

def mock_command_processor():
    """Return a mock command processor for testing."""
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