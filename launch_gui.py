#!/usr/bin/env python3
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pyaudio
import wave
import tempfile
import whisper
import threading

# Add src to sys.path so we can import core modules
project_root = Path(__file__).parent.resolve()
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.ai_handler import AIHandler
from uaibot.core.command_processor.command_processor import CommandProcessor

class AudioThread(QThread):
    transcribed = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._lock = threading.Lock()

    def run(self):
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            frames = []
            self._running = True
            while self._running:
                data = stream.read(1024)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            audio.terminate()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(16000)
                    wf.writeframes(b''.join(frames))
            try:
                model = whisper.load_model("base")
                result = model.transcribe(temp_path)
                transcribed_text = result.get("text", "")
                self.transcribed.emit(transcribed_text.strip())
            except Exception as e:
                self.error.emit(f"Transcription error: {str(e)}")
            finally:
                import os
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
        except Exception as e:
            self.error.emit(f"Audio error: {str(e)}")

    def stop(self):
        with self._lock:
            self._running = False

class UaiBotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot - Voice & Text Command GUI")
        self.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()
        self.label = QLabel("Hold the button to speak, or type a command below:")
        layout.addWidget(self.label)
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type a command and press Enter...")
        layout.addWidget(self.input_line)
        self.button = QPushButton("Hold to Talk")
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.audio_thread = None
        # Set up AI pipeline
        config_manager = ConfigManager()
        model_manager = ModelManager(config_manager)
        ai_handler = AIHandler(model_manager)
        self.processor = CommandProcessor(ai_handler)
        # Connect signals
        self.button.pressed.connect(self.start_recording)
        self.button.released.connect(self.stop_recording)
        self.input_line.returnPressed.connect(self.process_text_command)

    def start_recording(self):
        self.text_display.append("[Listening...]")
        self.audio_thread = AudioThread()
        self.audio_thread.transcribed.connect(self.process_voice_command)
        self.audio_thread.error.connect(self.display_error)
        self.audio_thread.start()

    def stop_recording(self):
        if self.audio_thread:
            self.audio_thread.stop()
            self.audio_thread.wait()
            self.audio_thread = None
            self.text_display.append("[Processing voice input...]")

    def process_voice_command(self, text):
        if not text:
            self.text_display.append("[No speech detected]")
            return
        self.text_display.append(f"You said: {text}")
        result = self.processor.process_command(text)
        self.display_result(result)

    def process_text_command(self):
        text = self.input_line.text().strip()
        if not text:
            return
        self.text_display.append(f"You typed: {text}")
        self.input_line.clear()
        result = self.processor.process_command(text)
        self.display_result(result)

    def display_result(self, result):
        if hasattr(result, 'output'):
            self.text_display.append(f"UaiBot: {result.output}")
        elif isinstance(result, dict) and 'output' in result:
            self.text_display.append(f"UaiBot: {result['output']}")
        else:
            self.text_display.append("UaiBot: [No output]")

    def display_error(self, msg):
        self.text_display.append(f"[Error] {msg}")
        QMessageBox.warning(self, "Error", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UaiBotGUI()
    window.show()
    sys.exit(app.exec_()) 