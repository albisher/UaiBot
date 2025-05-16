import sys
import math # For heart shape
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
                             QGraphicsItem, QStyleOptionGraphicsItem, QWidget,
                             QPushButton, QVBoxLayout, QHBoxLayout, QFrame)
from PyQt5.QtGui import (QPainter, QBrush, QColor, QPen, QRadialGradient,
                         QFont, QPainterPath, QPolygonF)
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer

class RobotEmoEyesItem(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_emotion = "neutral"
        self.eye_spacing = 160
        self.eye_base_width = 120
        self.eye_base_height = 70 # For almond shape

        # Emo Color Palette
        self.base_color = QColor(60, 70, 90) # Dark blue-gray
        self.iris_color = QColor(40, 50, 70) # Deeper iris
        self.pupil_color = QColor(10, 10, 20) # Almost black
        self.glow_color = QColor(100, 90, 140, 70) # Soft, dim purple glow
        self.line_color = QColor(90, 100, 130) # For outlines, cracks
        self.tear_glow_color = QColor(120, 150, 200, 100) # For light tears

        self.flicker_alpha = 255 # For flickering effect
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(150) # Animation tick

        self.flicker_on = False

    def _animate(self):
        if self.current_emotion == "melancholy":
            self.flicker_on = not self.flicker_on
            self.update()
        else:
            if self.flicker_on: # Ensure flicker is off if not melancholy
                self.flicker_on = False
                self.update()


    def set_emotion(self, emotion):
        self.current_emotion = emotion.lower()
        # Reset animation states if needed
        if self.current_emotion != "melancholy":
            self.flicker_on = False
        self.update()

    def boundingRect(self):
        return QRectF(-self.eye_spacing * 1.2, -self.eye_base_height * 1.5,
                      self.eye_spacing * 2.4 + self.eye_base_width, self.eye_base_height * 3)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left_eye_center = QPointF(-self.eye_spacing / 2, 0)
        right_eye_center = QPointF(self.eye_spacing / 2, 0)

        self._draw_single_emo_eye(painter, left_eye_center, is_left=True)
        self._draw_single_emo_eye(painter, right_eye_center, is_left=False)

    def _get_almond_eye_path(self, rect, top_lid_factor, bottom_lid_factor, center_y_offset=0):
        path = QPainterPath()
        center_x = rect.center().x()
        center_y = rect.center().y() + center_y_offset

        path.moveTo(rect.left(), center_y)
        path.quadTo(center_x, center_y - rect.height() * top_lid_factor, rect.right(), center_y)
        path.quadTo(center_x, center_y + rect.height() * bottom_lid_factor, rect.left(), center_y)
        path.closeSubpath()
        return path

    def _get_teardrop_pupil_path(self, center, radius):
        path = QPainterPath()
        path.moveTo(center.x(), center.y() - radius) # Top point
        path.quadTo(center.x() + radius * 0.8, center.y() + radius * 0.2, center.x(), center.y() + radius * 1.2) # Right curve to bottom
        path.quadTo(center.x() - radius * 0.8, center.y() + radius * 0.2, center.x(), center.y() - radius) # Left curve to top
        path.closeSubpath()
        return path

    def _get_cracked_heart_pupil_path(self, center, size):
        path = QPainterPath()
        s = size / 2.0
        # Basic heart shape
        path.moveTo(center.x(), center.y() + s * 0.5) # Bottom point
        path.cubicTo(center.x(), center.y() - s * 0.2, center.x() - s * 1.2, center.y() - s * 0.8, center.x() - s * 0.6, center.y() - s * 1.2)
        path.cubicTo(center.x(), center.y() - s * 1.6, center.x() + s * 0.6, center.y() - s * 1.2, center.x() + s * 0.6, center.y() - s * 1.2)
        path.cubicTo(center.x() + s * 1.2, center.y() - s * 0.8, center.x(), center.y() - s * 0.2, center.x(), center.y() + s * 0.5)
        path.closeSubpath()

        # Add a crack line
        crack_path = QPainterPath()
        crack_path.moveTo(center.x() - s*0.1, center.y() - s * 1.0)
        crack_path.lineTo(center.x() + s*0.05, center.y() - s*0.2)
        crack_path.lineTo(center.x() - s*0.2, center.y() + s*0.1)
        return path, crack_path


    def _draw_single_emo_eye(self, painter: QPainter, center: QPointF, is_left: bool):
        # Emotion-driven parameters
        top_lid_factor = 0.6  # Controls how much the top lid curves/droops
        bottom_lid_factor = 0.5 # Controls bottom lid
        pupil_type = "dot" # dot, teardrop, cracked_heart
        pupil_size = self.eye_base_height * 0.15
        glow_opacity = 70
        show_tear = False
        num_cracks = 0
        eye_y_offset = 0 # Vertical shift for the whole eye for expression

        if self.current_emotion == "neutral":
            top_lid_factor = 0.4 # More closed
            bottom_lid_factor = 0.3
        elif self.current_emotion == "melancholy":
            top_lid_factor = 0.25 # Droopier
            bottom_lid_factor = 0.2
            pupil_type = "teardrop"
            pupil_size = self.eye_base_height * 0.2
            glow_opacity = 90 if self.flicker_on else 50 # Flickering glow
            show_tear = True
            eye_y_offset = self.eye_base_height * 0.1
        elif self.current_emotion == "introspective":
            top_lid_factor = 0.2 # Very narrow
            bottom_lid_factor = 0.15
            pupil_size = self.eye_base_height * 0.1
            num_cracks = 1
        elif self.current_emotion == "vulnerable":
            top_lid_factor = 0.7 # More open, rounded
            bottom_lid_factor = 0.6
            pupil_type = "cracked_heart"
            pupil_size = self.eye_base_height * 0.25
            glow_opacity = 100
            num_cracks = 2

        eye_rect = QRectF(center.x() - self.eye_base_width / 2,
                           center.y() - self.eye_base_height / 2,
                           self.eye_base_width, self.eye_base_height)

        # --- Soft Glow ---
        glow_radius = self.eye_base_width * 0.9
        current_glow_color = QColor(self.glow_color)
        current_glow_color.setAlpha(glow_opacity)
        gradient = QRadialGradient(center + QPointF(0, eye_y_offset), glow_radius)
        gradient.setColorAt(0, QColor(current_glow_color.red(), current_glow_color.green(), current_glow_color.blue(), int(glow_opacity * 1.5))) # Brighter center
        gradient.setColorAt(0.7, current_glow_color)
        gradient.setColorAt(1, QColor(0,0,0,0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center + QPointF(0, eye_y_offset), glow_radius, glow_radius)

        # --- Main Eye Shape (Almond with mechanical lid suggestion) ---
        eye_path = self._get_almond_eye_path(eye_rect, top_lid_factor, bottom_lid_factor, eye_y_offset)
        painter.setBrush(QBrush(self.iris_color)) # Fill with iris color
        painter.setPen(QPen(self.line_color, 1.5))
        painter.drawPath(eye_path)

        # Suggestion of mechanical eyelid crease
        crease_path = QPainterPath()
        crease_path.moveTo(eye_rect.left() + 5, center.y() + eye_y_offset - eye_rect.height() * top_lid_factor * 0.6)
        crease_path.quadTo(center.x(), center.y() + eye_y_offset - eye_rect.height() * top_lid_factor * 1.1, eye_rect.right() - 5, center.y() + eye_y_offset - eye_rect.height() * top_lid_factor * 0.6)
        painter.setPen(QPen(self.line_color.darker(120), 1))
        painter.drawPath(crease_path)


        painter.save()
        painter.setClipPath(eye_path) # Clip pupil and details to eye shape

        # --- Pupil ---
        pupil_center = center + QPointF(0, eye_y_offset)
        painter.setBrush(QBrush(self.pupil_color))
        painter.setPen(Qt.PenStyle.NoPen)

        if pupil_type == "dot":
            painter.drawEllipse(pupil_center, pupil_size, pupil_size * 1.2) # Slightly oval dot
        elif pupil_type == "teardrop":
            td_path = self._get_teardrop_pupil_path(pupil_center, pupil_size)
            painter.drawPath(td_path)
        elif pupil_type == "cracked_heart":
            ch_path, crack_line_path = self._get_cracked_heart_pupil_path(pupil_center, pupil_size * 2) # Heart needs more space
            painter.drawPath(ch_path)
            painter.setPen(QPen(self.line_color.lighter(120), 1)) # Crack line on heart
            painter.drawPath(crack_line_path)


        # --- Subtle Shimmer/Reflection on Pupil (if not too complex) ---
        if pupil_type != "cracked_heart": # Avoid cluttering heart
            shimmer_size = pupil_size * 0.3
            shimmer_pos = pupil_center + QPointF(-pupil_size * 0.2, -pupil_size * 0.3)
            painter.setBrush(QBrush(QColor(200, 200, 220, 60)))
            painter.drawEllipse(shimmer_pos, shimmer_size, shimmer_size)

        painter.restore() # Remove clip path

        # --- Additional Details ---
        # Cracks on eye surface
        if num_cracks > 0:
            painter.setPen(QPen(self.line_color.darker(110), 0.8))
            for i in range(num_cracks):
                start_x = center.x() + (self.eye_base_width * 0.1 * (i - num_cracks/2.0)) * (1 if is_left else -1)
                start_y = center.y() + eye_y_offset - self.eye_base_height * 0.1 + (i * 5)
                crack = QPainterPath(QPointF(start_x, start_y))
                crack.lineTo(start_x + 5 * (1 if is_left else -1) , start_y + 7)
                crack.lineTo(start_x - 3 * (1 if is_left else -1), start_y + 12)
                painter.drawPath(crack)

        # Tear of Light
        if show_tear:
            tear_path = QPainterPath()
            tear_start_x = center.x() + (self.eye_base_width * 0.1 if not is_left else -self.eye_base_width * 0.1)
            tear_start_y = center.y() + eye_y_offset + self.eye_base_height * bottom_lid_factor * 0.3

            tear_path.moveTo(tear_start_x, tear_start_y)
            tear_path.quadTo(tear_start_x + 5 * (1 if not is_left else -1), tear_start_y + 15,
                             tear_start_x + 2 * (1 if not is_left else -1), tear_start_y + 25)
            tear_path.quadTo(tear_start_x - 3 * (1 if not is_left else -1), tear_start_y + 15,
                             tear_start_x, tear_start_y) # Close it for fill

            tear_gradient = QRadialGradient(QPointF(tear_start_x, tear_start_y + 10), 15)
            tear_gradient.setColorAt(0, QColor(self.tear_glow_color.red(), self.tear_glow_color.green(), self.tear_glow_color.blue(), 200))
            tear_gradient.setColorAt(1, QColor(self.tear_glow_color.red(), self.tear_glow_color.green(), self.tear_glow_color.blue(), 0))
            painter.setBrush(QBrush(tear_gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(tear_path)


class EmoEyesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emo Robot Eyes")
        self.setGeometry(100, 100, 700, 500) # Adjusted size for wider eyes

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor(20, 20, 30)) # Very dark background

        self.robot_eyes_item = RobotEmoEyesItem()
        self.scene.addItem(self.robot_eyes_item)
        self.robot_eyes_item.setPos(0,0) # Centered in its own coordinate system

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setMinimumHeight(350)
        # Fit item in view after it's properly sized
        self.scene.setSceneRect(self.robot_eyes_item.boundingRect().adjusted(-20,-20,20,20))

        main_layout.addWidget(self.view)

        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        main_layout.addWidget(controls_frame)

        emotions = ["Neutral", "Melancholy", "Introspective", "Vulnerable"]
        for emotion in emotions:
            btn = QPushButton(emotion)
            btn.clicked.connect(lambda checked, e=emotion: self.robot_eyes_item.set_emotion(e))
            controls_layout.addWidget(btn)

        self.robot_eyes_item.set_emotion("Neutral") # Initial state

    def showEvent(self, event):
        super().showEvent(event)
        # Ensure view is fitted after window is shown and layout is applied
        self.view.fitInView(self.robot_eyes_item.boundingRect().adjusted(-10, -10, 10, 10), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.view.fitInView(self.robot_eyes_item.boundingRect().adjusted(-10, -10, 10, 10), Qt.KeepAspectRatio)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmoEyesWindow()
    window.show()
    sys.exit(app.exec_())