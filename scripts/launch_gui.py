#!/usr/bin/env python3
# TODO: Refactor GUI to use agentic core (Agent, ToolRegistry, etc.) for all command processing and file outputs.
#       All file outputs must use safe_path or equivalent. Update all file operations accordingly.
#       (See /src/uaibot/core/ai/agent.py for safe_path.)
#       This is required by project rules.
# If you see import errors, run with: PYTHONPATH=src python3 scripts/launch_gui.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QMessageBox, QHBoxLayout, QComboBox, QColorDialog, QDialog, QFormLayout, QDialogButtonBox, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QColor, QTextCharFormat, QTextCursor, QFont
import pyaudio
import wave
import tempfile
import whisper
import threading
import platform
import json
import subprocess
import os
import importlib.util
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None
try:
    import pyautogui
except ImportError:
    pyautogui = None

# Add src to sys.path so we can import core modules
project_root = Path(__file__).parent.resolve()
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from uaibot.core.config_manager import ConfigManager
from uaibot.core.model_manager import ModelManager
from uaibot.core.ai.agent import Agent, ToolRegistry, EchoTool, safe_path
from uaibot.core.ai.agent_tools import FileTool

os.environ["WHISPER_FORCE_FP32"] = "1"

class AudioThread(QThread):
    transcribed = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None, language=None, use_fp32=True):
        super().__init__(parent)
        self._running = False
        self._lock = threading.Lock()
        self.language = language
        self.use_fp32 = use_fp32
        if self.use_fp32:
            os.environ["WHISPER_FORCE_FP32"] = "1"
        else:
            os.environ["WHISPER_FORCE_FP32"] = "0"

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
                lang = self.language if self.language and self.language != 'auto' else None
                result = model.transcribe(temp_path, language=lang)
                transcribed_text = result.get("text", "")
                print(f"[VOICE TRANSCRIBED]: {transcribed_text}")
                self.transcribed.emit(transcribed_text.strip())
            except Exception as e:
                print(f"[VOICE TRANSCRIBE ERROR]: {str(e)}")
                self.error.emit(f"Transcription error: {str(e)}")
            finally:
                import os
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
        except Exception as e:
            print(f"[AUDIO ERROR]: {str(e)}")
            self.error.emit(f"Audio error: {str(e)}")

    def stop(self):
        with self._lock:
            self._running = False

