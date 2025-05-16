#!/usr/bin/env python3
"""
UaiBot Interface Comparison
Shows both the old and new interfaces side by side for comparison
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import both interfaces
from gui.dual_window import UaiBotDualInterface as OldInterface
from gui.dual_window_emoji import UaiBotDualInterface as EmojiInterface

def main():
    """Main function to start both interfaces"""
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Initialize both interfaces
    old_interface = OldInterface()
    emoji_interface = EmojiInterface()
    
    # Show both interfaces
    old_interface.show()
    emoji_interface.show()
    
    # Position windows - old interface on left, emoji interface on right
    old_interface.eyes_window.move(100, 100)
    old_interface.text_window.move(100, 450)
    
    emoji_interface.emoji_window.move(550, 100)
    emoji_interface.text_window.move(550, 500)
    
    # Add welcome messages to distinguish
    old_interface.text_window.add_output_text("This is the OLD interface with traditional eyes")
    emoji_interface.text_window.add_output_text("This is the NEW interface with emoji renderer")
    
    # Set different emotions to show contrast
    old_interface.eyes_window.set_emotion("happy")
    emoji_interface.emoji_window.set_emotion("happy")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
