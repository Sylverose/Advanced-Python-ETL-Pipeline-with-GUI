"""
API Data Retrieval Module - Fetches data from external API endpoints
"""

import requests
import pandas as pd
import json
import logging
from typing import Optional, Dict, List
from datetime import datetime
import time

# Set up logging with less verbose output
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class APIClient:
    """Client for retrieving data from the ETL API server endpoints."""
    
    def __init__(self, base_url: str = "https://etl-server.fly.dev"):
        """
        Initialize API client.
        
        Args:
            base_url (str): Base URL for the API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # Set reasonable timeout and retry settings
        self.session.headers.update({
            'User-Agent': 'ETL-Pipeline/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
        
        # Define available endpoints
        self.endpoints = {
            'orders': '/orders',
            'order_items': '/order_items',
            'customers': '/customers'
        }

    def fetch_data(self, endpoint_name: str, retry_count: int = 0) -> Optional[pd.DataFrame]:
        """
        Fetch data from the specified API endpoint.
        
        Args:
            endpoint_name (str): Name of the endpoint ('orders', 'order_items', 'customers')
            retry_count (int): Current retry attempt number
            
        Returns:
            pd.DataFrame: Data as DataFrame, None if failed
        """
        if endpoint_name not in self.endpoints:
            logger.error(f"Unknown endpoint: {endpoint_name}. Available: {list(self.endpoints.keys())}")
            return None
            
        try:
            endpoint_url = f"{self.base_url}{self.endpoints[endpoint_name]}"
            
            response = self.session.get(endpoint_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse JSON response and convert to DataFrame
            data = response.json()
            df = pd.DataFrame(data)
            
            # Data cleaning based on endpoint type
            cleaning_methods = {
                'orders': self._clean_orders_data,
                'order_items': self._clean_order_items_data,
                'customers': self._clean_customers_data
            }
            
            if endpoint_name in cleaning_methods:
                df = cleaning_methods[endpoint_name](df)
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint_name}: {e}")
            
            # Retry logic with exponential backoff
            if retry_count < self.max_retries:
                wait_time = self.retry_delay * (2 ** retry_count)
                time.sleep(wait_time)
                return self.fetch_data(endpoint_name, retry_count + 1)
            else:
                logger.error(f"Failed to fetch {endpoint_name} after {self.max_retries} attempts")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for {endpoint_name}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching {endpoint_name}: {e}")
            return None

    def fetch_orders(self, retry_count: int = 0) -> Optional[pd.DataFrame]:
        """Fetch orders data (backward compatibility method)."""
        return self.fetch_data('orders', retry_count)

    def fetch_order_items(self, retry_count: int = 0) -> Optional[pd.DataFrame]:
        """Fetch order_items data."""
        return self.fetch_data('order_items', retry_count)

    def fetch_customers(self, retry_count: int = 0) -> Optional[pd.DataFrame]:
        """Fetch customers data."""
        return self.fetch_data('customers', retry_count)

    def fetch_all_data(self) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Fetch data from all available endpoints.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary with endpoint names as keys and DataFrames as values
        """
        all_data = {}
        
        for endpoint_name in self.endpoints.keys():
            df = self.fetch_data(endpoint_name)
            all_data[endpoint_name] = df
            
        return all_data

    def _clean_orders_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate the orders data.
        
        Args:
            df (pd.DataFrame): Raw orders DataFrame
            
        Returns:
            pd.DataFrame: Cleaned orders DataFrame
        """
        try:
            # Convert date columns to proper datetime format
            date_columns = ['order_date', 'required_date', 'shipped_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = df[col].replace('NULL', None)
                    df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
            
            # Convert numeric columns
            numeric_columns = ['order_id', 'customer_id', 'order_status']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Handle order_status mapping (if needed)
            status_mapping = {
                1: 'Pending',
                2: 'Processing', 
                3: 'Rejected',
                4: 'Completed'
            }
            
            if 'order_status' in df.columns:
                df['order_status_name'] = df['order_status'].map(status_mapping)
            
            # Remove duplicates based on order_id
            if 'order_id' in df.columns:
                df = df.drop_duplicates(subset=['order_id'], keep='first')
            
            # Quick validation for critical issues only
            self._validate_data(df, 'orders')
            
            return df
            
        except Exception as e:
            logger.error(f"Error during data cleaning: {e}")
            return df  # Return original df if cleaning fails

    def _validate_data(self, df: pd.DataFrame, endpoint_type: str) -> None:
        """Unified validation method for all data types."""
        validation_rules = {
            'orders': (['order_id', 'customer_id', 'order_date', 'order_status'], ['order_id', 'customer_id']),
            'order_items': (['item_id', 'order_id', 'product_id', 'quantity'], ['item_id', 'order_id', 'product_id']),
            'customers': (['customer_id', 'first_name', 'last_name'], ['customer_id', 'first_name', 'last_name'])
        }
        
        try:
            required_columns, critical_columns = validation_rules.get(endpoint_type, ([], []))
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                logger.warning(f"Missing required {endpoint_type} columns: {missing_cols}")
            
            for col in critical_columns:
                if col in df.columns and (null_count := df[col].isnull().sum()) > 0:
                    logger.warning(f"Found {null_count} null values in critical {endpoint_type} column '{col}'")
        except Exception as e:
            logger.error(f"Error during {endpoint_type} data validation: {e}")

    def _clean_order_items_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the order_items data."""
        try:
            # Convert numeric columns and handle NULL values
            for col in ['item_id', 'order_id', 'product_id', 'quantity', 'list_price', 'discount']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.replace('NULL', None)
            if 'item_id' in df.columns:
                df = df.drop_duplicates(subset=['item_id'], keep='first')
            
            self._validate_data(df, 'order_items')
            return df
        except Exception as e:
            logger.error(f"Error during order_items data cleaning: {e}")
            return df

    def _clean_customers_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate the customers data."""
        try:
            # Convert customer_id and handle NULL values
            if 'customer_id' in df.columns:
                df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce')
            
            df = df.replace('NULL', None)
            
            # Clean string columns efficiently
            for col in ['first_name', 'last_name', 'email', 'phone', 'street', 'city', 'state', 'zip_code']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().replace('nan', None)
            
            if 'customer_id' in df.columns:
                df = df.drop_duplicates(subset=['customer_id'], keep='first')
            
            self._validate_data(df, 'customers')
            return df
        except Exception as e:
            logger.error(f"Error during customers data cleaning: {e}")
            return df

    def save_to_csv(self, df: pd.DataFrame, filename: str = "orders_api_data.csv", 
                   output_dir: str = "../data/API") -> bool:
        """
        Save the orders DataFrame to CSV file.
        
        Args:
            df (pd.DataFrame): Orders DataFrame to save
            filename (str): Output filename
            output_dir (str): Output directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import os
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return False

    def save_all_api_data_to_csv(self, output_dir: str = "../data/API") -> bool:
        """
        Fetch all API data and save each endpoint as CSV files.
        
        Args:
            output_dir (str): Output directory for CSV files
            
        Returns:
            bool: True if all files saved successfully, False otherwise
        """
        try:
            import os
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Fetch all API data
            all_data = self.fetch_all_data()
            
            success_count = 0
            total_endpoints = len(all_data)
            
            # Save each endpoint data as CSV
            for endpoint_name, df in all_data.items():
                if df is not None and not df.empty:
                    filename = f"{endpoint_name}.csv"
                    filepath = os.path.join(output_dir, filename)
                    
                    try:
                        df.to_csv(filepath, index=False)
                        print(f"SUCCESS: Saved {endpoint_name}: {len(df):,} rows → {filename}")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to save {endpoint_name} CSV: {e}")
                else:
                    logger.warning(f"No data available for {endpoint_name}")
            
            if success_count == total_endpoints:
                print(f"\nSuccessfully saved all {success_count} API datasets to CSV files!")
                return True
            else:
                logger.warning(f"Only {success_count}/{total_endpoints} CSV files saved successfully")
                return False
                
        except Exception as e:
            logger.error(f"Error saving API data to CSV: {e}")
            return False

    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate a summary of the orders data.
        
        Args:
            df (pd.DataFrame): Orders DataFrame
            
        Returns:
            Dict: Summary statistics
        """
        try:
            summary = {
                'total_orders': len(df),
                'unique_customers': df['customer_id'].nunique() if 'customer_id' in df.columns else 0,
                'date_range': {
                    'earliest': df['order_date'].min().strftime('%Y-%m-%d') if 'order_date' in df.columns and not df['order_date'].isnull().all() else None,
                    'latest': df['order_date'].max().strftime('%Y-%m-%d') if 'order_date' in df.columns and not df['order_date'].isnull().all() else None
                },
                'order_status_counts': df['order_status'].value_counts().to_dict() if 'order_status' in df.columns else {},
                'stores': df['store'].value_counts().to_dict() if 'store' in df.columns else {},
                'staff': df['staff_name'].value_counts().to_dict() if 'staff_name' in df.columns else {}
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {}

    def close(self):
        """Close the HTTP session."""
        self.session.close()

def main():
    """Main function to demonstrate API data retrieval."""
    client = APIClient()
    
    try:
        # Fetch all endpoint data
        all_data = client.fetch_all_data()
        
        # Display basic summary for each endpoint
        for endpoint_name, df in all_data.items():
            if df is not None:
                print(f"\n{endpoint_name.upper()}: {len(df):,} records")
                
                # Display basic info based on endpoint type
                if endpoint_name == 'orders':
                    if 'customer_id' in df.columns:
                        print(f"Unique Customers: {df['customer_id'].nunique():,}")
                    if 'order_date' in df.columns:
                        try:
                            earliest = pd.to_datetime(df['order_date']).min()
                            latest = pd.to_datetime(df['order_date']).max()
                            print(f"Date Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
                        except:
                            pass
                    if 'order_status' in df.columns:
                        status_counts = df['order_status'].value_counts()
                        print("Status Distribution:")
                        for status, count in status_counts.items():
                            print(f"  {status}: {count:,}")
                
                elif endpoint_name == 'order_items':
                    if 'order_id' in df.columns:
                        print(f"Unique Orders: {df['order_id'].nunique():,}")
                    if 'product_id' in df.columns:
                        print(f"Unique Products: {df['product_id'].nunique():,}")
                    if 'quantity' in df.columns:
                        print(f"Total Quantity: {df['quantity'].sum():,}")
                
                elif endpoint_name == 'customers':
                    if 'state' in df.columns:
                        state_counts = df['state'].value_counts()
                        print(f"States Represented: {len(state_counts)}")
                        top_states = state_counts.head()
                        print("Top States:")
                        for state, count in top_states.items():
                            print(f"  {state}: {count:,}")
                
                print("="*60)
                
                # Save to CSV
                filename = f"{endpoint_name}_data.csv"
                try:
                    df.to_csv(filename, index=False)
                    logger.info(f"Data saved successfully to {filename}")
                    print(f"SUCCESS: {endpoint_name} data saved to {filename}")
                except Exception as e:
                    logger.error(f"Failed to save {endpoint_name} data to CSV: {e}")
                    print(f"ERROR: Failed to save {endpoint_name} data: {e}")
                
                # Display first few rows
                print(f"\nFirst 5 {endpoint_name} records:")
                print(df.head().to_string())
                
                logger.info(f"{endpoint_name} data processing completed successfully!")
            else:
                logger.error(f"Failed to retrieve {endpoint_name} data from API")
                
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()
