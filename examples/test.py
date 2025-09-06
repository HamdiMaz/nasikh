import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QApplication,
    QTabWidget,
    QLineEdit,
    QDialogButtonBox,
    QSystemTrayIcon, 
    QMenu,
    QDialog,
    QComboBox,
    QTextEdit,
    QStyleFactory,
)


class TestApp(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Application")
        self.setWindowIcon(QIcon("nasikh_icon.ico"))
        self.resize(400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("This is a test application.")
        layout.addWidget(self.label)
        
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_app = TestApp()
    test_app.show()
    sys.exit(app.exec())