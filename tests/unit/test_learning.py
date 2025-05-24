import pytest
import os
import json
from uaibot.core.learning import LearningManager

class TestLearningManager:
    """Test suite for the LearningManager."""

    @pytest.fixture
    def learning_manager(self):
        """Create a LearningManager instance for testing."""
        # Use a temporary file for testing
        test_file = "test_knowledge_base.json"
        manager = LearningManager(knowledge_base_file=test_file)
        yield manager
        # Clean up the test file after tests
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_learn_from_result(self, learning_manager):
        """Test learning from a command execution result."""
        command = "move mouse to (100, 200)"
        result = {
            "status": "success",
            "os": "darwin",
            "action": "move_to",
            "capability": "mouse_control"
        }
        learning_manager.learn_from_result(command, result)
        assert "mouse_control" in learning_manager.knowledge_base
        assert "darwin" in learning_manager.knowledge_base["mouse_control"]
        assert "move_to" in learning_manager.knowledge_base["mouse_control"]["darwin"]["actions"]
        assert learning_manager.knowledge_base["mouse_control"]["darwin"]["actions"]["move_to"]["success_count"] == 1

    def test_suggest_alternatives(self, learning_manager):
        """Test suggesting alternatives based on the knowledge base."""
        # First, learn a successful action
        command = "move mouse to (100, 200)"
        result = {
            "status": "success",
            "os": "darwin",
            "action": "move_to",
            "capability": "mouse_control"
        }
        learning_manager.learn_from_result(command, result)
        # Now suggest alternatives
        alternatives = learning_manager.suggest_alternatives("move mouse to (150, 150)", "darwin")
        assert "Try using move_to instead." in alternatives

    def test_command_pattern_learning(self, learning_manager):
        """Test learning command patterns."""
        command = "move mouse to (100, 200)"
        result = {
            "status": "success",
            "os": "darwin",
            "action": "move_to",
            "capability": "mouse_control"
        }
        learning_manager.learn_from_result(command, result)
        pattern = learning_manager._extract_command_pattern(command)
        assert pattern == "move mouse to (x, y)"
        assert pattern in learning_manager.knowledge_base["mouse_control"]["darwin"]["command_patterns"]
        assert learning_manager.knowledge_base["mouse_control"]["darwin"]["command_patterns"][pattern]["success_count"] == 1

    def test_embedding_based_learning(self, learning_manager):
        """Test the embedding-based learning mechanism using Milvus and Sentence Transformers."""
        # First, learn a successful action
        command = "move mouse to (100, 200)"
        result = {
            "status": "success",
            "os": "darwin",
            "action": "move_to",
            "capability": "mouse_control"
        }
        learning_manager.learn_from_result(command, result)
        # Now find similar commands
        similar_commands = learning_manager._find_similar_commands("move mouse to (150, 150)")
        assert len(similar_commands) > 0
        assert "move mouse to (100, 200)" in similar_commands 