#!/usr/bin/env python3
"""
UaiBot GUI Launcher

This module provides a modern PyQt5-based GUI for UaiBot.
It includes features like:
- Command input and output display
- Model selection and configuration
- Plugin management
- Status updates and notifications
"""
import sys
import asyncio
from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                            QLabel, QComboBox, QTabWidget, QGroupBox,
                            QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor

from uaibot.core.ai.uaibot_agent import UaiAgent
from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.cache import Cache
from uaibot.core.auth_manager import AuthManager
from uaibot.core.plugin_manager import PluginManager

class AgentWorker(QThread):
    """Worker thread for running agent operations."""
    resultReady = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    statusUpdated = pyqtSignal(str)
    
    def __init__(self, agent: UaiAgent, command: str):
        super().__init__()
        self.agent = agent
        self.command = command
        
    def run(self):
        try:
            # Create event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Update status
            self.statusUpdated.emit("Processing command...")
            
            # Run agent operations
            result = loop.run_until_complete(self.agent.plan_and_execute(self.command))
            
            # Emit result
            if isinstance(result, dict):
                if "error" in result:
                    self.errorOccurred.emit(result["error"])
                else:
                    self.resultReady.emit(str(result.get("response", "No response")))
            else:
                self.resultReady.emit(str(result))
            
            # Update status
            self.statusUpdated.emit("Ready")
            
        except Exception as e:
            self.errorOccurred.emit(str(e))
            self.statusUpdated.emit("Error occurred")
        finally:
            loop.close()

class ModelWorker(QThread):
    """Worker thread for model operations."""
    modelsReady = pyqtSignal(dict)
    errorOccurred = pyqtSignal(str)
    
    def __init__(self, model_manager: ModelManager):
        super().__init__()
        self.model_manager = model_manager
        
    def run(self):
        try:
            models = self.model_manager.list_available_models()
            self.modelsReady.emit(models)
        except Exception as e:
            self.errorOccurred.emit(str(e))

class MainWindow(QMainWindow):
    """Main window for UaiBot GUI."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot")
        self.setGeometry(100, 100, 1000, 800)
        
        # Initialize components
        self.config = ConfigManager()
        self.model_manager = ModelManager(self.config)
        self.cache = Cache()
        self.auth_manager = AuthManager()
        self.plugin_manager = PluginManager()
        
        # Initialize agent
        self.agent = UaiAgent(
            config=self.config,
            model_manager=self.model_manager,
            cache=self.cache,
            auth_manager=self.auth_manager,
            plugin_manager=self.plugin_manager
        )
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create main tab
        self.main_tab = QWidget()
        self.tabs.addTab(self.main_tab, "Main")
        
        # Create settings tab
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Set up main tab
        self._setup_main_tab()
        
        # Set up settings tab
        self._setup_settings_tab()
        
        # Display welcome message
        self.output.append("Welcome to UaiBot GUI!\n")
        self.output.append("Type a command and press Enter or click Send.\n")
        
        # Load available models
        self._load_models()
    
    def _setup_main_tab(self):
        """Set up the main tab."""
        layout = QVBoxLayout(self.main_tab)
        
        # Create output display
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Courier", 10))
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output)
        
        # Create input area
        input_layout = QHBoxLayout()
        
        # Create input field
        self.input = QLineEdit()
        self.input.returnPressed.connect(self.process_command)
        input_layout.addWidget(self.input)
        
        # Create send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_command)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def _setup_settings_tab(self):
        """Set up the settings tab."""
        layout = QVBoxLayout(self.settings_tab)
        
        # Model settings group
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout()
        
        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["ollama", "huggingface"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        model_layout.addRow("Provider:", self.provider_combo)
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        model_layout.addRow("Model:", self.model_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Plugin settings group
        plugin_group = QGroupBox("Plugin Settings")
        plugin_layout = QVBoxLayout()
        
        # Add plugin management UI here
        
        plugin_group.setLayout(plugin_layout)
        layout.addWidget(plugin_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def _load_models(self):
        """Load available models."""
        self.status_bar.showMessage("Loading models...")
        self.worker = ModelWorker(self.model_manager)
        self.worker.modelsReady.connect(self._on_models_loaded)
        self.worker.errorOccurred.connect(self._on_model_error)
        self.worker.start()
    
    def _on_models_loaded(self, models: Dict[str, List[str]]):
        """Handle loaded models."""
        # Clear existing items
        self.model_combo.clear()
        
        # Add models for current provider
        provider = self.provider_combo.currentText()
        if provider in models:
            self.model_combo.addItems(models[provider])
            
            # Select current model if available
            current_model = self.model_manager.model_info.name
            index = self.model_combo.findText(current_model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
        
        self.status_bar.showMessage("Ready")
    
    def _on_model_error(self, error: str):
        """Handle model loading error."""
        self.status_bar.showMessage(f"Error loading models: {error}")
        QMessageBox.warning(self, "Error", f"Failed to load models: {error}")
    
    def _on_provider_changed(self, provider: str):
        """Handle provider change."""
        self._load_models()
    
    def _on_model_changed(self, model: str):
        """Handle model change."""
        try:
            provider = self.provider_combo.currentText()
            self.model_manager.set_model(provider, model)
            self.status_bar.showMessage(f"Switched to {model}")
        except Exception as e:
            self.status_bar.showMessage(f"Error switching model: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to switch model: {str(e)}")
    
    def process_command(self):
        """Process the command entered by the user."""
        command = self.input.text().strip()
        if not command:
            return
            
        # Clear input
        self.input.clear()
        
        # Display command
        self.output.append(f"\nCommand: {command}")
        
        # Create and start worker
        self.worker = AgentWorker(self.agent, command)
        self.worker.resultReady.connect(self.handle_result)
        self.worker.errorOccurred.connect(self.handle_error)
        self.worker.statusUpdated.connect(self.status_bar.showMessage)
        self.worker.start()
        
    def handle_result(self, result: str):
        """Handle successful result from agent."""
        self.output.append(f"Result: {result}\n")
        self.output.moveCursor(QTextCursor.End)
        
    def handle_error(self, error: str):
        """Handle error from agent."""
        self.output.append(f"Error: {error}\n")
        self.output.moveCursor(QTextCursor.End)

def main():
    """Main entry point for GUI."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 