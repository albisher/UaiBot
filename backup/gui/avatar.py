"""
Enhanced Avatar rendering for UaiBot GUI
Provides an animated 2D cartoonish robot avatar with different emotional states
"""
import os
import sys
import math
import random
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QPointF, QPropertyAnimation, QEasingCurve, QTimer, QRectF
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
        # self.rotation_angle = 0 # Not needed in modern design
        # self.antenna_wave = 0 # Not needed in modern design
        # self.antenna_direction = 1 # Not needed in modern design
        self.eye_movement = 0 # Kept for subtle animation
        self.particle_positions = [] # For thinking/confused states
        
        self.current_emotion = "neutral"
        self.emotions = {
            "neutral": {
                "eye_size": 22,
                "mouth_curve": 20,
                "color": QColor(255, 140, 0),
                "darker_color": QColor(220, 110, 0),
                "eye_color": QColor(0, 224, 208),
                "blink": False,
                "animation_speed": 1.0,
            },
            "happy": {
                "eye_size": 22,
                "mouth_curve": 30,
                "color": QColor(255, 150, 20),
                "darker_color": QColor(220, 120, 10),
                "eye_color": QColor(0, 224, 208),
                "blink": False,
                "animation_speed": 1.5,
            },
            "sad": {
                "eye_size": 20,
                "mouth_curve": -25,
                "color": QColor(230, 120, 0),
                "darker_color": QColor(200, 100, 0),
                "eye_color": QColor(0, 200, 180),
                "blink": True,
                "animation_speed": 0.5,
            },
            "thinking": {
                "eye_size": 25,
                "mouth_curve": -10,
                "color": QColor(255, 140, 0),
                "darker_color": QColor(220, 110, 0),
                "eye_color": QColor(0, 224, 208),
                "blink": True,
                "animation_speed": 0.8,
            },
            "confused": {
                "eye_size": 28,
                "mouth_curve": 0,
                "color": QColor(255, 150, 80),
                "darker_color": QColor(220, 120, 60),
                "eye_color": QColor(0, 224, 208),
                "blink": True,
                "animation_speed": 1.2,
            },
            "concerned": {
                "eye_size": 20,
                "mouth_curve": -15,
                "color": QColor(240, 130, 20),
                "darker_color": QColor(210, 100, 0),
                "eye_color": QColor(0, 210, 190),
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
        if abs(self.hover_offset) > 3:  # Reduced hover range for subtlety
            self.hover_direction *= -1
        
        # Update eye movement - more subtle
        self.eye_movement = math.sin(self.animation_counter * 0.05) * 1.5
        
        # Update particle positions only for thinking/confused emotions
        if self.current_emotion in ["thinking", "confused"]:
            for particle in self.particle_positions:
                particle['y'] += particle['speed']
                if particle['y'] > 30:  # Reset when it goes too far
                    particle['y'] = random.randint(-60, -20)
                    particle['x'] = random.randint(-30, 30)
                    particle['size'] = random.randint(3, 8)
        
        # Update animation counter
        self.animation_counter += 1
        
        # Update blinking based on emotion
        emotion_params = self.emotions[self.current_emotion]
        if emotion_params["blink"]:
            self.blink_counter += 1
            # Adjust blink frequency based on emotion
            blink_threshold = int(30 / emotion_params["animation_speed"])
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
        
        # Adjusted scaling to make the robot fit well and proportions match image
        base_size = min(width, height) * 0.8 
        head_radius = base_size // 3  # Head will be a bit wider than tall
        
        # Center calculation to allow more space for body
        center_x = width // 2
        center_y = height // 2 + int(self.hover_offset) - head_radius * 0.3  # Shift up a bit
        
        # Save the painter state
        painter.save()
        
        # Draw robot body first (so head overlaps neck correctly)
        self.draw_robot_body(painter, center_x, center_y, head_radius, emotion)
        
        # Draw head (includes ear pods now)
        self.draw_robot_head(painter, center_x, center_y, head_radius, emotion)
        
        # Eye positions on the faceplate
        eye_distance = head_radius * 0.45
        left_eye_x = center_x - eye_distance + int(self.eye_movement)
        right_eye_x = center_x + eye_distance + int(self.eye_movement)
        eye_y = center_y - head_radius * 0.1  # Position eyes lower on the head
        eye_size = emotion["eye_size"]
        
        # Draw eyes
        self.draw_robot_eyes(painter, left_eye_x, right_eye_x, eye_y, eye_size, emotion)
        
        # Draw mouth
        self.draw_robot_mouth(painter, center_x, center_y, head_radius, emotion)
        
        # Draw particle effects for certain emotions
        if self.current_emotion in ["thinking", "confused"]:
            self.draw_particles(painter, center_x, center_y - head_radius * 1.5)  # Particles above head
            
        # Draw antennas
        self.draw_robot_antennas(painter, center_x, center_y, head_radius)
        
        # Restore painter state
        painter.restore()
    
    def draw_robot_body(self, painter, center_x, center_y, head_radius, emotion):
        """Draw the robot's body with modern design"""
        body_top_y = center_y + head_radius * 0.8  # Neck connection point
        neck_width = head_radius * 0.6
        neck_height = head_radius * 0.3
        neck_color = QColor(70, 70, 80)  # Darker grey for neck
        
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(neck_color))
        painter.drawRect(center_x - neck_width//2, 
                         body_top_y,
                         neck_width, neck_height)
        
        body_y_offset = body_top_y + neck_height
        body_width = head_radius * 2.8  # Wider body
        body_height = head_radius * 1.3  # Taller body
        body_corner_radius = 20

        body_gradient = QLinearGradient(center_x, body_y_offset, center_x, body_y_offset + body_height)
        body_gradient.setColorAt(0, emotion["color"])
        body_gradient.setColorAt(1, emotion["color"].darker(120))
        
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(body_gradient)
        painter.drawRoundedRect(center_x - body_width//2, 
                               body_y_offset,
                               body_width, body_height, body_corner_radius, body_corner_radius)

        # Chest detail
        chest_detail_width = body_width * 0.6
        chest_detail_height = body_height * 0.4
        chest_detail_x = center_x - chest_detail_width / 2
        chest_detail_y = body_y_offset + body_height * 0.2
        
        painter.setBrush(emotion["darker_color"])  # Darker orange for chest
        painter.drawRoundedRect(chest_detail_x, chest_detail_y,
                                chest_detail_width, chest_detail_height, 15, 15)

        # Pauldrons (Shoulders)
        pauldron_radius = head_radius * 0.65
        pauldron_y = body_y_offset + pauldron_radius * 0.3
        
        # Connecting arm bit (dark grey)
        arm_connector_width = pauldron_radius * 0.5
        arm_connector_height = pauldron_radius * 0.6

        painter.setBrush(QColor(80, 80, 90))  # Dark grey for arm connectors
        # Left arm connector
        painter.drawRoundedRect(center_x - body_width//2 + arm_connector_width*0.1, 
                                pauldron_y - arm_connector_height*0.2,
                                arm_connector_width, arm_connector_height, 5, 5)
        # Right arm connector
        painter.drawRoundedRect(center_x + body_width//2 - arm_connector_width*1.1, 
                                pauldron_y - arm_connector_height*0.2,
                                arm_connector_width, arm_connector_height, 5, 5)

        # Pauldrons
        pauldron_gradient = QRadialGradient(QPointF(0,0), pauldron_radius)
        pauldron_gradient.setColorAt(0, emotion["color"].lighter(110))
        pauldron_gradient.setColorAt(1, emotion["color"].darker(110))
        
        painter.setBrush(QBrush(pauldron_gradient))
        # Left Pauldron
        painter.save()
        painter.translate(center_x - body_width//2 - pauldron_radius*0.3, pauldron_y)
        painter.drawEllipse(QRectF(-pauldron_radius, -pauldron_radius, pauldron_radius*2, pauldron_radius*2))
        painter.restore()
        
        # Right Pauldron
        painter.save()
        painter.translate(center_x + body_width//2 + pauldron_radius*0.3, pauldron_y)
        painter.drawEllipse(QRectF(-pauldron_radius, -pauldron_radius, pauldron_radius*2, pauldron_radius*2))
        painter.restore()
    
    def draw_robot_head(self, painter, center_x, center_y, head_radius, emotion):
        """Draw the robot's head with modern design"""
        # Head shape: A rounded rectangle, wider than tall
        head_width = head_radius * 2.2
        head_height = head_radius * 1.8  # Slightly less tall than wide
        head_corner_radius = head_radius * 0.7  # More rounded corners

        head_rect = QRect(int(center_x - head_width / 2), 
                          int(center_y - head_height / 2), 
                          int(head_width), int(head_height))
        
        head_gradient = QRadialGradient(QPointF(center_x, center_y - head_height * 0.1), head_width * 0.7)
        head_gradient.setColorAt(0, emotion["color"].lighter(110))
        head_gradient.setColorAt(0.7, emotion["color"])
        head_gradient.setColorAt(1, emotion["color"].darker(130))
        
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(head_gradient))
        painter.drawRoundedRect(head_rect, head_corner_radius, head_corner_radius)

        # Add ear pods
        self.draw_ear_pods(painter, center_x, center_y, head_width, head_height, head_radius, emotion)
        
        # Add face plate
        self.draw_face_plate(painter, center_x, center_y, head_radius)
    
    def draw_robot_eyes(self, painter, left_eye_x, right_eye_x, eye_y, eye_size, emotion):
        """Draw the robot's eyes with simplified modern style"""
        eye_color = emotion["eye_color"]
        
        # Simplified eye drawing
        painter.setPen(Qt.NoPen)  # No outline for the eyes for a cleaner look
        
        if self.blink_state:
            # Blinking eyes (horizontal lines)
            painter.setPen(QPen(eye_color, 3))  # Thickness for the blink line
            painter.drawLine(int(left_eye_x - eye_size//1.5), int(eye_y), 
                             int(left_eye_x + eye_size//1.5), int(eye_y))
            painter.drawLine(int(right_eye_x - eye_size//1.5), int(eye_y), 
                             int(right_eye_x + eye_size//1.5), int(eye_y))
        else:
            # Normal eyes (simple circles)
            painter.setBrush(QBrush(eye_color))
            painter.drawEllipse(QPointF(left_eye_x, eye_y), eye_size/2, eye_size/2)
            painter.drawEllipse(QPointF(right_eye_x, eye_y), eye_size/2, eye_size/2)
            
            # Optional: Simple highlight if desired
            highlight_color = QColor(255, 255, 255, 150)
            painter.setBrush(highlight_color)
            highlight_size = eye_size * 0.3
            painter.drawEllipse(QPointF(left_eye_x - eye_size * 0.15, eye_y - eye_size * 0.15), 
                               highlight_size/2, highlight_size/2)
            painter.drawEllipse(QPointF(right_eye_x - eye_size * 0.15, eye_y - eye_size * 0.15), 
                               highlight_size/2, highlight_size/2)
    
    def draw_robot_mouth(self, painter, center_x, center_y, head_radius, emotion):
        """Draw the robot's mouth with modern curved path"""
        mouth_width_factor = 0.8  # Relative to faceplate width potential
        mouth_width = head_radius * 1.7 * mouth_width_factor 
        mouth_y_offset = head_radius * 0.5  # Position below eyes on faceplate
        mouth_y = (center_y - head_radius * 0.05) + mouth_y_offset  # Relative to face_plate center_y
        
        mouth_curve_val = emotion["mouth_curve"]
        
        painter.setPen(QPen(emotion["eye_color"], 3))  # Mouth color same as eyes, thickness 3
        painter.setBrush(Qt.NoBrush)
        
        path = QPainterPath()
        start_x = center_x - mouth_width / 2
        end_x = center_x + mouth_width / 2
        
        if mouth_curve_val == 0:  # Neutral straight line
            path.moveTo(start_x, mouth_y)
            path.lineTo(end_x, mouth_y)
        else:  # Curved mouth
            path.moveTo(start_x, mouth_y)
            # Control point y calculation for curve
            # A positive mouth_curve_val makes control point lower (smile)
            # A negative mouth_curve_val makes control point higher (frown)
            ctrl_y = mouth_y + mouth_curve_val * (mouth_width / 100.0)  # Adjust multiplier for curve intensity
            path.quadTo(center_x, ctrl_y, end_x, mouth_y)
            
        painter.drawPath(path)
    
    def draw_robot_antennas(self, painter, center_x, center_y, head_radius):
        """Draw antennas on top of the robot's head"""
        # Updated antenna design to match new robot aesthetic
        
        head_width = head_radius * 2.2
        head_height = head_radius * 1.8
        
        # Antenna proportions (uses fractional values for better scaling)
        antenna_base_width = head_radius * 0.25
        antenna_base_height = head_radius * 0.16
        antenna_rod_height = head_radius * 0.5
        antenna_top_y = center_y - head_height/2 - antenna_base_height
        
        # Left antenna position
        left_antenna_x = center_x - head_width * 0.25
        antenna_base_y = center_y - head_height/2
        
        # Base - rounded rectangle in dark grey
        painter.setPen(QPen(QColor(20, 20, 20), 1.5))
        painter.setBrush(QColor(70, 70, 80))  # Darker grey to match ear pods
        
        painter.drawRoundedRect(
            int(left_antenna_x - antenna_base_width/2),
            int(antenna_base_y - antenna_base_height),
            int(antenna_base_width), 
            int(antenna_base_height),
            5, 5
        )
        
        # Rod with smooth animation
        wave_offset = int(math.sin(self.animation_counter * 0.08) * 3)
        rod_color = QColor(60, 60, 65)
        
        painter.setPen(QPen(QColor(20, 20, 20), 2))
        painter.setBrush(rod_color)
        
        # Draw rod as thin rounded rectangle instead of line
        rod_width = antenna_base_width * 0.3
        
        # Calculate rod angle based on wave offset
        painter.save()
        painter.translate(left_antenna_x, antenna_base_y - antenna_base_height)
        painter.rotate(-wave_offset * 2)  # Slight rotation for animation
        painter.drawRoundedRect(
            int(-rod_width/2),
            int(-antenna_rod_height), 
            int(rod_width), 
            int(antenna_rod_height),
            3, 3
        )
        painter.restore()
        
        # Top light with gradients for glow effect
        light_size = antenna_base_width * 0.7
        light_color = QColor(255, 0, 0)  # Red
        light_pos_x = left_antenna_x + wave_offset * 1.5
        light_pos_y = antenna_top_y - antenna_rod_height - light_size/2
        
        # Make the light blink and add glowing effect
        if self.animation_counter % 20 < 10:
            light_color = light_color.lighter(130)
        
        # Draw light with gradient
        light_gradient = QRadialGradient(
            QPointF(light_pos_x, light_pos_y), 
            light_size
        )
        light_gradient.setColorAt(0, light_color)
        light_gradient.setColorAt(0.7, light_color.darker(110))
        light_gradient.setColorAt(1, QColor(150, 0, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(light_gradient))
        painter.drawEllipse(
            QPointF(light_pos_x, light_pos_y), 
            light_size/2, light_size/2
        )
        
        # Draw glow effect
        glow_color = QColor(light_color)
        glow_color.setAlpha(50)
        painter.setBrush(glow_color)
        painter.drawEllipse(
            QPointF(light_pos_x, light_pos_y), 
            light_size/1.5, light_size/1.5
        )
        
        # Right antenna (slightly different phase)
        right_antenna_x = center_x + head_width * 0.25
        
        # Base
        painter.setPen(QPen(QColor(20, 20, 20), 1.5))
        painter.setBrush(QColor(70, 70, 80))
        painter.drawRoundedRect(
            int(right_antenna_x - antenna_base_width/2),
            int(antenna_base_y - antenna_base_height),
            int(antenna_base_width), 
            int(antenna_base_height),
            5, 5
        )
        
        # Rod with smooth animation (different phase)
        wave_offset = int(math.sin((self.animation_counter + 5) * 0.08) * 3)  # Different phase
        rod_color = QColor(60, 60, 65)
        
        painter.setPen(QPen(QColor(20, 20, 20), 2))
        painter.setBrush(rod_color)
        
        # Calculate rod angle based on wave offset
        painter.save()
        painter.translate(right_antenna_x, antenna_base_y - antenna_base_height)
        painter.rotate(-wave_offset * 2)  # Slight rotation for animation
        painter.drawRoundedRect(
            int(-rod_width/2),
            int(-antenna_rod_height), 
            int(rod_width), 
            int(antenna_rod_height),
            3, 3
        )
        painter.restore()
        
        # Top light with gradients for glow effect
        light_color = QColor(0, 255, 0)  # Green
        light_pos_x = right_antenna_x + wave_offset * 1.5
        light_pos_y = antenna_top_y - antenna_rod_height - light_size/2
        
        # Make the light blink in opposite phase
        if self.animation_counter % 20 >= 10:
            light_color = light_color.lighter(130)
        
        # Draw light with gradient
        light_gradient = QRadialGradient(
            QPointF(light_pos_x, light_pos_y), 
            light_size
        )
        light_gradient.setColorAt(0, light_color)
        light_gradient.setColorAt(0.7, light_color.darker(110))
        light_gradient.setColorAt(1, QColor(0, 150, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(light_gradient))
        painter.drawEllipse(
            QPointF(light_pos_x, light_pos_y), 
            light_size/2, light_size/2
        )
        
        # Draw glow effect
        glow_color = QColor(light_color)
        glow_color.setAlpha(50)
        painter.setBrush(glow_color)
        painter.drawEllipse(
            QPointF(light_pos_x, light_pos_y), 
            light_size/1.5, light_size/1.5
        )
    
    def draw_particles(self, painter, center_x, center_y):
        """Draw animated particles for thinking/confused state"""
        painter.setPen(Qt.NoPen)
        for particle in self.particle_positions:
            x = center_x + particle['x']
            y = center_y + particle['y']
            size = particle['size']
            
            # Create gradient for better particle appearance
            particle_gradient = QRadialGradient(x, y, size)
            particle_gradient.setColorAt(0, QColor(200, 200, 255, 180))  # Adjusted particle color
            particle_gradient.setColorAt(1, QColor(150, 150, 220, 30))
            
            painter.setBrush(QBrush(particle_gradient))
            painter.drawEllipse(int(x - size//2), int(y - size//2), int(size), int(size))
    
    def sizeHint(self):
        """Suggest a good size for the widget"""
        return QSize(300, 350)  # Adjusted for the new design proportions
    
    def draw_ear_pods(self, painter, center_x, center_y, head_w, head_h, head_r, emotion):
        """Draw the ear pods on the sides of the head"""
        pod_radius = head_r * 0.55
        pod_offset_x = head_w / 2 - pod_radius * 0.3  # How much they stick out
        pod_y = center_y  # Vertically centered with head
        
        inner_pod_color = QColor(70, 70, 80)  # Dark grey
        outer_ring_thickness = head_r * 0.12

        for side in [-1, 1]:  # -1 for left, 1 for right
            pod_x = center_x + side * pod_offset_x
            
            # Outer ring (orange)
            painter.setPen(QPen(Qt.black, 1.5))
            painter.setBrush(QBrush(emotion["color"]))
            painter.drawEllipse(QPointF(pod_x, pod_y), pod_radius, pod_radius)
            
            # Inner part (dark grey)
            painter.setPen(Qt.NoPen)  # No Pen for inner for cleaner look
            painter.setBrush(QBrush(inner_pod_color))
            painter.drawEllipse(QPointF(pod_x, pod_y), 
                                pod_radius - outer_ring_thickness, 
                                pod_radius - outer_ring_thickness)
    
    def draw_face_plate(self, painter, center_x, center_y, head_radius):
        """Draw the face plate on the front of the head"""
        plate_width = head_radius * 1.7
        plate_height = head_radius * 0.9
        plate_y = center_y - head_radius * 0.05  # Slightly above head's vertical center
        plate_corner_radius = 15
        
        face_plate_color = QColor(40, 40, 45)  # Dark grey/black

        painter.setPen(QPen(QColor(20,20,20), 1))  # Subtle border
        painter.setBrush(face_plate_color)
        painter.drawRoundedRect(int(center_x - plate_width / 2), 
                                int(plate_y - plate_height / 2),
                                int(plate_width), int(plate_height), 
                                plate_corner_radius, plate_corner_radius)