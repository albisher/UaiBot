"""
Model Configuration Manager Module

This module manages configuration settings for different AI models,
including model-specific parameters, version tracking, and optimization settings.
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Data class for storing model-specific configuration."""
    name: str
    version: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    optimization_settings: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True

class ModelConfigManager:
    """Manages configuration settings for AI models."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the model configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'models')
        self.configs: Dict[str, ModelConfig] = {}
        self._ensure_config_dir()
        self._load_configs()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _load_configs(self) -> None:
        """Load all model configurations from files."""
        try:
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    model_name = filename[:-5]  # Remove .json extension
                    config_path = os.path.join(self.config_dir, filename)
                    with open(config_path, 'r') as f:
                        data = json.load(f)
                        self.configs[model_name] = ModelConfig(
                            name=model_name,
                            version=data.get('version', '1.0.0'),
                            parameters=data.get('parameters', {}),
                            optimization_settings=data.get('optimization_settings', {}),
                            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
                            is_active=data.get('is_active', True)
                        )
        except Exception as e:
            logger.error(f"Error loading model configurations: {e}")
    
    def get_config(self, model_name: str) -> Optional[ModelConfig]:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelConfig object if found, None otherwise
        """
        return self.configs.get(model_name)
    
    def set_config(
        self,
        model_name: str,
        version: str,
        parameters: Dict[str, Any],
        optimization_settings: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set configuration for a model.
        
        Args:
            model_name: Name of the model
            version: Version of the model
            parameters: Model-specific parameters
            optimization_settings: Optional optimization settings
        """
        config = ModelConfig(
            name=model_name,
            version=version,
            parameters=parameters,
            optimization_settings=optimization_settings or {},
            last_updated=datetime.now()
        )
        self.configs[model_name] = config
        self._save_config(model_name)
    
    def _save_config(self, model_name: str) -> None:
        """
        Save configuration for a model to file.
        
        Args:
            model_name: Name of the model
        """
        config = self.configs[model_name]
        config_path = os.path.join(self.config_dir, f"{model_name}.json")
        
        data = {
            'version': config.version,
            'parameters': config.parameters,
            'optimization_settings': config.optimization_settings,
            'last_updated': config.last_updated.isoformat(),
            'is_active': config.is_active
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_parameters(self, model_name: str, parameters: Dict[str, Any]) -> None:
        """
        Update parameters for a model.
        
        Args:
            model_name: Name of the model
            parameters: New parameters to set
        """
        if model_name in self.configs:
            config = self.configs[model_name]
            config.parameters.update(parameters)
            config.last_updated = datetime.now()
            self._save_config(model_name)
    
    def update_optimization_settings(
        self,
        model_name: str,
        optimization_settings: Dict[str, Any]
    ) -> None:
        """
        Update optimization settings for a model.
        
        Args:
            model_name: Name of the model
            optimization_settings: New optimization settings
        """
        if model_name in self.configs:
            config = self.configs[model_name]
            config.optimization_settings.update(optimization_settings)
            config.last_updated = datetime.now()
            self._save_config(model_name)
    
    def set_model_active(self, model_name: str, is_active: bool) -> None:
        """
        Set whether a model is active.
        
        Args:
            model_name: Name of the model
            is_active: Whether the model should be active
        """
        if model_name in self.configs:
            config = self.configs[model_name]
            config.is_active = is_active
            config.last_updated = datetime.now()
            self._save_config(model_name)
    
    def get_active_models(self) -> Dict[str, ModelConfig]:
        """
        Get all active model configurations.
        
        Returns:
            Dictionary of active model configurations
        """
        return {
            name: config
            for name, config in self.configs.items()
            if config.is_active
        }
    
    def get_model_versions(self) -> Dict[str, str]:
        """
        Get versions of all configured models.
        
        Returns:
            Dictionary mapping model names to their versions
        """
        return {
            name: config.version
            for name, config in self.configs.items()
        } 