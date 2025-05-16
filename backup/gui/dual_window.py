"""
UaiBot - Dual Window Implementation
Creates two separate windows: one for the robot emoji avatar and one for text I/O
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGraphicsScene, 
                            QGraphicsView, QGraphicsItem, QStyleOptionGraphicsItem,
                            QVBoxLayout, QHBoxLayout, QTextEdit, QFrame, QSplitter,
                            QPushButton, QLabel, QLineEdit)
from PyQt5.QtGui import (QPainter, QBrush, QColor, QPen, QRadialGradient, QPixmap,
                        QFont, QPainterPath, QPolygonF)
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal, QSize

# Import the RobotEmojiRenderer from new_avatar.py
from gui.new_avatar import RobotEmojiRenderer, RobotEmojiItem

# Create a RobotEmojiItem for the dual window interface
            else:  # Right eye
                top_lid_curve = self.eye_height * 0.15
            pupil_size_factor = 0.35
            pupil_offset_x = self.eye_width * 0.05 * (1 if center.x() < 0 else -1)  # Pupils slightly inward/focused
        elif self.current_emotion == "surprise" or self.current_emotion == "confused":
            current_eye_height = self.eye_height * 1.2
            pupil_size_factor = 0.6  # Large pupils
            led_ring_intensity = 1.5
        elif self.current_emotion == "sad" or self.current_emotion == "concerned":
            top_lid_curve = -self.eye_height * 0.25  # Drooping top
            bottom_lid_curve = self.eye_height * 0.1  # Slight downturn or flat
            pupil_size_factor = 0.3
            pupil_offset_y = self.eye_height * 0.1  # Looking slightly down
        elif self.current_emotion == "neutral":
            pass  # Use defaults

        # Apply blinking if in blink animation
        if self._is_blinking:
            # When blinking, reduce the eye opening by adjusting the eyelid curves
            blink_factor = self._blink_progress
            current_eye_height = self.eye_height * (1.0 - blink_factor * 0.8)
            top_lid_curve = top_lid_curve * (1.0 - blink_factor)
            bottom_lid_curve = bottom_lid_curve * (1.0 - blink_factor)

        eye_rect = QRectF(center.x() - self.eye_width / 2,
                         center.y() - current_eye_height / 2,
                         self.eye_width, current_eye_height)

        # --- Glow Effect (Outer) ---
        glow_radius = self.eye_width * 0.8 * led_ring_intensity
        gradient_outer = QRadialGradient(center, glow_radius)
        gradient_outer.setColorAt(0, self.glow_color_inner)
        gradient_outer.setColorAt(0.7, self.glow_color_outer)
        gradient_outer.setColorAt(1, QColor(0, 0, 0, 0))  # Transparent outer edge
        painter.setBrush(QBrush(gradient_outer))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, glow_radius, glow_radius)
        
        # --- Eye Shape (Clipping Path for Iris/Pupil) ---
        eye_path = QPainterPath()
        # Top curve
        eye_path.moveTo(eye_rect.left(), center.y())
        eye_path.quadTo(center.x(), center.y() - top_lid_curve - current_eye_height * 0.5, eye_rect.right(), center.y())
        # Bottom curve
        eye_path.quadTo(center.x(), center.y() - bottom_lid_curve + current_eye_height * 0.5, eye_rect.left(), center.y())
        eye_path.closeSubpath()
        
        painter.save()
        painter.setClipPath(eye_path)  # Iris and pupil will be clipped to this eye shape

        # --- Iris ---
        iris_radius = min(self.eye_width, current_eye_height) * 0.45
        painter.setBrush(QBrush(self.base_eye_color))
        painter.setPen(Qt.NoPen)  # No outline for iris
        painter.drawEllipse(center, iris_radius, iris_radius)

        # --- LED Ring (inside iris, around pupil) ---
        led_ring_radius_outer = iris_radius * 0.8 * led_ring_intensity
        led_ring_radius_inner = iris_radius * 0.7 * led_ring_intensity
        pen_led = QPen(self.glow_color_inner, 2 * led_ring_intensity)
        painter.setPen(pen_led)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, led_ring_radius_outer, led_ring_radius_outer)
        if self.current_emotion in ["surprise", "confused"]:  # extra inner ring for surprise/confused
             painter.drawEllipse(center, led_ring_radius_inner*0.8, led_ring_radius_inner*0.8)

        # --- Pupil ---
        pupil_radius = iris_radius * pupil_size_factor
        pupil_center = QPointF(center.x() + pupil_offset_x, center.y() + pupil_offset_y)
        painter.setBrush(QBrush(self.pupil_color))
        painter.drawEllipse(pupil_center, pupil_radius, pupil_radius)

        # --- Highlight ---
        highlight_size = pupil_radius * 0.5
        highlight_pos = QPointF(pupil_center.x() - pupil_radius * 0.3,
                                pupil_center.y() - pupil_radius * 0.3)
        painter.setBrush(QBrush(self.highlight_color))
        painter.drawEllipse(highlight_pos, highlight_size, highlight_size)
        if self.current_emotion == "happy":  # Extra smaller highlight for happy
            highlight_pos2 = QPointF(pupil_center.x() + pupil_radius * 0.4,
                                    pupil_center.y() + pupil_radius * 0.1)
            painter.drawEllipse(highlight_pos2, highlight_size*0.6, highlight_size*0.6)

        painter.restore()  # Restore clipping

        # --- Optional: Outer line for the eye shape itself for definition ---
        painter.setPen(QPen(self.base_eye_color.darker(120), 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(eye_path)


class EyesWindow(QMainWindow):
    """Window that displays the robot eyes"""
    emotion_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot Eyes")
        self.setGeometry(100, 100, 400, 300)  # Smaller, more compact window
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)  # Add a small margin
        
        # Create graphics scene for robot eyes
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor(50, 50, 65))  # Slightly lighter background
        
        # Create and add robot eyes
        self.robot_eyes = RobotEyesItem()
        self.scene.addItem(self.robot_eyes)
        
        # Create view for the eyes
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setFrameShape(QFrame.NoFrame)  # No border
        
        # Add view to layout
        layout.addWidget(self.view)
        
        # Set initial emotion
        self.robot_eyes.set_emotion("neutral")
        
    def resizeEvent(self, event):
        """Handle window resize to keep eyes properly sized and centered"""
        super().resizeEvent(event)
        # Update eye view to fit properly with more padding
        # This helps show more context and not zoom in too closely on the eyes
        self.scene.setSceneRect(self.robot_eyes.boundingRect().adjusted(-80, -80, 80, 80))
        
        # Use a smaller adjustment for the view - shows a bit more surrounding space
        self.view.fitInView(
            self.robot_eyes.boundingRect().adjusted(-50, -50, 50, 50),
            Qt.KeepAspectRatio
        )
        
        # Add a slight delay to ensure proper rendering after resize
        QTimer.singleShot(50, lambda: self.view.fitInView(
            self.robot_eyes.boundingRect().adjusted(-50, -50, 50, 50),
            Qt.KeepAspectRatio
        ))
        
    def set_emotion(self, emotion):
        """Set the robot eyes' emotion"""
        self.robot_eyes.set_emotion(emotion)
        self.emotion_changed.emit(emotion)  # Emit signal for other windows to sync


