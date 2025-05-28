import gettext
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from .basic_interface import BasicInterface

# Initialize translations
LOCALE_DIR = Path(__file__).parent.parent.parent / 'locales'
gettext.bindtextdomain('labeeb', str(LOCALE_DIR))
gettext.textdomain('labeeb')
_ = gettext.gettext

class LabeebGUI(QMainWindow):
    """Main GUI window for Labeeb with i18n support."""
    
    def __init__(self):
        super().__init__()
        self.interface = BasicInterface()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(self.interface.get_text('Labeeb AI Assistant'))
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add welcome message
        welcome_label = QLabel(self.interface.get_text('Welcome to Labeeb AI Assistant'))
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Add language selection buttons
        lang_layout = QVBoxLayout()
        lang_label = QLabel(self.interface.get_text('Select Language / اختر اللغة'))
        lang_layout.addWidget(lang_label)
        
        en_button = QPushButton('English')
        en_button.clicked.connect(lambda: self.interface.set_language('en'))
        lang_layout.addWidget(en_button)
        
        ar_button = QPushButton('العربية')
        ar_button.clicked.connect(lambda: self.interface.set_language('ar'))
        lang_layout.addWidget(ar_button)
        
        layout.addLayout(lang_layout)
        
        # Add main action buttons
        start_button = QPushButton(self.interface.get_text('Start Labeeb / ابدأ لبيب'))
        start_button.clicked.connect(self.start_labeeb)
        layout.addWidget(start_button)
        
        settings_button = QPushButton(self.interface.get_text('Settings / الإعدادات'))
        settings_button.clicked.connect(self.show_settings)
        layout.addWidget(settings_button)
        
        help_button = QPushButton(self.interface.get_text('Help / المساعدة'))
        help_button.clicked.connect(self.show_help)
        layout.addWidget(help_button)
    
    def start_labeeb(self):
        """Start the Labeeb AI assistant."""
        # TODO: Implement Labeeb startup logic
        pass
    
    def show_settings(self):
        """Show settings dialog."""
        # TODO: Implement settings dialog
        pass
    
    def show_help(self):
        """Show help dialog."""
        # TODO: Implement help dialog
        pass

def launch_gui():
    """Launch the Labeeb GUI application."""
    app = QApplication([])
    window = LabeebGUI()
    window.show()
    return app.exec_()
