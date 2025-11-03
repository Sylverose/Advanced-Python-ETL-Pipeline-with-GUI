"""
Dark Theme Implementation - Modern dark theme with cyan accents
"""

from .base_theme import BaseTheme


class DarkTheme(BaseTheme):
    """Dark theme with cyan accents and modern styling"""
    
    def __init__(self):
        super().__init__("Dark Theme")
    
    def get_qt_material_theme(self) -> str:
        return 'dark_cyan.xml'
    
    def get_button_text(self) -> str:
        return "Toggle Light Theme"
    
    def _get_component_styles(self) -> str:
        """Shared component styles used by both custom and fallback"""
        return """
            QLabel[objectName="title_label"] {
                color: #0d6efd; font-weight: bold; font-size: 16px;
                margin: 10px 0; padding: 10px 15px; border-radius: 8px;
                background-color: rgba(13, 110, 253, 0.2); border: 2px solid #0d6efd;
            }
            QPushButton { height: 50px; min-height: 50px; }
            QPushButton[objectName="load_api_btn"] { min-width: 80px; }
            QPushButton[objectName="select_csv_btn"] { min-width: 140px; }
            QLineEdit[objectName="api_url_input"] {
                border: 2px solid #555; border-radius: 6px; padding: 10px 15px;
                background-color: #2b2b2b; color: #fff; font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit[objectName="api_url_input"]:focus {
                border-color: #0d6efd; background-color: #1a1a1a;
            }
            QLabel[objectName="selected_files_label"] {
                color: #999; font-style: italic; padding: 8px 12px; font-size: 10px;
                background-color: #3c3c3c; border: 1px solid #555; border-radius: 6px;
            }
            QProgressBar[objectName="progress_bar"] {
                border: 2px solid #555; border-radius: 8px;
                background-color: #3c3c3c; height: 25px;
            }
            QProgressBar[objectName="progress_bar"]::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0d6efd, stop:1 #0b5ed7); border-radius: 6px;
            }
            QPushButton[objectName="theme_toggle_btn"] {
                background-color: #404040; color: #fff; border: 1px solid #555;
                border-radius: 4px; padding: 6px 12px; font-weight: 600; font-size: 10px;
            }
            QPushButton[objectName="theme_toggle_btn"]:hover { background-color: #505050; }
            QPushButton[objectName="theme_toggle_btn"]:pressed { background-color: #2b2b2b; }
            QTextEdit[objectName="output_text"] {
                background-color: #2b2b2b; border: 2px solid #555; border-radius: 8px;
                padding: 15px; color: #fff; font-size: 9px; line-height: 1.5;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                selection-background-color: #0d6efd; selection-color: #fff;
            }
            QTextEdit[objectName="output_text"]:focus {
                border-color: #0d6efd; outline: none;
            }
            QGroupBox {
                background-color: #3c3c3c; border: 1px solid #555; border-radius: 8px;
                margin-top: 8px; padding-top: 25px; color: #fff; font-weight: bold;
            }
            QGroupBox::title {
                color: #fff; subcontrol-origin: padding; left: 10px; top: 8px;
                subcontrol-position: top left; padding: 8px 12px;
            }
            QPushButton[objectName="load_selected_files_btn"] {
                background-color: #505050; color: #999; border: 2px solid #666;
                padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 10px;
            }
            QPushButton[objectName="load_selected_files_btn"]:enabled {
                background-color: #0d6efd; color: #fff; border: 2px solid #0b5ed7;
            }
            QPushButton[objectName="load_selected_files_btn"]:enabled:hover {
                background-color: #0b5ed7; border: 2px solid #0a58ca;
            }
            QPushButton[objectName="load_selected_files_btn"]:enabled:pressed {
                background-color: #0a58ca; border: 2px solid #084298;
            }
        """
    
    def get_custom_styles(self) -> str:
        return self._get_component_styles()
    
    def get_fallback_styles(self) -> str:
        return f"""
            QMainWindow {{ background-color: #2b2b2b; color: #fff; }}
            {self._get_component_styles()}
        """