class TextWindow(QMainWindow):
    """Window for text input/output interaction"""
    command_submitted = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot Command Interface")
        self.setGeometry(100, 450, 700, 500)  # Position below the eyes window, wider for better text display
        
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


class UaiBotDualInterface:
    """Controller class that manages both windows and their interactions"""
    def __init__(self, ai_handler=None, shell_handler=None):
        self.eyes_window = EyesWindow()
        self.text_window = TextWindow()
        
        # Store handlers if provided
        self.ai_handler = ai_handler
        self.shell_handler = shell_handler
        
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
        self.text_window.move(self.eyes_window.x(), self.eyes_window.y() + self.eyes_window.height() + 30)
        
    def set_handlers(self, ai_handler=None, shell_handler=None):
        """Set or update the AI and shell handlers"""
        if ai_handler:
            self.ai_handler = ai_handler
        if shell_handler:
            self.shell_handler = shell_handler
            
    def handle_command(self, command):
        """Process user commands"""
        # Display user's command
        self.text_window.add_output_text(f"\nYou: {command}")
        
        # Set eyes to thinking state while "processing"
        self.eyes_window.set_emotion("thinking")
        
        # Special commands for emotions
        emotion_commands = {
            "happy": "I'm happy to help!",
            "sad": "I'm sorry to hear that.",
            "surprise": "Wow, that's amazing!",
            "confused": "I'm not sure I understand...",
            "neutral": "I'm here to assist you!"
        }
        
        # Check for direct emotion commands or special UaiBot commands
        if command.lower().startswith("emotion "):
            emotion = command.lower().split(" ", 1)[1].strip()
            if emotion in ["happy", "sad", "surprise", "confused", "neutral", "curious", "thinking"]:
                self.eyes_window.set_emotion(emotion)
                self.text_window.add_output_text(f"UaiBot: Emotion set to {emotion}!")
                return
            else:
                self.text_window.add_output_text(f"UaiBot: Unknown emotion '{emotion}'. Available emotions: happy, sad, surprise, confused, neutral, curious, thinking")
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
            import re
            
            # Search for markdown code blocks
            code_blocks = re.findall(r'```(?:bash|shell|\w*)\s*(.*?)```', output_text, re.DOTALL)
            
            # Search for specific terminal commands on separate lines (common for commands without code blocks)
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
                
        # Use AI handler for normal commands if available
        if self.ai_handler:
            try:
                # Query AI for response
                ai_response = self.ai_handler.query_ai(command)
                
                # Determine emotion based on response content
                emotion = "neutral"
                for emotion_key in emotion_commands.keys():
                    if emotion_key in command.lower() or emotion_key in ai_response.lower():
                        emotion = emotion_key
                        break
                
                # Check if response appears to be a command
                if ai_response.strip().startswith("!") or ai_response.strip().startswith("`"):
                    proposed_command = ai_response.strip()
                    # Remove command markers
                    if proposed_command.startswith("!"):
                        proposed_command = proposed_command[1:].strip()
                    elif proposed_command.startswith("`") and proposed_command.endswith("`"):
                        proposed_command = proposed_command[1:-1].strip()
                    
                    self.text_window.add_output_text(f"UaiBot: I suggest this command:\n{proposed_command}")
                    self.text_window.add_output_text("To execute, type '!' followed by the command.")
                else:
                    # Regular response
                    self.text_window.add_output_text(f"UaiBot: {ai_response}")
                
                # Set emotion based on response
                self.eyes_window.set_emotion(emotion)
                
            except Exception as e:
                self.text_window.add_output_text(f"Error: {str(e)}")
                self.eyes_window.set_emotion("sad")
        else:
            # No AI handler, use simple response
            for emotion, response in emotion_commands.items():
                if emotion in command.lower():
                    self.eyes_window.set_emotion(emotion)
                    self.text_window.add_output_text(f"UaiBot: {response}")
                    return
                    
            # Default response if no specific emotion mentioned
            self.eyes_window.set_emotion("neutral")
            self.text_window.add_output_text("UaiBot: I'm here to help with commands! (AI handler not available)")
            
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