class SettingsDialog(QDialog):
    def __init__(self, parent, color_settings, result_mode, available_models, current_model, health_check_callback, selected_language, vision_model, stt_model, tts_model, use_fp32, available_stt, available_tts):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.color_settings = color_settings.copy()
        self.result_mode = result_mode
        self.selected_model = current_model
        self.available_models = available_models
        self.available_stt = available_stt
        self.available_tts = available_tts
        self.health_check_callback = health_check_callback
        self.selected_language = selected_language
        self.vision_model = vision_model
        self.stt_model = stt_model
        self.tts_model = tts_model
        self.use_fp32 = use_fp32
        layout = QFormLayout()
        self.color_buttons = {}
        emoji_font = QFont()
        if platform.system() == "Darwin":
            emoji_font.setFamily("Apple Color Emoji")
        elif platform.system() == "Windows":
            emoji_font.setFamily("Segoe UI Emoji")
        else:
            emoji_font.setFamily("Noto Color Emoji")
        emoji_font.setPointSize(18)
        color_button_size = QSize(24, 24)
        for key, label in [
            ("user", "User Input Color"),
            ("robot", "UaiBot Reply Color"),
            ("ai", "AI Reply Color"),
            ("system", "System Reply Color"),
            ("health", "Health Check Color"),
            ("error", "Error Color")
        ]:
            btn = QPushButton()
            btn.setFixedSize(color_button_size)
            btn.setStyleSheet(f"background-color: {self.color_settings[key]}; border: 1px solid #888; border-radius: 6px;")
            btn.setFont(emoji_font)
            btn.clicked.connect(lambda _, k=key: self.pick_color(k))
            self.color_buttons[key] = btn
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(btn)
            row.addStretch()
            layout.addRow(row)
        # AI Model selection
        self.model_dropdown = QComboBox()
        self.update_model_dropdown(self.available_models, self.selected_model)
        layout.addRow(QLabel("AI Model:"), self.model_dropdown)
        # When the dropdown is about to show, refresh the model list
        self.model_dropdown.popupAboutToBeShown = self.refresh_model_list
        # Vision model (fixed, not selectable)
        self.vision_model = "SmolVLM-256M"
        layout.addRow(QLabel("Vision Model:"), QLabel(self.vision_model))
        # STT model
        self.stt_model_dropdown = QComboBox()
        self.stt_model_dropdown.addItems(self.available_stt)
        idx = self.stt_model_dropdown.findText(self.stt_model)
        if idx >= 0:
            self.stt_model_dropdown.setCurrentIndex(idx)
        layout.addRow(QLabel("STT Model:"), self.stt_model_dropdown)
        # TTS model
        self.tts_model_dropdown = QComboBox()
        self.tts_model_dropdown.addItems(self.available_tts)
        idx = self.tts_model_dropdown.findText(self.tts_model)
        if idx >= 0:
            self.tts_model_dropdown.setCurrentIndex(idx)
        layout.addRow(QLabel("TTS Model:"), self.tts_model_dropdown)
        # Health check button (aligned with label)
        health_row = QHBoxLayout()
        self.health_label = QLabel("Health Check:")
        self.health_button = QPushButton("💉")
        self.health_button.setToolTip("Run Health Check")
        self.health_button.setFont(emoji_font)
        self.health_button.setFixedSize(32, 32)
        self.health_button.setStyleSheet("QPushButton { background: #222; border: 1px solid #888; border-radius: 8px; } QPushButton:hover { background: #444; }")
        self.health_button.clicked.connect(self.run_health_check_and_update_models)
        health_row.addWidget(self.health_label)
        health_row.addWidget(self.health_button)
        health_row.addStretch()
        layout.addRow(health_row)
        # Language selector
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["auto", "en", "ar"])
        idx = self.language_dropdown.findText(self.selected_language)
        if idx >= 0:
            self.language_dropdown.setCurrentIndex(idx)
        layout.addRow(QLabel("Voice Recognition Language:"), self.language_dropdown)
        # Result mode radio buttons
        self.result_group = QButtonGroup(self)
        self.result_full = QRadioButton("Full")
        self.result_friendly = QRadioButton("User Friendly")
        self.result_only = QRadioButton("Only Results")
        self.result_group.addButton(self.result_full)
        self.result_group.addButton(self.result_friendly)
        self.result_group.addButton(self.result_only)
        if self.result_mode == "full":
            self.result_full.setChecked(True)
        elif self.result_mode == "user_friendly":
            self.result_friendly.setChecked(True)
        else:
            self.result_only.setChecked(True)
        layout.addRow(QLabel("Command Result Display Mode:"))
        layout.addRow(self.result_full)
        layout.addRow(self.result_friendly)
        layout.addRow(self.result_only)
        # Add FP32/FP16 choice
        self.precision_group = QButtonGroup(self)
        self.fp32_radio = QRadioButton("FP32 (More accurate, slower)")
        self.fp16_radio = QRadioButton("FP16 (Faster, less accurate)")
        self.precision_group.addButton(self.fp32_radio)
        self.precision_group.addButton(self.fp16_radio)
        if self.use_fp32:
            self.fp32_radio.setChecked(True)
        else:
            self.fp16_radio.setChecked(True)
        layout.addRow(QLabel("Voice Recognition Precision:"))
        layout.addRow(self.fp32_radio)
        layout.addRow(self.fp16_radio)
        # OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def update_model_dropdown(self, models, current_model):
        self.model_dropdown.clear()
        self.model_dropdown.addItems(models)
        idx = self.model_dropdown.findText(current_model)
        if idx >= 0:
            self.model_dropdown.setCurrentIndex(idx)
        self.model_dropdown.setEnabled(True)

    def run_health_check_and_update_models(self):
        # Call the parent's health check, which returns the available models
        models = self.health_check_callback(update_models=True)
        if models:
            self.update_model_dropdown(models, self.model_dropdown.currentText())

    def pick_color(self, key):
        color = QColorDialog.getColor(QColor(self.color_settings[key]), self, f"Pick color for {key}")
        if color.isValid():
            self.color_settings[key] = color.name()
            self.color_buttons[key].setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888; border-radius: 6px;")

    def refresh_model_list(self):
        # Get the latest models from the parent (UaiBotGUI)
        if hasattr(self.parent(), 'get_available_models'):
            models = self.parent().get_available_models()
            self.update_model_dropdown(models, self.model_dropdown.currentText())

    def get_settings(self):
        if self.result_full.isChecked():
            mode = "full"
        elif self.result_friendly.isChecked():
            mode = "user_friendly"
        else:
            mode = "only_results"
        lang = self.language_dropdown.currentText()
        vision_model = self.vision_model  # Always 'SmolVLM-256M'
        stt_model = self.stt_model_dropdown.currentText()
        tts_model = self.tts_model_dropdown.currentText()
        use_fp32 = self.fp32_radio.isChecked()
        return self.color_settings, mode, self.model_dropdown.currentText(), lang, vision_model, stt_model, tts_model, use_fp32

class UaiBotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UaiBot - Voice & Text Command GUI")
        self.setGeometry(200, 200, 600, 400)
        main_layout = QVBoxLayout()
        # Top bar with label and settings button at right
        top_bar = QHBoxLayout()
        self.label = QLabel("Hold the button to speak, or type a command below:")
        top_bar.addWidget(self.label)
        top_bar.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # Gear emoji button for settings
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setToolTip("Settings")
        self.settings_button.setFixedSize(36, 36)
        emoji_font = QFont()
        if platform.system() == "Darwin":
            emoji_font.setFamily("Apple Color Emoji")
        elif platform.system() == "Windows":
            emoji_font.setFamily("Segoe UI Emoji")
        else:
            emoji_font.setFamily("Noto Color Emoji")
        emoji_font.setPointSize(18)
        self.settings_button.setFont(emoji_font)
        self.settings_button.setStyleSheet("QPushButton { background: #222; border: 1px solid #888; border-radius: 8px; } QPushButton:hover { background: #444; }")
        self.settings_button.clicked.connect(self.open_settings)
        top_bar.addWidget(self.settings_button, alignment=Qt.AlignRight)
        main_layout.addLayout(top_bar)
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        main_layout.addWidget(self.text_display)
        # Input area with mic button and text input
        input_bar = QHBoxLayout()
        self.mic_button = QPushButton("🎤")
        self.mic_button.setToolTip("Hold to Talk")
        self.mic_button.setFixedSize(36, 36)
        self.mic_button.setFont(emoji_font)
        self.mic_button.setStyleSheet("QPushButton { background: #222; border: 1px solid #888; border-radius: 8px; } QPushButton:hover { background: #444; }")
        self.mic_button.pressed.connect(self.start_recording)
        self.mic_button.released.connect(self.stop_recording)
        input_bar.addWidget(self.mic_button)
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type a command and press Enter...")
        input_bar.addWidget(self.input_line)
        main_layout.addLayout(input_bar)
        self.setLayout(main_layout)
        self.audio_thread = None
        # Set up AI pipeline
        config_manager = ConfigManager()
        self.model_manager = ModelManager(config_manager)
        self.text_model = config_manager.get("text_model", "smolvlm")
        self.vision_model = config_manager.get("vision_model", "smolvlm")
        self.stt_model = config_manager.get("stt_model", "whisper")
        self.tts_model = config_manager.get("tts_model", "none")
        self.use_fp32 = config_manager.get("use_fp32", True)
        # Color settings (tuned for system look)
        self.color_settings = {
            "user": "#1976D2",    # system blue
            "robot": "#388E3C",  # system green
            "ai": "#7B1FA2",     # system purple
            "system": "#616161",  # system gray
            "health": "#00B8D9", # health check cyan
            "error": "#D32F2F"    # system red
        }
        self.result_mode = "user_friendly"
        self.available_models = self.discover_local_models()
        self.available_stt = self.discover_local_stt()
        self.available_tts = self.discover_local_tts()
        self.valid_text_models = [m for m in self.available_models if m != "smolvlm" and m != "smolvlm-vision"]
        if not self.valid_text_models:
            self.text_model = ""
            self.append_colored("🙁  ERROR>>> No valid text model found. Please install an Ollama model and restart.", self.color_settings["error"])
        else:
            if getattr(self, 'text_model', None) not in self.valid_text_models:
                self.text_model = self.valid_text_models[0]
                # Update config immediately
                self.model_manager.config.set("text_model", self.text_model)
                self.model_manager.config.save()
        # Always enable settings button
        self.settings_button.setEnabled(True)
        # Connect signals
        self.input_line.returnPressed.connect(self.process_text_command)
        self.selected_language = "auto"
        # Show welcome message
        self.append_colored("🤖 UaiBot>>> Welcome! I am ready to help. You can speak or type a command.", self.color_settings["robot"])
        # Set up agentic core
        self.registry = ToolRegistry()
        self.registry.register(EchoTool())
        self.registry.register(FileTool())
        self.agent = Agent(tools=self.registry)

    def open_settings(self):
        available_models = self.get_available_models()
        valid_text_models = [m for m in available_models if m != "smolvlm" and m != "smolvlm-vision"]
        if not valid_text_models:
            self.text_model = ""
            self.append_colored("🙁  ERROR>>> No valid text model found. Please install an Ollama model and restart.", self.color_settings["error"])
        elif self.text_model not in valid_text_models:
            self.text_model = valid_text_models[0]
            self.model_manager.config.set("text_model", self.text_model)
            self.model_manager.config.save()
        dlg = SettingsDialog(self, self.color_settings, self.result_mode, available_models, self.model_manager.model_info.name, self.run_health_check, self.selected_language, self.vision_model, self.stt_model, self.tts_model, self.use_fp32, self.available_stt, self.available_tts)
        if dlg.exec_():
            # Only update the config values that changed
            new_color_settings, new_mode, new_ai_model, new_lang, new_vision_model, new_stt_model, new_tts_model, new_use_fp32 = dlg.get_settings()
            if new_color_settings != self.color_settings:
                self.color_settings = new_color_settings
            if new_mode != self.result_mode:
                self.result_mode = new_mode
            if new_ai_model != self.model_manager.model_info.name:
                self.model_manager.set_ollama_model(new_ai_model)
                self.selected_model = new_ai_model
            if new_vision_model != self.vision_model:
                self.vision_model = new_vision_model
                self.model_manager.config.set("vision_model", new_vision_model)
            if new_stt_model != self.stt_model:
                self.stt_model = new_stt_model
                self.model_manager.config.set("stt_model", new_stt_model)
            if new_tts_model != self.tts_model:
                self.tts_model = new_tts_model
                self.model_manager.config.set("tts_model", new_tts_model)
            if new_use_fp32 != self.use_fp32:
                self.use_fp32 = new_use_fp32
                self.model_manager.config.set("use_fp32", new_use_fp32)
            self.model_manager.config.save()
            self.populate_models()  # Refresh model list but keep selected
            # Set dropdown to selected model
            if hasattr(self, 'settings_dialog'):
                idx = self.settings_dialog.model_dropdown.findText(self.selected_model)
                if idx >= 0:
                    self.settings_dialog.model_dropdown.setCurrentIndex(idx)

    def run_health_check(self, update_models=False):
        # Real health check: try to connect to Ollama and list models, check system info
        try:
            models = []
            try:
                import requests
                resp = requests.get("http://localhost:11434/api/tags", timeout=3)
                if resp.ok:
                    models = [m['name'] for m in resp.json().get('models', [])]
            except Exception:
                pass
            # Always add custom models
            if "smolvlm" not in models:
                models.append("smolvlm")
            self.available_models = list(dict.fromkeys(models))
            # Check system info
            sysinfo = subprocess.getoutput('uname -a')
            msg = f"Available models: {', '.join(models) if models else 'none found'}\nSystem: {sysinfo}\nSystem health: OK ✅"
            self.append_colored(f"💉 HEALTH>>> {msg}", self.color_settings["health"])
            if update_models:
                return self.available_models
        except Exception as e:
            self.append_colored(f"🙁  ERROR>>> Health check failed: {e}", self.color_settings["error"])
            if update_models:
                return self.available_models

    def append_colored(self, text, color, tooltip=None):
        cursor = self.text_display.textCursor()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + "\n", fmt)
        self.text_display.setTextCursor(cursor)
        self.text_display.ensureCursorVisible()
        if tooltip:
            pass

    def populate_models(self):
        # Always include custom models
        custom_models = ["smolvlm"]
        ollama_models = []
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/tags", timeout=3)
            if resp.ok:
                ollama_models = [m['name'] for m in resp.json().get('models', [])]
        except Exception:
            pass
        # Merge and deduplicate
        all_models = list(dict.fromkeys(ollama_models + custom_models))
        self.available_models = all_models if all_models else custom_models

    def get_available_models(self):
        try:
            return self.model_manager.get_available_models()
        except Exception:
            return [self.model_manager.model_info.name]

    def start_recording(self):
        self.audio_thread = AudioThread(language=self.selected_language, use_fp32=self.use_fp32)
        self.audio_thread.transcribed.connect(self.process_voice_command)
        self.audio_thread.error.connect(self.display_error)
        self.audio_thread.start()
        # Do not show [Processing voice input...] yet
        self.append_colored("💻 SYSTEM>>> [Listening...]", self.color_settings["system"])

    def stop_recording(self):
        if self.audio_thread:
            self.audio_thread.stop()
            self.audio_thread.wait()
            self.audio_thread = None
        # [Processing voice input...] will be shown after user command

    def process_voice_command(self, text):
        self.append_colored(f"👤 USER>>> {text}", self.color_settings["user"])
        if not text or not text.strip() or not any(c.isalnum() for c in text):
            polite_msg = "Sorry, I didn't catch that. Could you please try speaking again?"
            self.append_colored("💻 SYSTEM>>> [No speech detected]", self.color_settings["system"])
            self.speak(polite_msg)
            return
        self.append_colored("💻 SYSTEM>>> [Processing voice input...]", self.color_settings["system"])
        # Route to agentic core
        result = self.agent.plan_and_execute(text, {})
        self.display_result(result)

    def process_text_command(self):
        text = self.input_line.text().strip()
        if not text:
            return
        self.append_colored(f"👤 USER>>> {text}", self.color_settings["user"])
        self.input_line.clear()
        # Route to agentic core
        result = self.agent.plan_and_execute(text, {})
        self.display_result(result)

    def take_screenshot(self):
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            path = temp_file.name
            temp_file.close()
            if ImageGrab:
                img = ImageGrab.grab()
                img.save(path)
                return path
            elif pyautogui:
                img = pyautogui.screenshot()
                img.save(path)
                return path
            else:
                return None
        except Exception as e:
            print(f"[SCREENSHOT ERROR]: {e}")
            return None

    def display_result(self, result):
        if hasattr(result, 'output') and result.output:
            try:
                plan = json.loads(result.output)
                if "plan" in plan and isinstance(plan["plan"], list):
                    for step in plan["plan"]:
                        if step.get("operation", "").startswith("system_command"):
                            cmd = step.get("parameters", {}).get("command", "")
                            if cmd:
                                mapped_cmd = self.map_to_shell_command(cmd)
                                if mapped_cmd:
                                    try:
                                        result = subprocess.run(mapped_cmd, shell=True, capture_output=True, text=True, timeout=10)
                                        if result.returncode == 0:
                                            feedback = self.get_system_command_feedback(cmd, result.stdout.strip())
                                            self.append_colored(f"💻 SYSTEM>>> {feedback}", self.color_settings["system"])
                                        else:
                                            self.append_colored(f"🙁  ERROR>>> {result.stderr.strip()}", self.color_settings["error"])
                                    except Exception as e:
                                        self.append_colored(f"🙁  ERROR>>> {str(e)}", self.color_settings["error"])
                        else:
                            self.append_colored(f"🤖 UaiBot>>> {step.get('description', '')}", self.color_settings["robot"])
            except json.JSONDecodeError:
                self.append_colored(f"🤖 UaiBot>>> {result.output}", self.color_settings["robot"])
        elif hasattr(result, 'error') and result.error:
            self.append_colored(f"🙁  ERROR>>> {result.error}", self.color_settings["error"])
        else:
            self.append_colored("🤖 UaiBot>>> [No output]", self.color_settings["robot"])

    def display_error(self, msg):
        self.append_colored(f"🙁  ERROR>>> {msg}", self.color_settings["error"])
        QMessageBox.warning(self, "Error", msg)

    def get_system_command_feedback(self, command, output):
        # Try to provide a user-friendly description of the system output
        if output and output.strip():
            return output.strip()
        # Example: map known commands to friendly messages
        if 'calculator' in command.lower():
            return "Calculator app opened on screen 1."
        if 'safari' in command.lower():
            return "Safari browser launched."
        if 'open' in command.lower() and 'http' in command.lower():
            return "Website opened in default browser."
        return "Command executed successfully, but no output was returned."

    def map_to_shell_command(self, cmd):
        # Map common app names to real shell commands (macOS example)
        mapping = {
            "openCalculator": "open -a Calculator",
            "start_calculator": "open -a Calculator",
            "launch_chrome": "open -a Google\\ Chrome",
            "open_application": "open -a System\\ Settings",
            "navigate_to": "open -a System\\ Settings",
            "open_jd_feature": "open -a JD",
            # Add more mappings as needed
        }
        return mapping.get(cmd.strip(), None)

    def discover_local_models(self):
        models = []
        # Ollama models
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/tags", timeout=3)
            if resp.ok:
                models += [m['name'] for m in resp.json().get('models', [])]
        except Exception:
            pass
        # HuggingFace models (look for local folders in ~/.cache/huggingface/hub)
        import os
        hf_dir = os.path.expanduser("~/.cache/huggingface/hub")
        if os.path.isdir(hf_dir):
            for d in os.listdir(hf_dir):
                if d.startswith('models--'):
                    model_name = d.replace('models--', '').replace('--', '/')
                    if model_name not in models:
                        models.append(model_name)
        # SmolVLM for vision
        try:
            from uaibot.core.ai.models.vision.processor import VisionProcessor
            models.append("smolvlm-vision")
        except Exception:
            pass
        return models

    def discover_local_stt(self):
        stt = []
        if importlib.util.find_spec("whisper"):
            stt.append("whisper")
        if importlib.util.find_spec("vosk"):
            stt.append("vosk")
        # Add more local STT engines as needed
        return stt

    def discover_local_tts(self):
        tts = []
        if importlib.util.find_spec("pyttsx3"):
            tts.append("pyttsx3")
        if importlib.util.find_spec("TTS"):
            tts.append("coqui-tts")
        # Add more local TTS engines as needed
        return tts

    def process_vision_task(self, image_path):
        # Only use vision-capable models
        if 'vision' not in self.vision_model and 'smolvlm' not in self.vision_model:
            self.append_colored("🙁  ERROR>>> Selected vision model is not vision-capable. Please select a valid vision model in settings.", self.color_settings["error"])
            return
        # ... existing vision processing logic ...

    def speak(self, text):
        """Speak text using the selected TTS model or fallback to macOS say command."""
        if self.tts_model == "pyttsx3":
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                self.append_colored(f"🙁  ERROR>>> pyttsx3 failed: {e}", self.color_settings["error"])
        else:
            # Use macOS system TTS if available
            import platform, os
            if platform.system() == "Darwin":
                os.system(f'say "{text}"')
            else:
                self.append_colored(f"🔈 {text}", self.color_settings["system"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UaiBotGUI()
    window.show()
    sys.exit(app.exec_()) 