"""
Light Theme Implementation
Clean, professional light theme with white sections and grey accents
"""

from .base_theme import BaseTheme


class LightTheme(BaseTheme):
    """Light theme with white sections and professional styling"""
    
    def __init__(self):
        super().__init__("Light Theme")
    
    def get_qt_material_theme(self) -> str:
        """Return the qt-material theme name for light mode"""
        return 'light_blue.xml'
    
    def get_button_text(self) -> str:
        """Return button text for theme toggle"""
        return "Toggle Dark Theme"
    
    def get_custom_styles(self) -> str:
        """Return custom CSS styles for light theme"""
        return """
            QGroupBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 25px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #666;
                subcontrol-origin: padding;
                subcontrol-position: top left;
                padding: 8px 12px;
                left: 10px;
                top: 8px;
            }
            QPushButton[objectName="load_selected_files_btn"] {
                border: 2px solid #cccccc;
                color: #cccccc;
            }
        """
    
    def get_fallback_styles(self) -> str:
        """Return fallback styles if qt-material is not available"""
        return """
            QMainWindow {
                background-color: #ffffff;
                color: #333333;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 25px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #666;
                subcontrol-origin: padding;
                subcontrol-position: top left;
                padding: 8px 12px;
                left: 10px;
                top: 8px;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 16px;
                color: #495057;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton[objectName="load_selected_files_btn"] {
                border: 2px solid #cccccc;
                color: #cccccc;
            }
        """