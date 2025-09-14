from openai import OpenAI
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QTextEdit,
    QLineEdit,
)


class ChatTab(QWidget):
    def __init__(self, tab_name: str, chat_endpoints: Dict[str, str], provider: Optional[str], 
                 model: Optional[str], prompt: Optional[str], api_keys: Dict[str, Optional[str]]):
        
        super().__init__()
        self.tab_name = tab_name
        self.chat_endpoints = chat_endpoints
        self.api_keys = api_keys
        self.provider = provider
        self.model = model
        self.prompt = prompt

        self.provider_label = QLabel(f"{self.tab_name} Chat Provider:")
        self.create_provider_menu()

        self.model_label = QLabel(f"{self.tab_name} Chat Model:")
        self.create_model_menu()

        self.prompt_label = QLabel(f"{self.tab_name} Prompt:")
        self.create_prompt_field()

        self.create_layout()
        self.setLayout(self._layout)

    def create_provider_menu(self) -> None:
        """Create the provider combo box and populate it"""
        self.provider_menu = QComboBox()
        self.provider_menu.addItems(self.chat_endpoints.keys())
        if self.provider is not None:
            self.provider_menu.setCurrentText(self.provider)

    def create_model_menu(self) -> None:
        """Create the model combo box and populate it"""
        self.models = self.get_provider_models(self.provider_menu.currentText())
        self.model_menu = QComboBox()
        self.model_menu.addItems(self.models)
        if self.model is not None:
            self.model_menu.setCurrentText(self.model)

        self.provider_menu.currentTextChanged.connect(self.update_model_menu)

    def create_prompt_field(self) -> None:
        """Create the prompt text edit field"""
        self.prompt_field = QTextEdit()
        if self.prompt is not None:
            self.prompt_field.setText(self.prompt)

    def create_layout(self) -> None:
        """Create the layout for the tab"""
        self._layout = QVBoxLayout()
        self._layout.addWidget(self.provider_label)
        self._layout.addWidget(self.provider_menu)
        self._layout.addWidget(self.model_label)
        self._layout.addWidget(self.model_menu)
        self._layout.addWidget(self.prompt_field)
        self._layout.addStretch(1)

    def get_provider_models(self, provider: str) -> List[str]:
        """Fetch available models from the provider"""
        if self.api_keys.get(provider) is not None:
            client = OpenAI(
                base_url=self.chat_endpoints[provider],
                api_key=self.api_keys[provider],
            )
            
            models = client.models.list()
            chat_models = [model.id for model in models.data]
            return chat_models
        else:
            return []
        
    def update_model_menu(self) -> None:
        """Update the model combo box when provider changes"""
        self.model_menu.clear()
        models = self.get_provider_models(self.provider_menu.currentText())
        self.model_menu.addItems(models)


class TranscriptionTab(QWidget):
    def __init__(self, transcription_endpoints: Dict[str, str], provider: Optional[str], 
                 model: Optional[str], api_keys: Dict[str, Optional[str]]):
        
        super().__init__()
        self.transcription_endpoints = transcription_endpoints
        self.transcription_provider = provider
        self.transcription_model = model
        self.api_keys = api_keys

        self.provider_label = QLabel("Transcription Provider:")
        self.create_provider_menu()

        self.model_label = QLabel("Transcription Model:")
        self.create_model_menu()

        self.create_layout()
        self.setLayout(self._layout)

    def create_provider_menu(self) -> None:
        """Create the provider combo box and populate it"""
        self.provider_menu = QComboBox()
        self.provider_menu.addItems(self.transcription_endpoints.keys())
        if self.transcription_provider is not None:
            self.provider_menu.setCurrentText(self.transcription_provider)

    def create_model_menu(self) -> None:
        """Create the model combo box and populate it"""
        models = self.get_provider_models(self.provider_menu.currentText())
        self.model_menu = QComboBox()
        self.model_menu.addItems(models)
        if self.transcription_model is not None:
            self.model_menu.setCurrentText(self.transcription_model)

        self.provider_menu.currentTextChanged.connect(self.update_model_menu)

    def create_layout(self) -> None:
        """Create the layout for the tab"""
        self._layout = QVBoxLayout()
        self._layout.addWidget(self.provider_label)
        self._layout.addWidget(self.provider_menu)
        self._layout.addWidget(self.model_label)
        self._layout.addWidget(self.model_menu)
        self._layout.addStretch(1)

    def get_provider_models(self, provider: str) -> List[str]:
        """Fetch available transcription models from the provider"""
        if self.api_keys.get(provider) is not None:
            client = OpenAI(
                base_url=self.transcription_endpoints[provider],
                api_key=self.api_keys[provider],
            )
            
            models = client.models.list()
            
            if provider == "groq":
                transcription_models = [
                    model.id for model in models.data if "whisper" in model.id.lower()
                ]
                return transcription_models
        else:
            return []
        
    def update_model_menu(self) -> None:
        """Update the model combo box when provider changes"""
        self.model_menu.clear()
        models = self.get_provider_models(self.provider_menu.currentText())
        self.model_menu.addItems(models)


class APIKeysTab(QWidget):
    def __init__(self, api_keys: Dict[str, Optional[str]]):
        super().__init__()
        self.api_keys = api_keys
        
        self.groq_api_label = QLabel("Groq API:")
        self.create_groq_api_field()

        self.openrouter_api_label = QLabel("OpenRouter API:")
        self.create_openrouter_api_field()

        self.create_layout()
        self.setLayout(self._layout)

    def create_groq_api_field(self) -> None:
        """Create the Groq API key input field"""
        self.groq_api_field = QLineEdit()
        self.groq_api_field.setClearButtonEnabled(True)
        self.groq_api_field.setEchoMode(QLineEdit.EchoMode.Password)
        if self.api_keys.get("groq"):
            self.groq_api_field.setText(self.api_keys["groq"])

    def create_openrouter_api_field(self) -> None:
        """Create the OpenRouter API key input field"""
        self.openrouter_api_field = QLineEdit()
        self.openrouter_api_field.setClearButtonEnabled(True)
        self.openrouter_api_field.setEchoMode(QLineEdit.EchoMode.Password)
        if self.api_keys.get("openrouter"):
            self.openrouter_api_field.setText(self.api_keys["openrouter"])

    def create_layout(self) -> None:
        """Create the layout for the API keys tab"""
        self._layout = QVBoxLayout()
        self._layout.addWidget(self.groq_api_label)
        self._layout.addWidget(self.groq_api_field)
        self._layout.addWidget(self.openrouter_api_label)
        self._layout.addWidget(self.openrouter_api_field)
        self._layout.addStretch(1)