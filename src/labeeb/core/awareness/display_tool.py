"""
Labeeb Display Tool

This module provides display-related functionality for Labeeb.
It handles screen management, display settings, and visual output capabilities.
"""
import logging
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon

@dataclass
class DisplayConfig:
    """Configuration for display output."""
    width: int = 800
    height: int = 600
    title: str = "Labeeb GUI"
    font_size: int = 14
    background_color: str = "#f0f0f0"
    text_color: str = "#000000"
    theme: str = "light"

class DisplayTool:
    """Tool for displaying visual elements in a GUI window."""
    
    name = 'display'
    description = "Display visual elements (emojis, images, text) in a GUI window"
    
    def __init__(self):
        self.logger = logging.getLogger("DisplayTool")
        self.app = QApplication.instance() or QApplication([])
        self.window = None
        self.config = DisplayConfig()
        self._setup_styles()
        
    def _setup_styles(self):
        """Setup default styles for the GUI."""
        self.styles = {
            "light": {
                "background": "#f0f0f0",
                "text": "#000000",
                "button": "#e0e0e0",
                "button_hover": "#d0d0d0"
            },
            "dark": {
                "background": "#2d2d2d",
                "text": "#ffffff",
                "button": "#3d3d3d",
                "button_hover": "#4d4d4d"
            }
        }
        
    def _ensure_window(self):
        """Ensure the display window exists."""
        if self.window is None:
            self.window = QMainWindow()
            self.window.setWindowTitle(self.config.title)
            self.window.setMinimumSize(self.config.width, self.config.height)
            
            # Create central widget and layout
            central_widget = QWidget()
            self.window.setCentralWidget(central_widget)
            self.layout = QVBoxLayout(central_widget)
            
            # Set window style
            style = self.styles[self.config.theme]
            self.window.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {style['background']};
                }}
                QLabel {{
                    color: {style['text']};
                    padding: 10px;
                }}
                QPushButton {{
                    background-color: {style['button']};
                    color: {style['text']};
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {style['button_hover']};
                }}
            """)
            
    async def show_emoji(self, emoji: str, size: int = 40) -> bool:
        """Display an emoji in the GUI window."""
        try:
            self._ensure_window()
            
            # Create label for emoji
            label = QLabel(emoji)
            font = QFont()
            font.setPointSize(size // 4)  # Convert pixel size to point size
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
            
            # Add to layout
            self.layout.addWidget(label)
            self.window.show()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to show emoji: {e}")
            return False
            
    async def show_text(self, text: str, size: int = 14, color: str = None) -> bool:
        """Display text in the GUI window."""
        try:
            self._ensure_window()
            
            # Create label for text
            label = QLabel(text)
            font = QFont()
            font.setPointSize(size)
            label.setFont(font)
            
            # Use theme color if not specified
            if color is None:
                color = self.styles[self.config.theme]['text']
            label.setStyleSheet(f"color: {color};")
            
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            
            # Add to layout
            self.layout.addWidget(label)
            self.window.show()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to show text: {e}")
            return False
            
    async def show_image(self, image_path: str, size: Tuple[int, int] = (400, 400)) -> bool:
        """Display an image in the GUI window."""
        try:
            self._ensure_window()
            
            # Create label for image
            label = QLabel()
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(*size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            
            # Add to layout
            self.layout.addWidget(label)
            self.window.show()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to show image: {e}")
            return False
            
    async def clear(self) -> bool:
        """Clear all displayed elements."""
        try:
            if self.window:
                # Clear layout
                while self.layout.count():
                    item = self.layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to clear display: {e}")
            return False
            
    async def configure(self, **kwargs) -> bool:
        """Configure display settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to configure display: {e}")
            return False
            
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute a display action."""
        try:
            # Handle text display directly
            if "text" in kwargs:
                return await self.show_text(kwargs["text"])
            
            # Handle other actions
            actions = {
                "show_emoji": lambda: self.show_emoji(kwargs.get("emoji", ""), kwargs.get("size", 40)),
                "show_text": lambda: self.show_text(kwargs.get("text", ""), kwargs.get("size", 14)),
                "show_image": lambda: self.show_image(kwargs.get("image_path", ""), kwargs.get("size", (400, 400))),
                "clear": self.clear,
                "configure": lambda: self.configure(**kwargs)
            }
            
            if action not in actions:
                raise ValueError(f"Unknown action: {action}")
                
            return await actions[action]()
        except Exception as e:
            self.logger.error(f"Error executing display action: {e}")
            return False 