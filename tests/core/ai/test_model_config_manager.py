"""
Tests for the Model Configuration Manager module.
"""
import pytest
import json
import os
from uaibot.datetime import datetime
from uaibot.core.model_config_manager import ModelConfigManager, ModelConfig

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary directory for configuration files."""
    config_dir = tmp_path / "model_configs"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def config_manager(temp_config_dir):
    """Create a model configuration manager with a temporary directory."""
    return ModelConfigManager(str(temp_config_dir))

def test_set_and_get_config(config_manager):
    """Test setting and getting model configuration."""
    # Set configuration
    config_manager.set_config(
        model_name="test-model",
        version="1.0.0",
        parameters={"temperature": 0.7, "max_tokens": 100},
        optimization_settings={"batch_size": 32}
    )
    
    # Get configuration
    config = config_manager.get_config("test-model")
    assert config is not None
    assert config.name == "test-model"
    assert config.version == "1.0.0"
    assert config.parameters == {"temperature": 0.7, "max_tokens": 100}
    assert config.optimization_settings == {"batch_size": 32}
    assert config.is_active is True

def test_update_parameters(config_manager):
    """Test updating model parameters."""
    # Set initial configuration
    config_manager.set_config(
        model_name="test-model",
        version="1.0.0",
        parameters={"temperature": 0.7}
    )
    
    # Update parameters
    config_manager.update_parameters(
        model_name="test-model",
        parameters={"max_tokens": 200}
    )
    
    # Verify updated configuration
    config = config_manager.get_config("test-model")
    assert config.parameters == {"temperature": 0.7, "max_tokens": 200}

def test_update_optimization_settings(config_manager):
    """Test updating optimization settings."""
    # Set initial configuration
    config_manager.set_config(
        model_name="test-model",
        version="1.0.0",
        optimization_settings={"batch_size": 32}
    )
    
    # Update optimization settings
    config_manager.update_optimization_settings(
        model_name="test-model",
        optimization_settings={"learning_rate": 0.001}
    )
    
    # Verify updated configuration
    config = config_manager.get_config("test-model")
    assert config.optimization_settings == {
        "batch_size": 32,
        "learning_rate": 0.001
    }

def test_set_model_active(config_manager):
    """Test setting model active status."""
    # Set initial configuration
    config_manager.set_config(
        model_name="test-model",
        version="1.0.0",
        parameters={}
    )
    
    # Set model as inactive
    config_manager.set_model_active("test-model", False)
    
    # Verify active models
    active_models = config_manager.get_active_models()
    assert "test-model" not in active_models
    
    # Set model as active again
    config_manager.set_model_active("test-model", True)
    active_models = config_manager.get_active_models()
    assert "test-model" in active_models

def test_get_model_versions(config_manager):
    """Test getting model versions."""
    # Set configurations for multiple models
    config_manager.set_config("model1", "1.0.0", {})
    config_manager.set_config("model2", "2.0.0", {})
    
    # Get versions
    versions = config_manager.get_model_versions()
    assert versions == {
        "model1": "1.0.0",
        "model2": "2.0.0"
    }

def test_config_persistence(config_manager, temp_config_dir):
    """Test that configurations are persisted to files."""
    # Set configuration
    config_manager.set_config(
        model_name="test-model",
        version="1.0.0",
        parameters={"temperature": 0.7}
    )
    
    # Verify file was created
    config_file = temp_config_dir / "test-model.json"
    assert config_file.exists()
    
    # Verify file contents
    with open(config_file) as f:
        data = json.load(f)
        assert data["version"] == "1.0.0"
        assert data["parameters"] == {"temperature": 0.7}
        assert data["is_active"] is True

def test_load_existing_configs(config_manager, temp_config_dir):
    """Test loading existing configurations."""
    # Create a configuration file manually
    config_file = temp_config_dir / "existing-model.json"
    config_data = {
        "version": "1.0.0",
        "parameters": {"temperature": 0.7},
        "optimization_settings": {"batch_size": 32},
        "last_updated": datetime.now().isoformat(),
        "is_active": True
    }
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    
    # Create new manager to load existing configs
    new_manager = ModelConfigManager(str(temp_config_dir))
    
    # Verify configuration was loaded
    config = new_manager.get_config("existing-model")
    assert config is not None
    assert config.version == "1.0.0"
    assert config.parameters == {"temperature": 0.7}
    assert config.optimization_settings == {"batch_size": 32} 