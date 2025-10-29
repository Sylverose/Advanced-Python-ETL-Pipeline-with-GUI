"""
ETL Pipeline GUI Interface using PySide6
Optimized version with improved performance, error handling, and maintainability
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import partial

# Prevent Python cache files from being created
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QTextEdit, QLabel, QLineEdit,
                               QGroupBox, QGridLayout, QMessageBox, QFileDialog,
                               QProgressBar, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSettings
from PySide6.QtGui import QFont, QIcon, QTextCursor

try:
    from qt_material import apply_stylesheet
    QT_MATERIAL_AVAILABLE = True
except ImportError:
    QT_MATERIAL_AVAILABLE = False

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
DATA_PATH = PROJECT_ROOT / "data"
CSV_PATH = DATA_PATH / "CSV"
API_PATH = DATA_PATH / "API"

# Add the src directory to the path to import our modules
sys.path.insert(0, str(SRC_PATH))

# Module imports with graceful error handling
MODULES_AVAILABLE = True
try:
    from db_manager import DatabaseManager
    from connect import mysql_connection, config
    from data_from_api import APIClient
except ImportError as e:
    print(f"Warning: Could not import ETL modules: {e}")
    MODULES_AVAILABLE = False
    DatabaseManager = None


class ETLWorker(QThread):
    """Optimized worker thread for ETL operations with better error handling"""
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(str)
    data_ready = Signal(dict)  # For passing structured data back
    
    def __init__(self, operation: str, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False
    
    def cancel(self):
        """Cancel the current operation"""
        self._is_cancelled = True
        
    def run(self):
        """Main execution method with operation routing"""
        if not MODULES_AVAILABLE and self.operation != "select_csv_files":
            self.error.emit("ETL modules not available")
            return
            
        operation_map = {
            "test_connection": self._test_connection,
            "test_api": self._test_api,
            "create_tables": self._create_tables,
            "load_csv": self._load_csv,
            "load_api": self._load_api,
            "select_csv_files": self._select_csv_files
        }
        
        try:
            if self.operation in operation_map:
                operation_map[self.operation]()
            else:
                self.error.emit(f"Unknown operation: {self.operation}")
        except Exception as e:
            self.error.emit(f"Error in {self.operation}: {str(e)}")
    
    def _test_connection(self):
        """Test database connection"""
        self.progress.emit("Testing database connection...")
        db_manager = DatabaseManager()
        with mysql_connection(config) as conn:
            if conn and not self._is_cancelled:
                self.finished.emit("Database connection successful!")
            else:
                self.error.emit("Failed to connect to database")
    
    def _test_api(self):
        """Test API connection"""
        api_url = self.args[0]
        self.progress.emit(f"Testing API connection to: {api_url}")
        try:
            api_client = APIClient(api_url)
            test_data = api_client.fetch_data('orders') if not self._is_cancelled else None
            api_client.close()
            
            if test_data is not None:
                self.finished.emit(f"API connection successful! Found {len(test_data)} records")
            else:
                self.error.emit("API connection failed - no data received")
        except Exception as e:
            self.error.emit(f"API connection failed: {str(e)}")
    
    def _create_tables(self):
        """Create database tables"""
        self.progress.emit("Creating database tables...")
        db_manager = DatabaseManager()
        
        if not self._is_cancelled:
            success = db_manager.create_database_if_not_exists()
            if success and not self._is_cancelled:
                csv_success = db_manager.create_all_tables_from_csv()
                result = "All database tables created successfully!" if csv_success else "Failed to create some tables"
                (self.finished if csv_success else self.error).emit(result)
            else:
                self.error.emit("Failed to create database")
    
    def _load_csv(self):
        """Load CSV data"""
        self.progress.emit("Loading CSV data...")
        db_manager = DatabaseManager()
        success = db_manager.create_all_tables_from_csv()
        
        if success and not self._is_cancelled:
            # Get counts for each table
            table_counts = {table: db_manager.get_row_count(table) 
                          for table in db_manager.csv_files.keys()}
            
            summary = "\n".join([f"  {table}: {count} rows" for table, count in table_counts.items()])
            self.finished.emit(f"CSV data loaded successfully!\n{summary}")
            self.data_ready.emit(table_counts)
        else:
            self.error.emit("Failed to load CSV data")
    
    def _load_api(self):
        """Load API data"""
        api_url = self.args[0]
        self.progress.emit(f"Loading API data from: {api_url}")
        try:
            api_client = APIClient(api_url)
            csv_success = api_client.save_all_api_data_to_csv(str(API_PATH))
            api_client.close()
            
            if csv_success and not self._is_cancelled:
                self.finished.emit(f"API data exported to CSV files in {API_PATH}")
            else:
                self.error.emit("Failed to export API data to CSV")
        except Exception as e:
            self.error.emit(f"Failed to load API data: {str(e)}")
    
    def _select_csv_files(self):
        """Handle CSV file selection and copying"""
        selected_files = self.args[0]
        CSV_PATH.mkdir(parents=True, exist_ok=True)
        
        copied_files = []
        for file_path in selected_files:
            if self._is_cancelled:
                break
                
            try:
                src_path = Path(file_path)
                dest_path = CSV_PATH / src_path.name
                shutil.copy2(src_path, dest_path)
                copied_files.append(src_path.name)
                self.progress.emit(f"Copied: {src_path.name}")
            except Exception as e:
                self.progress.emit(f"Failed to copy {Path(file_path).name}: {str(e)}")
        
        if copied_files:
            self.finished.emit(f"Successfully copied {len(copied_files)} files to CSV folder:\n" + 
                             "\n".join([f"  - {f}" for f in copied_files]))
        else:
            self.error.emit("No files were copied successfully")


class ETLMainWindow(QMainWindow):
    """Optimized main window with improved architecture and performance"""
    
    def __init__(self):
        super().__init__()
        self.current_worker: Optional[ETLWorker] = None
        self.selected_csv_files: List[str] = []
        self.settings = QSettings("ETL Solutions", "ETL Pipeline Manager")
        
        self._setup_ui()
        self._load_settings()
        self._initialize_status()
    
    def _setup_ui(self):
        """Set up the user interface with optimized layout"""
        self.setWindowTitle("ETL Pipeline Manager")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget with splitter for better layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Use splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(splitter)
        
        # Control panel
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # Title with improved styling
        self._create_title_section(controls_layout)
        
        # Control groups
        self._create_api_section(controls_layout)
        self._create_database_section(controls_layout)
        self._create_file_section(controls_layout)
        self._create_data_section(controls_layout)
        self._create_test_section(controls_layout)
        
        # Theme toggle section
        self._create_theme_section(controls_layout)
        
        # Progress bar with enhanced styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                text-align: center;
                background-color: #f8f9fa;
                color: #495057;
                font-weight: bold;
                font-size: 10px;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d6efd, stop: 1 #6610f2);
                border-radius: 6px;
                margin: 2px;
            }
        """)
        controls_layout.addWidget(self.progress_bar)
        
        # Output section
        output_widget = self._create_output_section()
        
        # Add to splitter
        splitter.addWidget(controls_widget)
        splitter.addWidget(output_widget)
        splitter.setSizes([400, 300])  # Initial size distribution
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_title_section(self, layout: QVBoxLayout):
        """Create optimized title section"""
        title_label = QLabel("ETL Pipeline Manager")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #0d6efd;
                margin: 15px;
                padding: 10px;
                border-radius: 8px;
                background-color: rgba(13, 110, 253, 0.1);
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)
    
    def _create_api_section(self, layout: QVBoxLayout):
        """Create API configuration section"""
        api_group = QGroupBox("API Configuration")
        api_layout = QHBoxLayout(api_group)
        
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("Enter API URL (e.g., https://etl-server.fly.dev)")
        self.api_url_input.setText(self.settings.value("api_url", "https://etl-server.fly.dev"))
        self.api_url_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #0d6efd;
                border-radius: 6px;
                padding: 10px 15px;
                background-color: #ffffff;
                color: #495057;
                font-size: 11px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
                border-color: #0b5ed7;
                background-color: #f8f9ff;
            }
        """)
        
        self.load_api_btn = QPushButton("Test")
        self.load_api_btn.clicked.connect(self.test_api_connection)
        self.load_api_btn.setFixedWidth(80)
        
        api_layout.addWidget(QLabel("API URL:"))
        api_layout.addWidget(self.api_url_input)
        api_layout.addWidget(self.load_api_btn)
        
        layout.addWidget(api_group)
    
    def _create_database_section(self, layout: QVBoxLayout):
        """Create database operations section"""
        db_group = QGroupBox("Database Operations")
        db_layout = QGridLayout(db_group)
        
        self.test_conn_btn = QPushButton("Test Connection")
        self.test_conn_btn.clicked.connect(self.test_db_connection)
        
        self.create_tables_btn = QPushButton("Create Tables")
        self.create_tables_btn.clicked.connect(self.create_tables)
        
        db_layout.addWidget(self.test_conn_btn, 0, 0)
        db_layout.addWidget(self.create_tables_btn, 0, 1)
        
        layout.addWidget(db_group)
    
    def _create_file_section(self, layout: QVBoxLayout):
        """Create file management section"""
        file_group = QGroupBox("File Management")
        file_layout = QGridLayout(file_group)
        
        self.select_csv_btn = QPushButton("Select CSV Files")
        self.select_csv_btn.clicked.connect(self.select_csv_files)
        
        self.load_selected_files_btn = QPushButton("Load Selected Files")
        self.load_selected_files_btn.clicked.connect(self.load_selected_files)
        self.load_selected_files_btn.setEnabled(False)  # Disabled until files are selected
        
        self.selected_files_label = QLabel("No files selected")
        self.selected_files_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-style: italic;
                padding: 8px 12px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                font-size: 10px;
            }
        """)
        
        file_layout.addWidget(self.select_csv_btn, 0, 0)
        file_layout.addWidget(self.load_selected_files_btn, 0, 1)
        file_layout.addWidget(self.selected_files_label, 1, 0, 1, 2)  # Span across both columns
        
        layout.addWidget(file_group)
    
    def _create_data_section(self, layout: QVBoxLayout):
        """Create data loading section"""
        data_group = QGroupBox("Data Loading")
        data_layout = QGridLayout(data_group)
        
        self.load_csv_btn = QPushButton("Load CSV Data")
        self.load_csv_btn.clicked.connect(self.load_csv_data)
        
        self.load_api_data_btn = QPushButton("Load API Data")
        self.load_api_data_btn.clicked.connect(self.load_api_data)
        
        data_layout.addWidget(self.load_csv_btn, 0, 0)
        data_layout.addWidget(self.load_api_data_btn, 0, 1)
        
        layout.addWidget(data_group)
    
    def _create_test_section(self, layout: QVBoxLayout):
        """Create test operations section"""
        test_group = QGroupBox("Test Operations")
        test_layout = QGridLayout(test_group)
        
        self.test_csv_btn = QPushButton("Test CSV Access")
        self.test_csv_btn.clicked.connect(self.test_csv_access)
        
        self.test_api_export_btn = QPushButton("Test API Export")
        self.test_api_export_btn.clicked.connect(self.test_api_export)
        
        test_layout.addWidget(self.test_csv_btn, 0, 0)
        test_layout.addWidget(self.test_api_export_btn, 0, 1)
        
        layout.addWidget(test_group)
    
    def _create_theme_section(self, layout: QVBoxLayout):
        """Create theme toggle section"""
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QHBoxLayout(theme_group)
        
        self.theme_toggle_btn = QPushButton("Toggle Dark Theme")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        self.theme_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        theme_layout.addWidget(self.theme_toggle_btn)
        theme_layout.addStretch()  # Push button to the left
        
        layout.addWidget(theme_group)
    
    def _create_output_section(self) -> QWidget:
        """Create optimized output section"""
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        output_label = QLabel("Output:")
        output_label.setFont(QFont("Arial", 10, QFont.Bold))
        output_layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                color: #212529;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 9px;
                line-height: 1.5;
                selection-background-color: #0d6efd;
                selection-color: #ffffff;
            }
            QTextEdit:focus {
                border-color: #0d6efd;
                outline: none;
            }
        """)
        output_layout.addWidget(self.output_text)
        
        return output_widget
    
    def _load_settings(self):
        """Load user settings"""
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Load and apply saved theme (default to dark)
        self.is_dark_theme = self.settings.value("theme/dark_mode", True, type=bool)
        self._apply_theme(self.is_dark_theme)
    
    def _save_settings(self):
        """Save user settings"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("api_url", self.api_url_input.text())
    
    def _initialize_status(self):
        """Initialize application status"""
        self.append_output("ETL Pipeline Manager initialized.")
        self.append_output("Ready for operations.")
        
        if MODULES_AVAILABLE:
            self.append_output("ETL modules loaded successfully")
        else:
            self.append_output("WARNING: ETL modules not available - limited functionality")
            self._disable_etl_buttons()
    
    def _apply_theme(self, dark_mode: bool = False):
        """Apply light or dark theme using qt-material"""
        if QT_MATERIAL_AVAILABLE:
            app = QApplication.instance()
            if dark_mode:
                apply_stylesheet(app, theme='dark_cyan.xml')
                self.theme_toggle_btn.setText("Toggle Light Theme")
            else:
                apply_stylesheet(app, theme='light_blue.xml')
                self.theme_toggle_btn.setText("Toggle Dark Theme")
        else:
            # Fallback if qt-material is not available
            if dark_mode:
                self.setStyleSheet("QMainWindow { background-color: #2b2b2b; color: #ffffff; }")
                self.theme_toggle_btn.setText("Toggle Light Theme")
            else:
                self.setStyleSheet("")  # Use default light theme
                self.theme_toggle_btn.setText("Toggle Dark Theme")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark_theme = not self.is_dark_theme
        
        # Save theme preference
        self.settings.setValue("theme/dark_mode", self.is_dark_theme)
        
        # Apply theme
        self._apply_theme(self.is_dark_theme)
        
        # Update the interface immediately
        self.update()
        self.repaint()
        
        # Provide feedback
        theme_name = "dark" if self.is_dark_theme else "light"
        self.append_output(f"Switched to {theme_name} theme")
    
    def _disable_etl_buttons(self):
        """Disable ETL-related buttons when modules are unavailable"""
        buttons = [self.test_conn_btn, self.create_tables_btn, self.load_csv_btn, 
                  self.load_api_data_btn, self.load_api_btn, self.test_csv_btn, 
                  self.test_api_export_btn]
        for button in buttons:
            button.setEnabled(False)
    
    def append_output(self, text: str):
        """Optimized output appending with auto-scroll and formatting"""
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Add timestamp for better tracking
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {text}"
        
        cursor.insertText(formatted_text + "\n")
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()
    
    def show_error(self, title: str, message: str):
        """Show optimized error dialog"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    def show_info(self, title: str, message: str):
        """Show optimized info dialog"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    def _start_operation(self, operation: str, *args, operation_name: str = None, **kwargs):
        """Unified method to start operations with consistent error handling"""
        if self.current_worker and self.current_worker.isRunning():
            self.show_error("Operation In Progress", "Please wait for the current operation to complete.")
            return
        
        if not operation_name:
            operation_name = operation.replace("_", " ").title()
        
        self.statusBar().showMessage(f"Starting {operation_name}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Disable relevant buttons during operation
        self._set_buttons_enabled(False)
        
        self.current_worker = ETLWorker(operation, *args, **kwargs)
        self.current_worker.progress.connect(self.append_output)
        self.current_worker.finished.connect(
            partial(self._on_operation_finished, operation_name)
        )
        self.current_worker.error.connect(
            partial(self._on_operation_error, operation_name)
        )
        if hasattr(self.current_worker, 'data_ready'):
            self.current_worker.data_ready.connect(self._on_data_ready)
        
        self.current_worker.start()
    
    def _set_buttons_enabled(self, enabled: bool):
        """Enable/disable all operation buttons"""
        buttons = [self.test_conn_btn, self.create_tables_btn, self.load_csv_btn, 
                  self.load_api_data_btn, self.load_api_btn, self.test_csv_btn, 
                  self.test_api_export_btn, self.select_csv_btn, self.load_selected_files_btn]
        for button in buttons:
            if MODULES_AVAILABLE or button in [self.select_csv_btn, self.load_selected_files_btn]:
                button.setEnabled(enabled)
    
    def _on_operation_finished(self, operation_name: str, message: str):
        """Optimized operation completion handler"""
        self.append_output(f"COMPLETED: {operation_name}: {message}")
        self.statusBar().showMessage(f"{operation_name} completed successfully")
        self._cleanup_operation()
    
    def _on_operation_error(self, operation_name: str, message: str):
        """Optimized operation error handler"""
        self.append_output(f"ERROR: {operation_name} failed: {message}")
        self.statusBar().showMessage(f"{operation_name} failed")
        self.show_error(f"{operation_name} Error", message)
        self._cleanup_operation()
    
    def _on_data_ready(self, data: Dict[str, Any]):
        """Handle structured data from worker threads"""
        # Can be used for updating UI with specific data
        pass
    
    def _cleanup_operation(self):
        """Clean up after operation completion"""
        self.progress_bar.setVisible(False)
        self._set_buttons_enabled(True)
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
    
    def closeEvent(self, event):
        """Handle application close with cleanup"""
        # Cancel any running operations
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait(3000)  # Wait up to 3 seconds
        
        # Save settings
        self._save_settings()
        event.accept()
    
    # Optimized operation methods using the unified starter
    def test_db_connection(self):
        """Test database connection using optimized method"""
        self._start_operation("test_connection", operation_name="Database Connection Test")
    
    def test_api_connection(self):
        """Test API connection using optimized method"""
        api_url = self.api_url_input.text().strip()
        if not api_url:
            self.show_error("Input Error", "Please enter an API URL")
            return
        
        # Save API URL to settings
        self.settings.setValue("api_url", api_url)
        self._start_operation("test_api", api_url, operation_name="API Connection Test")
    
    def create_tables(self):
        """Create database tables using optimized method"""
        self._start_operation("create_tables", operation_name="Table Creation")
    
    def load_csv_data(self):
        """Load CSV data using optimized method"""
        self._start_operation("load_csv", operation_name="CSV Data Loading")
    
    def load_api_data(self):
        """Load API data using optimized method"""
        api_url = self.api_url_input.text().strip()
        if not api_url:
            self.show_error("Input Error", "Please enter an API URL")
            return
        
        self._start_operation("load_api", api_url, operation_name="API Data Loading")
    
    def select_csv_files(self):
        """Select CSV files and store for later loading"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("CSV Files (*.csv);;All Files (*)")
        file_dialog.setWindowTitle("Select CSV Files")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                self.selected_csv_files = file_paths  # Store the selected files
                file_names = [Path(fp).name for fp in file_paths]
                self.selected_files_label.setText(f"{len(file_paths)} files selected: {', '.join(file_names[:3])}{' ...' if len(file_names) > 3 else ''}")
                self.load_selected_files_btn.setEnabled(True)  # Enable the Load button
                self.append_output(f"Selected {len(file_paths)} CSV files (ready to load)")
            else:
                self.selected_files_label.setText("No files selected")
                self.load_selected_files_btn.setEnabled(False)
                self.selected_csv_files = []
    
    def load_selected_files(self):
        """Load the selected CSV files to the data folder"""
        if not self.selected_csv_files:
            self.show_error("No Files Selected", "Please select CSV files first")
            return
        
        self._start_operation("select_csv_files", self.selected_csv_files, operation_name="Loading Selected Files")
    
    def test_csv_access(self):
        """Optimized CSV file access test"""
        self.append_output("Testing CSV file access...")
        
        if not MODULES_AVAILABLE:
            self.append_output("ERROR: Database modules not available")
            return
        
        try:
            db_manager = DatabaseManager()
            self.append_output(f"Data directory: {db_manager.data_dir}")
            
            # Test reading each CSV file
            for table_name, csv_file in db_manager.csv_files.items():
                try:
                    df = db_manager.read_csv_file(csv_file)
                    if df is not None:
                        self.append_output(f"SUCCESS: {table_name}: {len(df)} rows, {len(df.columns)} columns - {csv_file}")
                    else:
                        self.append_output(f"FAILED: {table_name}: Failed to read {csv_file}")
                except Exception as e:
                    self.append_output(f"ERROR: {table_name}: Error - {e}")
            
            self.append_output("CSV access test completed!")
        except Exception as e:
            self.append_output(f"ERROR: Error in CSV access test: {e}")
        
        self.statusBar().showMessage("CSV test completed")
    
    def test_api_export(self):
        """Optimized API data export test"""
        self.append_output("Testing API data export...")
        
        if not MODULES_AVAILABLE:
            self.append_output("ERROR: Database modules not available")
            return
        
        try:
            db_manager = DatabaseManager()
            success = db_manager.export_api_data_to_csv()
            
            if success:
                self.append_output("SUCCESS: API data export successful!")
                
                # Check created files efficiently
                if API_PATH.exists():
                    csv_files = list(API_PATH.glob("*.csv"))
                    if csv_files:
                        self.append_output(f"Found {len(csv_files)} CSV files:")
                        for file_path in sorted(csv_files):
                            size = file_path.stat().st_size
                            self.append_output(f"  {file_path.name:<20} ({size:,} bytes)")
                    else:
                        self.append_output("ERROR: No CSV files found in API directory")
                else:
                    self.append_output("ERROR: API directory does not exist")
            else:
                self.append_output("ERROR: API data export failed")
        except Exception as e:
            self.append_output(f"ERROR: Error in API export test: {e}")
        
        self.statusBar().showMessage("API export test completed")


def main():
    """Optimized main application entry point"""
    # Application setup
    app = QApplication(sys.argv)
    app.setApplicationName("ETL Pipeline Manager")
    app.setOrganizationName("ETL Solutions")
    app.setApplicationVersion("2.0")
    
    # Set application style and properties
    app.setStyle('Fusion')
    
    # Apply qt-material grey theme by default
    if QT_MATERIAL_AVAILABLE:
        apply_stylesheet(app, theme='dark_cyan.xml')
    else:
        print("qt-material not available, using default styling")
    
    # Error handling for the main window
    try:
        window = ETLMainWindow()
        window.show()
        
        # Handle application exit
        return app.exec()
    except Exception as e:
        print(f"Fatal error: {e}")
        QMessageBox.critical(None, "Fatal Error", f"Failed to start application:\n{e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
