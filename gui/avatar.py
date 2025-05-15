"""
Avatar rendering for UaiBot GUI
Provides a simple 2D cartoonish avatar with different emotional states
"""
import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QPolygon

class AvatarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        # Use cross-version compatible size policy
        try:
            # For newer PyQt versions
            self.setSizePolicy(QWidget.Policy.Expanding, QWidget.Policy.Minimum)
        except AttributeError:
            # For older PyQt versions
            import PyQt5.QtWidgets as QtWidgets
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        self.current_emotion = "neutral"
        self.emotions = {
            "neutral": {
                "eye_size": 25,
                "mouth_curve": 0,
                "color": QColor(120, 180, 255),
                "eye_color": QColor(30, 30, 30),
                "blink": False,
            },
            "happy": {
                "eye_size": 25,
                "mouth_curve": 100,
                "color": QColor(120, 220, 120),
                "eye_color": QColor(30, 30, 30),
                "blink": False,
            },
            "sad": {
                "eye_size": 25,
                "mouth_curve": -80,
                "color": QColor(150, 150, 230),
                "eye_color": QColor(30, 30, 30),
                "blink": False,
            },
            "thinking": {
                "eye_size": 30,
                "mouth_curve": -20,
                "color": QColor(220, 180, 80),
                "eye_color": QColor(30, 30, 30),
                "blink": True,
            },
            "confused": {
                "eye_size": 35,
                "mouth_curve": 0,
                "color": QColor(230, 180, 100),
                "eye_color": QColor(30, 30, 30),
                "blink": False,
            },
            "concerned": {
                "eye_size": 30,
                "mouth_curve": -40,
                "color": QColor(230, 150, 150),
                "eye_color": QColor(30, 30, 30),
                "blink": True,
            },
        }
        
        # Setup animation
        self.blink_state = False
        self.blink_counter = 0
        
        # Animation timer
        self.startTimer(200)  # 200ms for animation updates
        
        # Setup layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Add label for emotion text
        self.emotion_label = QLabel(self.current_emotion.capitalize())
        self.emotion_label.setAlignment(Qt.AlignCenter)
        self.emotion_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.emotion_label)
        
    def set_emotion(self, emotion):
        """Set the avatar's current emotion"""
        if emotion in self.emotions:
            self.current_emotion = emotion
            self.emotion_label.setText(emotion.capitalize())
            self.update()
        
    def paintEvent(self, event):
        """Draw the avatar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get current emotion parameters
        emotion = self.emotions[self.current_emotion]
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        face_size = min(width, height) - 40
        face_radius = face_size // 2
        
        # Draw face background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(emotion["color"]))
        painter.drawEllipse(center_x - face_radius, center_y - face_radius, face_size, face_size)
        
        # Eye positions
        eye_distance = face_radius // 2
        left_eye_x = center_x - eye_distance
        right_eye_x = center_x + eye_distance
        eye_y = center_y - face_radius // 3
        eye_size = emotion["eye_size"]
        
        # Draw eyes
        painter.setBrush(QBrush(emotion["eye_color"]))
        
        # Handle blinking
        if emotion["blink"]:
            self.blink_counter += 1
            if self.blink_counter >= 10:
                self.blink_state = not self.blink_state
                self.blink_counter = 0
        else:
            self.blink_state = False
            
        if self.blink_state:
            # Blinking eyes (horizontal lines)
            painter.setPen(QPen(emotion["eye_color"], 3))
            painter.drawLine(left_eye_x - eye_size//2, eye_y, 
                             left_eye_x + eye_size//2, eye_y)
            painter.drawLine(right_eye_x - eye_size//2, eye_y, 
                             right_eye_x + eye_size//2, eye_y)
        else:
            # Normal eyes (ellipses)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(left_eye_x - eye_size//2, eye_y - eye_size//2, 
                               eye_size, eye_size)
            painter.drawEllipse(right_eye_x - eye_size//2, eye_y - eye_size//2, 
                               eye_size, eye_size)
        
        # Draw mouth
        mouth_width = face_radius
        mouth_height = abs(emotion["mouth_curve"]) // 2
        mouth_y = center_y + face_radius // 3
        
        painter.setPen(QPen(Qt.black, 3))
        painter.setBrush(Qt.NoBrush)
        
        # Draw different mouth shapes based on emotion
        if emotion["mouth_curve"] > 0:
            # Happy/smiling mouth (curve up)
            painter.drawArc(center_x - mouth_width//2, mouth_y - mouth_height, 
                           mouth_width, mouth_height * 2,
                           0 * 16, 180 * 16)
        elif emotion["mouth_curve"] < 0:
            # Sad mouth (curve down)
            painter.drawArc(center_x - mouth_width//2, mouth_y, 
                           mouth_width, mouth_height * 2,
                           180 * 16, 180 * 16)
        else:
            # Neutral mouth (straight line)
            painter.drawLine(center_x - mouth_width//2, mouth_y,
                            center_x + mouth_width//2, mouth_y)
    
    def timerEvent(self, event):
        """Handle animation timing"""
        self.update()  # Trigger repaint for animations
    
    def sizeHint(self):
        """Suggest a good size for the widget"""
        return QSize(300, 250)