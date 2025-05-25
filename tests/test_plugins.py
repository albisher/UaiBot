import pytest
import os
from pathlib import Path
from uaibot.core.plugins import PluginManager, PluginInfo

def create_test_plugin(plugin_dir: Path, name: str, dependencies: list = None) -> Path:
    """Create a test plugin file."""
    plugin_file = plugin_dir / f"{name}.py"
    plugin_file.write_text(f'''
PLUGIN_INFO = {{
    'name': '{name}',
    'version': '1.0.0',
    'description': 'Test plugin',
    'author': 'Test Author',
    'dependencies': {dependencies or []},
    'entry_point': '{name}.py'
}}

class TestPlugin:
    def __init__(self, config):
        self.config = config
        
    def handle_command(self, command, parameters):
        if command == 'test_command':
            return {{'result': 'success'}}
        return None

def initialize(config):
    return TestPlugin(config)
''')
    return plugin_file

def test_plugin_manager_initialization(plugin_manager):
    """Test plugin manager initialization."""
    assert plugin_manager.plugins_dir is not None
    assert os.path.exists(plugin_manager.plugins_dir)
    assert isinstance(plugin_manager.plugins, dict)
    assert isinstance(plugin_manager.loaded_modules, dict)

def test_register_plugin(plugin_manager):
    """Test plugin registration."""
    # Create a test plugin
    plugin_file = create_test_plugin(Path(plugin_manager.plugins_dir), "test_plugin")
    
    # Register the plugin
    plugin_info = plugin_manager.register_plugin(str(plugin_file))
    
    assert plugin_info is not None
    assert plugin_info.name == "test_plugin"
    assert plugin_info.version == "1.0.0"
    assert plugin_info.enabled is True
    assert plugin_info.loaded is False

def test_load_plugin(plugin_manager):
    """Test plugin loading."""
    # Create and register a test plugin
    plugin_file = create_test_plugin(Path(plugin_manager.plugins_dir), "test_plugin")
    plugin_info = plugin_manager.register_plugin(str(plugin_file))
    
    # Load the plugin
    success = plugin_manager.load_plugin("test_plugin")
    
    assert success is True
    assert plugin_info.loaded is True
    assert plugin_info.load_time is not None
    assert "test_plugin" in plugin_manager.loaded_modules

def test_plugin_dependencies(plugin_manager):
    """Test plugin dependency handling."""
    # Create dependent plugins
    create_test_plugin(Path(plugin_manager.plugins_dir), "base_plugin")
    create_test_plugin(Path(plugin_manager.plugins_dir), "dependent_plugin", ["base_plugin"])
    
    # Register plugins
    base_info = plugin_manager.register_plugin(str(Path(plugin_manager.plugins_dir) / "base_plugin.py"))
    dep_info = plugin_manager.register_plugin(str(Path(plugin_manager.plugins_dir) / "dependent_plugin.py"))
    
    # Try to load dependent plugin first (should fail)
    with pytest.raises(ValueError):
        plugin_manager.load_plugin("dependent_plugin")
    
    # Load base plugin first
    plugin_manager.load_plugin("base_plugin")
    
    # Now load dependent plugin
    success = plugin_manager.load_plugin("dependent_plugin")
    assert success is True

def test_plugin_commands(plugin_manager):
    """Test plugin command handling."""
    # Create and load a test plugin
    plugin_file = create_test_plugin(Path(plugin_manager.plugins_dir), "test_plugin")
    plugin_info = plugin_manager.register_plugin(str(plugin_file))
    plugin_manager.load_plugin("test_plugin")
    
    # Get the plugin module
    module = plugin_manager.get_plugin_module("test_plugin")
    plugin = module.initialize({})
    
    # Test command handling
    result = plugin.handle_command("test_command", {})
    assert result == {'result': 'success'}
    
    # Test unknown command
    result = plugin.handle_command("unknown_command", {})
    assert result is None

def test_plugin_management(plugin_manager):
    """Test plugin management functions."""
    # Create and register a test plugin
    plugin_file = create_test_plugin(Path(plugin_manager.plugins_dir), "test_plugin")
    plugin_info = plugin_manager.register_plugin(str(plugin_file))
    
    # Test enable/disable
    plugin_manager.disable_plugin("test_plugin")
    assert plugin_info.enabled is False
    
    plugin_manager.enable_plugin("test_plugin")
    assert plugin_info.enabled is True
    
    # Test load/unload
    plugin_manager.load_plugin("test_plugin")
    assert plugin_info.loaded is True
    
    plugin_manager.unload_plugin("test_plugin")
    assert plugin_info.loaded is False
    
    # Test listing plugins
    plugins = plugin_manager.list_plugins()
    assert len(plugins) == 1
    assert plugins[0]['name'] == "test_plugin" 