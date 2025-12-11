import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer

from storage import Storage
from note_window import NoteWindow

class FloatNoteApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False) # Keep app running in tray
        
        self.storage = Storage()
        self.windows = {} # Store references to keep windows alive
        
        self.setup_tray()
        self.load_existing_notes()
        
        # If no notes exist, create one
        if not self.windows:
            self.create_new_note()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app)
        # We need an icon. For now, let's use a standard system icon or create a simple pixmap
        # Since we don't have an image file, let's try to use a standard icon if possible, 
        # or just run without a specific icon image (might be invisible on some systems).
        # Better: Create a simple generated icon or use a standard one.
        # PyQt6 doesn't have built-in standard icons easily accessible for tray without QStyle.
        # Let's use a standard warning icon as a placeholder or just text if possible (Tray doesn't support text only).
        # We will try to load a system icon.
        style = self.app.style()
        icon = style.standardIcon(style.StandardPixmap.SP_FileIcon)
        self.tray_icon.setIcon(icon)
        
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
