# nasikh.py

import io
import sys
import wave
import json
import time
import logging
import platform
import keyboard
import pyperclip
import threading
import numpy as np
import sounddevice as sd
from openai import OpenAI
from typing import List, Dict
from src.gui.tray import Tray
from src.gui.tabs import ChatTab, TranscriptionTab, APIKeysTab
from src.hotkey.hotkey_manager import HotkeyManager
from src.gui.recording_window import RecordingWindow
from pynput.keyboard import Key, Controller, GlobalHotKeys
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
from PySide6.QtGui import QIcon, QAction, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QApplication,
    QTabWidget,
    QLineEdit,
    QDialogButtonBox,
    QDialog,
    QComboBox,
    QTextEdit,
    QStyleFactory,
)





class Nasikh:
    def __init__(self):
        # ________ Provider, Models And Prompts ________
        # Transcription Model
        self.transcription_provider: str = None
        self.transcription_model: str = None
        # Chat Models
        self.arabic_provider: str = None
        self.arabic_model: str = None
        self.english_provider: str = None
        self.english_model: str = None
        self.translation_provider: str = None
        self.translation_model: str = None
        # Prompts
        self.arabic_prompt: str = None
        self.english_prompt: str = None
        self.translation_prompt: str = None

        # __________ API Keys __________
        self.api_keys: Dict[str, str | None] = {
            "groq": None,
            "openrouter": None,
        }

        # ________ Trancription Endpoints __________
        self.transcription_endpoints: Dict[str, str] = {
            "groq": "https://api.groq.com/openai/v1/"
        }
        
        # ________ Chat Endpoints ________
        self.chat_endpoints: Dict[str:str] = {
            "groq": "https://api.groq.com/openai/v1/",
            "openrouter": "https://openrouter.ai/api/v1",
        }

        # ________ Audio settings ________
        self.stream = None
        self.audio_chunks: List = []
        self.MAX_FILE_SIZE_MB: int = 25
        self.RATE: int = 16000

        # __________ Operations __________
        self.mode: str | None = None
        self.recording: bool = False

        # ____________ System ____________
        self.system: str = platform.system().lower()
        self.controller = Controller()
        self.thread_lock = threading.Lock()

        # ________ GUI Application _________
        self.app: QApplication = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setStyle(QStyleFactory.create("macOS" if self.system == "darwin" else "Fusion"))
        self.icon: QIcon = QIcon("C:\\Users\\hamdy\\Documents\\nasikh\\nasikh_icon.ico")
        self.setting: QDialog = QDialog()
        self.tray: Tray = Tray(self.icon, self.app)
        self.tray.setting.connect(self.setting.show)
        self.recording_window: RecordingWindow = RecordingWindow()
        self.recording_window.recording_cancelled.connect(self.cancel_recording)

        # __________ Hotkeys __________
        self.hotkey = HotkeyManager()
        self.hotkey.hotkey_pressed.connect(lambda lang: self.toggle_dictation(lang))

        # __________ Logging __________
        # Set up logging
        self.log_level: str = "INFO"
        self.setup_logging()
        
        # Log initialization
        self.log.info("="*40)
        self.log.info("Nasikh initialized")

        # ___________ Performance __________
        self.dictation_start: float = None
        self.dictation_end: float = None
        self.dictation_time: float = None
        self.transcription_start: float = None
        self.transcription_end: float = None
        self.cleanup_start: float = None
        self.cleanup_end: float = None
        self.audio_processing_start: float = None
        self.audio_processing_end: float = None

    def setup_logging(self):
        """Configure logging for the dictation app."""
        # Create logger
        self.log = logging.getLogger('Nasikh')
        self.log.setLevel(self.log_level)

        # Prevent duplicate logs if logger already has handlers
        if self.log.handlers:
            self.log.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler("app.log", encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to handler
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.log.addHandler(file_handler)
        
        # Log the setup
        # self.log.info("Logging setup completed")
    
    def transcript(self, audio) -> str:
        """Transcribes audio using the configured transcription model."""
        config = self.get_transcription_config()
        
        # Log provider and model
        self.log.info(f"Transcription provider: {config['provider']}")
        self.log.info(f"Transcription model: {config['model_name']}")

        client = OpenAI(
            base_url=config["api_endpoint"],
            api_key=config["api_key"],
        )

        # construct the parameters for the transcription request
        language = "en" if self.mode == "english" else "ar"
        parameters = {
            "file": ("audio.wav", audio),
            "model": self.transcription_model,
            "language": language,
            "temperature": 0.0
        }
        # Special handling for Groq API
        if config["provider"] == "groq":
            parameters["response_format"] = "text"
        
        # Log the start of transcription
        self.transcription_start = time.time()

        transcription = client.audio.transcriptions.create(**parameters)

        # Log the end of transcription
        self.transcription_end = time.time()

        return transcription
    
    def cleanup(self, user_input: str) -> str:
        """Cleans up the user input using the configured chat model."""
        config = self.get_chat_config()

        # Log provider and model
        self.log.info(f"Cleanup provider: {config['provider']}")
        self.log.info(f"Cleanup model: {config['model_name']}")

        client = OpenAI(
            base_url=config["api_endpoint"],
            api_key=config["api_key"],
        )

        # construct the parameters for the chat completion request
        parameters = {
            "model": config["model_name"],
            "messages": [
            {
                "role": "user",
                "content": config["prompt"] + "\n\n" + user_input
            }
            ],
            "temperature": 0.1,
            "max_completion_tokens": 4096,
            "top_p": 1,
        }
        # Special handling for Groq API
        if config["provider"] == "groq":
            parameters["reasoning_effort"] = "none"
        
        # Log the start of cleanup
        self.cleanup_start = time.time()

        completion = client.chat.completions.create(**parameters)
        
        # Log the end of cleanup
        self.cleanup_end = time.time()
        
        return completion.choices[0].message.content
    
    def get_json_config(self) -> Dict:
        """Loads configuration from a JSON file."""
        try:
            with open("config.json", "r", encoding="utf-8") as file:
                config = json.load(file)
                
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)

        except FileNotFoundError:
            self.save_json_config()

    def save_json_config(self) -> None:
        """Saves the current configuration to a JSON file."""
        config = {
            "api_keys": self.api_keys,
            "transcription_provider": self.transcription_provider,
            "transcription_model": self.transcription_model,
            "english_provider": self.english_provider,
            "english_model": self.english_model,
            "english_prompt": self.english_prompt,
            "translation_provider": self.translation_provider,
            "translation_model": self.translation_model,
            "translation_prompt": self.translation_prompt,
            "arabic_provider": self.arabic_provider,
            "arabic_model": self.arabic_model,
            "arabic_prompt": self.arabic_prompt
        }
        with open("config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)

    def get_transcription_config(self) -> Dict:
        """
        Gets the transcription provider and model based on the current mode.
        Returns them in a single configuration dictionary.
        """
        if self.mode == "arabic":
            provider = self.transcription_provider
            model_name = self.transcription_model
        elif self.mode == "english":
            provider = self.english_provider
            model_name = self.english_model
        elif self.mode == "translation":
            provider = self.translation_provider
            model_name = self.translation_model
        
        return {
            "provider": provider,
            "api_endpoint": self.transcription_endpoints[provider],
            "api_key": self.api_keys[provider],
            "model_name": model_name,
        }
    
    def get_chat_config(self) -> dict:
        """
        Gets the chat provider, model, and prompt based on the current mode.
        Returns them in a single configuration dictionary.
        """
        if self.mode == "arabic":
            provider = self.arabic_provider
            api_key = self.api_keys[provider]
            model_name = self.arabic_model
            prompt = self.arabic_prompt
        elif self.mode == "english":
            provider = self.english_provider
            api_key = self.api_keys[provider]
            model_name = self.english_model
            prompt = self.english_prompt
        elif self.mode == "translation":
            provider = self.translation_provider
            api_key = self.api_keys[provider]
            model_name = self.translation_model
            prompt = self.translation_prompt

        return {
            "provider": provider,
            "api_endpoint": self.chat_endpoints[provider],
            "api_key": api_key,
            "model_name": model_name,
            "prompt": prompt,
        }

    def start_recording(self) -> None:
        """Starts the audio recording stream."""
        self.recording = True
        self.audio_chunks = []

        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_chunks.append((indata * 32767).astype(np.int16).copy())
        
        self.stream = sd.InputStream(
            samplerate=self.RATE,
            channels=1,
            callback=callback,
            dtype='float32'
        )
        self.stream.start()

    def stop_recording(self) -> io.BytesIO | None:
        """Stops the stream and returns the audio data as a WAV buffer."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        if not self.audio_chunks:
            return None
        
        audio_data = np.concatenate(self.audio_chunks)
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self.RATE)
            w.writeframes(audio_data.tobytes())
        
        wav_buffer.seek(0)
        
        file_size_mb = wav_buffer.getbuffer().nbytes / (1024 * 1024)
        duration_seconds = len(audio_data) / self.RATE

        #log the audio
        self.log.info(f"Audio size: {file_size_mb:.2f}MB")
        self.log.info(f"Audio duration: {duration_seconds:.1f} seconds")

        # Log dictation time
        self.dictation_time = duration_seconds

        if file_size_mb > self.MAX_FILE_SIZE_MB:
            # Log the file size warning
            self.log.warning(f"File size exceeds {self.MAX_FILE_SIZE_MB}MB limit!")
            return None
        
        return wav_buffer
    
    @Slot()
    def cancel_recording(self) -> None:
        """Cancels the current recording without processing the audio."""
        with self.thread_lock:
            if self.recording:
                self.stop_recording()
                self.recording = False
                self.recording_window.hide()

    @Slot()
    def toggle_dictation(self,  mode: str) -> None:
        """Starts or stops the dictation process."""
        with self.thread_lock:
            if self.recording:
                # If recording, stop it
                audio_buffer = self.stop_recording()
                self.recording = False
                self.recording_window.hide()
                
                if audio_buffer is None:
                    # Log the cancellation
                    self.log.debug("Recording cancelled, no audio to process.")
                    return 
            
                # Process the audio that was recorded
                self.process_and_paste(audio_buffer)

                # Log the end of dictation
                self.dictation_end = time.time()

                # Log the performance metrics
                self.log.debug(f"Dictation completed in {self.dictation_end - self.dictation_start:.2f} seconds.")
                self.log.debug(f"Recorded auido is {self.dictation_time:.2f} seconds.")
                self.log.debug(f"Transcription completed in {self.transcription_end - self.transcription_start:.2f} seconds.")
                self.log.debug(f"Cleanup completed in {self.cleanup_end - self.cleanup_start:.2f} seconds.")
            
            else:
                # Log the start of dictation
                self.dictation_start = time.time()

                # Log the dictation mode
                self.log.info(f"Starting dictation in {mode} mode.") 

                # If not recording, start a new one
                self.recording = True
                self.mode = mode
                self.start_recording()
                self.recording_window.show_window()

    def process_and_paste(self, audio_buffer: io.BytesIO) -> None:
        """Transcribes audio, cleans it, and pastes the result."""
        user_input = self.transcript(audio_buffer)
        # Log the transcription result
        self.log.info(f"Transcription result: {user_input}")

        clean_user_input = self.cleanup(user_input)
        # Log the cleanup result
        self.log.info(f"Cleanup result: {clean_user_input}")

        # Saving the original clipboard content
        try:
            original_clipboard = pyperclip.paste()
        except pyperclip.PyperclipException:
            original_clipboard = None

        # Paste the cleaned user input
        pyperclip.copy(clean_user_input)
        if self.system == "darwin": 
            with self.controller.pressed(Key.cmd):
                self.controller.tap('v')
        elif self.system in ["windows", "linux"]:
            with self.controller.pressed(Key.ctrl):
                self.controller.tap('v')
        
        # Give the application time to paste before restoring clipboard
        time.sleep(0.1)
        if original_clipboard is not None:
            pyperclip.copy(original_clipboard)
    
    def test_api_keys(self, provider: str, api_key: str) -> bool:
        """Checks if the provided API key is valid"""
        try:
            client = OpenAI(
                base_url=self.transcription_endpoints[provider],
                api_key=api_key,
            )
            client.models.list()
            return True
        
        except Exception as e:
            if "401" in str(e):
                self.log.debug(f"❌ Invalid API key for {provider}. Please check your configuration.")
            return False

    def save_setting_menu(self):
        self.api_keys["groq"] = self.api_keys_tab.groq_api_field.text().strip() or None
        self.api_keys["openrouter"] = self.api_keys_tab.openrouter_api_field.text().strip() or None

        self.transcription_provider = self.transcription_tab.provider_menu.currentText()
        self.transcription_model = self.transcription_tab.model_menu.currentText()

        self.english_provider = self.english_tab.provider_menu.currentText()
        self.english_model = self.english_tab.model_menu.currentText()
        self.english_prompt = self.english_tab.prompt_field.toPlainText()

        self.arabic_provider = self.arabic_tab.provider_menu.currentText()
        self.arabic_model = self.arabic_tab.model_menu.currentText()
        self.arabic_prompt = self.arabic_tab.prompt_field.toPlainText()

        self.translation_provider = self.translation_tab.provider_menu.currentText()
        self.translation_model = self.translation_tab.model_menu.currentText()
        self.translation_prompt = self.translation_tab.prompt_field.toPlainText()

        self.save_json_config()
        self.setting.accept()              

    def run(self) -> None:
        """Main method to handle dictation"""
        # Load the configuration
        self.get_json_config()

        #____________ API Keys Tab ____________

        self.api_keys_tab: APIKeysTab = APIKeysTab(self.api_keys)

        #____________ Transcription Tab ____________

        self.transcription_tab: TranscriptionTab = TranscriptionTab(self.transcription_endpoints,
                                                                   self.transcription_provider,
                                                                   self.transcription_model,
                                                                   self.api_keys)

        #____________ English Tab ____________

        self.english_tab: ChatTab = ChatTab("English", 
                                    self.chat_endpoints, 
                                    self.english_provider, 
                                    self.english_model, 
                                    self.english_prompt, 
                                    self.api_keys)

        #____________ Arabic Tab ____________

        self.arabic_tab: ChatTab = ChatTab("Arabic",
                                   self.chat_endpoints,
                                   self.arabic_provider,
                                   self.arabic_model,
                                   self.arabic_prompt,
                                   self.api_keys)

        #____________ Translation Tab ____________

        self.translation_tab: ChatTab = ChatTab("Translation",
                                        self.chat_endpoints,
                                        self.translation_provider,
                                        self.translation_model,
                                        self.translation_prompt,
                                        self.api_keys)

        #____________ Setting UI ____________

        tab_widget = QTabWidget()
        tab_widget.addTab(self.api_keys_tab, "API Keys")
        tab_widget.addTab(self.transcription_tab, "Transcription")
        tab_widget.addTab(self.english_tab, "English")
        tab_widget.addTab(self.arabic_tab, "Arabic")
        tab_widget.addTab(self.translation_tab, "Translation")

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )

        button_box.accepted.connect(self.save_setting_menu)
        button_box.rejected.connect(self.setting.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        main_layout.addWidget(button_box)
        self.setting.setLayout(main_layout)
        self.setting.setWindowTitle("Nasikh Settings")
        self.setting.setWindowIcon(self.icon)



        # run the GUI application
        sys.exit(self.app.exec())
        

    