import ctypes
import win32con 
from ctypes import wintypes
from PySide6.QtCore import QObject

ENGLISH_HOTKEY_ID = 1
TRANSLATION_HOTKEY_ID = 2
ARABIC_HOTKEY_ID = 3

class HotkeyListenerForWindows(QObject):
    """
    Listens for global hotkey events using the Windows API.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        
    def register_hotkeys(self):
        """
        Registers global hotkeys. 
        """
        self.hwnd = self.parent_window.winId().__int__()

        self.create_english_hotkey()
        self.create_translation_hotkey()
        self.create_arabic_hotkey()

    def create_english_hotkey(self):
        mods = win32con.MOD_ALT
        key = ord('Q')
        ctypes.windll.user32.RegisterHotKey(self.hwnd, ENGLISH_HOTKEY_ID, mods, key)
        return (mods, key)

    def create_translation_hotkey(self):
        mods = win32con.MOD_ALT
        key = ord('W')
        ctypes.windll.user32.RegisterHotKey(self.hwnd, TRANSLATION_HOTKEY_ID, mods, key)
        return (mods, key)

    def create_arabic_hotkey(self):
        mods = win32con.MOD_ALT
        key = ord('A')
        ctypes.windll.user32.RegisterHotKey(self.hwnd, ARABIC_HOTKEY_ID, mods, key)
        return (mods, key)

    def unregister_hotkeys(self):
        """Unregisters all hotkeys to clean up."""
        ctypes.windll.user32.UnregisterHotKey(self.hwnd, ENGLISH_HOTKEY_ID)
        ctypes.windll.user32.UnregisterHotKey(self.hwnd, TRANSLATION_HOTKEY_ID)
        ctypes.windll.user32.UnregisterHotKey(self.hwnd, ARABIC_HOTKEY_ID)

    def handle_native_event(self, event_type, message):
        """
        Processes native Windows events to detect hotkey presses.
        """
        if event_type == "windows_generic_MSG":
            msg = wintypes.MSG.from_address(message.__int__())

            if msg.message == win32con.WM_HOTKEY:
                if ENGLISH_HOTKEY_ID == msg.wParam:
                    self.parent_window.hotkey_pressed.emit("english")
                    return True, 0
                elif TRANSLATION_HOTKEY_ID == msg.wParam:
                    self.parent_window.hotkey_pressed.emit("translation")
                    return True, 0
                elif ARABIC_HOTKEY_ID == msg.wParam:
                    self.parent_window.hotkey_pressed.emit("arabic")
                    return True, 0
        return False, 0