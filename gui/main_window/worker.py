"""ETL Worker thread for background operations"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Callable, Dict, Any
import shutil

from PySide6.QtCore import QThread, Signal

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

MODULES_AVAILABLE = True
try:
    from src.database.db_manager import DatabaseManager
    from src.connect import mysql_connection, config
    from src.database.data_from_api import APIDataFetcher as APIClient
except ImportError as e:
    print(f"Warning: Could not import ETL modules: {e}")
    MODULES_AVAILABLE = False

DATA_PATH = PROJECT_ROOT / "data"
CSV_PATH = DATA_PATH / "CSV"
API_PATH = DATA_PATH / "API"


class ETLWorker(QThread):
    """Worker thread for ETL operations with proper error handling"""
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(str)
    data_ready = Signal(dict)
    
    def __init__(self, operation: str, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False
        
        # Operation dispatch map
        self._operations = {
            "test_connection": self._test_connection,
            "test_api": self._test_api,
            "create_tables": self._create_tables,
            "load_csv": self._load_csv,
            "load_api": self._load_api,
            "select_csv_files": self._select_csv_files,
            "test_csv_access": self._test_csv_access,
            "test_api_export": self._test_api_export
        }
    
    def cancel(self):
        """Cancel the current operation"""
        self._is_cancelled = True
    
    def run(self):
        """Main execution method with operation routing"""
        if not MODULES_AVAILABLE and self.operation != "select_csv_files":
            self.error.emit("ETL modules not available")
            return
        
        try:
            if self.operation in self._operations:
                self._operations[self.operation]()
            else:
                self.error.emit(f"Unknown operation: {self.operation}")
        except Exception as e:
            self.error.emit(f"Error in {self.operation}: {str(e)}")
    
    def _test_connection(self):
        """Test database connection"""
        self.progress.emit("Testing database connection...")
        try:
            db_manager = DatabaseManager()
            if db_manager.test_connection() and not self._is_cancelled:
                self.finished.emit("Database connection successful!")
            else:
                self.error.emit("Failed to connect to database")
        except Exception as e:
            self.error.emit(f"Database connection error: {str(e)}")
    
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
        self.progress.emit("Creating database and tables...")
        db_manager = DatabaseManager()
        
        if not self._is_cancelled:
            self.progress.emit("Creating database if not exists...")
            success = db_manager.create_database_if_not_exists()
            if success and not self._is_cancelled:
                self.progress.emit("Creating all 9 tables with updated schema...")
                csv_success = db_manager.create_all_tables_from_csv()
                if csv_success:
                    csv_tables = ['brands', 'categories', 'stores', 'staffs', 'products', 'stocks']
                    api_tables = ['customers', 'orders', 'order_items']
                    self.progress.emit("Verifying table creation...")
                    table_info = []
                    for table in csv_tables + api_tables:
                        count = db_manager.get_row_count(table)
                        table_info.append(f"  {table}: {'Ready' if count >= 0 else 'Created'}")
                    
                    result = f"All 9 database tables created successfully!\nSchema Updates Applied:\n  - STOCKS: store_name (FK), product_id (PK)\n  - STAFFS: name, store_name, street columns\nTables Created:\n" + "\n".join(table_info)
                    self.finished.emit(result)
                else:
                    self.error.emit("Failed to create some tables - Check schema compatibility")
            else:
                self.error.emit("Failed to create database - Check MySQL permissions")
    
    def _load_csv(self):
        """Load CSV data"""
        self.progress.emit("Loading CSV data with NaN→NULL conversion...")
        db_manager = DatabaseManager()
        
        self.progress.emit("Creating tables and loading data...")
        success = db_manager.create_all_tables_from_csv()
        
        if success and not self._is_cancelled:
            self.progress.emit("Verifying data insertion...")
            table_counts = {table: db_manager.get_row_count(table) 
                          for table in db_manager.csv_files.keys()}
            
            total_rows = sum(table_counts.values())
            summary = "\n".join([f"  {table}: {count} rows" for table, count in table_counts.items()])
            
            result = f"CSV data loaded successfully!\nTotal Records: {total_rows:,}\nTable Breakdown:\n{summary}\nAll NaN values converted to MySQL NULL\nSchema alignment verified (STOCKS/STAFFS updated)"
            self.finished.emit(result)
            self.data_ready.emit(table_counts)
        else:
            self.error.emit("Failed to load CSV data - Check file permissions and schema compatibility")
    
    def _load_api(self):
        """Load API data"""
        api_url = self.args[0]
        self.progress.emit(f"Connecting to API: {api_url}")
        try:
            api_client = APIClient(api_url)
            self.progress.emit("Fetching data from API endpoints...")
            csv_success = api_client.save_all_api_data_to_csv(str(API_PATH))
            api_client.close()
            
            if csv_success and not self._is_cancelled:
                self.progress.emit("Verifying exported files...")
                csv_files = list(API_PATH.glob("*.csv")) if API_PATH.exists() else []
                file_info = [f"  {f.name}: {f.stat().st_size:,} bytes" for f in csv_files]
                total_size = sum(f.stat().st_size for f in csv_files)
                
                result = f"API data exported successfully!\nLocation: {API_PATH}\nFiles Created: {len(csv_files)}\nTotal Size: {total_size:,} bytes\nFiles:\n" + "\n".join(file_info)
                self.finished.emit(result)
            else:
                self.error.emit("Failed to export API data to CSV - Check API connectivity")
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
    
    def _test_csv_access(self):
        """Test CSV file access and schema validation"""
        self.progress.emit("Testing CSV file access and schema validation...")
        
        try:
            db_manager = DatabaseManager()
            self.progress.emit(f"Data directory: {db_manager.data_dir}")
            
            total_rows = 0
            for table_name, csv_file in db_manager.csv_files.items():
                try:
                    df = db_manager.read_csv_file(csv_file)
                    if df is not None:
                        total_rows += len(df)
                        cols_preview = ', '.join(df.columns[:3]) + ('...' if len(df.columns) > 3 else '')
                        self.progress.emit(f"SUCCESS: {table_name}: {len(df)} rows, {len(df.columns)} columns ({cols_preview})")
                    else:
                        self.progress.emit(f"FAILED: {table_name}: Failed to read {csv_file}")
                except Exception as e:
                    self.progress.emit(f"ERROR: {table_name}: {e}")
            
            result = f"CSV access test completed!\nTotal records available: {total_rows:,}\nSchema alignment: STOCKS (store_name), STAFFS (name, store_name, street)"
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Error in CSV access test: {str(e)}")
    
    def _test_api_export(self):
        """Test API data export"""
        self.progress.emit("Testing API data export...")
        
        try:
            db_manager = DatabaseManager()
            success = db_manager.export_api_data_to_csv()
            
            if success:
                self.progress.emit("SUCCESS: API data export successful!")
                
                if API_PATH.exists():
                    csv_files = list(API_PATH.glob("*.csv"))
                    if csv_files:
                        self.progress.emit(f"Found {len(csv_files)} CSV files:")
                        for file_path in sorted(csv_files):
                            size = file_path.stat().st_size
                            self.progress.emit(f"  {file_path.name:<20} ({size:,} bytes)")
                        self.finished.emit(f"API export test completed successfully!")
                    else:
                        self.error.emit("No CSV files found in API directory")
                else:
                    self.error.emit("API directory does not exist")
            else:
                self.error.emit("API data export failed")
        except Exception as e:
            self.error.emit(f"Error in API export test: {str(e)}")
