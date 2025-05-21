"""
UaiBot - Dual Window Implementation with Emoji-Based Avatar
Creates two separate windows: one for the robot emoji avatar and one for text I/O
Supports multimodal inputs including text, images, audio, and gestures
"""
import sys
import re
import os
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGraphicsScene, 
                            QGraphicsView, QGraphicsItem, QStyleOptionGraphicsItem,
                            QVBoxLayout, QHBoxLayout, QTextEdit, QFrame, QSplitter,
                            QPushButton, QLabel, QLineEdit, QFileDialog, QToolBar, 
                            QAction, QMenu, QMessageBox)
from PyQt5.QtGui import (QPainter, QBrush, QColor, QPen, QRadialGradient, QPixmap,
                        QFont, QPainterPath, QPolygonF, QIcon)
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal, QSize, QByteArray, QBuffer, QUrl
from PyQt5.QtMultimedia import QAudioRecorder, QAudioEncoderSettings

# Import the new EmojiAvatar
from uaibot.gui.emoji_avatar import EmojiAvatar
from uaibot.utils import get_platform_name

class EmojiWindow(QMainWindow):
    """Window that displays the robot emoji face"""
    emotion_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot")
        self.setGeometry(100, 100, 400, 350)  # Slightly taller for emoji
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)  # Add a small margin
        
        # Create graphics scene for emoji avatar
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor(45, 45, 60))  # Slightly dark background
        
        # Create and add emoji avatar
        self.robot_emoji = EmojiAvatar()
        self.scene.addItem(self.robot_emoji)
        
        # Create view for the emoji
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setFrameShape(QFrame.NoFrame)  # No border
        
        # Add view to layout
        layout.addWidget(self.view)
        
        # Add a label for the current emotion
        self.emotion_label = QLabel("neutral")
        self.emotion_label.setAlignment(Qt.AlignCenter)
        self.emotion_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;
            }
        """)
        layout.addWidget(self.emotion_label)
        
        # Set initial emotion
        self.set_emotion("neutral")
        
    def resizeEvent(self, event):
        """Handle window resize to keep emoji properly sized and centered"""
        super().resizeEvent(event)
        # Update view to fit properly with padding
        self.scene.setSceneRect(self.robot_emoji.boundingRect().adjusted(-50, -50, 50, 50))
        
        # Make the emoji fit nicely in the view
        self.view.fitInView(
            self.robot_emoji.boundingRect().adjusted(-20, -20, 20, 20),
            Qt.KeepAspectRatio
        )
        
        # Add a slight delay to ensure proper rendering after resize
        QTimer.singleShot(50, lambda: self.view.fitInView(
            self.robot_emoji.boundingRect().adjusted(-20, -20, 20, 20),
            Qt.KeepAspectRatio
        ))
        
    def set_emotion(self, emotion):
        """Set the emoji avatar emotion"""
        # Map old emotions to new emoji avatar emotions if necessary
        emotion_mapping = {
            "surprise": "surprised",
            "curious": "thinking"
        }
        
        # Apply mapping if needed
        mapped_emotion = emotion_mapping.get(emotion, emotion)
        
        # Set the emotion
        self.robot_emoji.set_emotion(mapped_emotion)
        self.emotion_label.setText(emotion.capitalize())
        self.emotion_changed.emit(emotion)  # Emit signal for other windows to sync


class TextWindow(QMainWindow):
    """Window for text input/output interaction"""
    command_submitted = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot Command Interface")
        self.setGeometry(100, 450, 700, 500)  # Position below the emoji window
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)  # More padding for better readability
        
        # Output text area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumHeight(300)  # More space for output text (10+ lines)
        self.output_area.setStyleSheet("""
            QTextEdit { 
                background-color: #2d2d35; 
                color: #f0f0f0;
                border: 1px solid #3a3a45;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.output_area.setFont(QFont("Menlo", 12))  # Better font for code
        layout.addWidget(self.output_area)
        
        # Input area
        input_layout = QHBoxLayout()
        input_label = QLabel("Enter command:")
        input_layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.submit_command)
        self.input_field.setStyleSheet("""
            QLineEdit { 
                background-color: #2d2d35; 
                color: #f0f0f0; 
                border: 1px solid #3a3a45;
                border-radius: 5px;
                padding: 8px;
                selection-background-color: #3a5f8a;
            }
        """)
        self.input_field.setFont(QFont("Menlo", 12))
        self.input_field.setPlaceholderText("Type a command or question...")
        input_layout.addWidget(self.input_field)
        
        self.submit_button = QPushButton("Send")
        self.submit_button.clicked.connect(self.submit_command)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5b87;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a6fa8;
            }
            QPushButton:pressed {
                background-color: #1c4570;
            }
        """)
        input_layout.addWidget(self.submit_button)
        
        layout.addLayout(input_layout)
        
        # Toolbar for multimodal input
        self.toolbar = QToolBar("Multimodal Input")
        self.addToolBar(self.toolbar)
        
        # Action for image input
        self.image_action = QAction(QIcon.fromTheme("image-x-generic"), "Insert Image", self)
        self.image_action.setShortcut("Ctrl+I")
        self.image_action.triggered.connect(self.insert_image)
        self.toolbar.addAction(self.image_action)
        
        # Action for audio input
        self.audio_action = QAction(QIcon.fromTheme("audio-x-generic"), "Record Audio", self)
        self.audio_action.setShortcut("Ctrl+R")
        self.audio_action.triggered.connect(self.record_audio)
        self.toolbar.addAction(self.audio_action)
        
        # Action for gesture input (placeholder, not functional)
        self.gesture_action = QAction(QIcon.fromTheme("edit-undo"), "Gesture Input (Beta)", self)
        self.gesture_action.setShortcut("Ctrl+G")
        self.gesture_action.triggered.connect(self.gesture_input)
        self.toolbar.addAction(self.gesture_action)
        
        # Menu for file operations
        self.file_menu = self.menuBar().addMenu("File")
        self.file_menu.addAction(self.image_action)
        self.file_menu.addAction(self.audio_action)
        self.file_menu.addAction(self.gesture_action)
        
        # Status bar message
        self.statusBar().showMessage("Ready")
        
    def add_output_text(self, text):
        """Add text to the output area"""
        self.output_area.append(text)
        # Auto-scroll to the bottom
        scrollbar = self.output_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def submit_command(self):
        """Submit the command from the input field"""
        command = self.input_field.text().strip()
        if command:
            self.command_submitted.emit(command)
            self.input_field.clear()
            
    def insert_image(self):
        """Insert an image file into the input field"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", 
                                                   "Images (*.png *.xpm *.jpg *.jpeg *.bmp);;All Files (*)", 
                                                   options=options)
        if file_name:
            # For now, just insert the file path as text
            self.input_field.setText(f"![Image]({file_name})")
            self.submit_command()
        
    def record_audio(self):
        """Record audio input and insert file path"""
        # Use a temporary file for audio recording
        temp_file, _ = tempfile.mkstemp(suffix=".wav", prefix="uaibot_")
        os.close(temp_file)  # Close the file descriptor
        
        # Set up audio recorder
        self.audio_recorder = QAudioRecorder()
        audio_settings = QAudioEncoderSettings()
        audio_settings.setCodec("audio/pcm")
        audio_settings.setSampleRate(16000)
        audio_settings.setBitRate(128000)
        audio_settings.setChannelCount(1)
        self.audio_recorder.setEncodingSettings(audio_settings)
        
        # Set the output file
        self.audio_recorder.setOutputLocation(QUrl.fromLocalFile(temp_file))
        
        # Start recording
        self.audio_recorder.record()
        self.statusBar().showMessage("Recording audio... Press 'Stop' to end.")
        
        # Add a stop button to the toolbar
        self.stop_action = QAction("Stop Recording", self)
        self.stop_action.setShortcut("Ctrl+S")
        self.stop_action.triggered.connect(self.stop_audio_recording)
        self.toolbar.addAction(self.stop_action)
        
    def stop_audio_recording(self):
        """Stop audio recording and process the file"""
        self.audio_recorder.stop()
        self.statusBar().showMessage("Audio recording stopped.")
        
        # Get the recorded file path
        recorded_file = self.audio_recorder.outputLocation().toLocalFile()
        if recorded_file:
            # For now, just insert the file path as text
            self.input_field.setText(f"[Audio]({recorded_file})")
            self.submit_command()
        else:
            QMessageBox.warning(self, "Recording Error", "Failed to locate the recorded audio file.")
        
        # Remove the stop action
        self.toolbar.removeAction(self.stop_action)
        
    def gesture_input(self):
        """Placeholder for gesture input functionality"""
        QMessageBox.information(self, "Gesture Input", "Gesture input is not yet functional.")
        

