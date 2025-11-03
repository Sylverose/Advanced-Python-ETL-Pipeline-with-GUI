"""Main window module with component imports"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox

try:
    from qt_material import apply_stylesheet
    QT_MATERIAL_AVAILABLE = True
except ImportError:
    QT_MATERIAL_AVAILABLE = False

from .worker import ETLWorker
from .window import ETLMainWindow

__all__ = ['ETLWorker', 'ETLMainWindow', 'main']


def main():
    """Main application entry point"""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("ETL Pipeline Manager")
    app.setOrganizationName("ETL Solutions")
    app.setApplicationVersion("2.0")
    
    app.setStyle('Fusion')
    
    if QT_MATERIAL_AVAILABLE:
        apply_stylesheet(app, theme='dark_cyan.xml')
    else:
        print("qt-material not available, using default styling")
    
    try:
        window = ETLMainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        print(f"Fatal error: {e}")
        QMessageBox.critical(None, "Fatal Error", f"Failed to start application:\n{e}")
        return 1
