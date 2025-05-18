"""
Enhanced Emoji Avatar for UaiBot GUI
Uses simple emoji-style expressions that change based on the bot's state
Implements a clean 2D design with expressive features

Copyright (c) 2025 UaiBot Team
License: Custom license - free for personal and educational use.
Commercial use requires a paid license. See LICENSE file for details.
"""
import math
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QPainterPath, QPolygonF, QLinearGradient
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal, QSize

class EmojiAvatar(QGraphicsItem):
    """A simplified emoji-style avatar for UaiBot"""
    
    # Emotions that can be expressed
    EMOTIONS = {
        "neutral": {"color": "#81D4FA", "mouth": "neutral", "eyes": "normal"},
        "happy": {"color": "#A5D6A7", "mouth": "smile", "eyes": "happy"},
        "thinking": {"color": "#FFD54F", "mouth": "neutral", "eyes": "thinking"},
        "sad": {"color": "#EF9A9A", "mouth": "sad", "eyes": "sad"},
        "confused": {"color": "#FFF176", "mouth": "confused", "eyes": "confused"},
        "surprised": {"color": "#CE93D8", "mouth": "circle", "eyes": "wide"},
        "worried": {"color": "#FFB74D", "mouth": "worried", "eyes": "worried"},
    }
    
    def __init__(self):
        super().__init__()
        
        # Basic properties
        self.size = 300
        self.current_emotion = "neutral"
        
        # Animation properties
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.update_blink)
        self.blink_timer.start(4000)  # Blink every 4 seconds
        self.is_blinking = False
        self.blink_counter = 0
        
        # Bouncing animation
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self.update_bounce)
        self.bounce_timer.start(50)  # Update every 50ms
        self.bounce_offset = 0
        self.bounce_direction = 1
        self.bounce_speed = 0.2
        self.bounce_range = 5
        
        # Color definitions
        self.bg_color = QColor("#FAFAFA")  # Light background
        self.emoji_color = QColor("#FFEB3B")  # Emoji yellow
        self.accent_color = QColor("#81D4FA")  # Default accent (will change with emotion)
    
    def set_emotion(self, emotion):
        """Set the current emotion"""
        if emotion in self.EMOTIONS:
            self.current_emotion = emotion
            self.accent_color = QColor(self.EMOTIONS[emotion]["color"])
            self.update()
            # Add a little bounce when emotion changes
            self.bounce_direction = 1
            self.bounce_speed = 0.8  # Faster bounce on emotion change
    
    def update_blink(self):
        """Toggle blinking state"""
        self.is_blinking = True
        self.update()
        # Reset after a short duration
        QTimer.singleShot(150, self.end_blink)
    
    def end_blink(self):
        """End the blink"""
        self.is_blinking = False
        self.update()
    
    def update_bounce(self):
        """Update the bouncing animation"""
        self.bounce_offset += self.bounce_direction * self.bounce_speed
        if abs(self.bounce_offset) > self.bounce_range:
            self.bounce_direction *= -1
            
        # Gradually slow down bounce
        self.bounce_speed = max(0.1, self.bounce_speed * 0.99)
        
        self.update()
    
    def boundingRect(self):
        """Define the bounding rectangle for the avatar"""
        return QRectF(0, 0, self.size, self.size)
    
    def paint(self, painter, option, widget):
        """Paint the emoji avatar"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get current emotion settings
        emotion = self.EMOTIONS[self.current_emotion]
        
        # Center coordinates
        center_x = self.size // 2
        center_y = self.size // 2 + self.bounce_offset
        radius = min(self.size, self.size) * 0.4
        
        # Draw emoji face (circle)
        painter.setBrush(QBrush(self.emoji_color))
        painter.setPen(QPen(QColor("#E0E0E0"), 2))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # Eye spacing and size
        eye_spacing = radius * 0.5
        eye_size = radius * 0.25
        eye_y = center_y - radius * 0.2
        
        # Draw eyes based on emotion
        left_eye_x = center_x - eye_spacing
        right_eye_x = center_x + eye_spacing
        
        if self.is_blinking:
            # Draw closed eyes (just lines)
            painter.setPen(QPen(QColor("#333333"), 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(left_eye_x - eye_size, eye_y, left_eye_x + eye_size, eye_y)
            painter.drawLine(right_eye_x - eye_size, eye_y, right_eye_x + eye_size, eye_y)
        else:
            # Draw eyes based on emotion
            self._draw_eyes(painter, emotion["eyes"], left_eye_x, right_eye_x, eye_y, eye_size)
        
        # Draw mouth based on emotion
        mouth_y = center_y + radius * 0.3
        mouth_width = radius * 1.0
        self._draw_mouth(painter, emotion["mouth"], center_x, mouth_y, mouth_width)
        
        # Draw any additional features based on emotion
        if self.current_emotion == "thinking":
            # Draw thought bubble
            bubble_x = center_x + radius * 0.8
            bubble_y = center_y - radius * 0.8
            bubble_size = radius * 0.2
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#333333"), 1))
            painter.drawEllipse(QPointF(bubble_x, bubble_y), bubble_size, bubble_size)
            
            # Small bubbles leading to thought
            for i in range(1, 4):
                small_x = center_x + radius * (0.6 - i * 0.1)
                small_y = center_y - radius * (0.6 - i * 0.1)
                small_size = bubble_size * (0.3 - i * 0.05)
                painter.drawEllipse(QPointF(small_x, small_y), small_size, small_size)
        
        elif self.current_emotion == "confused":
            # Draw question mark
            question_x = center_x + radius * 0.7
            question_y = center_y - radius * 0.7
            painter.setPen(QPen(QColor("#333333"), 3, Qt.SolidLine, Qt.RoundCap))
            
            # Draw curved part of question mark
            path = QPainterPath()
            path.moveTo(question_x - 5, question_y - 15)
            path.cubicTo(
                question_x - 5, question_y - 5,
                question_x + 15, question_y - 5,
                question_x + 5, question_y + 5
            )
            path.cubicTo(
                question_x, question_y + 10,
                question_x, question_y + 15,
                question_x, question_y + 15
            )
            painter.drawPath(path)
            
            # Draw dot of question mark
            painter.setBrush(QBrush(QColor("#333333")))
            painter.drawEllipse(QPointF(question_x, question_y + 22), 2, 2)

    def _draw_eyes(self, painter, eye_type, left_x, right_x, y, size):
        """Draw eyes based on emotion type"""
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#333333"), 2))
        
        if eye_type == "normal":
            # Standard circular eyes
            painter.drawEllipse(QPointF(left_x, y), size, size)
            painter.drawEllipse(QPointF(right_x, y), size, size)
            
            # Draw pupils
            painter.setBrush(QBrush(QColor("#333333")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(left_x, y), size * 0.4, size * 0.4)
            painter.drawEllipse(QPointF(right_x, y), size * 0.4, size * 0.4)
            
        elif eye_type == "happy":
            # Happy curved eyes (upside-down U)
            painter.setPen(QPen(QColor("#333333"), 3, Qt.SolidLine, Qt.RoundCap))
            
            # Left eye arc
            path = QPainterPath()
            path.moveTo(left_x - size, y)
            path.cubicTo(
                left_x - size, y - size,
                left_x + size, y - size,
                left_x + size, y
            )
            painter.drawPath(path)
            
            # Right eye arc
            path = QPainterPath()
            path.moveTo(right_x - size, y)
            path.cubicTo(
                right_x - size, y - size,
                right_x + size, y - size,
                right_x + size, y
            )
            painter.drawPath(path)
            
        elif eye_type == "sad":
            # Sad downward eyes
            painter.setPen(QPen(QColor("#333333"), 3, Qt.SolidLine, Qt.RoundCap))
            
            # Left eye arc
            path = QPainterPath()
            path.moveTo(left_x - size, y)
            path.cubicTo(
                left_x - size, y + size,
                left_x + size, y + size,
                left_x + size, y
            )
            painter.drawPath(path)
            
            # Right eye arc
            path = QPainterPath()
            path.moveTo(right_x - size, y)
            path.cubicTo(
                right_x - size, y + size,
                right_x + size, y + size,
                right_x + size, y
            )
            painter.drawPath(path)
            
        elif eye_type == "thinking":
            # Circular eyes with pupils looking up-right
            painter.drawEllipse(QPointF(left_x, y), size, size)
            painter.drawEllipse(QPointF(right_x, y), size, size)
            
            # Draw pupils looking up
            painter.setBrush(QBrush(QColor("#333333")))
            painter.setPen(Qt.NoPen)
            pupil_offset_x = size * 0.3
            pupil_offset_y = -size * 0.3
            painter.drawEllipse(QPointF(left_x + pupil_offset_x, y + pupil_offset_y), size * 0.4, size * 0.4)
            painter.drawEllipse(QPointF(right_x + pupil_offset_x, y + pupil_offset_y), size * 0.4, size * 0.4)
            
        elif eye_type == "confused":
            # One normal eye, one raised eyebrow
            # Normal right eye
            painter.drawEllipse(QPointF(right_x, y), size, size)
            painter.setBrush(QBrush(QColor("#333333")))
            painter.drawEllipse(QPointF(right_x, y), size * 0.4, size * 0.4)
            
            # Left eye with raised eyebrow
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#333333"), 2))
            painter.drawEllipse(QPointF(left_x, y + size * 0.2), size, size)
            
            # Raised eyebrow
            painter.setPen(QPen(QColor("#333333"), 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(left_x - size, y - size * 0.8, left_x + size, y - size * 0.3)
            
            # Left pupil
            painter.setBrush(QBrush(QColor("#333333")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(left_x, y + size * 0.2), size * 0.4, size * 0.4)
            
        elif eye_type == "wide":
            # Wide surprised eyes
            painter.drawEllipse(QPointF(left_x, y), size * 1.3, size * 1.3)
            painter.drawEllipse(QPointF(right_x, y), size * 1.3, size * 1.3)
            
            # Draw pupils
            painter.setBrush(QBrush(QColor("#333333")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(left_x, y), size * 0.6, size * 0.6)
            painter.drawEllipse(QPointF(right_x, y), size * 0.6, size * 0.6)
            
        elif eye_type == "worried":
            # Worried eyes (similar to confused but both eyebrows up)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.setPen(QPen(QColor("#333333"), 2))
            painter.drawEllipse(QPointF(left_x, y + size * 0.2), size, size)
            painter.drawEllipse(QPointF(right_x, y + size * 0.2), size, size)
            
            # Raised eyebrows
            painter.setPen(QPen(QColor("#333333"), 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(left_x - size, y - size * 0.5, left_x + size, y - size * 0.8)
            painter.drawLine(right_x - size, y - size * 0.8, right_x + size, y - size * 0.5)
            
            # Pupils
            painter.setBrush(QBrush(QColor("#333333")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(left_x, y + size * 0.2), size * 0.4, size * 0.4)
            painter.drawEllipse(QPointF(right_x, y + size * 0.2), size * 0.4, size * 0.4)

    def _draw_mouth(self, painter, mouth_type, center_x, y, width):
        """Draw mouth based on emotion type"""
        painter.setPen(QPen(QColor("#333333"), 3, Qt.SolidLine, Qt.RoundCap))
        
        if mouth_type == "neutral":
            # Straight line
            painter.drawLine(center_x - width / 2, y, center_x + width / 2, y)
            
        elif mouth_type == "smile":
            # Happy smile (U shape)
            path = QPainterPath()
            path.moveTo(center_x - width / 2, y - width * 0.1)
            path.cubicTo(
                center_x - width / 2, y + width * 0.3,
                center_x + width / 2, y + width * 0.3,
                center_x + width / 2, y - width * 0.1
            )
            painter.drawPath(path)
            
        elif mouth_type == "sad":
            # Sad frown (upside-down U)
            path = QPainterPath()
            path.moveTo(center_x - width / 2, y + width * 0.1)
            path.cubicTo(
                center_x - width / 2, y - width * 0.3,
                center_x + width / 2, y - width * 0.3,
                center_x + width / 2, y + width * 0.1
            )
            painter.drawPath(path)
            
        elif mouth_type == "circle":
            # O shaped mouth (surprise)
            painter.setBrush(QBrush(QColor("#333333").lighter(150)))
            painter.drawEllipse(QPointF(center_x, y), width * 0.3, width * 0.3)
            
        elif mouth_type == "confused":
            # Wavy confused mouth
            path = QPainterPath()
            path.moveTo(center_x - width / 2, y)
            path.cubicTo(
                center_x - width / 4, y - width * 0.1,
                center_x, y + width * 0.1,
                center_x + width / 4, y - width * 0.1
            )
            path.cubicTo(
                center_x + width / 3, y,
                center_x + width / 2.5, y + width * 0.05,
                center_x + width / 2, y
            )
            painter.drawPath(path)
            
        elif mouth_type == "worried":
            # Slight frown with tighter curve
            path = QPainterPath()
            path.moveTo(center_x - width / 2, y)
            path.cubicTo(
                center_x - width / 3, y - width * 0.1,
                center_x + width / 3, y - width * 0.1,
                center_x + width / 2, y
            )
            painter.drawPath(path)
