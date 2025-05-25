import os
import sys
import importlib
import logging
from typing import Dict, Any, List, Optional

class PluginManager:
    """
    Minimal plugin manager for UaiBot.
    Handles registration, loading, and management of plugins.
    """
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}
        self.logger = logging.getLogger("PluginManager")
        self._load_all_plugins()

    def _load_all_plugins(self):
        if not os.path.isdir(self.plugin_dir):
            self.logger.info(f"Plugin directory '{self.plugin_dir}' does not exist.")
            return
        for fname in os.listdir(self.plugin_dir):
            if fname.endswith(".py") and not fname.startswith("__"):
                name = fname[:-3]
                self.load_plugin(name)

    def register_plugin(self, path: str) -> Any:
        """Register a plugin by path."""
        name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(name, path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            self.plugins[name] = module
            return module
        else:
            self.logger.error(f"Failed to register plugin: {path}")
            return None

    def load_plugin(self, name: str) -> Optional[Any]:
        """Load a plugin by name from the plugin directory."""
        try:
            sys.path.insert(0, self.plugin_dir)
            module = importlib.import_module(name)
            self.plugins[name] = module
            return module
        except Exception as e:
            self.logger.error(f"Failed to load plugin '{name}': {e}")
            return None
        finally:
            if self.plugin_dir in sys.path:
                sys.path.remove(self.plugin_dir)

    def get_plugins(self) -> List[Any]:
        return list(self.plugins.values())

    def get_plugin(self, name: str) -> Optional[Any]:
        return self.plugins.get(name)

    def get_plugin_module(self, name: str) -> Optional[Any]:
        return self.get_plugin(name) 