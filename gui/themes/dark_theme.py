"""
Dark Theme Implementation
Modern dark theme with cyan accents
"""

from .base_theme import BaseTheme


class DarkTheme(BaseTheme):
    """Dark theme with cyan accents and modern styling"""
    
    def __init__(self):
        super().__init__("Dark Theme")
    
    def get_qt_material_theme(self) -> str:
        """Return the qt-material theme name for dark mode"""
        return 'dark_cyan.xml'
    
    def get_button_text(self) -> str:
        """Return button text for theme toggle"""
        return "Toggle Light Theme"
    
    def get_custom_styles(self) -> str:
        """Return custom CSS styles for dark theme"""
        return """
            QGroupBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 25px;
                color: #ffffff;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: padding;
                subcontrol-position: top left;
                padding: 8px 12px;
                left: 10px;
                top: 8px;
            }
        """
    
    def get_fallback_styles(self) -> str:
        """Return fallback styles if qt-material is not available"""
        return """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 25px;
                color: #ffffff;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: padding;
                subcontrol-position: top left;
                padding: 8px 12px;
                left: 10px;
                top: 8px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """