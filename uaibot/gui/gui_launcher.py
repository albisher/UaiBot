#!/usr/bin/env python3
"""
UaiBot GUI launcher
Starts the graphical user interface for UaiBot with dual window interface
"""
import os
import sys
import platform

# Add project root to sys.path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)  # Add the UaiBot directory itself

from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

# Import UI components with fallback paths
try:
    # Try to import the dual window interface
    from uaibot.gui.dual_window_emoji import UaiBotDualInterface
    USE_DUAL_INTERFACE = True
except ImportError:
    # Fall back to the basic interface
    from uaibot.gui.basic_interface import UaiBotBasicInterface
    USE_DUAL_INTERFACE = False

from uaibot.utils import load_config, get_project_root
from uaibot.core.ai_handler import AIHandler
from uaibot.core.shell_handler import ShellHandler
from platform_uai.platform_manager import PlatformManager

def show_error_and_exit(message):
    """Display error message and exit application"""
    app = QApplication.instance() or QApplication(sys.argv)
    QMessageBox.critical(None, "UaiBot Error", message)
    sys.exit(1)

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
    
    # Create splash screen if available
    try:
        splash_path = os.path.join(project_root, "gui", "resources", "splash.png")
        if os.path.exists(splash_path):
            splash_pixmap = QPixmap(splash_path)
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            app.processEvents()
        else:
            splash = None
    except Exception:
        splash = None
    
    # Load configuration
    config = load_config()
    if not config:
        if splash:
            splash.close()
        show_error_and_exit("Failed to load configuration. Please check config/settings.json")
        
    # Initialize platform manager
    platform_manager = PlatformManager()
    if not platform_manager.platform_supported:
        if splash:
            splash.close()
        show_error_and_exit(f"Unsupported platform: {platform.system()}")
        
    # Initialize platform-specific components
    if splash:
        splash.showMessage("Initializing platform components...", Qt.AlignBottom | Qt.AlignCenter)
        app.processEvents()
        
    if not platform_manager.initialize():
        if splash:
            splash.close()
        show_error_and_exit("Failed to initialize platform components")
    
    # Initialize shell and AI handlers
    if splash:
        splash.showMessage("Initializing system handlers...", Qt.AlignBottom | Qt.AlignCenter)
        app.processEvents()
        
    shell_handler = ShellHandler()
    ai_handler = AIHandler(config)
    
    # Create main interface
    if splash:
        splash.showMessage("Starting UaiBot interface...", Qt.AlignBottom | Qt.AlignCenter)
        app.processEvents()
    
    try:
        # Create the appropriate interface based on availability
        if USE_DUAL_INTERFACE:
            main_window = UaiBotDualInterface(
                shell_handler=shell_handler,
                ai_handler=ai_handler,
                platform_manager=platform_manager,
                config=config
            )
        else:
            main_window = UaiBotBasicInterface(
                shell_handler=shell_handler,
                ai_handler=ai_handler,
                platform_manager=platform_manager,
                config=config
            )
    except Exception as e:
        if splash:
            splash.close()
        show_error_and_exit(f"Failed to initialize the UI: {str(e)}")
    
    # Show main window and close splash
    main_window.show()
    if splash:
        splash.finish(main_window)
    
    # Run the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
