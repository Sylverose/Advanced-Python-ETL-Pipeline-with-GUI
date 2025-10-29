"""
Schema manager - handles table schema definitions and creation.
"""

import logging
from typing import Dict, List, Optional
from mysql.connector import Error

logger = logging.getLogger(__name__)

class SchemaManager:
    """Manages database table schemas and creation."""
    
    def __init__(self, db_connection):
        """
        Initialize schema manager.
        
        Args:
            db_connection: DatabaseConnection instance
        """
        self.db_connection = db_connection
        
        # Engine clause for consistent table creation
        self.engine_clause = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        
        # Table schema definitions
        self.table_schemas = self._define_schemas()
    
    def _define_schemas(self) -> Dict[str, str]:
        """Define all table schemas with consistent engine clause."""
        return {
            'brands': f"CREATE TABLE IF NOT EXISTS brands (brand_id INT PRIMARY KEY, brand_name VARCHAR(255) NOT NULL) {self.engine_clause}",
            'categories': f"CREATE TABLE IF NOT EXISTS categories (category_id INT PRIMARY KEY, category_name VARCHAR(255) NOT NULL) {self.engine_clause}",
            'stores': f"""CREATE TABLE IF NOT EXISTS stores (store_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, phone VARCHAR(20), 
                         email VARCHAR(255), street VARCHAR(255), city VARCHAR(100), state VARCHAR(50), zip_code VARCHAR(20)) {self.engine_clause}""",
            'staffs': f"""CREATE TABLE IF NOT EXISTS staffs (staff_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, 
                         email VARCHAR(255), phone VARCHAR(20), active BOOLEAN DEFAULT TRUE, store_name VARCHAR(255), street VARCHAR(255), manager_id INT, 
                         FOREIGN KEY (manager_id) REFERENCES staffs(staff_id)) {self.engine_clause}""",
            'products': f"""CREATE TABLE IF NOT EXISTS products (product_id INT PRIMARY KEY, product_name VARCHAR(255) NOT NULL, brand_id INT, category_id INT, 
                           model_year INT, list_price DECIMAL(10, 2), FOREIGN KEY (brand_id) REFERENCES brands(brand_id), 
                           FOREIGN KEY (category_id) REFERENCES categories(category_id)) {self.engine_clause}""",
            'stocks': f"""CREATE TABLE IF NOT EXISTS stocks (store_name VARCHAR(255), product_id INT, quantity INT DEFAULT 0, PRIMARY KEY (product_id, store_name), 
                         FOREIGN KEY (product_id) REFERENCES products(product_id)) {self.engine_clause}""",
            'orders': f"""CREATE TABLE IF NOT EXISTS orders (order_id INT PRIMARY KEY, customer_id INT NOT NULL, order_status INT NOT NULL, 
                         order_status_name VARCHAR(50), order_date DATE, required_date DATE, shipped_date DATE, staff_name VARCHAR(255), 
                         store VARCHAR(255), INDEX idx_customer_id (customer_id), INDEX idx_order_date (order_date), 
                         INDEX idx_order_status (order_status), INDEX idx_store (store)) {self.engine_clause}""",
            'order_items': f"""CREATE TABLE IF NOT EXISTS order_items (item_id INT PRIMARY KEY, order_id INT NOT NULL, product_id INT NOT NULL, 
                              quantity INT NOT NULL DEFAULT 1, list_price DECIMAL(10, 2) NOT NULL, discount DECIMAL(4, 2) DEFAULT 0.00, 
                              INDEX idx_order_id (order_id), INDEX idx_product_id (product_id)) {self.engine_clause}""",
            'customers': f"""CREATE TABLE IF NOT EXISTS customers (customer_id INT PRIMARY KEY, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, 
                            email VARCHAR(255) UNIQUE, phone VARCHAR(20), street VARCHAR(255), city VARCHAR(100), state VARCHAR(50), zip_code VARCHAR(20), 
                            INDEX idx_email (email), INDEX idx_state (state), INDEX idx_city (city)) {self.engine_clause}"""
        }
    
    def get_schema(self, table_name: str) -> Optional[str]:
        """
        Get schema definition for a specific table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            str: SQL schema definition or None if not found
        """
        return self.table_schemas.get(table_name)
    
    def create_table(self, table_name: str) -> bool:
        """
        Create a specific table in the database.
        
        Args:
            table_name (str): Name of the table to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            schema = self.get_schema(table_name)
            if not schema:
                logger.error(f"No schema defined for table: {table_name}")
                return False
            
            with self.db_connection.get_connection() as conn:
                if conn is None:
                    logger.error("Failed to connect to database")
                    return False
                
                cursor = conn.cursor()
                cursor.execute(schema)
                conn.commit()
                
                logger.info(f"Table '{table_name}' created successfully")
                return True
                
        except Error as e:
            logger.error(f"Error creating table {table_name}: {e}")
            return False
    
    def create_all_tables(self, table_order: List[str] = None) -> bool:
        """
        Create all tables in the correct order (respecting foreign key constraints).
        
        Args:
            table_order (List[str]): Order to create tables. Uses default if None.
            
        Returns:
            bool: True if all tables created successfully
        """
        # Default order respecting foreign key constraints
        order = table_order or ['brands', 'categories', 'stores', 'staffs', 'products', 'stocks', 'orders', 'order_items', 'customers']
        
        success_count = 0
        for table_name in order:
            if self.create_table(table_name):
                success_count += 1
            else:
                logger.warning(f"Failed to create table: {table_name}")
        
        total_tables = len(order)
        logger.info(f"Created {success_count}/{total_tables} tables")
        
        return success_count == total_tables
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Get expected columns for a table (for data validation).
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            List[str]: List of column names
        """
        table_columns = {
            'orders': ['order_id', 'customer_id', 'order_status', 'order_status_name', 
                      'order_date', 'required_date', 'shipped_date', 'staff_name', 'store'],
            'order_items': ['item_id', 'order_id', 'product_id', 'quantity', 'list_price', 'discount'],
            'customers': ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'street', 'city', 'state', 'zip_code'],
            'brands': ['brand_id', 'brand_name'],
            'categories': ['category_id', 'category_name'],
            'stores': ['store_id', 'name', 'phone', 'email', 'street', 'city', 'state', 'zip_code'],
            'products': ['product_id', 'product_name', 'brand_id', 'category_id', 'model_year', 'list_price'],
            'staffs': ['staff_id', 'name', 'last_name', 'email', 'phone', 'active', 'store_name', 'street', 'manager_id'],
            'stocks': ['store_name', 'product_id', 'quantity']
        }
        return table_columns.get(table_name, [])
    
    def get_all_table_names(self) -> List[str]:
        """
        Get list of all defined table names.
        
        Returns:
            List[str]: List of table names
        """
        return list(self.table_schemas.keys())
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            bool: True if table exists, False otherwise
        """
        try:
            with self.db_connection.get_connection() as conn:
                if conn is None:
                    return False
                
                cursor = conn.cursor()
                cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                result = cursor.fetchone()
                return result is not None
                
        except Error as e:
            logger.error(f"Error checking if table exists: {e}")
            return False