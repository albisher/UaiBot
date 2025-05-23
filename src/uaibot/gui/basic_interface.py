#!/usr/bin/env python3
"""
Basic UaiBot GUI Interface
Provides a simplified GUI for UaiBot with a single input/output window
"""
import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, 
    QHBoxLayout, QLabel, QSplitter, 
    QStatusBar, QAction, QMenu, QMenuBar,
    QToolBar, QSizePolicy, QComboBox,
    QMessageBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QTextCursor

class CommandThread(QThread):
    """Thread for executing commands without blocking the UI"""
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, shell_handler, ai_handler, command):
        super().__init__()
        self.shell_handler = shell_handler
        self.ai_handler = ai_handler
        self.command = command
        
    def run(self):
        try:
            response = self.ai_handler.process_command(self.command, self.shell_handler)
            self.result_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))

class UaiBotBasicInterface(QMainWindow):
    """Basic UaiBot GUI interface with a single window for I/O"""
    
    def __init__(self, shell_handler, ai_handler, platform_manager, config):
        super().__init__()
        
        self.shell_handler = shell_handler
        self.ai_handler = ai_handler
        self.platform_manager = platform_manager
        self.config = config
        
        self.setWindowTitle("UaiBot - AI Assistant")
        self.resize(800, 600)
        
        # Set up the UI
        self._setup_ui()
        
        # Display welcome message
        self.display_system_message("🤖 Welcome to UaiBot! I'm your AI assistant. Type your question or command below.")
        self.display_system_message(f"Running on: {self.platform_manager.get_platform_info()['name']}")
        
    def _setup_ui(self):
        """Set up the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumHeight(300)
        
        # Set monospace font for command output
        font = QFont("Courier")
        font.setStyleHint(QFont.Monospace)
        self.output_area.setFont(font)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your question or command here...")
        self.input_field.returnPressed.connect(self.process_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_input)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        # Add to main layout
        main_layout.addWidget(self.output_area)
        main_layout.addLayout(input_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Menu bar
        self._setup_menu()
        
    def _setup_menu(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        clear_action = QAction("Clear Output", self)
        clear_action.triggered.connect(self.output_area.clear)
        file_menu.addAction(clear_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About UaiBot", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def process_input(self):
        """Process user input"""
        command = self.input_field.text().strip()
        if not command:
            return
            
        # Display user input
        self.display_user_message(command)
        
        # Clear input field
        self.input_field.clear()
        
        # Disable UI while processing
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_bar.showMessage("Processing...")
        
        # Process command in a separate thread
        self.command_thread = CommandThread(self.shell_handler, self.ai_handler, command)
        self.command_thread.result_ready.connect(self.display_response)
        self.command_thread.error_occurred.connect(self.display_error)
        self.command_thread.finished.connect(self.processing_finished)
        self.command_thread.start()
    
    @pyqtSlot(str)
    def display_response(self, response):
        """Display the bot's response"""
        self.display_bot_message(response)
    
    @pyqtSlot(str)
    def display_error(self, error_message):
        """Display an error message"""
        self.display_system_message(f"❌ Error: {error_message}")
    
    def display_user_message(self, message):
        """Display a user message in the output area"""
        self.output_area.append(f"\n<b>You:</b> {message}")
        
    def display_bot_message(self, message):
        """Display a bot message in the output area"""
        self.output_area.append(f"\n<b>UaiBot:</b> {message}")
        
    def display_system_message(self, message):
        """Display a system message in the output area"""
        self.output_area.append(f"\n<i>{message}</i>")
    
    def processing_finished(self):
        """Called when command processing is finished"""
        # Re-enable UI
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_bar.showMessage("Ready")
        
        # Scroll to bottom
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_area.setTextCursor(cursor)
        
    def show_about(self):
        """Show the about dialog"""
        QMessageBox.about(self, "About UaiBot", 
            """<b>UaiBot</b> v1.0.0<br><br>
            An AI-powered shell assistant.<br><br>
            UaiBot helps you learn about command-line interactions,
            understand system operations, and provides general AI assistance.<br><br>
            Copyright © 2025 UaiBot Team<br>
            Licensed under the UaiBot License (free for personal and educational use)"""
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Clean up platform-specific resources
        if self.platform_manager:
            self.platform_manager.cleanup()
        event.accept()
