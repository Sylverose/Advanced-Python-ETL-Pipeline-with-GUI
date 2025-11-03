"""
Modular Database Manager - Main orchestration class for database operations.
Uses specialized utility modules for focused responsibilities.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from contextlib import contextmanager

# Core database imports
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

# Optional imports with graceful fallbacks
try:
    from logging_system import get_database_logger, performance_context
    LOGGING_SYSTEM_AVAILABLE = True
except ImportError:
    LOGGING_SYSTEM_AVAILABLE = False

try:
    from .pandas_optimizer import PandasOptimizer
    PANDAS_OPTIMIZER_AVAILABLE = True
except ImportError:
    PANDAS_OPTIMIZER_AVAILABLE = False
from .utilities import ConfigUtils, DataUtils, safe_operation
from .batch_operations import BatchProcessor  
from .csv_operations import CSVImporter
from .schema_manager import SCHEMA_DEFINITIONS, TABLE_COLUMNS

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages database connections with proper connection handling."""
    
    def __init__(self, config: Dict = None):
        self.config = config or ConfigUtils.get_env_config()
        if not self.config:
            self.config = {'user': 'root', 'password': '', 'host': '127.0.0.1', 'database': 'store_manager'}
    
    def create_connection(self):
        """Creates and returns a database connection"""
        try:
            if PYMYSQL_AVAILABLE:
                return pymysql.connect(**self.config)
            else:
                logger.error("No MySQL connector available")
                return None
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper cleanup"""
        conn = None
        try:
            conn = self.create_connection()
            if conn:
                yield conn
            else:
                yield None
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            logger.error(f"Connection error: {e}")
            yield None
        finally:
            if conn:
                try:
                    conn.commit()
                    conn.close()
                except:
                    pass
    
    def create_database_if_not_exists(self, database_name: str = None) -> bool:
        """Create database if it doesn't exist."""
        try:
            db_name = database_name or self.config.get('database', 'store_manager')
            temp_config = self.config.copy()
            temp_config.pop('database', None)
            
            # Connect without specifying database
            try:
                if PYMYSQL_AVAILABLE:
                    conn = pymysql.connect(**temp_config)
                else:
                    logger.error("No MySQL connector available")
                    return False
            except Exception as e:
                logger.error(f"Failed to connect to MySQL server: {e}")
                return False
            
            cursor = conn.cursor()
            try:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                cursor.execute(f"USE {db_name}")
                conn.commit()
                logger.info(f"Database '{db_name}' ready")
                return True
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error(f"Database creation error: {e}")
            return False


