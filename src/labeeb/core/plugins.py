import os
import sys
import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
import logging
from datetime import datetime

@dataclass
class PluginInfo:
    """Information about a plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    entry_point: str
    enabled: bool = True
    loaded: bool = False
    load_time: Optional[datetime] = None

class PluginManager:
    """Manages plugin loading, unloading, and lifecycle."""
    
    def __init__(self, plugins_dir: Optional[str] = None):
        self.plugins_dir = plugins_dir or os.path.expanduser("~/Documents/labeeb/plugins")
        self.config_file = os.path.join(self.plugins_dir, "plugins.json")
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_modules: Dict[str, Any] = {}
        self.logger = self._setup_logger()
        os.makedirs(self.plugins_dir, exist_ok=True)
        self._load_config()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the plugin manager."""
        logger = logging.getLogger('PluginManager')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / f'plugins_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def _load_config(self):
        """Load plugin configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for name, info in data.items():
                        self.plugins[name] = PluginInfo(
                            name=name,
                            version=info['version'],
                            description=info['description'],
                            author=info['author'],
                            dependencies=info.get('dependencies', []),
                            entry_point=info['entry_point'],
                            enabled=info.get('enabled', True),
                            loaded=False
                        )
            except Exception as e:
                self.logger.error(f"Error loading plugin config: {e}")
                
    def _save_config(self):
        """Save plugin configuration to file."""
        data = {}
        for name, plugin in self.plugins.items():
            data[name] = {
                'version': plugin.version,
                'description': plugin.description,
                'author': plugin.author,
                'dependencies': plugin.dependencies,
                'entry_point': plugin.entry_point,
                'enabled': plugin.enabled
            }
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin config: {e}")
            
    def register_plugin(self, plugin_path: str) -> Optional[PluginInfo]:
        """Register a new plugin from a Python file."""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            if not spec:
                raise ValueError(f"Could not load plugin from {plugin_path}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin info
            if not hasattr(module, 'PLUGIN_INFO'):
                raise ValueError("Plugin must define PLUGIN_INFO")
                
            info = module.PLUGIN_INFO
            plugin = PluginInfo(
                name=info['name'],
                version=info['version'],
                description=info['description'],
                author=info['author'],
                dependencies=info.get('dependencies', []),
                entry_point=info['entry_point'],
                enabled=True
            )
            
            # Check dependencies
            for dep in plugin.dependencies:
                if dep not in self.plugins:
                    raise ValueError(f"Missing dependency: {dep}")
                    
            # Register the plugin
            self.plugins[plugin.name] = plugin
            self._save_config()
            
            return plugin
            
        except Exception as e:
            self.logger.error(f"Error registering plugin {plugin_path}: {e}")
            return None
            
    def load_plugin(self, name: str) -> bool:
        """Load a registered plugin."""
        plugin = self.plugins.get(name)
        if not plugin:
            self.logger.error(f"Plugin {name} not found")
            return False
            
        if plugin.loaded:
            return True
            
        try:
            # Load dependencies first
            for dep in plugin.dependencies:
                if not self.load_plugin(dep):
                    raise ValueError(f"Failed to load dependency: {dep}")
                    
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(
                f"labeeb.plugins.{name}",
                os.path.join(self.plugins_dir, plugin.entry_point)
            )
            if not spec:
                raise ValueError(f"Could not load plugin module: {name}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Store the loaded module
            self.loaded_modules[name] = module
            
            # Update plugin info
            plugin.loaded = True
            plugin.load_time = datetime.now()
            self._save_config()
            
            self.logger.info(f"Loaded plugin: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading plugin {name}: {e}")
            return False
            
    def unload_plugin(self, name: str) -> bool:
        """Unload a loaded plugin."""
        plugin = self.plugins.get(name)
        if not plugin or not plugin.loaded:
            return False
            
        try:
            # Remove the module from sys.modules
            module_name = f"labeeb.plugins.{name}"
            if module_name in sys.modules:
                del sys.modules[module_name]
                
            # Remove from loaded modules
            if name in self.loaded_modules:
                del self.loaded_modules[name]
                
            # Update plugin info
            plugin.loaded = False
            plugin.load_time = None
            self._save_config()
            
            self.logger.info(f"Unloaded plugin: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {name}: {e}")
            return False
            
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""
        plugin = self.plugins.get(name)
        if not plugin:
            return False
            
        plugin.enabled = True
        self._save_config()
        return True
        
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        plugin = self.plugins.get(name)
        if not plugin:
            return False
            
        plugin.enabled = False
        if plugin.loaded:
            self.unload_plugin(name)
        self._save_config()
        return True
        
    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """Get information about a plugin."""
        return self.plugins.get(name)
        
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins."""
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'author': plugin.author,
                'dependencies': plugin.dependencies,
                'enabled': plugin.enabled,
                'loaded': plugin.loaded,
                'load_time': plugin.load_time.isoformat() if plugin.load_time else None
            }
            for plugin in self.plugins.values()
        ]
        
    def get_plugin_module(self, name: str) -> Optional[Any]:
        """Get a loaded plugin module."""
        return self.loaded_modules.get(name) 