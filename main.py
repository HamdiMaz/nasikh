# main.py

import sys
from src.nasikh import Nasikh
from PySide6.QtCore import QLockFile, QDir


def main():
    """Main function to run the Dictation Application."""
    LOCK_FILE_NAME = "nasikh.lock"
    # Create a lock file in the system's temporary directory
    lock_file_path = QDir.tempPath() + "/" + LOCK_FILE_NAME
    lock_file = QLockFile(lock_file_path)

    # Attempt to lock the file
    if not lock_file.lock():
        sys.exit(0)
    
    dictation = Nasikh()
    dictation.run()


if __name__ == "__main__":
    main()