#!/usr/bin/env python3
"""
UaiBot GUI launcher
Starts the graphical user interface for UaiBot
"""
import os
import sys
import platform

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Main function to start the GUI"""
    # Handle high DPI scaling on macOS
    if platform.system() == 'Darwin':
        os.environ['QT_MAC_WANTS_LAYER'] = '1'  # For macOS Retina displays
        
    # Check that we're not running from a PyInstaller binary
    # (which would have special handling)
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("UaiBot")
    app.setOrganizationName("UaiBot")
    app.setApplicationVersion("1.0.0")
    
    # Create main window
    window = MainWindow()
    
    # Show window and run application
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
