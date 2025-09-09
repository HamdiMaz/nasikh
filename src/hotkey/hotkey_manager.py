import win32con 
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from src.hotkey.hotkey_win import HotkeyListenerForWindows

class HotkeyManager(QWidget):
    """
    Manages global hotkeys using the Windows API.
    """
    hotkey_pressed = Signal(str) 

    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | win32con.WS_EX_TOOLWINDOW)
        self.setGeometry(0, 0, 1, 1) 
        self.hide()

        self.hotkey_listener = HotkeyListenerForWindows(self)
        self.hotkey_listener.register_hotkeys()
    
    def nativeEvent(self, event_type, message):
        """
        Override the nativeEvent method to pass events to our listener.
        """
        handled, result = self.hotkey_listener.handle_native_event(event_type, message)
        if handled:
            return True, result
        return super().nativeEvent(event_type, message)

    def closeEvent(self, event):
        """Ensure hotkeys are unregistered on exit."""
        self.hotkey_listener.unregister_hotkeys()
        event.accept()

