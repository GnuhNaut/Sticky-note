import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer

from storage import Storage
from note_window import NoteWindow


def get_resource_path(filename):
    """Get path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


class FloatNoteApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.storage = Storage()
        self.windows = {}
        
        self.setup_tray()
        self.load_existing_notes()
        
        if not self.windows:
            self.create_new_note()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app)
        
        # Load custom icon
        icon_path = get_resource_path("logo.ico")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Fallback to PNG
            png_path = get_resource_path("logo.png")
            if os.path.exists(png_path):
                icon = QIcon(png_path)
            else:
                style = self.app.style()
                icon = style.standardIcon(style.StandardPixmap.SP_FileIcon)
        
        self.tray_icon.setIcon(icon)
        self.app.setWindowIcon(icon)

        
        menu = QMenu()
        
        new_note_action = QAction("New Note", self.app)
        new_note_action.triggered.connect(self.create_new_note)
        menu.addAction(new_note_action)
        
        show_all_action = QAction("Show All", self.app)
        show_all_action.triggered.connect(self.show_all_notes)
        menu.addAction(show_all_action)
        
        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def load_existing_notes(self):
        notes_data = self.storage.load_notes()
        for note in notes_data:
            self.create_note_window(note)

    def create_new_note(self):
        self.create_note_window()

    def create_note_window(self, note_data=None):
        window = NoteWindow(note_data)
        window.closed.connect(self.on_note_closed)
        window.new_note.connect(self.create_new_note)
        window.show()
        self.windows[window.note_id] = window

    def on_note_closed(self, note_id):
        if note_id in self.windows:
            # The window is already closed and deleted from storage by the window itself
            # We just need to remove the reference
            del self.windows[note_id]

    def show_all_notes(self):
        for window in self.windows.values():
            window.show()
            window.raise_()

    def quit_app(self):
        # Save all states one last time (though they auto-save)
        for window in self.windows.values():
            window.save_note()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = FloatNoteApp()
    controller.run()