class UaiBotDualInterface:
    """Controller class that manages both windows and their interactions"""
    def __init__(self, ai_handler=None, shell_handler=None, command_processor=None, quiet_mode=False):
        self.eyes_window = EmojiWindow()  # Keep old name for compatibility
        self.emoji_window = self.eyes_window  # Add new name 
        self.text_window = TextWindow()
        
        # Store handlers if provided
        self.ai_handler = ai_handler
        self.shell_handler = shell_handler
        self.command_processor = command_processor
        self.quiet_mode = quiet_mode
        
        # Connect signals
        self.text_window.command_submitted.connect(self.handle_command)
        
        # Welcome message
        self.text_window.add_output_text("Welcome to UaiBot!")
        self.text_window.add_output_text("I'm your AI assistant.")
        self.text_window.add_output_text("Type commands or questions for help.")
        
    def show(self):
        """Show both windows and initialize the interface"""
        self.eyes_window.show()
        self.text_window.show()
        
        # Position the windows appropriately on screen for better visibility
        self.text_window.move(self.eyes_window.x(), 
                              self.eyes_window.y() + self.eyes_window.height() + 30)
        
    def set_handlers(self, ai_handler=None, shell_handler=None, command_processor=None, quiet_mode=None):
        """Set or update the handlers"""
        if ai_handler:
            self.ai_handler = ai_handler
        if shell_handler:
            self.shell_handler = shell_handler
        if command_processor:
            self.command_processor = command_processor
        if quiet_mode is not None:
            self.quiet_mode = quiet_mode
            
    def handle_command(self, command):
        """Process user commands"""
        # Display user's command
        self.text_window.add_output_text(f"\nYou: {command}")
        
        # Set emoji to thinking state while "processing"
        self.eyes_window.set_emotion("thinking")
        
        # Determine current platform
        import platform
        self.system_platform = platform.system().lower()
        self.platform_name = get_platform_name()
        
        # Special commands for emotions (handle locally in GUI)
        emotion_commands = {
            "happy": "I'm happy to help!",
            "sad": "I'm sorry to hear that.",
            "surprise": "Wow, that's amazing!",
            "surprised": "Wow, that's amazing!",
            "confused": "I'm not sure I understand...",
            "neutral": "I'm here to assist you!",
            "thinking": "Let me think about that...",
            "worried": "I'm a bit concerned about that."
        }
        
        # Check for direct emotion commands or special UaiBot commands
        if command.lower().startswith("emotion "):
            emotion = command.lower().split(" ", 1)[1].strip()
            if emotion in ["happy", "sad", "surprise", "surprised", "confused", "neutral", "curious", "thinking", "worried"]:
                self.eyes_window.set_emotion(emotion)
                self.text_window.add_output_text(f"UaiBot: Emotion set to {emotion}!")
                return
            else:
                self.text_window.add_output_text(f"UaiBot: Unknown emotion '{emotion}'. Available emotions: happy, sad, surprised, confused, neutral, thinking, worried")
                return
        
        # Check for VS Code reading requests
        vscode_patterns = [
            "read vscode", "read vs code", "read what's on vscode", "read what is on vscode",
            "what's open in vscode", "what is open in vscode", "show vscode files", 
            "read what is opened on my vscode screen", "what's on my vscode screen", 
            "read my vscode screen", "show me what's open in vscode", "open new vscode window",
            "what is now on my current vscode", "what is now on my vscode page", 
            "what is on my vscode page", "what's on my vscode page", "what's on my current vscode page",
            "check vscode", "see vscode files", "open vscode and read", "check what's in vscode",
            "view vscode content", "see what's in vs code", "read vs files", "get vscode content",
            "show vs code content", "read current vscode files", "what files are open in vscode",
            "display vscode files", "show code editor content", "what's in the code editor"
        ]
        
        def is_vscode_read_request(text):
            """Better detection of VS Code read requests"""
            text = text.lower()
            # Check direct patterns
            if any(pattern in text for pattern in vscode_patterns):
                return True
            
            # Look for specific keywords that strongly indicate a VS Code read request
            strong_indicators = [
                "show me vs", "check vs", "read vs", "look at vs", 
                "show me what's in vs", "read what's in vs", 
                "show vs", "current vs", "vs content",
                "open files", "editor files", "editor content",
                "what's on my screen"
            ]
            
            if any(indicator in text for indicator in strong_indicators):
                return True
                
            # Check for VS Code + reading related words in the same sentence
            vscode_terms = ["vscode", "vs code", "visual studio code", "code editor", "editor", "vs"]
            read_terms = ["read", "show", "see", "check", "display", "view", "get", "what's open", 
                         "what is open", "what's in", "what is in", "content", "files", "opened", "current"]
            
            # Only match if both types of terms are present, with a higher threshold for generic terms
            if any(vt in text for vt in vscode_terms) and any(rt in text for rt in read_terms):
                # For more generic terms like "editor" + "show", require more context or proximity
                generic_terms = ["editor", "vs"]
                if any(gt in text for gt in generic_terms):
                    # Look for closer proximity of terms or additional context indicators
                    if "files" in text or "open" in text or "code" in text or "current" in text:
                        return True
                else:
                    # More specific VS Code terms can match with fewer constraints
                    return True
                    
            return False
        
        if is_vscode_read_request(command):
            self.text_window.add_output_text("\nUaiBot: Reading content from VS Code...")
            self.eyes_window.set_emotion("thinking")
            
            try:
                if self.shell_handler:
                    # For "open new vscode window" or similar, try to launch VS Code first
                    should_launch = any(p in command.lower() for p in ["open", "launch", "start"]) and \
                                   any(p in command.lower() for p in ["vscode", "vs code", "visual studio"])
                                   
                    if should_launch:
                        launch_cmd = None
                        if self.system_platform == "darwin":  # macOS
                            launch_cmd = "open -a 'Visual Studio Code'"
                        elif self.system_platform in ["linux", "windows"]:
                            launch_cmd = "code"
                            
                        if launch_cmd:
                            try:
                                open_result = self.shell_handler.execute_command(launch_cmd)
                                self.text_window.add_output_text(f"\nLaunching VS Code... Please wait a moment.")
                                # Give VS Code time to open
                                import time
                                time.sleep(3)
                            except Exception as e:
                                self.text_window.add_output_text(f"\nFailed to launch VS Code: {str(e)}")
                    
                    # Use the enhanced method to get VS Code open files and content
                    result = self.shell_handler.get_vscode_open_files()
                    
                    # Check if the result actually contains files or error conditions
                    if "Error" in result or "not appear to be running" in result:
                        self.text_window.add_output_text(f"\n{result}")
                        self.eyes_window.set_emotion("confused")
                        
                        # Suggest opening VS Code if it's not running
                        if "not appear to be running" in result:
                            if self.system_platform == "darwin":
                                self.text_window.add_output_text("\nWould you like to open VS Code now? Type '!open -a \"Visual Studio Code\"' to launch it.")
                            elif self.system_platform in ["linux", "windows"]:
                                self.text_window.add_output_text("\nWould you like to open VS Code now? Type '!code' to launch it.")
                    elif "Could not access" in result:
                        # Permissions issue or other access problem
                        self.text_window.add_output_text(f"\n{result}")
                        self.text_window.add_output_text("\nThere might be a permissions issue. VS Code may need to be the active application.")
                        self.eyes_window.set_emotion("confused")
                    else:
                        # We got some content to show
                        self.text_window.add_output_text(f"\n{result}")
                        self.eyes_window.set_emotion("happy")
                else:
                    # No shell handler available
                    self.text_window.add_output_text("Shell handler not initialized! Cannot access VS Code content.")
                    self.eyes_window.set_emotion("confused")
            except Exception as e:
                self.text_window.add_output_text(f"Error reading VS Code files: {str(e)}")
                self.eyes_window.set_emotion("sad")
            return
                
        # Check for browser reading requests
        browser_patterns = [
            "read browser", "what's in my browser", "what is in my browser", "show browser tabs",
            "what's open in browser", "what is open in browser", "show browser content", 
            "read what is opened in my browser", "what's on my browser", 
            "read my browser", "show me what's open in browser", "open browser",
            "what is now on my browser", "what is on my browser page", 
            "what's on my browser page", "check browser", "see browser tabs", 
            "check what's in browser", "view browser content", "see what's in browser",
            "read browser tabs", "get browser content", "show browser content", 
            "what tabs are open in browser", "display browser tabs", "read firefox", 
            "read chrome", "read safari", "show me chrome tabs", "show me firefox tabs",
            "what's in chrome", "what's in firefox", "what's in safari", "what is in firefox", 
            "what is in chrome", "what is in safari"
        ]
        
        def is_browser_read_request(text):
            """Detection of browser read requests"""
            text = text.lower()
            # Check direct patterns
            if any(pattern in text for pattern in browser_patterns):
                return True
            
            # Look for specific keywords that strongly indicate a browser read request
            browser_names = ["browser", "chrome", "firefox", "safari", "edge", "brave", "opera"]
            read_terms = ["read", "show", "see", "check", "display", "view", "get", "what's open", 
                         "what is open", "what's in", "what is in", "content", "tabs", "opened", "current"]
            
            # Return browser name if mentioned specifically
            for browser in ["firefox", "chrome", "safari", "edge", "brave", "opera"]:
                if browser in text:
                    return browser
                    
            # Only match if both types of terms are present
            if any(bn in text for bn in browser_names) and any(rt in text for rt in read_terms):
                return True
                    
            return False
        
        # Check if this is a browser content request and process it
        browser_request = is_browser_read_request(command)
        if browser_request:
            self.text_window.add_output_text("\nUaiBot: Reading content from your browser...")
            self.eyes_window.set_emotion("thinking")
            
            try:
                if self.shell_handler:
                    # If a specific browser was mentioned, use that
                    specific_browser = None
                    if browser_request in ["firefox", "chrome", "safari", "edge", "brave", "opera"]:
                        specific_browser = browser_request
                    
                    # For "open browser" or similar, try to launch a browser first
                    should_launch = any(p in command.lower() for p in ["open", "launch", "start"])
                    
                    if should_launch:
                        launch_cmd = None
                        default_browser = "chrome" if not specific_browser else specific_browser
                        
                        if self.system_platform == "darwin":  # macOS
                            browser_apps = {
                                "chrome": "Google Chrome",
                                "firefox": "Firefox",
                                "safari": "Safari",
                                "edge": "Microsoft Edge",
                                "brave": "Brave Browser",
                                "opera": "Opera"
                            }
                            browser_app = browser_apps.get(default_browser, "Safari")
                            launch_cmd = f"open -a '{browser_app}'"
                            
                        elif self.system_platform == "linux":
                            browser_commands = {
                                "chrome": "google-chrome",
                                "firefox": "firefox",
                                "edge": "microsoft-edge",
                                "brave": "brave-browser",
                                "opera": "opera"
                            }
                            launch_cmd = browser_commands.get(default_browser, "xdg-open https://www.google.com")
                            
                        elif self.system_platform == "windows":
                            browser_commands = {
                                "chrome": "start chrome",
                                "firefox": "start firefox",
                                "edge": "start msedge",
                                "brave": "start brave",
                                "opera": "start opera"
                            }
                            launch_cmd = browser_commands.get(default_browser, "start https://www.google.com")
                            
                        if launch_cmd:
                            try:
                                open_result = self.shell_handler.execute_command(launch_cmd)
                                self.text_window.add_output_text(f"\nLaunching browser... Please wait a moment.")
                                # Give browser time to open
                                import time
                                time.sleep(3)
                            except Exception as e:
                                self.text_window.add_output_text(f"\nFailed to launch browser: {str(e)}")
                    
                    # Use the browser content detection method
                    result = self.shell_handler.get_browser_content(specific_browser)
                    
                    # Check if the result contains content or error conditions
                    if "Error" in result or "No" in result or "not detected" in result:
                        self.text_window.add_output_text(f"\n{result}")
                        self.eyes_window.set_emotion("confused")
                        
                        # Suggest opening browser if nothing is running
                        if "No" in result or "not detected" in result:
                            if self.system_platform == "darwin":
                                self.text_window.add_output_text("\nWould you like to open a browser now? Type '!open -a \"Google Chrome\"' to launch Chrome.")
                            elif self.system_platform == "linux":
                                self.text_window.add_output_text("\nWould you like to open a browser now? Type '!firefox' to launch Firefox.")
                            else:  # Windows
                                self.text_window.add_output_text("\nWould you like to open a browser now? Type '!start chrome' to launch Chrome.")
                    else:
                        # We got browser content to show
                        self.text_window.add_output_text(f"\n{result}")
                        self.eyes_window.set_emotion("happy")
                else:
                    # No shell handler available
                    self.text_window.add_output_text("Shell handler not initialized! Cannot access browser content.")
                    self.eyes_window.set_emotion("confused")
            except Exception as e:
                self.text_window.add_output_text(f"Error reading browser content: {str(e)}")
                self.eyes_window.set_emotion("sad")
            return
                
        # Check for direct command execution
        if command.lower().startswith("!"):
            # Shell command execution mode
            shell_command = command[1:].strip()
            self.text_window.add_output_text(f"Executing shell command: {shell_command}")
            try:
                if self.shell_handler:
                    # Execute using the shell handler
                    result = self.shell_handler.execute_command(shell_command)
                    self.text_window.add_output_text(f"Output: {result}")
                    self.eyes_window.set_emotion("happy")
                else:
                    # No shell handler available
                    self.text_window.add_output_text("Shell handler not initialized!")
                    self.eyes_window.set_emotion("confused")
            except Exception as e:
                self.text_window.add_output_text(f"Error executing command: {str(e)}")
                self.eyes_window.set_emotion("sad")
            return
            
        # Check for "run" or task execution commands
        if command.lower() in ["run", "execute", "do it"] or "take the needed steps" in command.lower() or "do the task" in command.lower():
            # Look for the most recent code block in the output
            output_text = self.text_window.output_area.toPlainText()
            
            # Try to find code blocks with ``` or commands suggested by AI
            # Search for markdown code blocks
            code_blocks = re.findall(r'```(?:bash|shell|\w*)\s*(.*?)```', output_text, re.DOTALL)
            
            # Search for specific terminal commands on separate lines
            if not code_blocks:
                command_lines = re.findall(r'(?:^|\n)\s*(?:[$>]|command:|run:)?\s*((?:find|grep|ls|cat|cp|mv|mkdir)\s+[^\n]+)', output_text)
                if command_lines:
                    code_blocks = command_lines
            
            # If the AI suggested a specific command with `-name cv` in it, prioritize it
            cv_commands = [cmd for cmd in code_blocks if '-name cv' in cmd or '-name "*cv*"' in cmd]
            if cv_commands:
                code_blocks = cv_commands
            
            if code_blocks:
                # Get the most relevant command and clean it
                shell_command = code_blocks[-1].strip()
                self.text_window.add_output_text(f"Executing command: {shell_command}")
                try:
                    if self.shell_handler:
                        result = self.shell_handler.execute_command(shell_command)
                        self.text_window.add_output_text(f"Output: {result}")
                        self.eyes_window.set_emotion("happy")
                    else:
                        self.text_window.add_output_text("Shell handler not initialized!")
                        self.eyes_window.set_emotion("confused")
                except Exception as e:
                    self.text_window.add_output_text(f"Error executing command: {str(e)}")
                    self.eyes_window.set_emotion("sad")
                return
            else:
                # Search harder for any command looking pattern in the AI's response
                command_search = re.search(r'(?:\n|^)[\s*`]*((?:find|grep|ls|cat)\s+\/?\S+(?:\s+-\w+\s+\S+)*)', output_text)
                if command_search:
                    shell_command = command_search.group(1).strip('`* ')
                    self.text_window.add_output_text(f"Found and executing command: {shell_command}")
                    try:
                        if self.shell_handler:
                            result = self.shell_handler.execute_command(shell_command)
                            self.text_window.add_output_text(f"Output: {result}")
                            self.eyes_window.set_emotion("happy")
                        else:
                            self.text_window.add_output_text("Shell handler not initialized!")
                            self.eyes_window.set_emotion("confused")
                    except Exception as e:
                        self.text_window.add_output_text(f"Error executing command: {str(e)}")
                        self.eyes_window.set_emotion("sad")
                    return
                
                self.text_window.add_output_text("No specific command found to execute. Please specify a command or say '!find $HOME -name \"*cv*\"' to search for files containing 'cv'.")
                self.eyes_window.set_emotion("confused")
                return
                
        # Check for automatic task execution request
        if "it needs to take the needed steps" in command.lower() or "needs to do the task" in command.lower():
            # Automatically execute the task without waiting for user input
            self.text_window.add_output_text("\nUaiBot: I'll execute the appropriate command for you...")
            
            # Parse the intent and run the command directly
            if "find" in command.lower() and "cv" in command.lower():
                shell_command = 'find $HOME -name "*cv*" 2>/dev/null | head -20'
                self.eyes_window.set_emotion("happy")
                try:
                    if self.shell_handler:
                        self.text_window.add_output_text(f"Executing command: {shell_command}")
                        result = self.shell_handler.execute_command(shell_command)
                        self.text_window.add_output_text(f"Output:\n{result}")
                    else:
                        self.text_window.add_output_text("Shell handler not initialized!")
                except Exception as e:
                    self.text_window.add_output_text(f"Error: {str(e)}")
                    self.eyes_window.set_emotion("sad")
            else:
                self.text_window.add_output_text("I'm not sure what task you want me to execute. Please be more specific.")
                self.eyes_window.set_emotion("curious")
            return
                
        # Use command processor for handling commands
        if self.command_processor:
            try:
                # Process the command through main's command processor
                result = self.command_processor.process_command(command)
                
                # Display the result in the GUI
                self.text_window.add_output_text(f"UaiBot: {result}")
                
                # Also print to terminal if not in quiet mode
                if not self.quiet_mode:
                    print(f"[GUI Command] {command}")
                    print(f"Result: {result}")
                
                # Determine emotion based on response content
                emotion = "neutral"
                if "error" in result.lower() or "failed" in result.lower():
                    emotion = "confused"
                elif "sorry" in result.lower():
                    emotion = "sad"
                elif "great" in result.lower() or "success" in result.lower():
                    emotion = "happy"
                
                # Set emotion based on response
                self.eyes_window.set_emotion(emotion)
                
            except Exception as e:
                error_msg = f"Error processing command: {str(e)}"
                self.text_window.add_output_text(error_msg)
                if not self.quiet_mode:
                    print(error_msg)
                self.eyes_window.set_emotion("sad")
        
        # Fall back to AI handler if command processor not available
        elif self.ai_handler:
            try:
                # Query AI for response
                ai_response = self.ai_handler.query_ai(command)
                
                # Determine emotion based on response content
                emotion = "neutral"
                for emotion_key in emotion_commands.keys():
                    if emotion_key in command.lower() or emotion_key in ai_response.lower():
                        emotion = emotion_key
                        break
                
                # Display the AI response
                self.text_window.add_output_text(f"UaiBot: {ai_response}")
                
                # Set emotion based on response
                self.eyes_window.set_emotion(emotion)
                
            except Exception as e:
                self.text_window.add_output_text(f"Error: {str(e)}")
                self.eyes_window.set_emotion("sad")
        else:
            # No command processor or AI handler available
            self.text_window.add_output_text("UaiBot: Command processors not initialized! Cannot process your request.")
            self.eyes_window.set_emotion("confused")
            
    def shutdown(self):
        """Clean shutdown of the interface"""
        # Close windows
        self.eyes_window.close()
        self.text_window.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    interface = UaiBotDualInterface()
    interface.show()
    sys.exit(app.exec_())
