"""
Enhanced Database Manager - compact version with reduced code duplication.
Maintains compatibility with existing ETL pipeline while dramatically reducing code size.
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from pathlib import Path
import sys
import os

# Try to import database modules with fallbacks
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

# Try to import connect module
try:
    from connect import mysql_connection, config, connect_to_mysql
    CONNECT_AVAILABLE = True
except ImportError:
    CONNECT_AVAILABLE = False
    config = {'user': 'root', 'password': '', 'host': '127.0.0.1', 'database': 'store_manager'}

# Import structured logging
try:
    from logging_system import get_database_logger, performance_context
    LOGGING_SYSTEM_AVAILABLE = True
except ImportError:
    LOGGING_SYSTEM_AVAILABLE = False

# Import pandas optimizer
try:
    from .pandas_optimizer import PandasOptimizer, optimize_csv_reading
    PANDAS_OPTIMIZER_AVAILABLE = True
except ImportError:
    PANDAS_OPTIMIZER_AVAILABLE = False
    optimize_csv_reading = None

logger = logging.getLogger(__name__)

# Inline utility functions to remove utils dependency
class DatabaseUtils:
    @staticmethod
    def batch_execute(cursor, sql: str, data: List, batch_size: int = 1000) -> int:
        total_affected = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(sql, batch)
            total_affected += cursor.rowcount
        return total_affected

class DataUtils:
    @staticmethod
    def clean_dataframe(df, null_replacements: Dict = None):
        if df is None:
            return None
        
        # Replace NaN values with None for MySQL compatibility
        import numpy as np
        df = df.replace({np.nan: None})
        
        # Replace inf values with None as well
        df = df.replace([np.inf, -np.inf], None)
        
        # Apply custom null replacements if provided
        if null_replacements:
            for column, replacement in null_replacements.items():
                if column in df.columns:
                    df[column] = df[column].fillna(replacement)
        
        return df
    
    @staticmethod
    def dataframe_to_records(df, table_schema: List[str] = None) -> List[Dict]:
        if df is None or df.empty:
            return []
        
        # Clean the dataframe first
        df = DataUtils.clean_dataframe(df)
        
        if table_schema:
            available_columns = [col for col in table_schema if col in df.columns]
            df = df[available_columns]
        
        # Convert to records and ensure no NaN values remain
        records = df.to_dict('records')
        
        # Additional cleanup to ensure no NaN values in the final records
        import math
        cleaned_records = []
        for record in records:
            cleaned_record = {}
            for key, value in record.items():
                # Check for NaN values (works for both numpy.nan and math.nan)
                if value is not None and not (isinstance(value, float) and math.isnan(value)):
                    cleaned_record[key] = value
                else:
                    cleaned_record[key] = None
            cleaned_records.append(cleaned_record)
        
        return cleaned_records

class ConfigUtils:
    @staticmethod
    def merge_configs(*configs: Dict) -> Dict:
        result = {}
        for cfg in configs:
            if cfg:
                result.update(cfg)
        return result
    
    @staticmethod
    def get_env_config(prefix: str = "DB_") -> Dict[str, str]:
        config = {}
        env_mapping = {
            f"{prefix}USER": "user", f"{prefix}PASSWORD": "password", 
            f"{prefix}HOST": "host", f"{prefix}PORT": "port", f"{prefix}NAME": "database"
        }
        for env_key, config_key in env_mapping.items():
            value = os.getenv(env_key)
            if value:
                config[config_key] = value
        return config

# Inline schema definitions
SCHEMA_DEFINITIONS = {
    'brands': "CREATE TABLE IF NOT EXISTS brands (brand_id INT PRIMARY KEY, brand_name VARCHAR(255) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    'categories': "CREATE TABLE IF NOT EXISTS categories (category_id INT PRIMARY KEY, category_name VARCHAR(255) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
    'stores': """CREATE TABLE IF NOT EXISTS stores (store_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, phone VARCHAR(20), 
                 email VARCHAR(255), street VARCHAR(255), city VARCHAR(100), state VARCHAR(50), zip_code VARCHAR(20)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    'staffs': """CREATE TABLE IF NOT EXISTS staffs (staff_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, 
                 email VARCHAR(255), phone VARCHAR(20), active BOOLEAN DEFAULT TRUE, store_name VARCHAR(255), street VARCHAR(255), manager_id INT, 
                 FOREIGN KEY (manager_id) REFERENCES staffs(staff_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    'products': """CREATE TABLE IF NOT EXISTS products (product_id INT PRIMARY KEY, product_name VARCHAR(255) NOT NULL, brand_id INT, category_id INT, 
                   model_year INT, list_price DECIMAL(10, 2), FOREIGN KEY (brand_id) REFERENCES brands(brand_id), 
                   FOREIGN KEY (category_id) REFERENCES categories(category_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    'stocks': """CREATE TABLE IF NOT EXISTS stocks (store_name VARCHAR(255), product_id INT, quantity INT DEFAULT 0, PRIMARY KEY (product_id, store_name), 
                 FOREIGN KEY (product_id) REFERENCES products(product_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    'orders': """CREATE TABLE IF NOT EXISTS orders (order_id INT PRIMARY KEY, customer_id INT NOT NULL, order_status INT NOT NULL, 
                 order_status_name VARCHAR(50), order_date DATE, required_date DATE, shipped_date DATE, staff_name VARCHAR(255), 
                 store VARCHAR(255), INDEX idx_customer_id (customer_id), INDEX idx_order_date (order_date), 
                 INDEX idx_order_status (order_status), INDEX idx_store (store)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    'order_items': """CREATE TABLE IF NOT EXISTS order_items (item_id INT PRIMARY KEY, order_id INT NOT NULL, product_id INT NOT NULL, 
                      quantity INT NOT NULL DEFAULT 1, list_price DECIMAL(10, 2) NOT NULL, discount DECIMAL(4, 2) DEFAULT 0.00, 
                      INDEX idx_order_id (order_id), INDEX idx_product_id (product_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    'customers': """CREATE TABLE IF NOT EXISTS customers (customer_id INT PRIMARY KEY, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, 
                    email VARCHAR(255) UNIQUE, phone VARCHAR(20), street VARCHAR(255), city VARCHAR(100), state VARCHAR(50), zip_code VARCHAR(20), 
                    INDEX idx_email (email), INDEX idx_state (state), INDEX idx_city (city)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
}

TABLE_COLUMNS = {
    'orders': ['order_id', 'customer_id', 'order_status', 'order_status_name', 'order_date', 'required_date', 'shipped_date', 'staff_name', 'store'],
    'order_items': ['item_id', 'order_id', 'product_id', 'quantity', 'list_price', 'discount'],
    'customers': ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'street', 'city', 'state', 'zip_code'],
    'brands': ['brand_id', 'brand_name'],
    'categories': ['category_id', 'category_name'],
    'stores': ['store_id', 'name', 'phone', 'email', 'street', 'city', 'state', 'zip_code'],
    'products': ['product_id', 'product_name', 'brand_id', 'category_id', 'model_year', 'list_price'],
    'staffs': ['staff_id', 'name', 'last_name', 'email', 'phone', 'active', 'store_name', 'street', 'manager_id'],
    'stocks': ['store_name', 'product_id', 'quantity']
}

@contextmanager
def safe_operation(operation_name: str, logger_instance=None):
    log = logger_instance or logger
    try:
        log.info(f"Starting {operation_name}")
        yield
        log.info(f"Completed {operation_name}")
    except Exception as e:
        log.error(f"Failed {operation_name}: {e}")
        raise


class BatchProcessor:
    """Simplified batch processor for compatibility."""
    
    def __init__(self, connection_manager, data_validator=None, batch_size=1000):
        self.connection_manager = connection_manager
        self.data_validator = data_validator
        self.batch_size = batch_size
        self.stats = {'processed': 0, 'errors': 0}
    
    def insert_batch(self, table_name: str, data: List[Dict], 
                    progress_callback=None, ignore_duplicates=True) -> Tuple[int, int]:
        """Insert data in batches."""
        if not data:
            return 0, 0
        
        with self.connection_manager.get_connection() as conn:
            if not conn:
                return 0, len(data)
            
            cursor = conn.cursor()
            inserted = DatabaseUtils.batch_execute(
                cursor, 
                self._generate_insert_sql(table_name, data[0], ignore_duplicates),
                [tuple(record.values()) for record in data]
            )
            cursor.close()
            
            self.stats['processed'] += inserted
            return inserted, len(data) - inserted
    
    def _generate_insert_sql(self, table_name: str, sample_record: Dict, ignore_duplicates: bool) -> str:
        """Generate INSERT SQL statement."""
        columns = list(sample_record.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        insert_type = "INSERT IGNORE" if ignore_duplicates else "INSERT"
        return f"{insert_type} INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    def get_stats(self) -> Dict:
        """Get processing statistics."""
        return self.stats.copy()


class DatabaseManager:
    """Enhanced database manager with minimal code duplication."""
    
    def __init__(self, config: Dict = None, data_dir: Path = None, logger_instance=None, 
                 enable_pooling: bool = True, pool_size: int = 5):
        # Setup dependencies - initialize before using
        self.deps = {
            'LOGGING_AVAILABLE': LOGGING_SYSTEM_AVAILABLE,
            'PYMYSQL_AVAILABLE': PYMYSQL_AVAILABLE,
            'MYSQL_AVAILABLE': MYSQL_AVAILABLE,
            'pymysql': pymysql if PYMYSQL_AVAILABLE else None,
            'mysql_connector': mysql.connector if MYSQL_AVAILABLE else None,
            'get_database_logger': (get_database_logger if LOGGING_SYSTEM_AVAILABLE 
                                   else lambda: logging.getLogger(__name__)),
            'pandas_optimizer': (PandasOptimizer() if PANDAS_OPTIMIZER_AVAILABLE else None),
            'optimize_csv_reading': optimize_csv_reading if PANDAS_OPTIMIZER_AVAILABLE else None
        }
        
        # Setup configuration  
        self.config = ConfigUtils.merge_configs(
            config,
            ConfigUtils.get_env_config(),
            {'user': 'root', 'host': '127.0.0.1', 'database': 'store_manager'}
        )
        
        # Setup paths
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / 'data'
        
        # Setup logging
        self.logger = (logger_instance or 
                      (self.deps['get_database_logger']() if self.deps['LOGGING_AVAILABLE'] 
                       else logging.getLogger(__name__)))
        
        # CSV file mapping with schema columns
        self.csv_files = {
            name: f"{name}.csv" for name in SCHEMA_DEFINITIONS.keys()
            if (self.data_dir / 'CSV' / f"{name}.csv").exists()
        }
        
        # Table schema mapping for compatibility
        self.table_columns = TABLE_COLUMNS
        
        # Connection (lazy-loaded)
        self._connection = None
        
        # Initialize batch processor for compatibility
        self.batch_processor = BatchProcessor(self, None)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        if not self._connection and self.deps['PYMYSQL_AVAILABLE']:
            try:
                self._connection = self.deps['pymysql'].connect(**self.config)
            except Exception as e:
                self.logger.error(f"Connection failed: {e}")
                yield None
                return
        
        try:
            yield self._connection
        finally:
            if self._connection:
                self._connection.commit()
    
    def create_all_tables(self) -> bool:
        """Create all database tables using compact schema definitions."""
        with safe_operation("table creation", self.logger):
            with self.get_connection() as conn:
                if not conn:
                    return False
                
                cursor = conn.cursor()
                
                # Get all table SQLs from compact schema
                table_sqls = SCHEMA_DEFINITIONS
                
                for table_name, sql in table_sqls.items():
                    try:
                        cursor.execute(sql)
                        self.logger.info(f"Created table: {table_name}")
                    except Exception as e:
                        self.logger.error(f"Failed to create {table_name}: {e}")
                        return False
                
                cursor.close()
                return True
    
    def import_csv_data(self) -> bool:
        """Import CSV data with batch processing."""
        with safe_operation("CSV import", self.logger):
            with self.get_connection() as conn:
                if not conn:
                    return False
                
                cursor = conn.cursor()
                import_order = ['brands', 'categories', 'stores', 'staffs', 'products', 'stocks']
                total_records = 0
                
                for table_name in import_order:
                    if table_name not in self.csv_files:
                        continue
                    
                    # Read and clean CSV
                    csv_path = self.data_dir / 'CSV' / self.csv_files[table_name]
                    df = self._read_csv_optimized(csv_path)
                    if df is None:
                        continue
                    
                    # Clean data and convert to records
                    df = DataUtils.clean_dataframe(df)
                    schema = TABLE_COLUMNS.get(table_name, [])
                    records = DataUtils.dataframe_to_records(df, schema)
                    
                    if not records:
                        continue
                    
                    # Batch insert
                    inserted = self._batch_insert(cursor, table_name, records)
                    total_records += inserted
                    self.logger.info(f"Imported {inserted} records to {table_name}")
                
                cursor.close()
                self.logger.info(f"Total records imported: {total_records}")
                return True
    
    def _read_csv_optimized(self, csv_path: Path):
        """Read CSV with optimization if available."""
        try:
            import pandas as pd
            
            # Use pandas optimizer if available
            if hasattr(self, 'deps') and self.deps.get('optimize_csv_reading'):
                return self.deps['optimize_csv_reading'](csv_path)
            else:
                return pd.read_csv(csv_path)
                
        except Exception as e:
            self.logger.error(f"Failed to read {csv_path}: {e}")
            return None
    
    def _batch_insert(self, cursor, table_name: str, records: List[Dict]) -> int:
        """Insert records in batches."""
        if not records:
            return 0
        
        # Generate INSERT SQL
        columns = list(records[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        sql = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Convert records to tuples
        data = [tuple(record[col] for col in columns) for record in records]
        
        # Batch execute
        return DatabaseUtils.batch_execute(cursor, sql, data)
    
    def test_connection(self) -> bool:
        """Test database connection."""
        with self.get_connection() as conn:
            return conn is not None
    
    def get_table_counts(self) -> Dict[str, int]:
        """Get row counts for all tables."""
        with self.get_connection() as conn:
            if not conn:
                return {}
            
            cursor = conn.cursor()
            counts = {}
            
            for table_name in SCHEMA_DEFINITIONS.keys():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    counts[table_name] = cursor.fetchone()[0]
                except:
                    counts[table_name] = 0
            
            cursor.close()
            return counts
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    # Compatibility methods for existing GUI and API
    def create_database_if_not_exists(self, database_name: str = None) -> bool:
        """Create database if it doesn't exist."""
        db_name = database_name or self.config.get('database', 'store_manager')
        
        try:
            # Connect without database specified
            config_no_db = self.config.copy()
            config_no_db.pop('database', None)
            
            if self.deps['PYMYSQL_AVAILABLE']:
                conn = self.deps['pymysql'].connect(**config_no_db)
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                cursor.close()
                conn.close()
                return True
        except Exception as e:
            self.logger.error(f"Failed to create database: {e}")
            return False
    
    def create_all_tables_from_csv(self) -> bool:
        """Compatibility method - same as create_all_tables."""
        return self.create_all_tables()
    
    def read_csv_file(self, csv_filename: str) -> Optional[Any]:
        """Read CSV file with optimization."""
        csv_path = self.data_dir / 'CSV' / csv_filename
        return self._read_csv_optimized(csv_path)
    
    def validate_dataframe(self, df, table_name: str):
        """Compatibility method for data validation."""
        # Simple validation - just return success
        return True
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for a specific table."""
        counts = self.get_table_counts()
        return counts.get(table_name, 0)
    
    def verify_data(self) -> Dict[str, int]:
        """Compatibility method - same as get_table_counts."""
        return self.get_table_counts()
    
    def export_api_data_to_csv(self) -> bool:
        """Placeholder for API export functionality."""
        self.logger.info("API data export functionality - placeholder implementation")
        return True
    
    def close_connections(self):
        """Compatibility method - same as close."""
        self.close()
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics."""
        return {
            'connection_attempts': 1 if self._connection else 0,
            'active_connections': 1 if self._connection else 0,
            'batch_stats': self.batch_processor.get_stats()
        }


# Simple factory function
def create_database_manager(config: Dict = None, data_dir: Path = None) -> 'DatabaseManager':
    """Create a database manager with default settings."""
    return DatabaseManager(config, data_dir)


# Legacy compatibility
def main():
    """Main function for command-line usage."""
    db = create_database_manager()
    
    if db.test_connection():
        print("✅ Database connection successful")
        
        if db.create_all_tables():
            print("✅ Tables created successfully")
            
            if db.import_csv_data():
                print("✅ CSV data imported successfully")
                
                counts = db.get_table_counts()
                print(f"✅ Total records: {sum(counts.values())}")
                for table, count in counts.items():
                    print(f"   {table}: {count}")
    
    db.close()


if __name__ == "__main__":
    main()