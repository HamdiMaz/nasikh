# Nasikh

Nasikh (meaning "transcript" in Arabic) is a dictation application that utilizes Groq and Openrouter models for audio transcription and text cleanup. The application is built with Qt library and PySide6, providing a desktop interface for voice-to-text functionality.

## Features

- **Multi-mode dictation**: Supports English, Arabic, and Translation modes
- **Keyboard shortcuts**: Quick access to different dictation modes
- **Real-time transcription**: Uses external AI models for accurate speech-to-text conversion
- **Text cleanup**: Automated text processing for improved readability
- **Cross-platform**: Currently supports Windows with macOS support planned

## Usage

### Prerequisites

- API keys for Groq and Openrouter services (user-provided)
- Windows operating system (macOS support coming soon)

### Installation

#### Option 1: Pre-built Executable
Download and run `Nasikh.exe` from the `dist` folder.

#### Option 2: Build from Source
Execute the build script:
```bash
python build_exe.py
```

### Keyboard Shortcuts

- **English Mode**: `Alt + Q`
- **Arabic Mode**: `Alt + A`
- **Translation Mode**: `Alt + W`
- **Pause Dictation**: `Space`
- **Cancel Dictation**: `Esc`

## Configuration

Users must provide their own API keys for Groq and Openrouter services to enable transcription functionality.

## Roadmap

- Custom keyboard shortcuts configuration
- Custom dictation modes
- macOS support
- Enhanced recording interface

## Inspiration

This project was inspired by:
- [whisper-writer](https://github.com/savbell/whisper-writer) repository
- [Lewis's tutorial video](https://youtu.be/GCffvbfnnq0?si=HczD8va5WJOQh-cR)

## Development Notes

The application was initially designed with Arabic speakers in mind, hence the specific mode selection. Future updates will include more customizable options for broader language support.

No AI models are integrated into the codebase itself, except for development assistance through auto-completion tools.

## Contributing

Contributions are welcome. Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License.

## Technical Stack

- **GUI Framework**: Qt with PySide6
- **Language**: Python
- **Transcription Services**: Groq and Openrouter APIs
- **Platform**: Windows (macOS support planned)