class DatabaseManager:
    """
    Modular database manager - orchestrates specialized components.
    
    Key responsibilities:
    - Connection management
    - Component coordination 
    - High-level database operations
    """
    
    def __init__(self, config: Dict = None, data_dir: Path = None, logger = None):
        self.connection_manager = ConnectionManager(config)
        
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / 'data'
        self.data_dir = data_dir
        
        # Set up logging
        if logger:
            self.logger = logger
        elif LOGGING_SYSTEM_AVAILABLE:
            self.logger = get_database_logger()
        else:
            import logging
            self.logger = logging.getLogger(__name__)
        
        # Initialize specialized processors
        self.batch_processor = BatchProcessor(self.connection_manager)
        
        # Use the imported TABLE_COLUMNS for CSVImporter
        self.csv_importer = CSVImporter(
            self.connection_manager, 
            self.data_dir, 
            TABLE_COLUMNS, 
            batch_size=1000
        )
        
        # Initialize optimizer if available
        self.optimizer = PandasOptimizer() if PANDAS_OPTIMIZER_AVAILABLE else None
    
    def _execute_single_query(self, query: str, params=None, fetch_one=False):
        """Execute a single query and return result(s). Reduces duplication of connection handling."""
        with self.connection_manager.get_connection() as conn:
            if not conn:
                return None
            
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchone() if fetch_one else cursor.fetchall()
                return result
            except Exception as e:
                self.logger.error(f"Query execution failed: {e}")
                return None
            finally:
                cursor.close()
    
    def _execute_multiple_queries(self, queries: List[str]):
        """Execute multiple queries in sequence within a single connection."""
        with self.connection_manager.get_connection() as conn:
            if not conn:
                return False
            
            cursor = conn.cursor()
            try:
                for query in queries:
                    cursor.execute(query)
                cursor.close()
                return True
            except Exception as e:
                self.logger.error(f"Batch query execution failed: {e}")
                return False
    
    def get_db_info(self) -> Dict[str, Any]:
        """Returns database information and available features"""
        version_result = self._execute_single_query("SELECT VERSION()", fetch_one=True)
        version = version_result[0] if version_result else "Unknown"
        
        return {
            'status': 'connected' if version_result else 'disconnected',
            'version': version,
            'features': {
                'PYMYSQL_AVAILABLE': PYMYSQL_AVAILABLE,
                'pandas_optimizer': self.optimizer is not None,
                'batch_processor': True,
                'csv_importer': True
            }
        }
    
    def create_database_if_not_exists(self, database_name: str = None) -> bool:
        """Create database if it doesn't exist. Delegates to connection manager."""
        return self.connection_manager.create_database_if_not_exists(database_name)
    
    def create_tables(self) -> bool:
        """Creates all tables based on schema definitions"""
        if not SCHEMA_DEFINITIONS:
            self.logger.warning("No schema definitions available")
            return False
        
        queries = list(SCHEMA_DEFINITIONS.values())
        success = self._execute_multiple_queries(queries)
        
        if success:
            self.logger.info(f"Created {len(SCHEMA_DEFINITIONS)} tables")
        else:
            self.logger.error("Failed to create tables")
        
        return success
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a table"""
        try:
            columns = self._execute_single_query(f"DESCRIBE {table_name}")
            row_count = self._execute_single_query(f"SELECT COUNT(*) FROM {table_name}", fetch_one=True)
            
            if columns and row_count:
                return {
                    'name': table_name,
                    'columns': columns,
                    'row_count': row_count[0],
                    'schema': SCHEMA_DEFINITIONS.get(table_name, "Not available")
                }
            return None
        except Exception as e:
            self.logger.error(f"Failed to get table info for {table_name}: {e}")
            return None
    
    def get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        try:
            result = self._execute_single_query(f"SELECT COUNT(*) FROM {table_name}", fetch_one=True)
            if result:
                return result[0]
            return -1
        except Exception as e:
            self.logger.debug(f"Failed to get row count for {table_name}: {e}")
            return -1
    
    def import_csv_data(self, csv_file_path: str, table_name: str, 
                       progress_callback=None, batch_size: int = 1000) -> Dict[str, Any]:
        """Import data from CSV file using CSVImporter"""
        return self.csv_importer.import_csv(
            csv_file_path=csv_file_path,
            table_name=table_name, 
            progress_callback=progress_callback,
            batch_size=batch_size
        )
    
    def export_table_to_csv(self, table_name: str, output_path: str, 
                           batch_size: int = 10000) -> Dict[str, Any]:
        """Export table data to CSV file using chunked processing"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with self.connection_manager.get_connection() as conn:
                if not conn:
                    return {"status": "error", "message": "Database connection failed"}
                
                # Get total row count
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_rows = cursor.fetchone()[0]
                
                if total_rows == 0:
                    return {"status": "warning", "message": "Table is empty"}
                
                # Export in chunks
                import pandas as pd
                first_chunk = True
                exported_rows = 0
                
                for offset in range(0, total_rows, batch_size):
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}")
                    columns = [desc[0] for desc in cursor.description]
                    chunk_data = cursor.fetchall()
                    
                    if chunk_data:
                        chunk_df = pd.DataFrame(chunk_data, columns=columns)
                        
                        # Optimize if available
                        if self.optimizer:
                            chunk_df = self.optimizer.optimize_dataframe(chunk_df)
                        
                        # Write to CSV
                        mode = 'w' if first_chunk else 'a'
                        header = first_chunk
                        chunk_df.to_csv(output_file, mode=mode, header=header, index=False)
                        
                        exported_rows += len(chunk_df)
                        first_chunk = False
                
                cursor.close()
                
                return {
                    "status": "success",
                    "table": table_name,
                    "output_file": str(output_file),
                    "rows_exported": exported_rows,
                    "total_rows": total_rows
                }
                
        except Exception as e:
            self.logger.error(f"CSV export failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        result = self._execute_single_query("SHOW TABLES")
        return [table[0] for table in result] if result else []
    
    def validate_connection(self) -> bool:
        """Validate database connection"""
        result = self._execute_single_query("SELECT 1", fetch_one=True)
        return result is not None
    
    # Convenience delegation methods - delegate directly to batch processor
    def insert_batch(self, table_name: str, data: List[Dict], progress_callback=None, batch_size: int = 1000):
        """Insert batches - delegates to BatchProcessor"""
        return self.batch_processor.insert_batch(table_name, data, progress_callback)
    
    def update_batch(self, table_name: str, data: List[Dict], key_columns: List[str], progress_callback=None, batch_size: int = 1000):
        """Update batches - delegates to BatchProcessor"""  
        return self.batch_processor.update_batch(table_name, data, key_columns, progress_callback)
    
    def upsert_batch(self, table_name: str, data: List[Dict], key_columns: List[str], progress_callback=None, batch_size: int = 1000):
        """Upsert batches - delegates to BatchProcessor"""
        return self.batch_processor.upsert_batch(table_name, data, key_columns, progress_callback)
    
    # Get processing statistics
    def get_stats(self) -> Dict:
        """Get combined processing statistics"""
        return {
            'batch_processor': self.batch_processor.get_stats(),
            'csv_importer': self.csv_importer.get_stats() if hasattr(self.csv_importer, 'get_stats') else {}
        }
    
    def cleanup(self):
        """Cleanup resources"""
        # Individual components handle their own cleanup
        pass

    # Legacy compatibility methods for existing GUI and API
    def create_all_tables(self) -> bool:
        """Legacy compatibility - same as create_tables"""
        return self.create_tables()
    
    def create_all_tables_from_csv(self) -> bool:
        """Create all tables and import CSV data in one operation."""
        try:
            # Step 1: Create tables
            if not self.create_tables():
                self.logger.error("Failed to create tables")
                return False
            
            # Step 2: Import all CSV data
            csv_files = self.csv_files
            if not csv_files:
                self.logger.warning("No CSV files found to import")
                return False
            
            success = self.csv_importer.import_all_csv_data(csv_files)
            if success:
                self.logger.info("All tables created and CSV data imported successfully")
            else:
                self.logger.warning("Tables created but CSV import had issues")
            
            return success
        
        except Exception as e:
            self.logger.error(f"Failed to create all tables from CSV: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Legacy compatibility - same as validate_connection"""
        return self.validate_connection()
    
    def get_table_counts(self) -> Dict[str, int]:
        """Get row counts for all tables efficiently"""
        counts = {}
        tables = self.get_all_tables()
        
        for table_name in tables:
            result = self._execute_single_query(f"SELECT COUNT(*) FROM {table_name}", fetch_one=True)
            counts[table_name] = result[0] if result else 0
        
        return counts
    
    def close(self):
        """Close connections - handled by connection manager"""
        pass
    
    @property
    def csv_files(self) -> Dict[str, Path]:
        """Get mapping of table names to CSV file paths"""
        csv_files = {}
        csv_dir = self.data_dir / 'CSV'
        
        for table_name in TABLE_COLUMNS.keys():
            csv_file = csv_dir / f"{table_name}.csv"
            if csv_file.exists():
                csv_files[table_name] = csv_file
        
        return csv_files
    
    def read_csv_file(self, csv_path: Path):
        """Read CSV file using the CSV importer"""
        try:
            return self.csv_importer._read_csv_optimized(csv_path)
        except Exception as e:
            self.logger.error(f"Failed to read CSV file {csv_path}: {e}")
            return None
    
    def export_api_data_to_csv(self) -> bool:
        """Export API data to CSV files"""
        try:
            from .data_from_api import export_api_data_to_csv
            output_dir = str(self.data_dir / 'API')
            return export_api_data_to_csv(output_dir=output_dir)
        except Exception as e:
            self.logger.error(f"Failed to export API data to CSV: {e}")
            return False


# Factory function for easy initialization
def create_database_manager(config: Dict = None) -> DatabaseManager:
    """Create a database manager with default settings."""
    return DatabaseManager(config)


# Main function for CLI usage
def main():
    """Main function for command-line usage."""
    db = create_database_manager()
    
    print("🔧 Testing Database Manager...")
    
    if db.validate_connection():
        print("✅ Database connection successful")
        
        info = db.get_db_info()
        print(f"📊 Database version: {info.get('version', 'Unknown')}")
        print(f"🔧 Features: {list(info.get('features', {}).keys())}")
        
        if db.create_tables():
            print("✅ Tables created successfully")
            
            tables = db.get_all_tables()
            print(f"📋 Available tables: {len(tables)}")
            for table in tables:
                print(f"   - {table}")
        else:
            print("❌ Failed to create tables")
    else:
        print("❌ Database connection failed")
    
    stats = db.get_stats()
    print(f"📈 Statistics: {stats}")


if __name__ == "__main__":
    main()