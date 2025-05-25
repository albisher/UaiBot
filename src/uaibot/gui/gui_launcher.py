#!/usr/bin/env python3
"""
UaiBot GUI Launcher
"""
import sys
import asyncio
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QTextEdit, QLineEdit, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from uaibot.core.ai.agent import UaiBotAgent
from uaibot.core.ai.tools.base_tool import UaiBotTool
from uaibot.core.ai.workflows.base_workflow import UaiBotWorkflow

class EchoTool(UaiBotTool):
    """Simple echo tool for testing."""
    def __init__(self):
        super().__init__(
            name="echo",
            description="Echoes back the input text",
            parameters={"text": "The text to echo"}
        )
    
    async def execute(self, params: Dict[str, Any]) -> str:
        return params.get("text", "")

class AgentWorker(QThread):
    """Worker thread for running agent operations."""
    resultReady = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    
    def __init__(self, agent: UaiBotAgent, command: str):
        super().__init__()
        self.agent = agent
        self.command = command
        
    def run(self):
        try:
            # Create event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run agent operations
            plan = loop.run_until_complete(self.agent.plan(self.command))
            result = loop.run_until_complete(self.agent.execute(plan))
            
            # Emit result
            self.resultReady.emit(str(result))
            
        except Exception as e:
            self.errorOccurred.emit(str(e))
        finally:
            loop.close()

class MainWindow(QMainWindow):
    """Main window for UaiBot GUI."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize agent
        self.agent = UaiBotAgent()
        self.agent.register_tool(EchoTool())
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create output display
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output)
        
        # Create input field
        self.input = QLineEdit()
        self.input.returnPressed.connect(self.process_command)
        layout.addWidget(QLabel("Command:"))
        layout.addWidget(self.input)
        
        # Create send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_command)
        layout.addWidget(self.send_button)
        
        # Display welcome message
        self.output.append("Welcome to UaiBot GUI!\n")
        self.output.append("Type a command and press Enter or click Send.\n")
        
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
        self.worker.start()
        
    def handle_result(self, result: str):
        """Handle successful result from agent."""
        self.output.append(f"Result: {result}\n")
        
    def handle_error(self, error: str):
        """Handle error from agent."""
        self.output.append(f"Error: {error}\n")

def main():
    """Main entry point for GUI."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 