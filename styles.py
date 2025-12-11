class Colors:
    PASTEL_YELLOW = "#FFF7D1"
    PASTEL_BLUE = "#E2F0FB"
    PASTEL_GREEN = "#E2FBE2"
    PASTEL_PINK = "#FBE2E2"
    
    TEXT_DARK = "#333333"
    TOOLBAR_BG = "rgba(255, 255, 255, 0.5)"
    BORDER = "#CCCCCC"

class Styles:
    NOTE_WINDOW = """
        QMainWindow {{
            background-color: {bg_color};
            border-radius: 10px;
            border: 1px solid {border_color};
        }}
        QWidget#centralWidget {{
            background-color: {bg_color};
            border-radius: 10px;
        }}
    """
    
    TOOLBAR = """
        QFrame {{
            background-color: {toolbar_bg};
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }}
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }}
        QPushButton:hover {{
            background-color: rgba(0,0,0,0.1);
        }}
    """
    
    EDITOR = """
        QTextEdit {{
            background-color: transparent;
            border: none;
            color: {text_color};
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            padding: 10px;
        }}
    """
    
    SCROLLBAR = """
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: rgba(0,0,0,0.2);
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """
