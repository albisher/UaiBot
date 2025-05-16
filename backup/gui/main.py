"""
UaiBot - Main Application
Implements a split interface with robot eyes and text interaction
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QSplitter, QShortcut
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence

from new_avatar import AvatarInterface


class UaiBotApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = AvatarInterface()
        
        # Set up the interface
        self.setup_interface()
        
        # Connect signals
        self.setup_signals()
        
    def setup_interface(self):
        """Set up the UI components"""
        self.window.setWindowTitle("UaiBot - Ubuntu AI Assistant")
        self.window.resize(900, 700)
        
        # Enable word wrap on output area
        self.window.output_area.setLineWrapMode(self.window.output_area.WidgetWidth)
        
        # Create a keyboard shortcut for sending messages (Enter key)
        self.send_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self.window)
        self.send_shortcut.activated.connect(self.process_input)
        
    def setup_signals(self):
        """Connect signals to slots"""
        # Example connection - normally you would connect to your AI processing function
        self.send_shortcut.activated.connect(self.process_input)
        
    def process_input(self):
        """Process user input and generate a response"""
        user_input = self.window.input_area.toPlainText().strip()
        if not user_input:
            return
        
        # Display user input in output area
        self.window.add_output_text(f"User: {user_input}")
        
        # Clear input box
        self.window.input_area.clear()
        
        # Process the input (placeholder for actual AI processing)
        self.handle_command(user_input)
    
    def handle_command(self, text):
        """Handle user input and generate appropriate response"""
        # This is just a placeholder for actual command processing
        # In a real implementation, this would connect to your AI/LLM backend
        
        text = text.lower()
        
        # Simple emotion commands for testing
        if "happy" in text:
            self.window.set_emotion("happy")
            self.window.add_output_text("UaiBot: I'm happy to help you!")
        elif "sad" in text:
            self.window.set_emotion("sad")
            self.window.add_output_text("UaiBot: I'm sorry to hear that...")
        elif "surprise" in text or "wow" in text:
            self.window.set_emotion("surprise")
            self.window.add_output_text("UaiBot: Wow! That's amazing!")
        elif "think" in text:
            self.window.set_emotion("thinking")
            self.window.add_output_text("UaiBot: Let me think about that...")
        elif "confused" in text or "what" in text:
            self.window.set_emotion("confused")
            self.window.add_output_text("UaiBot: I'm not sure I understand...")
        else:
            # Default response
            self.window.set_emotion("neutral")
            self.window.add_output_text("UaiBot: I'm here to help with Ubuntu commands!")
    
    def show_welcome_message(self):
        """Display welcome message"""
        welcome_messages = [
            "Welcome to UaiBot!",
            "I'm your Ubuntu AI assistant.",
            "You can type commands or questions, and I'll help you navigate your system.",
            "Try saying 'happy', 'sad', 'surprise', or 'thinking' to see my different expressions!"
        ]
        
        # Show welcome messages with a slight delay
        for i, msg in enumerate(welcome_messages):
            # Use a timer to add messages with delay
            QTimer.singleShot(i * 500, lambda m=msg: self.window.add_output_text(m))
        
    def run(self):
        """Run the application"""
        self.window.show()
        self.show_welcome_message()
        return self.app.exec_()


if __name__ == "__main__":
    uaibot = UaiBotApp()
    sys.exit(uaibot.run())
