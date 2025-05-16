"""
Redesigned Avatar rendering for UaiBot GUI
Provides an animated robot emoji-based avatar with different emotional states
Implements the RobotEmojiRenderer using QPainter
"""
import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGraphicsScene, 
                            QGraphicsView, QGraphicsItem, QStyleOptionGraphicsItem,
                            QVBoxLayout, QHBoxLayout, QTextEdit, QFrame, QSplitter,
                            QPushButton, QLabel)
from PyQt5.QtGui import (QPainter, QBrush, QColor, QPen, QRadialGradient, QPixmap,
                        QFont, QPainterPath, QPolygonF)
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal, QSize


class RobotEmojiRenderer:
    """
    A class responsible for rendering different robot emoji states onto a QPixmap.
    """
    def __init__(self, size=128):
        self.size = size
        # Define base colors (can be customized)
        self.body_color = QColor("#B0BEC5")  # Light bluish-grey
        self.visor_color = QColor("#263238")  # Dark grey for visor
        self.neutral_eye_mouth_color = QColor("#81D4FA")  # Cyan
        self.happy_eye_mouth_color = QColor("#A5D6A7")    # Light Green
        self.thinking_eye_mouth_color = QColor("#FFD54F")  # Yellow/Orange
        self.sad_eye_mouth_color = QColor("#EF9A9A")  # Light Red/Pink
        self.surprised_eye_mouth_color = QColor("#CE93D8")  # Purple
        self.confused_eye_mouth_color = QColor("#FFF176")  # Yellow
        self.concerned_eye_mouth_color = QColor("#FFB74D")  # Orange

        # Animation parameters
        self.animation_counter = 0
        self.blink_state = False
        self.blink_counter = 0
        self.blink_threshold = 20  # Frames between blinks

    def update_animation(self):
        """Update animation parameters for blinking and movement effects"""
        self.animation_counter += 1
        self.blink_counter += 1

        # Handle blinking
        if self.blink_counter >= self.blink_threshold:
            self.blink_state = not self.blink_state
            if self.blink_state:  # Just started blinking
                self.blink_counter = self.blink_threshold - 5  # Hold closed briefly
            else:  # Just stopped blinking
                self.blink_counter = 0

        return self.blink_state  # Return current blink state for convenience

    def get_emoji_pixmap(self, state="neutral"):
        """Generate and return a pixmap with the robot emoji in the specified emotional state"""
        pixmap = QPixmap(self.size, self.size)
        pixmap.fill(Qt.transparent)  # Transparent background

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # For smooth shapes

        # Common drawing parameters
        padding = self.size * 0.05
        head_height = self.size * 0.6
        head_y_offset = self.size * 0.1
        
        body_height = self.size * 0.25
        body_y_offset = head_y_offset + head_height * 0.8  # Body slightly under head

        # Draw Body (simple rounded rectangle)
        body_rect = QRectF(
            padding * 2.5, body_y_offset,
            self.size - padding * 5, body_height
        )
        painter.setBrush(QBrush(self.body_color.darker(110)))
        painter.setPen(Qt.NoPen)  # No outline for body
        painter.drawRoundedRect(body_rect, 10.0, 10.0)

        # Draw Head
        head_rect = QRectF(
            padding, head_y_offset,
            self.size - padding * 2, head_height
        )
        painter.setBrush(QBrush(self.body_color))
        painter.setPen(QPen(self.body_color.darker(120), 1))  # Subtle outline
        painter.drawRoundedRect(head_rect, 15.0, 15.0)

        # Draw Visor
        visor_padding = padding * 1.5
        visor_rect = QRectF(
            head_rect.x() + visor_padding, 
            head_rect.y() + visor_padding * 0.8,
            head_rect.width() - visor_padding * 2, 
            head_rect.height() - visor_padding * 1.6
        )
        painter.setBrush(QBrush(self.visor_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(visor_rect, 10.0, 10.0)

        # Draw Features based on state
        if state == "neutral":
            self._draw_neutral_face(painter, visor_rect)
        elif state == "happy":
            self._draw_happy_face(painter, visor_rect)
        elif state == "thinking":
            self._draw_thinking_face(painter, visor_rect)
        elif state == "sad" or state == "concerned":
            self._draw_sad_face(painter, visor_rect)
        elif state == "confused":
            self._draw_confused_face(painter, visor_rect)
        elif state == "surprise":
            self._draw_surprised_face(painter, visor_rect)
        else:
            # Default to neutral if state not recognized
            self._draw_neutral_face(painter, visor_rect)

        # Add antenna/details based on size
        if self.size >= 64:
            self._draw_antenna(painter, head_rect)

        painter.end()
        return pixmap

    def _draw_neutral_face(self, painter, visor_bounds):
        """Draw a neutral expression with horizontal eyes and straight mouth"""
        pen = QPen(self.neutral_eye_mouth_color, self.size * 0.04)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Check if blinking
        if self.blink_state:
            self._draw_blinking_eyes(painter, visor_bounds, self.neutral_eye_mouth_color)
            return

        eye_width = self.size * 0.12
        eye_height = self.size * 0.08
        eye_y_offset = visor_bounds.y() + visor_bounds.height() * 0.35
        eye_spacing = self.size * 0.08  # Space from center

        # Left Eye (oval)
        left_eye_rect = QRectF(
            visor_bounds.center().x() - eye_spacing - eye_width, 
            eye_y_offset - eye_height / 2,
            eye_width, eye_height
        )
        painter.drawEllipse(left_eye_rect)

        # Right Eye (oval)
        right_eye_rect = QRectF(
            visor_bounds.center().x() + eye_spacing, 
            eye_y_offset - eye_height / 2,
            eye_width, eye_height
        )
        painter.drawEllipse(right_eye_rect)
        
        # Mouth (line)
        mouth_y_offset = visor_bounds.y() + visor_bounds.height() * 0.7
        mouth_width = self.size * 0.25
        painter.drawLine(
            int(visor_bounds.center().x() - mouth_width / 2), int(mouth_y_offset),
            int(visor_bounds.center().x() + mouth_width / 2), int(mouth_y_offset)
        )

    def _draw_happy_face(self, painter, visor_bounds):
        """Draw a happy face with curved eye lines and a smile"""
        pen = QPen(self.happy_eye_mouth_color, self.size * 0.045)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Check if blinking
        if self.blink_state:
            self._draw_blinking_eyes(painter, visor_bounds, self.happy_eye_mouth_color)
            return

        eye_y_offset = visor_bounds.y() + visor_bounds.height() * 0.40
        eye_width = self.size * 0.15
        eye_height = self.size * 0.12  # for arc control points

        # Eyes (upward crescents using QPainterPath for arcs)
        # Left Eye Path
        left_eye_path = QPainterPath()
        left_eye_path.moveTo(visor_bounds.center().x() - self.size * 0.20, eye_y_offset + eye_height * 0.2)
        left_eye_path.quadTo(
            visor_bounds.center().x() - self.size * 0.12, eye_y_offset - eye_height * 0.5,  # control point
            visor_bounds.center().x() - self.size * 0.04, eye_y_offset + eye_height * 0.2   # end point
        )
        painter.drawPath(left_eye_path)

        # Right Eye Path
        right_eye_path = QPainterPath()
        right_eye_path.moveTo(visor_bounds.center().x() + self.size * 0.04, eye_y_offset + eye_height * 0.2)
        right_eye_path.quadTo(
            visor_bounds.center().x() + self.size * 0.12, eye_y_offset - eye_height * 0.5,  # control point
            visor_bounds.center().x() + self.size * 0.20, eye_y_offset + eye_height * 0.2   # end point
        )
        painter.drawPath(right_eye_path)

        # Mouth (wide smile arc)
        mouth_rect = QRectF(
            visor_bounds.center().x() - self.size * 0.15, 
            visor_bounds.y() + visor_bounds.height() * 0.55,
            self.size * 0.3, self.size * 0.25
        )
        start_angle = 0 * 16  # QPainter angles are in 1/16th of a degree
        span_angle = 180 * 16
        painter.drawArc(mouth_rect, start_angle, span_angle)
        
    def _draw_thinking_face(self, painter, visor_bounds):
        """Draw a thinking expression with asymmetric eyes and wavy mouth"""
        pen = QPen(self.thinking_eye_mouth_color, self.size * 0.04)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Check if blinking
        if self.blink_state:
            self._draw_blinking_eyes(painter, visor_bounds, self.thinking_eye_mouth_color)
            return

        eye_radius = self.size * 0.04
        eye_y_offset = visor_bounds.y() + visor_bounds.height() * 0.35
        
        # Left Eye (dot)
        painter.setBrush(self.thinking_eye_mouth_color)
        painter.drawEllipse(
            visor_bounds.center().x() - self.size * 0.15 - eye_radius, 
            eye_y_offset - eye_radius,
            eye_radius * 2, eye_radius * 2
        )
        
        # Right Eye (slightly narrowed or line)
        painter.setBrush(Qt.NoBrush)  # Line for this eye part
        painter.drawLine(
            int(visor_bounds.center().x() + self.size * 0.08), int(eye_y_offset),
            int(visor_bounds.center().x() + self.size * 0.18), 
            int(eye_y_offset - self.size * 0.01)  # slightly squinted
        )

        # Mouth (flat or slightly wavy line)
        mouth_y_offset = visor_bounds.y() + visor_bounds.height() * 0.7
        mouth_width = self.size * 0.2
        path = QPainterPath()
        path.moveTo(visor_bounds.center().x() - mouth_width / 2, mouth_y_offset)
        path.quadTo(
            visor_bounds.center().x(), mouth_y_offset + self.size * 0.02,  # control for slight wave
            visor_bounds.center().x() + mouth_width / 2, mouth_y_offset
        )
        painter.drawPath(path)
        
        # Optional: Add thought bubble or question mark for thinking state
        self._draw_thinking_particles(painter, visor_bounds)
    
    def _draw_thinking_particles(self, painter, visor_bounds):
        """Draw particles or small bubbles above the head to represent thinking"""
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.thinking_eye_mouth_color.lighter(120)))
        
        # Base positions for thought bubbles - adjusted by animation counter for movement
        bubble_x_base = visor_bounds.right() - self.size * 0.1
        bubble_y_base = visor_bounds.top() - self.size * 0.1
        
        # Animation offsets
        offset_x = math.sin(self.animation_counter * 0.2) * (self.size * 0.02)
        offset_y = math.cos(self.animation_counter * 0.15) * (self.size * 0.02)
        
        # Draw 3-4 bubbles of increasing size
        sizes = [self.size * 0.03, self.size * 0.045, self.size * 0.06]
        for i, size in enumerate(sizes):
            offset_factor = (i + 1) * 0.5
            x = bubble_x_base + offset_x * offset_factor
            y = bubble_y_base - (i * self.size * 0.06) + offset_y * offset_factor
            painter.drawEllipse(QPointF(x, y), size, size)
    
    def _draw_confused_face(self, painter, visor_bounds):
        """Draw a confused expression with asymmetric eyes and wavy/uncertain mouth"""
        pen = QPen(self.confused_eye_mouth_color, self.size * 0.04)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        # Check if blinking
        if self.blink_state:
            self._draw_blinking_eyes(painter, visor_bounds, self.confused_eye_mouth_color)
            return
        
        eye_y_offset = visor_bounds.y() + visor_bounds.height() * 0.35
        
        # Left Eye (raised eyebrow effect)
        left_eye_path = QPainterPath()
        left_eye_path.moveTo(visor_bounds.center().x() - self.size * 0.18, eye_y_offset)
        left_eye_path.quadTo(
            visor_bounds.center().x() - self.size * 0.12, eye_y_offset - self.size * 0.04,
            visor_bounds.center().x() - self.size * 0.06, eye_y_offset
        )
        painter.drawPath(left_eye_path)
        
        # Right Eye (circular or dot)
        right_eye_radius = self.size * 0.05
        painter.setBrush(self.confused_eye_mouth_color)  # Fill for this eye
        painter.drawEllipse(
            visor_bounds.center().x() + self.size * 0.12 - right_eye_radius, 
            eye_y_offset - right_eye_radius,
            right_eye_radius * 2, right_eye_radius * 2
        )
        painter.setBrush(Qt.NoBrush)
        
        # Mouth (zigzag or wavy line)
        mouth_y_offset = visor_bounds.y() + visor_bounds.height() * 0.7
        mouth_width = self.size * 0.25
        zigzag_path = QPainterPath()
        zigzag_path.moveTo(visor_bounds.center().x() - mouth_width / 2, mouth_y_offset)
        
        # Create zigzag with multiple control points
        zigzag_path.quadTo(
            visor_bounds.center().x() - mouth_width / 4, mouth_y_offset - self.size * 0.02,
            visor_bounds.center().x(), mouth_y_offset
        )
        zigzag_path.quadTo(
            visor_bounds.center().x() + mouth_width / 4, mouth_y_offset + self.size * 0.02,
            visor_bounds.center().x() + mouth_width / 2, mouth_y_offset
        )
        
        painter.drawPath(zigzag_path)
        
        # Add question mark or confusion swirl if desired
        if self.size >= 80:  # Only for larger sizes
            self._draw_confusion_swirl(painter, visor_bounds)
    
    def _draw_confusion_swirl(self, painter, visor_bounds):
        """Draw a small question mark or confusion swirl above the head"""
        pen = QPen(self.confused_eye_mouth_color, self.size * 0.03)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Question mark position
        qm_x = visor_bounds.center().x() + self.size * 0.08
        qm_y = visor_bounds.top() - self.size * 0.08
        qm_size = self.size * 0.1
        
        # Draw a simple question mark (?)
        # Draw the curve part
        painter.drawArc(
            QRectF(qm_x - qm_size/2, qm_y - qm_size, qm_size, qm_size),
            0 * 16, 230 * 16
        )
        
        # Draw the dot
        painter.setBrush(self.confused_eye_mouth_color)
        painter.drawEllipse(
            QRectF(qm_x - qm_size/6, qm_y + qm_size/2, qm_size/3, qm_size/3)
        )
    
    def _draw_sad_face(self, painter, visor_bounds):
        """Draw a sad expression with drooping eyes and downturned mouth"""
        pen = QPen(self.sad_eye_mouth_color, self.size * 0.04)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        # Check if blinking
        if self.blink_state:
            self._draw_blinking_eyes(painter, visor_bounds, self.sad_eye_mouth_color)
            return
        
        eye_y_offset = visor_bounds.y() + visor_bounds.height() * 0.35
        eye_width = self.size * 0.12
        
        # Left Eye (drooping)
        left_eye_path = QPainterPath()
        left_eye_path.moveTo(visor_bounds.center().x() - self.size * 0.18, eye_y_offset)
        left_eye_path.quadTo(
            visor_bounds.center().x() - self.size * 0.12, eye_y_offset + self.size * 0.03,
            visor_bounds.center().x() - self.size * 0.06, eye_y_offset - self.size * 0.01
        )
        painter.drawPath(left_eye_path)
        
        # Right Eye (drooping)
        right_eye_path = QPainterPath()
        right_eye_path.moveTo(visor_bounds.center().x() + self.size * 0.06, eye_y_offset - self.size * 0.01)
        right_eye_path.quadTo(
            visor_bounds.center().x() + self.size * 0.12, eye_y_offset + self.size * 0.03,
            visor_bounds.center().x() + self.size * 0.18, eye_y_offset
        )
        painter.drawPath(right_eye_path)
        
        # Mouth (downturned)
        mouth_y_offset = visor_bounds.y() + visor_bounds.height() * 0.7
        mouth_width = self.size * 0.22
        
        sad_mouth = QPainterPath()
        sad_mouth.moveTo(visor_bounds.center().x() - mouth_width / 2, mouth_y_offset)
        sad_mouth.quadTo(
            visor_bounds.center().x(), mouth_y_offset + self.size * 0.08,  # control point lower for frown
            visor_bounds.center().x() + mouth_width / 2, mouth_y_offset
        )
        painter.drawPath(sad_mouth)
    
    def _draw_surprised_face(self, painter, visor_bounds):
        """Draw a surprised expression with wide eyes and open mouth"""
        pen = QPen(self.surprised_eye_mouth_color, self.size * 0.04)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Check if blinking
        if self.blink_state:
            self._draw_blinking_eyes(painter, visor_bounds, self.surprised_eye_mouth_color)
            return
        
        eye_y_offset = visor_bounds.y() + visor_bounds.height() * 0.35
        eye_spacing = self.size * 0.1
        
        # Wide circular eyes
        eye_radius = self.size * 0.06  # Larger for surprise
        painter.setBrush(self.surprised_eye_mouth_color.lighter(120))
        
        # Left Eye (circle)
        painter.drawEllipse(
            QRectF(
                visor_bounds.center().x() - eye_spacing - eye_radius,
                eye_y_offset - eye_radius,
                eye_radius * 2, eye_radius * 2
            )
        )
        
        # Right Eye (circle)
        painter.drawEllipse(
            QRectF(
                visor_bounds.center().x() + eye_spacing - eye_radius,
                eye_y_offset - eye_radius,
                eye_radius * 2, eye_radius * 2
            )
        )
        
        # Mouth (small 'o')
        mouth_y_offset = visor_bounds.y() + visor_bounds.height() * 0.7
        mouth_radius = self.size * 0.06
        painter.drawEllipse(
            QRectF(
                visor_bounds.center().x() - mouth_radius,
                mouth_y_offset - mouth_radius,
                mouth_radius * 2, mouth_radius * 2
            )
        )
    
    def _draw_blinking_eyes(self, painter, visor_bounds, color):
        """Draw blinking eyes (horizontal lines)"""
        eye_y_offset = visor_bounds.y() + visor_bounds.height() * 0.35
        eye_width = self.size * 0.12
        
        # Left Eye Blink
        painter.drawLine(
            int(visor_bounds.center().x() - eye_width - self.size * 0.05), int(eye_y_offset),
            int(visor_bounds.center().x() - self.size * 0.05), int(eye_y_offset)
        )
        
        # Right Eye Blink
        painter.drawLine(
            int(visor_bounds.center().x() + self.size * 0.05), int(eye_y_offset),
            int(visor_bounds.center().x() + eye_width + self.size * 0.05), int(eye_y_offset)
        )
    
    def _draw_antenna(self, painter, head_rect):
        """Draw an antenna on top of the robot head"""
        antenna_base_width = self.size * 0.1
        antenna_base_height = self.size * 0.08
        antenna_base_x = head_rect.center().x() - antenna_base_width / 2
        antenna_base_y = head_rect.top() - antenna_base_height * 0.5
        
        # Antenna base
        painter.setBrush(self.body_color.darker(110))
        painter.setPen(QPen(self.body_color.darker(130), 1))
        painter.drawRoundedRect(
            QRectF(antenna_base_x, antenna_base_y, antenna_base_width, antenna_base_height),
            3, 3
        )
        
        # Antenna rod
        rod_width = antenna_base_width * 0.2
        rod_height = self.size * 0.15
        rod_x = head_rect.center().x() - rod_width / 2
        rod_y = antenna_base_y - rod_height
        
        # Animation for slight antenna movement
        rod_angle = math.sin(self.animation_counter * 0.1) * 5  # -5 to 5 degree tilt
        
        painter.save()
        painter.translate(head_rect.center().x(), antenna_base_y)
        painter.rotate(rod_angle)
        painter.setBrush(self.body_color.darker(120))
        painter.drawRect(
            -rod_width/2, -rod_height, rod_width, rod_height
        )
        painter.restore()
        
        # Antenna tip light
        light_radius = rod_width * 0.8
        light_x = head_rect.center().x() + (math.sin(rod_angle * math.pi/180) * rod_height)
        light_y = antenna_base_y - rod_height + (math.cos(rod_angle * math.pi/180) * rod_height * -1)
        
        # Make the light blink
        light_color = QColor(255, 100, 100)  # Red by default
        if self.animation_counter % 20 < 10:
            light_color = QColor(255, 160, 160)  # Lighter when blinking
        
        painter.setBrush(light_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            QPointF(light_x, light_y),
            light_radius, light_radius
        )
        
        # Add glow effect
        glow = QRadialGradient(QPointF(light_x, light_y), light_radius * 2)
        glow_color = QColor(light_color)
        glow_color.setAlpha(50)
        glow.setColorAt(0, glow_color)
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(
            QPointF(light_x, light_y),
            light_radius * 2, light_radius * 2
        )

