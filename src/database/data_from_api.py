"""
Compact API data retrieval module with async support and connection pooling.
"""

import pandas as pd
import json
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import asyncio

# Try to import requests directly
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Inline DataUtils functions
class DataUtils:
    @staticmethod
    def create_stats_tracker():
        return {
            'successful_requests': 0,
            'failed_requests': 0
        }
    
    @staticmethod
    def update_stats(stats, key, value):
        if key in stats:
            stats[key] += value
        else:
            stats[key] = value
    
    @staticmethod
    def normalize_column_names(df):
        df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        return df

try:
    from ..api import AsyncAPIClient, APIRequest, RequestMethod, RetryConfig
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    AsyncAPIClient = APIRequest = RequestMethod = RetryConfig = None

logger = logging.getLogger(__name__)

class APIDataFetcher:
    """Compact API data fetcher with async capabilities."""
    
    def __init__(self, base_url: str = "https://jsonplaceholder.typicode.com", 
                 timeout: int = 30, retries: int = 3):
        """Initialize with async client configuration."""
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.stats = DataUtils.create_stats_tracker()
        
        self.requests = requests if REQUESTS_AVAILABLE else None
        
    async def fetch_async(self, endpoints: List[str]) -> Dict[str, List[Dict]]:
        """Fetch data from multiple endpoints asynchronously."""
        if not ASYNC_AVAILABLE:
            logger.warning("Async client not available, using sync fallback")
            data = {}
            for endpoint in endpoints:
                data[endpoint] = self.fetch_sync(endpoint.lstrip('/'))
            return data
        
        retry_config = RetryConfig(max_attempts=self.retries, backoff_multiplier=1.5)
        
        async with AsyncAPIClient(
            base_url=self.base_url,
            timeout=self.timeout,
            retry_config=retry_config
        ) as client:
            
            requests = [
                APIRequest(
                    method=RequestMethod.GET,
                    endpoint=endpoint,
                    params={'_limit': 1000} if 'posts' in endpoint else {}
                )
                for endpoint in endpoints
            ]
            
            results = await client.batch_execute(requests)
            
            data = {}
            for endpoint, result in zip(endpoints, results):
                if result.success:
                    data[endpoint] = result.data
                    DataUtils.update_stats(self.stats, 'successful_requests', 1)
                    logger.info(f"Fetched {len(result.data)} records from {endpoint}")
                else:
                    logger.error(f"Failed to fetch from {endpoint}: {result.error}")
                    data[endpoint] = []
                    DataUtils.update_stats(self.stats, 'failed_requests', 1)
            
            return data
    
    def fetch_sync(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Synchronous fallback for single endpoint."""
        if not self.requests:
            logger.error("Requests library not available")
            return []
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.requests.get(url, params=params or {}, timeout=self.timeout)
            
            # Handle different HTTP status codes more gracefully
            if response.status_code == 404:
                logger.debug(f"Endpoint not found: {endpoint} (404)")
                return []
            elif response.status_code == 403:
                logger.warning(f"Access forbidden to {endpoint} (403)")
                return []
            elif response.status_code == 500:
                logger.error(f"Server error for {endpoint} (500)")
                return []
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError as json_error:
                logger.error(f"Invalid JSON response from {endpoint}: {json_error}")
                return []
            
            DataUtils.update_stats(self.stats, 'successful_requests', 1)
            logger.info(f"Sync fetch from {endpoint}: {len(data) if isinstance(data, list) else 1} records")
            
            return data if isinstance(data, list) else [data]
            
        except self.requests.exceptions.RequestException as e:
            # More specific error logging for HTTP-related issues
            error_msg = f"HTTP request failed for {endpoint}: {e}"
            if "404" in str(e):
                logger.debug(error_msg)  # 404s are common, log as debug
            else:
                logger.error(error_msg)
            DataUtils.update_stats(self.stats, 'failed_requests', 1)
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching {endpoint}: {e}")
            DataUtils.update_stats(self.stats, 'failed_requests', 1)
            return []
    
    def fetch_all_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch all available API data and convert to DataFrames."""
        # Auto-detect endpoints based on API type
        if "jsonplaceholder" in self.base_url.lower():
            endpoints = {
                '/users': 'customers',
                '/posts': 'orders',
                '/comments': 'order_items'
            }
        elif "etl-server.fly.dev" in self.base_url.lower():
            endpoints = {
                '/customers': 'customers',
                '/orders': 'orders',
                '/order_items': 'order_items'
            }
        else:
            endpoints = {
                '/customers': 'customers',
                '/orders': 'orders',
                '/order_items': 'order_items'
            }
        
        # Fetch only the mapped endpoints
        raw_data = {}
        for endpoint, table_name in endpoints.items():
            try:
                data = self.fetch_sync(endpoint)
                if data and len(data) > 0:
                    raw_data[table_name] = data
                    logger.info(f"Successfully fetched {len(data)} records from {endpoint} -> {table_name}")
            except Exception as e:
                logger.warning(f"Could not fetch from {endpoint}: {e}")
        
        dataframes = {}
        for table_name, data in raw_data.items():
            if data:
                df = pd.DataFrame(data)
                df = self._process_dataframe(df, table_name)
                dataframes[table_name] = df
        
        return dataframes
    
    def _process_dataframe(self, df: pd.DataFrame, endpoint: str) -> pd.DataFrame:
        """Process and normalize DataFrame based on table name."""
        if df.empty:
            return df
        
        df = DataUtils.normalize_column_names(df)
        
        if 'customers' in endpoint or 'users' in endpoint:
            df = self._process_users_data(df)
        elif 'orders' in endpoint or 'posts' in endpoint:
            df = self._process_posts_data(df)
        elif 'order_items' in endpoint or 'comments' in endpoint:
            df = self._process_comments_data(df)
        
        return df
    
    def _process_users_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process users data with address and company flattening."""
        processed_df = df.copy()
        
        # Flatten address if it exists
        if 'address' in processed_df.columns:
            address_df = pd.json_normalize(processed_df['address'])
            address_df.columns = ['address_' + col for col in address_df.columns]
            processed_df = pd.concat([processed_df.drop('address', axis=1), address_df], axis=1)
        
        # Flatten company if it exists
        if 'company' in processed_df.columns:
            company_df = pd.json_normalize(processed_df['company'])
            company_df.columns = ['company_' + col for col in company_df.columns]
            processed_df = pd.concat([processed_df.drop('company', axis=1), company_df], axis=1)
        
        # Ensure we have the expected columns for compatibility
        expected_columns = ['id', 'name', 'username', 'email', 'phone', 'website']
        for col in expected_columns:
            if col not in processed_df.columns:
                processed_df[col] = None
        
        return processed_df
    
    def _process_posts_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process posts data."""
        processed_df = df.copy()
        
        # Ensure expected columns
        expected_columns = ['id', 'userid', 'title', 'body']
        for col in expected_columns:
            if col not in processed_df.columns:
                processed_df[col] = None
        
        # Add timestamp
        processed_df['created_at'] = datetime.now().isoformat()
        
        return processed_df
    
    def _process_comments_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process comments data."""
        processed_df = df.copy()
        
        # Ensure expected columns
        expected_columns = ['id', 'postid', 'name', 'email', 'body']
        for col in expected_columns:
            if col not in processed_df.columns:
                processed_df[col] = None
        
        return processed_df
    
    def fetch_data(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """
        Compatibility method for GUI - fetch data from a single endpoint.
        
        Args:
            endpoint: API endpoint to fetch from
            params: Optional parameters for the request
        
        Returns:
            List of dictionaries containing the fetched data
        """
        try:
            # First, try to detect what kind of API server we're dealing with
            if 'jsonplaceholder.typicode.com' in self.base_url:
                # Standard JSONPlaceholder API
                endpoint_mapping = {
                    'orders': '/posts',  # Map orders to posts for demo API
                    'customers': '/users',
                    'products': '/posts',
                    'users': '/users',
                    'posts': '/posts',
                    'comments': '/comments'
                }
                actual_endpoint = endpoint_mapping.get(endpoint, f'/{endpoint}')
            else:
                # Custom API server - try the endpoint directly first
                actual_endpoint = f'/{endpoint}' if not endpoint.startswith('/') else endpoint
            
            # Try the primary endpoint
            data = self.fetch_sync(actual_endpoint, params)
            
            if data:
                logger.info(f"Fetched {len(data)} records from {endpoint}")
                return data
            
            # If no data and this is a custom server, try common alternatives
            if 'jsonplaceholder.typicode.com' not in self.base_url:
                alternative_endpoints = []
                
                if endpoint in ['orders', 'order']:
                    alternative_endpoints = ['/api/orders', '/orders', '/order', '/data']
                elif endpoint in ['customers', 'customer']:
                    alternative_endpoints = ['/api/customers', '/customers', '/customer', '/users']
                elif endpoint in ['products', 'product']:
                    alternative_endpoints = ['/api/products', '/products', '/product', '/items']
                
                # Try alternatives
                for alt_endpoint in alternative_endpoints:
                    if alt_endpoint != actual_endpoint:
                        try:
                            data = self.fetch_sync(alt_endpoint, params)
                            if data:
                                logger.info(f"Fetched {len(data)} records from {endpoint} using {alt_endpoint}")
                                return data
                        except Exception:
                            continue
            
            logger.warning(f"No data found for {endpoint} at {self.base_url}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch data from {endpoint}: {e}")
            return []
    
    def close(self):
        """Compatibility method for GUI - no-op since we don't maintain persistent connections."""
        pass
    
    def export_to_csv(self, output_dir: str = "data/API") -> bool:
        """Export all API data to CSV files."""
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            dataframes = self.fetch_all_data()
            
            for name, df in dataframes.items():
                if not df.empty:
                    output_path = os.path.join(output_dir, f"{name}.csv")
                    df.to_csv(output_path, index=False)
                    logger.info(f"Exported {len(df)} {name} records to {output_path}")
                else:
                    logger.warning(f"No data to export for {name}")
            
            return True
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False
    
    def save_all_api_data_to_csv(self, output_dir: str = "data/API") -> bool:
        """Compatibility method for GUI - alias for export_to_csv."""
        return self.export_to_csv(output_dir)
    
    def discover_endpoints(self) -> List[str]:
        """Discover available endpoints by trying common ones."""
        common_endpoints = [
            '/users', '/posts', '/comments',  # JSONPlaceholder
            '/orders', '/customers', '/products', '/order_items',  # Business API
            '/data', '/items', '/records', '/entries'  # Generic
        ]
        
        available = []
        for endpoint in common_endpoints:
            try:
                data = self.fetch_sync(endpoint)
                if data and len(data) > 0:
                    available.append(endpoint)
                    logger.info(f"Found endpoint {endpoint}: {len(data)} records")
            except Exception:
                pass  # Endpoint not available, skip silently
        
        return available
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API fetching statistics."""
        return {
            'base_url': self.base_url,
            'timeout': self.timeout,
            'retries': self.retries,
            **self.stats
        }


class DataProcessor:
    """Utility class for processing API data."""
    
    @staticmethod
    def normalize_api_response(data: Any) -> List[Dict]:
        """Normalize various API response formats."""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        elif isinstance(data, str):
            try:
                parsed = json.loads(data)
                return DataProcessor.normalize_api_response(parsed)
            except json.JSONDecodeError:
                return []
        else:
            return []
    
    @staticmethod
    def merge_api_dataframes(dataframes: Dict[str, pd.DataFrame], 
                            join_keys: Dict[str, str]) -> pd.DataFrame:
        """Merge multiple API DataFrames based on join keys."""
        if not dataframes:
            return pd.DataFrame()
        
        # Start with the first DataFrame
        result = None
        for name, df in dataframes.items():
            if df.empty:
                continue
            
            if result is None:
                result = df.copy()
            else:
                join_key = join_keys.get(name, 'id')
                if join_key in df.columns and join_key in result.columns:
                    result = result.merge(df, on=join_key, how='left', suffixes=('', f'_{name}'))
        
        return result if result is not None else pd.DataFrame()


# Convenience functions
def fetch_api_data(base_url: str = None) -> Dict[str, pd.DataFrame]:
    """Quick API data fetch with default configuration."""
    fetcher = APIDataFetcher(base_url or "https://jsonplaceholder.typicode.com")
    return fetcher.fetch_all_data()

def export_api_data_to_csv(output_dir: str = "data/API", base_url: str = None) -> bool:
    """Export API data directly to CSV files."""
    fetcher = APIDataFetcher(base_url or "https://jsonplaceholder.typicode.com")
    return fetcher.export_to_csv(output_dir)

# Factory function for backward compatibility
def create_api_data_fetcher(base_url: str = None, timeout: int = 30, retries: int = 3):
    """Create an APIDataFetcher instance."""
    return APIDataFetcher(
        base_url or "https://jsonplaceholder.typicode.com",
        timeout, 
        retries
    )