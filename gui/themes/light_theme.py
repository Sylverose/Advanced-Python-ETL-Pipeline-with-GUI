"""
Light Theme Implementation - Clean, professional light theme
"""

from .base_theme import BaseTheme


class LightTheme(BaseTheme):
    """Light theme with white sections and professional styling"""
    
    def __init__(self):
        super().__init__("Light Theme")
    
    def get_qt_material_theme(self) -> str:
        return 'light_blue.xml'
    
    def get_button_text(self) -> str:
        return "Toggle Dark Theme"
    
    def _get_component_styles(self) -> str:
        """Shared component styles used by both custom and fallback"""
        return """
            QLabel[objectName="title_label"] {
                color: #0d6efd; font-weight: bold; font-size: 16px;
                margin: 10px 0; padding: 10px 15px; border-radius: 8px;
                background-color: rgba(13, 110, 253, 0.1); border: 2px solid #90ee90;
            }
            QPushButton { height: 50px; min-height: 50px; }
            QPushButton[objectName="load_api_btn"] { min-width: 80px; }
            QPushButton[objectName="select_csv_btn"] { min-width: 140px; }
            QLineEdit[objectName="api_url_input"] {
                border: 2px solid #0d6efd; border-radius: 6px; padding: 10px 15px;
                background-color: #fff; color: #495057; font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit[objectName="api_url_input"]:focus {
                border-color: #0b5ed7; background-color: #f8f9ff;
            }
            QLabel[objectName="selected_files_label"] {
                color: #6c757d; font-style: italic; padding: 8px 12px; font-size: 10px;
                background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px;
            }
            QProgressBar[objectName="progress_bar"] {
                border: 2px solid #dee2e6; border-radius: 8px;
                background-color: #f8f9fa; height: 25px;
            }
            QProgressBar[objectName="progress_bar"]::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0d6efd, stop:1 #0b5ed7); border-radius: 6px;
            }
            QPushButton[objectName="theme_toggle_btn"] {
                background-color: #6c757d; color: #fff; border: 1px solid #5a6268;
                border-radius: 4px; padding: 6px 12px; font-weight: 600; font-size: 10px;
            }
            QPushButton[objectName="theme_toggle_btn"]:hover { background-color: #5a6268; }
            QPushButton[objectName="theme_toggle_btn"]:pressed { background-color: #495057; }
            QTextEdit[objectName="output_text"] {
                background-color: #fff; border: 2px solid #dee2e6; border-radius: 8px;
                padding: 15px; color: #212529; font-size: 9px; line-height: 1.5;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                selection-background-color: #0d6efd; selection-color: #fff;
            }
            QTextEdit[objectName="output_text"]:focus {
                border-color: #0d6efd; outline: none;
            }
            QGroupBox {
                background-color: #fff; border: 1px solid #ccc; border-radius: 8px;
                margin-top: 8px; padding-top: 25px; font-weight: bold;
            }
            QGroupBox::title {
                color: #666; subcontrol-origin: padding; left: 10px; top: 8px;
                subcontrol-position: top left; padding: 8px 12px;
            }
            QPushButton[objectName="load_selected_files_btn"] {
                background-color: #e9ecef; color: #6c757d; border: 2px solid #dee2e6;
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
            QMainWindow {{ background-color: #fff; color: #333; }}
            {self._get_component_styles()}
        """