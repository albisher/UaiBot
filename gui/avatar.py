"""
Enhanced Avatar rendering for UaiBot GUI
Provides an animated 2D cartoonish robot avatar with different emotional states
"""
import os
import sys
import math
import random
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QPointF, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QPolygon, QRadialGradient, QLinearGradient, QTransform

class AvatarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)
        # Use cross-version compatible size policy
        try:
            # For newer PyQt versions
            self.setSizePolicy(QWidget.Policy.Expanding, QWidget.Policy.Minimum)
        except AttributeError:
            # For older PyQt versions
            import PyQt5.QtWidgets as QtWidgets
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        # Animation parameters
        self.hover_offset = 0
        self.hover_direction = 1
        self.rotation_angle = 0
        self.antenna_wave = 0
        self.antenna_direction = 1
        self.eye_movement = 0
        self.particle_positions = []
        
        self.current_emotion = "neutral"
        self.emotions = {
            "neutral": {
                "eye_size": 25,
                "mouth_curve": 0,
                "color": QColor(255, 128, 64),  # Orange
                "eye_color": QColor(102, 217, 232),  # Cyan
                "blink": False,
                "animation_speed": 1.0,
            },
            "happy": {
                "eye_size": 25,
                "mouth_curve": 100,
                "color": QColor(255, 140, 30),  # Brighter orange
                "eye_color": QColor(102, 217, 232),  # Cyan
                "blink": False,
                "animation_speed": 1.5,
            },
            "sad": {
                "eye_size": 25,
                "mouth_curve": -80,
                "color": QColor(200, 120, 60),  # Darker orange
                "eye_color": QColor(80, 180, 210),  # Dimmer cyan
                "blink": False,
                "animation_speed": 0.5,
            },
            "thinking": {
                "eye_size": 30,
                "mouth_curve": -20,
                "color": QColor(255, 128, 64),  # Orange
                "eye_color": QColor(102, 217, 232),  # Cyan
                "blink": True,
                "animation_speed": 0.8,
            },
            "confused": {
                "eye_size": 35,
                "mouth_curve": 0,
                "color": QColor(255, 150, 80),  # Light orange
                "eye_color": QColor(102, 217, 232),  # Cyan
                "blink": False,
                "animation_speed": 1.2,
            },
            "concerned": {
                "eye_size": 30,
                "mouth_curve": -40,
                "color": QColor(230, 110, 50),  # Red-orange
                "eye_color": QColor(102, 217, 232),  # Cyan
                "blink": True,
                "animation_speed": 1.3,
            },
        }
        
        # Setup animation
        self.blink_state = False
        self.blink_counter = 0
        self.animation_counter = 0
        
        # Initialize random positions for particle effects
        for _ in range(5):
            self.particle_positions.append({
                'x': random.randint(-30, 30),
                'y': random.randint(-60, -20),
                'size': random.randint(3, 8),
                'speed': random.random() * 2 + 1
            })
        
        # Animation timer - faster for smoother animation
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 50ms for smoother animation updates
        
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
        
    def update_animation(self):
        """Update animation parameters"""
        # Update hovering effect
        self.hover_offset += 0.2 * self.hover_direction
        if abs(self.hover_offset) > 5:
            self.hover_direction *= -1
            
        # Update rotation
        self.rotation_angle = (self.rotation_angle + 1) % 360
        
        # Update antenna wave
        self.antenna_wave += 0.1 * self.antenna_direction
        if abs(self.antenna_wave) > 1:
            self.antenna_direction *= -1
            
        # Update eye movement
        self.eye_movement = math.sin(self.animation_counter * 0.05) * 3
        
        # Update particle positions
        for particle in self.particle_positions:
            particle['y'] += particle['speed']
            if particle['y'] > 30:  # Reset when it goes too far
                particle['y'] = random.randint(-60, -20)
                particle['x'] = random.randint(-30, 30)
                particle['size'] = random.randint(3, 8)
        
        # Update animation counter
        self.animation_counter += 1
        
        # Update blinking based on emotion
        emotion = self.emotions[self.current_emotion]
        if emotion["blink"]:
            self.blink_counter += 1
            # Adjust blink frequency based on emotion
            blink_threshold = int(20 / emotion["animation_speed"])
            if self.blink_counter >= blink_threshold:
                self.blink_state = not self.blink_state
                self.blink_counter = 0
        else:
            self.blink_state = False
        
        # Trigger a repaint
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
        center_y = height // 2 + int(self.hover_offset)
        head_size = min(width, height) - 80
        head_radius = head_size // 2
        
        # Save the painter state
        painter.save()
        
        # Draw robot body
        self.draw_robot_body(painter, center_x, center_y, head_radius, emotion)
        
        # Draw head with gradient
        self.draw_robot_head(painter, center_x, center_y, head_radius, emotion)
        
        # Eye positions
        eye_distance = head_radius // 2
        left_eye_x = center_x - eye_distance + int(self.eye_movement)
        right_eye_x = center_x + eye_distance + int(self.eye_movement)
        eye_y = center_y - head_radius // 3
        eye_size = emotion["eye_size"]
        
        # Draw eyes with glow effect
        self.draw_robot_eyes(painter, left_eye_x, right_eye_x, eye_y, eye_size, emotion)
        
        # Draw mouth display
        self.draw_robot_mouth(painter, center_x, center_y, head_radius, emotion)
        
        # Draw particle effects for certain emotions
        if self.current_emotion in ["thinking", "confused"]:
            self.draw_particles(painter, center_x, center_y - head_radius)
            
        # Draw antennas
        self.draw_robot_antennas(painter, center_x, center_y, head_radius)
        
        # Restore painter state
        painter.restore()
    
    def draw_robot_body(self, painter, center_x, center_y, head_radius, emotion):
        """Draw the robot's body"""
        # Draw neck
        neck_width = head_radius // 2
        neck_height = head_radius // 3
        
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.drawRoundedRect(center_x - neck_width//2, 
                               center_y + head_radius,
                               neck_width, neck_height, 8, 8)
        
        # Draw body (just the top part visible)
        body_width = head_radius * 2
        body_height = head_radius // 2
        
        # Create a gradient for the body
        body_gradient = QLinearGradient(0, center_y + head_radius + neck_height, 
                                       0, center_y + head_radius + neck_height + body_height)
        body_gradient.setColorAt(0, emotion["color"].darker(120))
        body_gradient.setColorAt(1, emotion["color"].darker(150))
        
        painter.setBrush(body_gradient)
        painter.drawRoundedRect(center_x - body_width//2, 
                               center_y + head_radius + neck_height,
                               body_width, body_height, 10, 10)
        
        # Draw shoulders/arms (circular joints)
        arm_size = head_radius // 3
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        
        # Left shoulder with slight animation
        shoulder_offset = int(math.sin(self.animation_counter * 0.03) * 2)
        painter.drawEllipse(center_x - body_width//2 - arm_size//2, 
                           center_y + head_radius + neck_height + shoulder_offset, 
                           arm_size, arm_size)
        
        # Right shoulder with different phase animation
        shoulder_offset = int(math.sin((self.animation_counter + 10) * 0.03) * 2)
        painter.drawEllipse(center_x + body_width//2 - arm_size//2, 
                           center_y + head_radius + neck_height + shoulder_offset, 
                           arm_size, arm_size)
    
    def draw_robot_head(self, painter, center_x, center_y, head_radius, emotion):
        """Draw the robot's head with gradient and features"""
        # Create a radial gradient for the head
        head_gradient = QRadialGradient(center_x, center_y, head_radius)
        head_gradient.setColorAt(0, emotion["color"])
        head_gradient.setColorAt(0.8, emotion["color"].darker(110))
        head_gradient.setColorAt(1, emotion["color"].darker(130))
        
        # Draw head with gradient
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(head_gradient))
        
        # Draw slightly rounded rectangle for robot head
        head_rect = QRect(center_x - head_radius, center_y - head_radius, 
                         head_radius * 2, head_radius * 2)
        painter.drawRoundedRect(head_rect, head_radius // 3, head_radius // 3)
        
        # Draw top panel/control section
        panel_height = head_radius // 4
        panel_gradient = QLinearGradient(0, center_y - head_radius, 0, center_y - head_radius + panel_height)
        panel_gradient.setColorAt(0, QColor(60, 60, 60))
        panel_gradient.setColorAt(1, QColor(40, 40, 40))
        
        painter.setBrush(QBrush(panel_gradient))
        painter.drawRoundedRect(center_x - head_radius, center_y - head_radius, 
                               head_radius * 2, panel_height,
                               8, 8)
        
        # Draw small control lights/buttons
        light_colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(255, 255, 0)]
        light_size = panel_height // 2
        light_spacing = head_radius * 2 // 6
        
        for i, color in enumerate(light_colors):
            x_pos = center_x - head_radius + light_spacing * (i+1)
            y_pos = center_y - head_radius + panel_height // 2
            
            # Add blinking effect to the lights
            if (self.animation_counter + i * 5) % 30 < 5:
                light_color = color.lighter(130)
            else:
                light_color = color
            
            painter.setBrush(QBrush(light_color))
            painter.drawEllipse(x_pos - light_size//2, y_pos - light_size//2, 
                               light_size, light_size)
    
    def draw_robot_eyes(self, painter, left_eye_x, right_eye_x, eye_y, eye_size, emotion):
        """Draw the robot's eyes with glow effects"""
        # Create eye backgrounds (rectangular display panels)
        eye_panel_width = eye_size * 1.5
        eye_panel_height = eye_size * 1.2
        
        # Draw eye panels
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QColor(20, 20, 20))
        
        painter.drawRoundedRect(left_eye_x - eye_panel_width//2, eye_y - eye_panel_height//2,
                               eye_panel_width, eye_panel_height, 4, 4)
        painter.drawRoundedRect(right_eye_x - eye_panel_width//2, eye_y - eye_panel_height//2,
                               eye_panel_width, eye_panel_height, 4, 4)
        
        # Draw glowing eyes
        if self.blink_state:
            # Blinking eyes (horizontal lines)
            painter.setPen(QPen(emotion["eye_color"], 3))
            painter.drawLine(left_eye_x - eye_size//2, eye_y, 
                             left_eye_x + eye_size//2, eye_y)
            painter.drawLine(right_eye_x - eye_size//2, eye_y, 
                             right_eye_x + eye_size//2, eye_y)
        else:
            # Normal eyes (with glowing effect)
            for i in range(3):
                # Draw multiple circles with decreasing opacity for glow effect
                glow_color = QColor(emotion["eye_color"])
                glow_color.setAlpha(100 - i * 30)
                
                glow_size = eye_size - i * 4
                if glow_size > 0:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(glow_color))
                    painter.drawEllipse(left_eye_x - glow_size//2, eye_y - glow_size//2, 
                                      glow_size, glow_size)
                    painter.drawEllipse(right_eye_x - glow_size//2, eye_y - glow_size//2, 
                                      glow_size, glow_size)
            
            # Draw the main eye circles
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(emotion["eye_color"]))
            painter.drawEllipse(left_eye_x - eye_size//2, eye_y - eye_size//2, 
                               eye_size, eye_size)
            painter.drawEllipse(right_eye_x - eye_size//2, eye_y - eye_size//2, 
                               eye_size, eye_size)
            
            # Add highlights to eyes
            painter.setBrush(QColor(255, 255, 255, 180))
            highlight_size = eye_size // 3
            painter.drawEllipse(left_eye_x - eye_size//3, eye_y - eye_size//3, 
                               highlight_size, highlight_size)
            painter.drawEllipse(right_eye_x - eye_size//3, eye_y - eye_size//3, 
                               highlight_size, highlight_size)
    
    def draw_robot_mouth(self, painter, center_x, center_y, head_radius, emotion):
        """Draw the robot's mouth/display screen"""
        mouth_width = head_radius
        mouth_height = head_radius // 3
        mouth_y = center_y + head_radius // 3
        
        # Draw mouth background (screen)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QColor(20, 20, 20))
        painter.drawRoundedRect(center_x - mouth_width//2, mouth_y - mouth_height//2,
                               mouth_width, mouth_height, 5, 5)
        
        # Draw mouth expression
        mouth_inner_width = mouth_width - 10
        mouth_inner_height = abs(emotion["mouth_curve"]) // 2
        
        painter.setPen(QPen(emotion["eye_color"], 3))
        painter.setBrush(Qt.NoBrush)
        
        # Draw different mouth shapes based on emotion
        if emotion["mouth_curve"] > 0:
            # Happy/smiling mouth (curve up)
            painter.drawArc(center_x - mouth_inner_width//2, mouth_y - mouth_inner_height, 
                           mouth_inner_width, mouth_inner_height * 2,
                           0 * 16, 180 * 16)
        elif emotion["mouth_curve"] < 0:
            # Sad mouth (curve down)
            painter.drawArc(center_x - mouth_inner_width//2, mouth_y, 
                           mouth_inner_width, mouth_inner_height * 2,
                           180 * 16, 180 * 16)
        else:
            # Neutral mouth (straight line)
            painter.drawLine(center_x - mouth_inner_width//2, mouth_y,
                            center_x + mouth_inner_width//2, mouth_y)
    
    def draw_robot_antennas(self, painter, center_x, center_y, head_radius):
        """Draw antennas on top of the robot's head"""
        antenna_base_width = head_radius // 4
        antenna_base_height = head_radius // 6
        antenna_rod_height = head_radius // 2
        
        # Draw left antenna
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QColor(80, 80, 80))
        
        # Base
        left_antenna_x = center_x - head_radius // 3
        antenna_base_y = center_y - head_radius
        
        painter.drawRoundedRect(left_antenna_x - antenna_base_width//2,
                               antenna_base_y - antenna_base_height,
                               antenna_base_width, antenna_base_height,
                               4, 4)
        
        # Rod
        painter.setPen(QPen(Qt.black, 3))
        wave_offset = int(math.sin(self.animation_counter * 0.1) * 3)
        painter.drawLine(left_antenna_x, antenna_base_y - antenna_base_height,
                        left_antenna_x + wave_offset, antenna_base_y - antenna_base_height - antenna_rod_height)
        
        # Top light
        light_size = antenna_base_width // 2
        light_color = QColor(255, 0, 0)  # Red
        
        # Make the light blink
        if self.animation_counter % 20 < 10:
            light_color = light_color.lighter(130)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(light_color))
        painter.drawEllipse(left_antenna_x + wave_offset - light_size//2,
                           antenna_base_y - antenna_base_height - antenna_rod_height - light_size//2,
                           light_size, light_size)
        
        # Draw right antenna (slightly different)
        right_antenna_x = center_x + head_radius // 3
        
        # Base
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QColor(80, 80, 80))
        painter.drawRoundedRect(right_antenna_x - antenna_base_width//2,
                               antenna_base_y - antenna_base_height,
                               antenna_base_width, antenna_base_height,
                               4, 4)
        
        # Rod
        painter.setPen(QPen(Qt.black, 3))
        wave_offset = int(math.sin((self.animation_counter + 5) * 0.1) * 3)  # Different phase
        painter.drawLine(right_antenna_x, antenna_base_y - antenna_base_height,
                        right_antenna_x + wave_offset, antenna_base_y - antenna_base_height - antenna_rod_height)
        
        # Top light
        light_color = QColor(0, 255, 0)  # Green
        
        # Make the light blink in opposite phase
        if self.animation_counter % 20 >= 10:
            light_color = light_color.lighter(130)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(light_color))
        painter.drawEllipse(right_antenna_x + wave_offset - light_size//2,
                           antenna_base_y - antenna_base_height - antenna_rod_height - light_size//2,
                           light_size, light_size)
    
    def draw_particles(self, painter, center_x, center_y):
        """Draw animated particles (for thinking/processing state)"""
        painter.setPen(Qt.NoPen)
        
        for particle in self.particle_positions:
            x = center_x + particle['x']
            y = center_y + particle['y']
            size = particle['size']
            
            # Draw particle with gradient
            particle_gradient = QRadialGradient(x, y, size)
            particle_gradient.setColorAt(0, QColor(255, 255, 255, 200))
            particle_gradient.setColorAt(1, QColor(200, 200, 255, 50))
            
            painter.setBrush(QBrush(particle_gradient))
            painter.drawEllipse(x - size//2, y - size//2, size, size)
    
    def sizeHint(self):
        """Suggest a good size for the widget"""
        return QSize(350, 350)