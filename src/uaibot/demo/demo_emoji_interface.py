#!/usr/bin/env python3
"""
UaiBot Interface Demo - Shows the new emoji-based avatar interface
"""
import sys
import os
from PyQt5.QtWidgets import QApplication

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the new emoji interface
from gui.dual_window_emoji import UaiBotDualInterface as EmojiInterface

def main():
    """Main function to start the interface"""
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Initialize emoji interface
    emoji_interface = EmojiInterface()
    
    # Show interface
    emoji_interface.show()
    
    # Test different emotions
    emoji_interface.text_window.add_output_text("Welcome to the NEW UaiBot interface with emoji renderer!")
    emoji_interface.text_window.add_output_text("\nThis interface uses the RobotEmojiRenderer from enhancements3.txt")
    emoji_interface.text_window.add_output_text("\nTry typing 'emotion happy' to see different expressions")
    emoji_interface.text_window.add_output_text("\nAvailable emotions: happy, sad, surprise, confused, neutral, thinking")
    
    # Start with happy emotion
    emoji_interface.eyes_window.set_emotion("happy")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