# QGraphicsItem that displays the robot emoji
class RobotEmojiItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_emotion = "neutral"
        self.renderer = RobotEmojiRenderer(size=200)  # Default size
        self.pixmap = self.renderer.get_emoji_pixmap(self.current_emotion)
        
        # Set up animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # 50ms = 20fps
    
    def update_animation(self):
        """Update animation state and request repaint"""
        self.renderer.update_animation()
        self.pixmap = self.renderer.get_emoji_pixmap(self.current_emotion)
        self.update()
    
    def set_emotion(self, emotion):
        """Change the emotional expression"""
        self.current_emotion = emotion.lower()
        self.pixmap = self.renderer.get_emoji_pixmap(self.current_emotion)
        self.update()
    
    def boundingRect(self):
        """Return the bounding rectangle of the emoji"""
        return QRectF(-100, -100, 200, 200)  # Fixed size for simplicity
    
    def paint(self, painter, option, widget=None):
        """Paint the emoji pixmap centered in the item's coordinates"""
        painter.drawPixmap(
            int(-self.pixmap.width() / 2),
            int(-self.pixmap.height() / 2),
            self.pixmap
        )


class AvatarInterface(QMainWindow):
    """Main interface window that contains both the emoji avatar display and text interaction area"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for eyes and text
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)

        # Create eye view container
        self.eye_view_container = QWidget()
        eye_layout = QVBoxLayout(self.eye_view_container)
        
        # Eye graphics scene setup
        self.eye_scene = QGraphicsScene()
        self.eye_scene.setBackgroundBrush(QColor(40, 40, 50))  # Dark background
        
        # Create and add the robot emoji avatar
        self.robot_emoji = RobotEmojiItem()
        self.eye_scene.addItem(self.robot_emoji)
        
        # Create and configure the view
        self.eye_view = QGraphicsView(self.eye_scene)
        self.eye_view.setRenderHint(QPainter.Antialiasing)
        self.eye_view.setMinimumHeight(250)
        self.eye_view.setFrameShape(QFrame.NoFrame)  # No border
        
        # Add eye view to layout
        eye_layout.addWidget(self.eye_view)
        
        # Create text interaction area container
        self.text_container = QWidget()
        text_layout = QVBoxLayout(self.text_container)
        
        # Create output text area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumHeight(200)  # Enough for 10 lines
        self.output_area.setStyleSheet("QTextEdit { background-color: #2a2a2a; color: #e0e0e0; }")
        self.output_area.setFont(QFont("Courier New", 11))
        
        # Create input text area
        self.input_area = QTextEdit()
        self.input_area.setMaximumHeight(80)
        self.input_area.setPlaceholderText("Type your message here...")
        self.input_area.setStyleSheet("QTextEdit { background-color: #2a2a2a; color: #e0e0e0; }")
        self.input_area.setFont(QFont("Courier New", 11))
        
        # Add text widgets to layout
        text_layout.addWidget(self.output_area)
        text_layout.addWidget(self.input_area)
        
        # Add containers to splitter
        splitter.addWidget(self.eye_view_container)
        splitter.addWidget(self.text_container)
        
        # Set initial splitter sizes (40% eyes, 60% text)
        splitter.setSizes([250, 350])
        
        # Set initial emotion
        self.robot_emoji.set_emotion("neutral")
        
    def resizeEvent(self, event):
        """Ensure eyes are centered in the view when window is resized"""
        super().resizeEvent(event)
        # Fit the view to the robot emoji with some padding
        self.eye_scene.setSceneRect(self.robot_emoji.boundingRect().adjusted(-50, -50, 50, 50))
        self.eye_view.fitInView(self.robot_emoji.boundingRect().adjusted(-20, -20, 20, 20), 
                               Qt.KeepAspectRatio)
    
    def set_emotion(self, emotion):
        """Set the current emotion of the robot emoji"""
        self.robot_emoji.set_emotion(emotion)
    
    def add_output_text(self, text):
        """Add text to the output area"""
        self.output_area.append(text)
        # Auto-scroll to the bottom
        scrollbar = self.output_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


# Demonstration code
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AvatarInterface()
    window.show()
    
    # Test with some sample text
    window.add_output_text("Welcome to UaiBot!")
    window.add_output_text("I'm here to assist you with your questions.")
    window.add_output_text("Type commands or questions for help.")
    window.set_emotion("happy")
    
    sys.exit(app.exec_())


class AvatarInterface(QMainWindow):
    """Main interface window that contains both the eyes display and the text interaction area"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for eyes and text
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)

        # Create eye view container
        self.eye_view_container = QWidget()
        eye_layout = QVBoxLayout(self.eye_view_container)
        
        # Eye graphics scene setup
        self.eye_scene = QGraphicsScene()
        self.eye_scene.setBackgroundBrush(QColor(40, 40, 50))  # Dark background
        
        # Create and add the robot eyes
        self.robot_eyes = RobotEyesItem()
        self.eye_scene.addItem(self.robot_eyes)
        
        # Create and configure the view
        self.eye_view = QGraphicsView(self.eye_scene)
        self.eye_view.setRenderHint(QPainter.Antialiasing)
        self.eye_view.setMinimumHeight(250)
        self.eye_view.setFrameShape(QFrame.NoFrame)  # No border
        
        # Add eye view to layout
        eye_layout.addWidget(self.eye_view)
        
        # Create text interaction area container
        self.text_container = QWidget()
        text_layout = QVBoxLayout(self.text_container)
        
        # Create output text area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setMinimumHeight(200)  # Enough for 10 lines
        self.output_area.setStyleSheet("QTextEdit { background-color: #2a2a2a; color: #e0e0e0; }")
        self.output_area.setFont(QFont("Courier New", 11))
        
        # Create input text area
        self.input_area = QTextEdit()
        self.input_area.setMaximumHeight(80)
        self.input_area.setPlaceholderText("Type your message here...")
        self.input_area.setStyleSheet("QTextEdit { background-color: #2a2a2a; color: #e0e0e0; }")
        self.input_area.setFont(QFont("Courier New", 11))
        
        # Add text widgets to layout
        text_layout.addWidget(self.output_area)
        text_layout.addWidget(self.input_area)
        
        # Add containers to splitter
        splitter.addWidget(self.eye_view_container)
        splitter.addWidget(self.text_container)
        
        # Set initial splitter sizes (40% eyes, 60% text)
        splitter.setSizes([250, 350])
        
        # Set initial emotion
        self.robot_eyes.set_emotion("neutral")
        
    def resizeEvent(self, event):
        """Ensure eyes are centered in the view when window is resized"""
        super().resizeEvent(event)
        # Fit the view to the robot eyes with some padding
        self.eye_scene.setSceneRect(self.robot_eyes.boundingRect().adjusted(-50, -50, 50, 50))
        self.eye_view.fitInView(self.robot_eyes.boundingRect().adjusted(-20, -20, 20, 20), 
                               Qt.AspectRatioMode.KeepAspectRatio)
    
    def set_emotion(self, emotion):
        """Set the current emotion of the robot eyes"""
        self.robot_eyes.set_emotion(emotion)
    
    def add_output_text(self, text):
        """Add text to the output area"""
        self.output_area.append(text)
        # Auto-scroll to the bottom
        scrollbar = self.output_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AvatarInterface()
    window.show()
    
    # Test with some sample text
    window.add_output_text("Welcome to UaiBot!")
    window.add_output_text("I'm here to assist you with your Ubuntu system.")
    window.add_output_text("You can ask me questions or request help with commands.")
    window.set_emotion("happy")
    
    sys.exit(app.exec_())
