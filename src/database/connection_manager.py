"""
Database connection manager - enhanced wrapper around connect.py functionality.
"""

import logging
from contextlib import contextmanager
from typing import Dict, Optional
from mysql.connector import Error

# Import the established connection utilities
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from connect import mysql_connection, config as default_config, connect_to_mysql
    CONNECT_AVAILABLE = True
except ImportError:
    # Fallback if connect module not available
    import mysql.connector
    from contextlib import contextmanager
    CONNECT_AVAILABLE = False
    
    default_config = {
        'user': 'root', 'password': '', 'host': '127.0.0.1', 
        'database': 'store_manager', 'raise_on_warnings': True
    }
    
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

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages MySQL database connections and configuration."""
    
    def __init__(self, config: Dict = None):
        """
        Initialize database connection manager.
        
        Args:
            config (Dict): Database configuration. Uses default if None.
        """
        self.config = config or self._load_default_config()
    
    def _load_default_config(self) -> Dict:
        """Load default database configuration from connect module."""
        return default_config
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection as context manager.
        Uses connect.py's mysql_connection with retry logic.
        
        Yields:
            MySQLConnection: Database connection object
        """
        with mysql_connection(self.config) as conn:
            yield conn
    
    def create_database_if_not_exists(self, database_name: str = None) -> bool:
        """
        Create database if it doesn't exist.
        
        Args:
            database_name (str): Name of database to create. Uses config default if None.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db_name = database_name or self.config.get('database', 'store_manager')
            
            # Connect without specifying database
            temp_config = self.config.copy()
            temp_config.pop('database', None)
            
            with self.get_connection_without_db(temp_config) as conn:
                if conn is None:
                    logger.error("Failed to connect to MySQL server")
                    return False
                
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                cursor.execute(f"USE {db_name}")
                conn.commit()
                
                logger.info(f"Database '{db_name}' ready")
                return True
                
        except Error as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    @contextmanager
    def get_connection_without_db(self, config: Dict):
        """Get connection without specifying database (for database creation)."""
        with mysql_connection(config) as conn:
            yield conn
    
    def test_connection(self) -> bool:
        """
        Test database connection using connect.py's connection logic.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if CONNECT_AVAILABLE:
            # Use connect.py's robust connection function
            conn = connect_to_mysql(self.config, attempts=1)
            if conn:
                conn.close()
                return True
            return False
        else:
            # Fallback method
            with self.get_connection() as conn:
                return conn is not None
    
    def get_config_summary(self) -> Dict:
        """
        Get sanitized configuration summary (without password).
        
        Returns:
            Dict: Configuration summary
        """
        summary = self.config.copy()
        if 'password' in summary:
            summary['password'] = '*' * len(summary['password']) if summary['password'] else 'empty'
        return summary