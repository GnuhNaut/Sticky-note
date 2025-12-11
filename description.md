# Role
Act as a Senior Python Developer with 10+ years of experience in GUI development using PyQt6. You are an expert in creating high-performance, memory-efficient, and aesthetically modern desktop applications.

# Project Goal
Create a complete "Sticky Notes" application named "FloatNote" for Windows/macOS. The app allows users to create floating notes that stay on top of other windows (Picture-in-Picture mode) but can be manually minimized when playing games or watching full-screen videos.

# Tech Stack & Requirements
- **Language:** Python 3.10+
- **GUI Framework:** PyQt6 (Must use `PyQt6.QtWidgets`, `PyQt6.QtGui`, `PyQt6.QtCore`).
- **Storage:** Local JSON file (for offline, fast access, and easy debugging).
- **Style:** Modern Flat Design using QSS (Qt Style Sheets). NO native OS title bars. Use Frameless Window with a custom toolbar/header.

# Core Features (Constraints)
1. **Floating Window:**
   - Notes must support `Qt.WindowType.WindowStaysOnTopHint`.
   - Provide a "Pin/Unpin" toggle button to enable/disable "Always on Top" (Crucial for gaming/fullscreen scenarios).
2. **Rich Text Editor:**
   - Support: Title, Bold, Italic, Underline, Font Size, Text Color, Highlight Color.
   - Embed images (optional but preferred if performance allows).
3. **Multi-Window Management:**
   - Allow opening multiple notes simultaneously.
   - Each note runs in its own instance/window but managed by a single Main Controller.
4. **Persistence:**
   - Auto-save content, position, size, and color of each note to `notes.json`.
   - Restore all notes exactly where they were upon restarting the app.
5. **System Integration:**
   - Option to "Start with Windows/macOS".
6. **UI/UX (Crucial):**
   - **Colors:** Pastel palette (Yellow, Blue, Green, Pink) for note backgrounds.
   - **Design:** Clean, minimalist, rounded corners, custom scrollbars.
   - **Performance:** Use event-driven programming. Debounce save operations to avoid disk I/O lag.

# File Structure
Please generate the full code for the following structure:
1. `requirements.txt`: Dependencies.
2. `main.py`: Entry point & Application Controller (manages tray icon and global state).
3. `note_window.py`: The GUI logic for a single note instance (Frameless window logic here).
4. `storage.py`: Singleton class for JSON read/write operations.
5. `styles.py` or `styles.qss`: String variables for CSS styling to ensure a beautiful look.

# Implementation Steps
1. Setup the `Storage` class to handle data safely.
2. Create the `NoteWindow` with a custom title bar (drag to move) and content area.
3. Implement the Rich Text logic in the toolbar.
4. Implement the `Main` logic to load saved notes on startup.
5. Ensure code is PEP8 compliant, modular, includes type hinting, and docstrings.

Let's build this step-by-step. Start by generating the complete file structure and code.