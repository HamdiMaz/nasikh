from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
)

class Tray(QSystemTrayIcon):
    setting = Signal()
    def __init__(self, icon, app):
        super().__init__(icon, parent=app)
        self.app = app
        self.setToolTip("Nasikh")
        self.menu = QMenu()

        # Create a "Setting" action
        self.setting_action = QAction("Setting")
        self.setting_action.triggered.connect(self.setting.emit)
        self.menu.addAction(self.setting_action)

        # Create a "Quit" action
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)

        self.setContextMenu(self.menu)
        self.setVisible(True)
