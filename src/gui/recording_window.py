from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QApplication,
)


class RecordingWindow(QWidget):
    """A simple window to indicate recording status."""

    recording_cancelled = Signal()
    recording_paused = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._layout = QVBoxLayout()
        self.label = QLabel("Recording...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 30px; color: red; background-color: rgba(255, 255, 255, 150); border-radius: 10px; padding: 20px;")
        self._layout.addWidget(self.label)
        self.setLayout(self._layout)
        self.setFixedSize(300, 100)
        self.center_on_screen()

        cancel_shortcut = QShortcut(QKeySequence("Escape"), self)
        cancel_shortcut.activated.connect(self.recording_cancelled.emit)

        pause_shortcut = QShortcut(QKeySequence("Space"), self)
        pause_shortcut.activated.connect(self.pause_recording)

    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def show_window(self):
        self.center_on_screen()
        self.show()
        self.activateWindow()

    def pause_recording(self):
        if self.label.text() == "Recording...":
            self.recording_paused.emit()
            self.label.setText("Paused")
            self.label.setStyleSheet("font-size: 30px; color: gray; background-color: rgba(255, 255, 255, 150); border-radius: 10px; padding: 20px;")
        else:
            self.recording_paused.emit()
            self.label.setText("Recording...")
            self.label.setStyleSheet("font-size: 30px; color: red; background-color: rgba(255, 255, 255, 150); border-radius: 10px; padding: 20px;")