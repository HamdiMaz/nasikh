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

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.layout = QVBoxLayout()
        self.label = QLabel("Recording...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 30px; color: red; background-color: rgba(255, 255, 255, 150); border-radius: 10px; padding: 20px;")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setFixedSize(300, 100)
        self.center_on_screen()

        shortcut = QShortcut(QKeySequence("Escape"), self)
        shortcut.activated.connect(self.recording_cancelled.emit)

    def center_on_screen(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def show_window(self):
        self.center_on_screen()
        self.show()
        self.activateWindow()