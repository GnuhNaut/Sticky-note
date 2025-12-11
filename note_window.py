import uuid
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QFrame, QMenu,
                             QApplication, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import (QAction, QFont, QTextCharFormat, QColor, QCursor,
                         QTextListFormat, QKeyEvent, QPainter, QPen)

from styles import Styles, Colors
from storage import Storage


class ResizeGrip(QWidget):
    """Custom resize grip for frameless window."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.parent_window = parent
        self.drag_start = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        for i in range(3):
            x = self.width() - 4 - i * 4
            y = self.height() - 4 - i * 4
            painter.drawLine(x, self.height() - 2, self.width() - 2, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = event.globalPosition().toPoint()
            self.initial_size = self.parent_window.size()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_start and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_start
            new_width = max(200, self.initial_size.width() + delta.x())
            new_height = max(150, self.initial_size.height() + delta.y())
            self.parent_window.resize(new_width, new_height)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_start = None
        self.parent_window.schedule_save()


class NoteEditor(QTextEdit):
    """Custom editor that removes link formatting on Enter."""
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            fmt = cursor.charFormat()
            if fmt.isAnchor():
                fmt.setAnchor(False)
                fmt.setAnchorHref("")
                fmt.setForeground(QColor(Colors.TEXT_DARK))
                fmt.setFontUnderline(False)
                cursor.setCharFormat(fmt)
                self.setTextCursor(cursor)
        super().keyPressEvent(event)


class NoteWindow(QMainWindow):
    closed = pyqtSignal(str)
    new_note = pyqtSignal()

    def __init__(self, note_data=None):
        super().__init__()
        self.storage = Storage()
        self.drag_pos = None
        
        if note_data:
            self.note_id = note_data.get('id')
            self.content = note_data.get('content', '')
            self.bg_color = note_data.get('color', Colors.PASTEL_YELLOW)
            self.is_pinned = note_data.get('pinned', False)
            rect = note_data.get('geometry')
            if rect:
                self.setGeometry(*rect)
            else:
                self.resize(300, 350)
        else:
            self.note_id = str(uuid.uuid4())
            self.content = ""
            self.bg_color = Colors.PASTEL_YELLOW
            self.is_pinned = False
            self.resize(300, 350)

        self.setup_ui()
        self.apply_styles()
        
        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.auto_save)

        # Style update timer
        self.style_update_timer = QTimer()
        self.style_update_timer.setSingleShot(True)
        self.style_update_timer.timeout.connect(self.update_style_buttons)

    def setup_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(200, 150)

        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(40)
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(8, 0, 8, 0)
        self.toolbar_layout.setSpacing(2)
        
        self.toolbar.mousePressEvent = self.toolbar_mouse_press
        self.toolbar.mouseMoveEvent = self.toolbar_mouse_move
        self.toolbar.mouseReleaseEvent = self.toolbar_mouse_release

        # Buttons
        self.add_toolbar_button("+", self.new_note_requested, "New Note")
        self.add_separator()
        
        self.bold_btn = self.add_toolbar_button("B", self.toggle_bold, "Bold")
        self.italic_btn = self.add_toolbar_button("I", self.toggle_italic, "Italic")
        self.underline_btn = self.add_toolbar_button("U", self.toggle_underline, "Underline")
        self.add_separator()
        self.heading_btn = self.add_toolbar_button("H", self.toggle_heading, "Heading")
        self.list_btn = self.add_toolbar_button("•", self.toggle_list, "Bullet List")
        self.add_separator()
        self.add_toolbar_button("🔗", self.insert_link, "Insert Link")
        self.add_separator()
        self.add_toolbar_button("🎨", self.change_color, "Change Color")
        
        self.pin_btn = self.add_toolbar_button("📌", self.toggle_pin, "Pin/Unpin")
        self.update_pin_style()

        self.toolbar_layout.addStretch()
        
        # Clear button
        self.add_toolbar_button("🗑", self.clear_note, "Clear")
        
        self.add_toolbar_button("✕", self.close_note, "Close")

        self.layout.addWidget(self.toolbar)

        # Editor
        self.editor = NoteEditor()
        self.editor.setHtml(self.content)
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.schedule_style_update)
        self.editor.setAcceptRichText(True)
        self.layout.addWidget(self.editor)

        # Resize grip
        self.resize_grip = ResizeGrip(self)
        self.position_resize_grip()

    def position_resize_grip(self):
        self.resize_grip.move(
            self.width() - self.resize_grip.width(),
            self.height() - self.resize_grip.height()
        )

    def resizeEvent(self, event):
        self.position_resize_grip()
        self.schedule_save()
        super().resizeEvent(event)

    def add_toolbar_button(self, text, callback, tooltip=""):
        btn = QPushButton(text)
        btn.setFixedSize(28, 28)
        btn.clicked.connect(callback)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            btn.setToolTip(tooltip)
        self.toolbar_layout.addWidget(btn)
        return btn

    def add_separator(self):
        sep = QFrame()
        sep.setFixedSize(1, 20)
        sep.setStyleSheet("background-color: rgba(0,0,0,0.1);")
        self.toolbar_layout.addWidget(sep)

    def apply_styles(self):
        self.central_widget.setStyleSheet(f"""
            QWidget#centralWidget {{
                background-color: {self.bg_color};
                border-radius: 10px;
                border: 1px solid {Colors.BORDER};
            }}
        """)
        self.toolbar.setStyleSheet(Styles.TOOLBAR.format(
            toolbar_bg=Colors.TOOLBAR_BG
        ))
        self.editor.setStyleSheet(Styles.EDITOR.format(
            text_color=Colors.TEXT_DARK
        ) + Styles.SCROLLBAR)

    # Style updates
    def schedule_style_update(self):
        self.style_update_timer.start(50)

    def update_style_buttons(self):
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        
        is_bold = fmt.fontWeight() == QFont.Weight.Bold
        self._set_button_active(self.bold_btn, is_bold)
        
        is_italic = fmt.fontItalic()
        self._set_button_active(self.italic_btn, is_italic)
        
        is_underline = fmt.fontUnderline()
        self._set_button_active(self.underline_btn, is_underline)
        
        font_size = fmt.fontPointSize()
        is_heading = font_size >= 18
        self._set_button_active(self.heading_btn, is_heading)
        
        is_list = cursor.currentList() is not None
        self._set_button_active(self.list_btn, is_list)

    def _set_button_active(self, btn, active):
        if active:
            btn.setStyleSheet("background-color: rgba(0,0,0,0.25); border-radius: 4px; font-weight: bold;")
        else:
            btn.setStyleSheet("")

    # Window Dragging
    def toolbar_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def toolbar_mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def toolbar_mouse_release(self, event):
        self.drag_pos = None
        self.schedule_save()

    # Actions
    def new_note_requested(self):
        self.new_note.emit()

    def toggle_bold(self):
        fmt = QTextCharFormat()
        cursor = self.editor.textCursor()
        current_weight = cursor.charFormat().fontWeight()
        new_weight = QFont.Weight.Normal if current_weight == QFont.Weight.Bold else QFont.Weight.Bold
        fmt.setFontWeight(new_weight)
        cursor.mergeCharFormat(fmt)
        self.editor.setTextCursor(cursor)
        self.update_style_buttons()

    def toggle_italic(self):
        fmt = QTextCharFormat()
        cursor = self.editor.textCursor()
        fmt.setFontItalic(not cursor.charFormat().fontItalic())
        cursor.mergeCharFormat(fmt)
        self.editor.setTextCursor(cursor)
        self.update_style_buttons()

    def toggle_underline(self):
        fmt = QTextCharFormat()
        cursor = self.editor.textCursor()
        fmt.setFontUnderline(not cursor.charFormat().fontUnderline())
        cursor.mergeCharFormat(fmt)
        self.editor.setTextCursor(cursor)
        self.update_style_buttons()

    def toggle_heading(self):
        cursor = self.editor.textCursor()
        fmt = QTextCharFormat()
        current_size = cursor.charFormat().fontPointSize()
        if current_size == 0:
            current_size = 14
        
        if current_size >= 18:
            fmt.setFontPointSize(14)
            fmt.setFontWeight(QFont.Weight.Normal)
        else:
            fmt.setFontPointSize(20)
            fmt.setFontWeight(QFont.Weight.Bold)
        
        cursor.mergeCharFormat(fmt)
        self.editor.setTextCursor(cursor)
        self.update_style_buttons()

    def toggle_list(self):
        cursor = self.editor.textCursor()
        current_list = cursor.currentList()
        
        if current_list:
            block_fmt = cursor.blockFormat()
            block_fmt.setIndent(0)
            cursor.setBlockFormat(block_fmt)
            current_list.remove(cursor.block())
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.Style.ListDisc)
            list_fmt.setIndent(1)
            cursor.createList(list_fmt)
        
        self.editor.setTextCursor(cursor)
        self.update_style_buttons()

    def insert_link(self):
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        
        url, ok = QInputDialog.getText(self, "Insert Link", "Enter URL:", text="https://")
        if ok and url:
            if not selected_text:
                selected_text = url
            
            fmt = QTextCharFormat()
            fmt.setAnchor(True)
            fmt.setAnchorHref(url)
            fmt.setForeground(QColor("#0066cc"))
            fmt.setFontUnderline(True)
            
            cursor.insertText(selected_text, fmt)
            self.editor.setTextCursor(cursor)

    def change_color(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(0,0,0,0.1);
            }
        """)
        
        color_map = {
            "Yellow": Colors.PASTEL_YELLOW,
            "Blue": Colors.PASTEL_BLUE,
            "Green": Colors.PASTEL_GREEN,
            "Pink": Colors.PASTEL_PINK
        }
        
        for name, color in color_map.items():
            action = QAction(f"● {name}", self)
            action.setData(color)
            action.triggered.connect(self.on_color_action_triggered)
            menu.addAction(action)
        
        menu.exec(QCursor.pos())

    def on_color_action_triggered(self):
        action = self.sender()
        if action:
            color = action.data()
            self.set_bg_color(color)

    def set_bg_color(self, color):
        self.bg_color = color
        self.apply_styles()
        self.schedule_save()

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        flags = Qt.WindowType.FramelessWindowHint
        if self.is_pinned:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.update_pin_style()
        self.schedule_save()

    def update_pin_style(self):
        if self.is_pinned:
            self.pin_btn.setStyleSheet("background-color: rgba(0,0,0,0.25); border-radius: 4px;")
        else:
            self.pin_btn.setStyleSheet("")

    def clear_note(self):
        """Clear content and delete from storage."""
        self.editor.clear()
        self.content = ""
        self.storage.delete_note(self.note_id)

    def close_note(self):
        self.close()
        self.closed.emit(self.note_id)

    # Persistence
    def has_content(self):
        """Check if editor has real content (not just empty HTML)."""
        plain_text = self.editor.toPlainText().strip()
        return len(plain_text) > 0

    def on_text_changed(self):
        self.content = self.editor.toHtml()
        self.schedule_save()

    def schedule_save(self):
        self.save_timer.stop()
        self.save_timer.start(500)

    def auto_save(self):
        """Auto-save only if there's content."""
        if self.has_content():
            self._do_save()
        else:
            # No content - remove from storage
            self.storage.delete_note(self.note_id)

    def _do_save(self):
        note_data = {
            'id': self.note_id,
            'content': self.content,
            'color': self.bg_color,
            'pinned': self.is_pinned,
            'geometry': [self.x(), self.y(), self.width(), self.height()]
        }
        notes = self.storage.load_notes()
        existing = False
        for i, n in enumerate(notes):
            if n.get('id') == self.note_id:
                notes[i] = note_data
                existing = True
                break
        if not existing:
            notes.append(note_data)
        self.storage.save_all(notes)
