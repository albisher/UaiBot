"""
Main window for UaiBot GUI
Compatible with Mac, Ubuntu, and Jetson platforms
"""
import os
import sys
import platform

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox,
    QTabWidget, QSplitter, QFrame, QMessageBox, QAction
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

from core.utils import load_config, save_config, get_project_root
from core.ai_handler import AIHandler
from core.shell_handler import ShellHandler
from platform.platform_manager import PlatformManager
from gui.avatar import AvatarWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot - AI-Powered Assistant")
        
        # Set minimum size - Mac displays need a reasonable minimum size
        self.setMinimumSize(800, 600)
        
        # Load configuration
        self.config = load_config()
        if not self.config:
            QMessageBox.critical(self, "Error", 
                "Failed to load configuration. Please check config/settings.json")
            sys.exit(1)
            
        # Initialize platform manager
        self.platform_manager = PlatformManager()
        if not self.platform_manager.platform_supported:
            QMessageBox.critical(self, "Error", 
                f"Unsupported platform: {platform.system()}")
            sys.exit(1)
            
        self.platform_manager.initialize()
        self.audio_handler = self.platform_manager.get_audio_handler()
        self.usb_handler = self.platform_manager.get_usb_handler()
        
        # Initialize AI and shell handlers
        self.init_handlers()
        
        # Set up the UI
        self.setup_ui()
        
    def init_handlers(self):
        """Initialize AI and shell handlers"""
        ai_provider = self.config.get("default_ai_provider")
        if not ai_provider:
            QMessageBox.critical(self, "Error", 
                "No default_ai_provider specified in configuration.")
            sys.exit(1)
            
        try:
            if ai_provider == "google":
                google_api_key = self.config.get("google_api_key")
                if not google_api_key:
                    google_api_key = os.getenv("GOOGLE_API_KEY")
                if not google_api_key:
                    QMessageBox.critical(self, "Error", 
                        "Google API key not configured.")
                    sys.exit(1)
                google_model = self.config.get("default_google_model")
                if not google_model:
                    google_model = "gemini-1.5-pro"
                self.ai_handler = AIHandler(
                    model_type="google", 
                    api_key=google_api_key,
                    google_model_name=google_model
                )
            elif ai_provider == "ollama":
                ollama_url = self.config.get("ollama_base_url", "http://localhost:11434")
                ollama_model = self.config.get("default_ollama_model", "gemma3:4b")
                self.ai_handler = AIHandler(
                    model_type="ollama",
                    ollama_base_url=ollama_url
                )
                self.ai_handler.set_ollama_model(ollama_model)
            else:
                QMessageBox.critical(self, "Error", 
                    f"Unknown AI provider '{ai_provider}'.")
                sys.exit(1)
                
            # Initialize shell handler
            shell_safe_mode = self.config.get("shell_safe_mode", True)
            shell_dangerous_check = self.config.get("shell_dangerous_check", True)
            self.shell_handler = ShellHandler(
                safe_mode=shell_safe_mode,
                enable_dangerous_command_check=shell_dangerous_check
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Failed to initialize handlers: {str(e)}")
            sys.exit(1)
            
    def setup_ui(self):
        """Set up the main UI components"""
        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Avatar and output section
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Avatar widget
        self.avatar_widget = AvatarWidget()
        top_layout.addWidget(self.avatar_widget)
        
        # Output text display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        top_layout.addWidget(self.output_text, 1)
        
        # Add the top widget to the splitter
        splitter.addWidget(top_widget)
        
        # Input section
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Input layout
        input_layout = QHBoxLayout()
        input_prompt = QLabel("Enter command:")
        input_layout.addWidget(input_prompt)
        
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.process_command)
        input_layout.addWidget(self.input_field, 1)
        
        self.submit_button = QPushButton("Send")
        self.submit_button.clicked.connect(self.process_command)
        input_layout.addWidget(self.submit_button)
        
        bottom_layout.addLayout(input_layout)
        
        # Add the bottom widget to the splitter
        splitter.addWidget(bottom_widget)
        
        # Set initial sizes for splitter
        splitter.setSizes([400, 200])
        
        # Status bar
        self.statusBar().showMessage(f"Connected to {self.config.get('default_ai_provider')} | Platform: {self.platform_manager.platform_name}")
        
        # Set up menu
        self.setup_menu()
        
        # Welcome message
        welcome_message = (
            "Welcome to UaiBot!\n\n"
            f"Platform: {self.platform_manager.platform_name}\n"
            f"AI Provider: {self.config.get('default_ai_provider')}\n"
            "Enter a command or question to get started."
        )
        self.output_text.append(welcome_message)
        
    def setup_menu(self):
        """Set up the application menu"""
        # File menu
        file_menu = self.menuBar().addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = self.menuBar().addMenu("Settings")
        
        toggle_safe_mode = QAction("Toggle Safe Mode", self)
        toggle_safe_mode.triggered.connect(self.toggle_safe_mode)
        settings_menu.addAction(toggle_safe_mode)
        
        # Help menu
        help_menu = self.menuBar().addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def toggle_safe_mode(self):
        """Toggle shell safe mode"""
        current_mode = self.config.get("shell_safe_mode", True)
        self.config["shell_safe_mode"] = not current_mode
        
        # Update shell handler
        self.shell_handler.safe_mode = not current_mode
        
        # Save to config
        save_config(self.config)
        
        # Show confirmation
        QMessageBox.information(self, "Settings Changed",
            f"Shell Safe Mode is now {'ON' if not current_mode else 'OFF'}")
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About UaiBot",
            "UaiBot - AI-Powered Assistant\n\n"
            "A friendly bot that helps you learn and use Linux commands.\n\n"
            f"Platform: {self.platform_manager.platform_name}\n"
            f"Version: 1.0")
    
    def process_command(self):
        """Process user command"""
        user_input = self.input_field.text().strip()
        if not user_input:
            return
            
        # Clear input field
        self.input_field.clear()
        
        # Display user input
        self.output_text.append(f"\n<b>You:</b> {user_input}")
        
        # Query AI
        prompt = (
            f"User request: '{user_input}'. "
            "Based on this request, suggest a single, common, and safe Linux shell command. "
            "Avoid generating complex command chains unless explicitly requested. "
            "If the request is ambiguous or potentially unsafe, respond with 'Error: Cannot fulfill request safely.'"
        )
        
        try:
            # Set avatar to thinking state
            self.avatar_widget.set_emotion("thinking")
            
            # Get AI response
            ai_response = self.ai_handler.query_ai(prompt)
            
            # Display AI response
            self.output_text.append(f"<b>AI suggested command:</b> <code>{ai_response}</code>")
            
            # Set avatar to happy state if successful
            self.avatar_widget.set_emotion("happy")
            
            # Check command safety
            if ai_response and not ai_response.startswith("Error:"):
                safety_level = self.shell_handler.check_command_safety_level(ai_response)
                
                if safety_level == 'POTENTIALLY_DANGEROUS':
                    self.avatar_widget.set_emotion("concerned")
                    self.output_text.append(f"<span style='color:red'>WARNING: Potentially dangerous command!</span>")
                    
                    if self.shell_handler.safe_mode:
                        self.output_text.append("Execution blocked by safe mode.")
                    else:
                        # Ask for confirmation
                        confirm = QMessageBox.question(self, "Confirm Execution",
                            f"The command '{ai_response}' is potentially dangerous.\nDo you want to execute it anyway?",
                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            
                        if confirm == QMessageBox.Yes:
                            output = self.shell_handler.execute_command(ai_response)
                            self.output_text.append(f"<b>Output:</b><pre>{output}</pre>")
                        else:
                            self.output_text.append("Execution cancelled.")
                else:
                    # Safe command, execute it
                    output = self.shell_handler.execute_command(ai_response)
                    self.output_text.append(f"<b>Output:</b><pre>{output}</pre>")
            elif ai_response.startswith("Error:"):
                self.avatar_widget.set_emotion("confused")
                self.output_text.append(f"<span style='color:orange'>{ai_response}</span>")
            else:
                self.avatar_widget.set_emotion("confused")
                self.output_text.append("<span style='color:orange'>AI did not return a valid command.</span>")
                
        except Exception as e:
            self.avatar_widget.set_emotion("sad")
            self.output_text.append(f"<span style='color:red'>Error: {str(e)}</span>")
            
        # Scroll to bottom
        self.output_text.moveCursor(self.output_text.textCursor().End)