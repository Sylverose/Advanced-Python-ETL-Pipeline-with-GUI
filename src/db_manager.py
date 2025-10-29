"""Database manager for ETL pipeline - creates and manages MySQL tables from CSV data."""

import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging
from typing import Dict, List, Optional

# Import modular components
try:
    from .database.connection_manager import DatabaseConnection
    from .database.schema_manager import SchemaManager
    MODULAR_AVAILABLE = True
except ImportError:
    try:
        # Try absolute import path
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from database.connection_manager import DatabaseConnection
        from database.schema_manager import SchemaManager
        MODULAR_AVAILABLE = True
    except ImportError:
        MODULAR_AVAILABLE = False

try:
    from connect import mysql_connection
    import connect
    CONNECT_AVAILABLE = True
except ImportError:
    CONNECT_AVAILABLE = False
    from contextlib import contextmanager
    
    default_config = {'user': 'root', 'password': '', 'host': '127.0.0.1', 'database': 'store_manager', 'raise_on_warnings': True}
    
    @contextmanager
    def mysql_connection(config):
        conn = None
        try:
            conn = mysql.connector.connect(**config)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            yield None
        finally:
            if conn: conn.close()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations for ETL pipeline."""
    
    def __init__(self, db_config: Dict = None):
        """Initialize DatabaseManager with database configuration."""
        self.db_config = db_config or (connect.config if CONNECT_AVAILABLE else default_config)
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'CSV')
        
        self.csv_files = {
            'brands': 'brands.csv', 'categories': 'categories.csv', 'products': 'products.csv',
            'staffs': 'staffs.csv', 'stocks': 'stocks.csv', 'stores': 'stores.csv'
        }
        
        # Initialize modular components if available
        if MODULAR_AVAILABLE:
            try:
                self.db_connection = DatabaseConnection(self.db_config)
                self.schema_manager = SchemaManager(self.db_connection)
                self.use_modular = True
            except Exception as e:
                logger.warning(f"Failed to initialize modular components: {e}. Using fallback.")
                self.use_modular = False
        else:
            self.use_modular = False
        
        # Fallback schema definitions (only used if modular components unavailable)
        if not self.use_modular:
            engine_clause = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            self.table_schemas = {
                'brands': f"CREATE TABLE IF NOT EXISTS brands (brand_id INT PRIMARY KEY, brand_name VARCHAR(255) NOT NULL) {engine_clause}",
                'categories': f"CREATE TABLE IF NOT EXISTS categories (category_id INT PRIMARY KEY, category_name VARCHAR(255) NOT NULL) {engine_clause}",
                'stores': f"""CREATE TABLE IF NOT EXISTS stores (store_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, phone VARCHAR(20), 
                             email VARCHAR(255), street VARCHAR(255), city VARCHAR(100), state VARCHAR(50), zip_code VARCHAR(20)) {engine_clause}""",
                'staffs': f"""CREATE TABLE IF NOT EXISTS staffs (staff_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, 
                             email VARCHAR(255), phone VARCHAR(20), active BOOLEAN DEFAULT TRUE, store_name VARCHAR(255), street VARCHAR(255), manager_id INT, 
                             FOREIGN KEY (manager_id) REFERENCES staffs(staff_id)) {engine_clause}""",
                'products': f"""CREATE TABLE IF NOT EXISTS products (product_id INT PRIMARY KEY, product_name VARCHAR(255) NOT NULL, brand_id INT, category_id INT, 
                               model_year INT, list_price DECIMAL(10, 2), FOREIGN KEY (brand_id) REFERENCES brands(brand_id), 
                               FOREIGN KEY (category_id) REFERENCES categories(category_id)) {engine_clause}""",
                'stocks': f"""CREATE TABLE IF NOT EXISTS stocks (store_name VARCHAR(255), product_id INT, quantity INT DEFAULT 0, PRIMARY KEY (product_id, store_name), 
                             FOREIGN KEY (product_id) REFERENCES products(product_id)) {engine_clause}""",
                'orders': f"""CREATE TABLE IF NOT EXISTS orders (order_id INT PRIMARY KEY, customer_id INT NOT NULL, order_status INT NOT NULL, 
                             order_status_name VARCHAR(50), order_date DATE, required_date DATE, shipped_date DATE, staff_name VARCHAR(255), 
                             store VARCHAR(255), INDEX idx_customer_id (customer_id), INDEX idx_order_date (order_date), 
                             INDEX idx_order_status (order_status), INDEX idx_store (store)) {engine_clause}""",
                'order_items': f"""CREATE TABLE IF NOT EXISTS order_items (item_id INT PRIMARY KEY, order_id INT NOT NULL, product_id INT NOT NULL, 
                                  quantity INT NOT NULL DEFAULT 1, list_price DECIMAL(10, 2) NOT NULL, discount DECIMAL(4, 2) DEFAULT 0.00, 
                                  INDEX idx_order_id (order_id), INDEX idx_product_id (product_id)) {engine_clause}""",
                'customers': f"""CREATE TABLE IF NOT EXISTS customers (customer_id INT PRIMARY KEY, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, 
                                email VARCHAR(255) UNIQUE, phone VARCHAR(20), street VARCHAR(255), city VARCHAR(100), state VARCHAR(50), zip_code VARCHAR(20), 
                                INDEX idx_email (email), INDEX idx_state (state), INDEX idx_city (city)) {engine_clause}"""
            }

    def read_csv_file(self, filename: str) -> Optional[pd.DataFrame]:
        """Read CSV file and return DataFrame."""
        try:
            file_path = os.path.join(self.data_dir, filename)
            return pd.read_csv(file_path) if os.path.exists(file_path) else None
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            return None

    def create_database_if_not_exists(self) -> bool:
        """Create database if it doesn't exist."""
        try:
            temp_config = self.db_config.copy()
            database_name = temp_config.pop('database', 'store_manager')
            
            with mysql_connection(temp_config) as conn:
                if conn is None:
                    return False
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
                cursor.execute(f"USE {database_name}")
                conn.commit()
                return True
        except Error as e:
            logger.error(f"Error creating database: {e}")
            return False

    def create_table(self, table_name: str) -> bool:
        """Create a specific table in the database."""
        if self.use_modular:
            return self.schema_manager.create_table(table_name)
        
        # Fallback to legacy method
        try:
            with mysql_connection(self.db_config) as conn:
                if conn is None or table_name not in self.table_schemas:
                    return False
                cursor = conn.cursor()
                cursor.execute(self.table_schemas[table_name])
                conn.commit()
                return True
        except Error as e:
            logger.error(f"Error creating table {table_name}: {e}")
            return False

    def insert_data_from_csv(self, table_name: str, df: pd.DataFrame) -> bool:
        """Insert data from DataFrame into MySQL table."""
        try:
            with mysql_connection(self.db_config) as conn:
                if conn is None:
                    return False
                
                # Handle stores table auto-increment
                if table_name == 'stores':
                    df = df.copy()
                    df.insert(0, 'store_id', range(1, len(df) + 1))
                
                # Handle staffs table auto-increment
                if table_name == 'staffs':
                    df = df.copy()
                    df.insert(0, 'staff_id', range(1, len(df) + 1))
                
                # Clean data: replace NaN values with None (NULL in MySQL)
                df_cleaned = df.copy()
                # Replace NaN values with None for MySQL NULL conversion
                df_cleaned = df_cleaned.where(pd.notna(df_cleaned), None)
                
                columns = list(df_cleaned.columns)
                placeholders = ', '.join(['%s'] * len(columns))
                insert_query = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                cursor = conn.cursor()
                # Convert to list of tuples, handling NaN properly
                data_tuples = [tuple(None if pd.isna(val) else val for val in row) for row in df_cleaned.to_numpy()]
                cursor.executemany(insert_query, data_tuples)
                conn.commit()
                return True
        except Error as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            return False

    def load_csv_to_table(self, table_name: str) -> bool:
        """Complete process: read CSV, create table, and insert data."""
        try:
            csv_filename = self.csv_files.get(table_name)
            if not csv_filename:
                return False
            
            df = self.read_csv_file(csv_filename)
            return df is not None and self.create_table(table_name) and self.insert_data_from_csv(table_name, df)
        except Exception as e:
            logger.error(f"Error in load_csv_to_table for {table_name}: {e}")
            return False

    def create_all_tables_from_csv(self) -> bool:
        """Create all tables and load data from CSV files."""
        try:
            if not self.create_database_if_not_exists():
                return False
            
            # Create tables in dependency order (respecting foreign keys)
            csv_table_order = ['brands', 'categories', 'stores', 'staffs', 'products', 'stocks']
            csv_success = all(self.load_csv_to_table(table) for table in csv_table_order)
            
            # Also create API tables (structure only, no data loading)
            api_tables = ['customers', 'orders', 'order_items']
            api_success = all(self.create_table(table) for table in api_tables)
            
            return csv_success and api_success
        except Exception as e:
            logger.error(f"Error in create_all_tables_from_csv: {e}")
            return False

    def get_table_info(self, table_name: str) -> Optional[List]:
        """
        Get information about a specific table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            List: Table information or None if error
        """
        try:
            with mysql_connection(self.db_config) as conn:
                if conn is None:
                    return None
                    
                cursor = conn.cursor()
                cursor.execute(f"DESCRIBE {table_name}")
                return cursor.fetchall()
                
        except Error as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return None

    def get_row_count(self, table_name: str) -> int:
        """
        Get the number of rows in a table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            int: Number of rows, -1 if error
        """
        try:
            with mysql_connection(self.db_config) as conn:
                if conn is None:
                    return -1
                    
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Error as e:
            logger.error(f"Error getting row count for {table_name}: {e}")
            return -1



    def _create_api_table(self, table_name: str, fetch_method: str) -> bool:
        """Create and populate API-based tables."""
        try:
            from data_from_api import APIClient
            
            if not self.create_table(table_name):
                return False
            
            api_client = APIClient()
            try:
                df = getattr(api_client, fetch_method)()
                return df is not None and self.insert_data_from_dataframe(table_name, df)
            finally:
                api_client.close()
        except Exception as e:
            logger.error(f"Error creating {table_name} table: {e}")
            return False

    def create_api_table_streaming(self, table_name: str, fetch_method: str, batch_size: int = 1000) -> bool:
        """Create and populate API table with streaming insertion for large datasets."""
        try:
            from data_from_api import APIClient
            
            if not self.create_table(table_name):
                return False
            
            api_client = APIClient()
            try:
                all_data = api_client.fetch_all_data()
                if table_name not in all_data or all_data[table_name] is None:
                    return False
                
                df = all_data[table_name]
                with mysql_connection(self.db_config) as conn:
                    if conn is None:
                        return False
                    
                    cursor = conn.cursor()
                    for start_idx in range(0, len(df), batch_size):
                        batch_df = self._prepare_dataframe_for_insert(df.iloc[start_idx:start_idx+batch_size], table_name)
                        columns = list(batch_df.columns)
                        insert_query = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
                        data_tuples = [tuple(None if pd.isna(val) else val for val in row) for row in batch_df.to_numpy()]
                        cursor.executemany(insert_query, data_tuples)
                        conn.commit()
                    return True
            finally:
                api_client.close()
        except Exception as e:
            logger.error(f"Error in streaming insertion for {table_name}: {e}")
            return False

    def create_api_table_direct_json(self, table_name: str, api_endpoint: str) -> bool:
        """Create and populate API table directly from JSON response."""
        try:
            import requests
            
            if not self.create_table(table_name):
                return False
            
            response = requests.get(api_endpoint)
            if response.status_code != 200 or not response.json():
                return response.status_code == 200  # True if empty data, False if error
            
            with mysql_connection(self.db_config) as conn:
                if conn is None:
                    return False
                
                table_columns = self._get_table_columns(table_name)
                insert_query = f"INSERT IGNORE INTO {table_name} ({', '.join(table_columns)}) VALUES ({', '.join(['%s'] * len(table_columns))})"
                
                data_tuples = [
                    tuple(record.get(col) if record.get(col) not in [None, 'NULL'] else None for col in table_columns)
                    for record in response.json()
                ]
                
                cursor = conn.cursor()
                cursor.executemany(insert_query, data_tuples)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error in direct JSON insertion for {table_name}: {e}")
            return False

    def _get_table_columns(self, table_name: str) -> list:
        """Get the expected columns for a table."""
        if self.use_modular:
            return self.schema_manager.get_table_columns(table_name)
        
        # Fallback column definitions
        columns = {
            'orders': ['order_id', 'customer_id', 'order_status', 'order_status_name', 'order_date', 'required_date', 'shipped_date', 'staff_name', 'store'],
            'order_items': ['item_id', 'order_id', 'product_id', 'quantity', 'list_price', 'discount'],
            'customers': ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'street', 'city', 'state', 'zip_code'],
        }
        return columns.get(table_name, [])

    def create_all_api_tables_direct(self, method: str = 'standard') -> bool:
        """Create all API tables with different insertion methods."""
        api_config = {
            'orders': ('https://etl-server.fly.dev/orders', 'fetch_orders'),
            'order_items': ('https://etl-server.fly.dev/order_items', 'fetch_order_items'),
            'customers': ('https://etl-server.fly.dev/customers', 'fetch_customers')
        }
        
        results = []
        for table_name, (endpoint, fetch_method) in api_config.items():
            if method == 'direct_json':
                success = self.create_api_table_direct_json(table_name, endpoint)
            elif method == 'streaming':
                success = self.create_api_table_streaming(table_name, fetch_method)
            else:
                success = self._create_api_table(table_name, fetch_method)
            results.append(success)
        
        return all(results)

    def create_all_api_tables(self) -> bool:
        """Create and populate all API-based tables."""
        api_tables = {'orders': 'fetch_orders', 'order_items': 'fetch_order_items', 'customers': 'fetch_customers'}
        return all(self._create_api_table(table, method) for table, method in api_tables.items())

    def export_api_data_to_csv(self) -> bool:
        """Export all API data to CSV files in the data/API folder."""
        try:
            from data_from_api import APIClient
            api_client = APIClient()
            api_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'API')
            success = api_client.save_all_api_data_to_csv(api_dir)
            api_client.close()
            return success
        except Exception as e:
            logger.error(f"Error exporting API data to CSV: {e}")
            return False



    def insert_data_from_dataframe(self, table_name: str, df: pd.DataFrame) -> bool:
        """Insert data from DataFrame into MySQL table."""
        try:
            with mysql_connection(self.db_config) as conn:
                if conn is None:
                    return False
                
                df_prepared = self._prepare_dataframe_for_insert(df, table_name)
                columns = list(df_prepared.columns)
                insert_query = f"INSERT IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
                data_tuples = [tuple(None if pd.isna(val) else val for val in row) for row in df_prepared.to_numpy()]
                
                cursor = conn.cursor()
                cursor.executemany(insert_query, data_tuples)
                conn.commit()
                return True
        except Error as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            return False

    def _prepare_dataframe_for_insert(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Prepare DataFrame for database insertion."""
        df_copy = df.copy()
        
        if table_name == 'stores':
            df_copy.insert(0, 'store_id', range(1, len(df_copy) + 1))
        
        if table_name == 'staffs':
            df_copy.insert(0, 'staff_id', range(1, len(df_copy) + 1))
        
        if self.use_modular:
            expected_columns = self.schema_manager.get_table_columns(table_name)
        else:
            # Fallback column definitions
            table_columns = {
                'orders': ['order_id', 'customer_id', 'order_status', 'order_status_name', 'order_date', 'required_date', 'shipped_date', 'staff_name', 'store'],
                'order_items': ['item_id', 'order_id', 'product_id', 'quantity', 'list_price', 'discount'],
                'customers': ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'street', 'city', 'state', 'zip_code'],
                'brands': ['brand_id', 'brand_name'], 'categories': ['category_id', 'category_name'],
                'stores': ['store_id', 'name', 'phone', 'email', 'street', 'city', 'state', 'zip_code'],
                'products': ['product_id', 'product_name', 'brand_id', 'category_id', 'model_year', 'list_price'],
                'staffs': ['staff_id', 'name', 'last_name', 'email', 'phone', 'active', 'store_name', 'street', 'manager_id'],
                'stocks': ['store_name', 'product_id', 'quantity']
            }
            expected_columns = table_columns.get(table_name, df_copy.columns.tolist())
        
        return df_copy[[col for col in expected_columns if col in df_copy.columns]]

def create_complete_database():
    """Create complete database with both CSV tables and API tables."""
    db_manager = DatabaseManager()
    
    if not db_manager.create_database_if_not_exists():
        return False
    
    csv_success = db_manager.create_all_tables_from_csv()
    api_success = db_manager.create_all_api_tables()
    
    print("\n" + "="*60)
    print("COMPLETE DATABASE SUMMARY")
    print("="*60)
    
    for table_name in db_manager.csv_files.keys():
        row_count = db_manager.get_row_count(table_name)
        print(f"  {'SUCCESS' if row_count > 0 else 'EMPTY'} {table_name:<15}: {row_count:>8} rows")
    
    orders_count = db_manager.get_row_count('orders')
    print(f"\nAPI Tables:")
    print(f"  {'SUCCESS' if orders_count > 0 else 'EMPTY'} {'orders':<15}: {orders_count:>8} rows")
    
    overall_success = csv_success and api_success
    print(f"\nOverall Status: {'SUCCESS' if overall_success else 'PARTIAL/FAILED'}")
    
    return overall_success

def create_api_tables_and_csv():
    """Create API database tables AND export data to CSV files."""
    db_manager = DatabaseManager()
    
    if not db_manager.create_database_if_not_exists():
        return False
    
    db_success = db_manager.create_all_api_tables()
    csv_success = db_manager.export_api_data_to_csv()
    
    print("\n" + "="*60)
    print("API DATA PROCESSING SUMMARY")
    print("="*60)
    print(f"Database Tables: {'SUCCESS' if db_success else 'FAILED'}")
    print(f"CSV File Export: {'SUCCESS' if csv_success else 'FAILED'}")
    
    overall_success = db_success and csv_success
    print(f"\nOverall Status: {'SUCCESS' if overall_success else 'PARTIAL/FAILED'}")
    
    return overall_success

def main():
    """Main function to demonstrate DatabaseManager usage."""
    import sys
    
    db_manager = DatabaseManager()
    
    options = {
        '--api-only': lambda: _run_api_only(db_manager),
        '--api-csv': lambda: _run_csv_export(db_manager),
        '--api-complete': create_api_tables_and_csv,
        '--csv-only': lambda: _run_csv_only(db_manager),
        '--api-streaming': lambda: _run_api_streaming(db_manager),
        '--api-direct': lambda: _run_api_direct_json(db_manager),
        '--api-method': lambda: _run_api_with_method(db_manager)
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in options:
        options[sys.argv[1]]()
    elif len(sys.argv) > 1 and sys.argv[1] == '--help':
        _show_help()
    elif len(sys.argv) > 1:
        print(f"ERROR: Unknown option: {sys.argv[1]}\n")
        _show_help()
    else:
        create_complete_database()

def _show_help():
    """Show available command line options."""
    print("\nDATABASE MANAGER - COMMAND LINE OPTIONS")
    print("="*50)
    print("  --csv-only        Create CSV tables only")
    print("  --api-only        Create API tables (standard method)")
    print("  --api-csv         Export API data to CSV files")
    print("  --api-complete    Create DB tables + CSV export")
    print("  --api-streaming   Use streaming insertion (batched)")
    print("  --api-direct      Use direct JSON insertion (fastest)")
    print("  --api-method [METHOD]  Specify method: standard|streaming|direct_json")
    print("  --help            Show this help")

def _run_api_only(db_manager):
    """Create API tables only."""
    success = db_manager.create_database_if_not_exists() and db_manager.create_all_api_tables()
    print(f"\n{'SUCCESS: All API tables created successfully!' if success else 'ERROR: Failed to create API tables'}")

def _run_csv_export(db_manager):
    """Export API data to CSV files only."""
    print(f"\n{'SUCCESS!' if db_manager.export_api_data_to_csv() else 'FAILED'}")

def _run_csv_only(db_manager):
    """Create CSV tables only."""
    print(f"\n{'SUCCESS: CSV tables created successfully!' if db_manager.create_all_tables_from_csv() else 'ERROR: Failed'}")

def _run_api_method(db_manager, method='streaming'):
    """Create API tables using specified method."""
    if not db_manager.create_database_if_not_exists():
        print("\nERROR: Database connection failed")
        return
    success = db_manager.create_all_api_tables_direct(method)
    print(f"\n{'SUCCESS!' if success else 'FAILED!'} Method: {method}")

def _run_api_streaming(db_manager):
    _run_api_method(db_manager, 'streaming')

def _run_api_direct_json(db_manager):
    _run_api_method(db_manager, 'direct_json')

def _run_api_with_method(db_manager):
    import sys
    method = sys.argv[2] if len(sys.argv) > 2 else 'standard'
    if method not in ['standard', 'streaming', 'direct_json']:
        print(f"ERROR: Invalid method: {method}")
        return
    _run_api_method(db_manager, method)

if __name__ == "__main__":
    main()
