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
sys.path.append(current_dir)  # Add the UaiBot directory itself

from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.dual_window_emoji import UaiBotDualInterface
from core.utils import load_config, get_project_root
from core.ai_handler import AIHandler
from core.shell_handler import ShellHandler
from platform_uai.platform_manager import PlatformManager

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
    
    # Load configuration
    config = load_config()
    if not config:
        QMessageBox.critical(None, "Error", "Failed to load configuration. Please check config/settings.json")
        return 1
        
    # Initialize platform manager
    platform_manager = PlatformManager()
    if not platform_manager.platform_supported:
        QMessageBox.critical(None, "Error", f"Unsupported platform: {platform.system()}")
        return 1
        
    platform_manager.initialize()
    audio_handler = platform_manager.get_audio_handler()
    usb_handler = platform_manager.get_usb_handler()
    
    # Initialize AI and shell handlers
    try:
        # Initialize AI handler based on configuration
        ai_provider = config.get("default_ai_provider")
        ai_handler = None
        
        if not ai_provider:
            print("Warning: No default_ai_provider specified in configuration.")
        else:
            if ai_provider == "google":
                google_api_key = config.get("google_api_key")
                if not google_api_key:
                    google_api_key = os.getenv("GOOGLE_API_KEY")
                if not google_api_key:
                    print("Warning: Google API key not configured.")
                else:
                    google_model = config.get("default_google_model", "gemini-1.5-pro")
                    ai_handler = AIHandler(
                        model_type="google", 
                        api_key=google_api_key,
                        google_model_name=google_model
                    )
            elif ai_provider == "ollama":
                ollama_url = config.get("ollama_base_url", "http://localhost:11434")
                ollama_model = config.get("default_ollama_model", "llama2")
                ai_handler = AIHandler(
                    model_type="ollama",
                    ollama_base_url=ollama_url
                )
                ai_handler.set_ollama_model(ollama_model)
            else:
                print(f"Warning: Unknown AI provider '{ai_provider}'.")
                
        # Initialize shell handler
        shell_safe_mode = config.get("shell_safe_mode", True)
        shell_dangerous_check = config.get("shell_dangerous_check", True)
        shell_handler = ShellHandler(
            safe_mode=shell_safe_mode,
            enable_dangerous_command_check=shell_dangerous_check
        )
        
    except Exception as e:
        print(f"Warning: Failed to initialize handlers: {str(e)}")
        ai_handler = None
        shell_handler = None
    
    # Create dual window interface
    interface = UaiBotDualInterface()
    
    # Set handlers
    interface.set_handlers(ai_handler=ai_handler, shell_handler=shell_handler)
    
    # Show windows and run application
    interface.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
