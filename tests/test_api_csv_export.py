"""Test API data export to CSV files."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.data_from_api import APIClient
from database.db_manager import DatabaseManager, create_api_tables_and_csv

def test_api_csv_export():
    """Test the API CSV export functionality."""
    print("Testing API CSV Export Functionality")
    print("="*50)
    
    # Method 1: Using API client directly
    print("\nMethod 1: Direct API Client CSV Export")
    client = APIClient()
    
    try:
        success = client.save_all_api_data_to_csv()
        client.close()
        
        if success:
            print("SUCCESS: Direct API CSV export successful!")
        else:
            print("ERROR: Direct API CSV export failed!")
            
    except Exception as e:
        print(f"ERROR: Error in direct API export: {e}")
    
    # Method 2: Using database manager
    print("\nMethod 2: Database Manager CSV Export")
    db_manager = DatabaseManager()
    
    try:
        success = db_manager.export_api_data_to_csv()
        
        if success:
            print("SUCCESS: Database manager CSV export successful!")
        else:
            print("ERROR: Database manager CSV export failed!")
            
    except Exception as e:
        print(f"ERROR: Error in database manager export: {e}")
    
    # Check if files were created
    print("\nChecking CSV Files in data/API/:")
    api_dir = os.path.join('..', 'data', 'API')
    
    if os.path.exists(api_dir):
        files = os.listdir(api_dir)
        csv_files = [f for f in files if f.endswith('.csv')]
        
        if csv_files:
            print(f"SUCCESS: Found {len(csv_files)} CSV files:")
            for file in sorted(csv_files):
                file_path = os.path.join(api_dir, file)
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"  {file:<20} ({size:,} bytes)")
        else:
            print("ERROR: No CSV files found in API directory")
    else:
        print("ERROR: API directory does not exist")

if __name__ == "__main__":
    test_api_csv_export()