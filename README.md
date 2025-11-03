# Python ETL Pipeline Manager

Professional ETL pipeline with modern PySide6 GUI interface, comprehensive error handling, and MySQL connectivity.

## Features

- **Modern PySide6 GUI** with professional dark/light themes
- **MySQL database integration** (9 tables with proper schema)
- **Intelligent API client** with automatic endpoint detection and fallback
- **Comprehensive exception handling** with structured error management
- **Multi-threaded operations** with progress tracking
- **CSV and API data processing** with NaN→NULL conversion
- **Modular architecture** with separated concerns for maintainability

## Requirements

### System Requirements
- **Python**: 3.11+ (recommended: 3.13.7)
- **MySQL Server**: 8.0+

### Python Dependencies
**Core ETL Dependencies:**
```
pandas>=2.0.0                    # Data processing and transformation
mysql-connector-python>=8.0.0   # MySQL database connectivity  
requests>=2.28.0                 # HTTP client for API calls
python-dotenv>=1.0.0             # Environment configuration
```

**GUI Dependencies:**
```
PySide6>=6.0.0                   # Modern Qt-based GUI framework
```

**Optional Dependencies:**
```
# Memory monitoring (provides better memory usage stats)
psutil>=5.9.0

# Development dependencies  
pytest>=7.0.0                   # For extended testing
black>=22.0.0                   # Code formatting
flake8>=5.0.0                   # Code linting
```

**Quick Install:**
```bash
pip install -r requirements.txt
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure database (.env file in project root)
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_NAME=store_manager
```

## Usage

```bash
# Launch GUI
python run_gui.py

# Command line
python src/main.py
```

## Project Structure

```
ETL/
├── data/                          # Data storage
│   ├── CSV/                       # Original CSV data sources
│   │   ├── brands.csv
│   │   ├── categories.csv
│   │   ├── products.csv
│   │   ├── staffs.csv
│   │   ├── stocks.csv
│   │   └── stores.csv
│   ├── API/                       # API-generated CSV exports
│   │   ├── customers.csv
│   │   ├── order_items.csv
│   │   └── orders.csv
│   ├── data_model.md              # Data model documentation
│   └── etl_data_model_diagram.mmd # ER diagram
├── gui/                           # PySide6 GUI Interface
│   ├── main_window.py             # Main application
│   └── themes/                    # Theme system (dark/light)
│       ├── __init__.py
│       ├── base_theme.py
│       ├── dark_theme.py
│       ├── light_theme.py
│       └── theme_manager.py
├── src/                           # Source modules
│   ├── connect.py                 # Connection management
│   ├── cache_cleaner.py           # Cache cleanup
│   ├── logging_system.py          # Logging infrastructure
│   ├── main.py                    # Entry point
│   ├── api/                       # API client package
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── api_models.py
│   │   ├── convenience.py
│   │   ├── data_processor.py
│   │   ├── rate_limiter.py
│   │   ├── retry_handler.py
│   │   └── example_usage.py
│   ├── config/                    # Configuration
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── database.py
│   │   └── environments.py
│   ├── exceptions/                # Exception handling
│   │   ├── __init__.py
│   │   ├── api_exceptions.py
│   │   ├── base_exceptions.py
│   │   ├── database_exceptions.py
│   │   ├── decorators.py
│   │   ├── exception_factories.py
│   │   ├── processing_exceptions.py
│   │   ├── system_exceptions.py
│   │   ├── validation_exceptions.py
│   │   └── example_usage.py
│   └── database/                  # Database operations
│       ├── __init__.py
│       ├── db_manager.py          # Core orchestration
│       ├── connection_manager.py  # Connection handling
│       ├── csv_operations.py      # CSV import/export
│       ├── data_from_api.py       # API data fetching
│       ├── data_validator.py      # Data validation
│       ├── pandas_optimizer.py    # Pandas operations
│       ├── schema_manager.py      # Schema definitions
│       ├── batch_operations/      # Batch processing
│       │   ├── __init__.py
│       │   ├── base_processor.py
│       │   ├── batch_processor.py
│       │   ├── delete_processor.py
│       │   ├── insert_processor.py
│       │   ├── update_processor.py
│       │   └── upsert_processor.py
│       └── utilities/             # Database utilities
│           ├── __init__.py
│           ├── config_utils.py
│           ├── context_managers.py
│           ├── data_utils.py
│           ├── database_utils.py
│           └── operation_stats.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── run_tests.py
│   ├── test_api_csv_export.py
│   └── test_csv_access.py
├── logs/                          # Application logs
│   └── etl_structured.json
├── .venv/                         # Virtual environment (ignored)
├── __pycache__/                   # Python cache (ignored)
├── clean_logs.ps1                 # Log cleanup script
├── run_gui.py                     # GUI launcher
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## Database Configuration

Create `.env` file in project root:
```
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_NAME=store_manager
```

The application automatically creates the database and tables if they don't exist.

## Current Status: ✅ FULLY OPERATIONAL

### System Health
- **Database Connection**: ✅ Working (PyMySQL with MySQL 8.0+)
- **Modular Architecture**: ✅ Organized by concern with clear separation
- **GUI Interface**: ✅ Professional PySide6 interface with theme system
- **Data Processing**: ✅ Pandas with proper NaN→NULL conversion for MySQL
- **API Integration**: ✅ Smart endpoint detection with multiple server support
- **Error Handling**: ✅ Comprehensive exception system with recovery suggestions

### Quick Start - GUI Mode
Launch the modern PySide6 interface for easy ETL management:

```bash
python gui/main_window.py
```

### Database Schema
- **9 Tables**: Complete schema with proper relationships
- **MySQL Compatibility**: Full InnoDB support with foreign keys
- **Data Validation**: Automated schema alignment and validation
- **Performance**: Optimized indexes and batch processing

### GUI Features

The ETL Pipeline Manager provides a professional interface with:

| Section | Features | Description |
|---------|----------|-------------|
| **API Configuration** | Smart URL handling + Connection testing | Supports multiple API servers (etl-server.fly.dev, jsonplaceholder.typicode.com) |
| **Database Operations** | Connection validation + Schema creation | MySQL connectivity testing and automatic table creation |
| **File Management** | CSV selection and loading | Drag-and-drop style file selection with batch processing |
| **Data Processing** | Multi-threaded ETL operations | Real-time progress tracking with error recovery |
| **Testing Suite** | Comprehensive validation tools | API endpoint testing, CSV validation, and connectivity checks |
| **Theme System** | Professional dark/light themes | Material design themes with proper contrast ratios |


## 🔧 Command Line Usage

### Database Manager Operations
```bash
python src/main.py
python src/database/db_manager.py
python -c "from src.database.db_manager import DatabaseManager; db = DatabaseManager(); print('Connection:', db.test_connection())"
```

### API Client Usage
```bash
python -c "from src.database.data_from_api import APIDataFetcher; api = APIDataFetcher('https://jsonplaceholder.typicode.com'); print('Data:', len(api.fetch_data('users')))"
python -c "from src.database.data_from_api import export_api_data_to_csv; export_api_data_to_csv()"
```

### Architecture Benefits
```
✅ MODULAR:     Organized by concern with clear interfaces
✅ RESILIENT:   Smart endpoint detection with automatic fallbacks  
✅ COMPATIBLE:  Works with multiple API server architectures
⚡ EFFICIENT:   Direct pandas DataFrame to MySQL with NaN handling
```

### Project Components
Extract → Transform → Load architecture for efficient data pipeline

## 📊 Data Sources

### API Integration
- **Smart Endpoint Detection**: Automatically detects and maps API endpoints
- **Multiple Server Support**: Works with different API architectures
- **Fallback Logic**: Tries multiple endpoint variations
- **Error Recovery**: Graceful handling of 404s and server errors

### CSV Data Processing
- **Products**: Product catalog with categories and brands
- **Stores**: Store locations and contact information
- **Staff**: Employee and management data
- **Inventory**: Stock levels and availability tracking
- **NaN Handling**: Automatic conversion to MySQL NULL

### MySQL Database Schema
- **Engine**: InnoDB with foreign key constraints
- **Tables**: 9 tables with proper relationships and indexes
- **Performance**: Batch processing and connection pooling
- **Validation**: Automatic schema alignment and data validation

## 🛠️ Development

### Setting Up Development Environment
1. Follow the installation steps above
2. Install development dependencies as needed

### Code Structure
Place reusable modules in the `src/` directory, keep data processing scripts in the `data/` directory.

### Testing
```bash
cd tests
python run_tests.py
```

## 📋 Configuration
Create configuration files for different environments as needed.

Note: Configuration files are ignored by git to protect sensitive information.

## 🔒 Database Configuration
The ETL pipeline connects to MySQL using `.env` configuration:

```bash
# .env file (create in project root)
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_NAME=store_manager
```

### Connection Details
- **Primary Driver**: PyMySQL
- **Database**: `store_manager` (auto-created if missing)
- **Schema**: 9 tables with proper foreign key relationships
- **Connection Pooling**: Configurable connection management

### Dependencies Management
```
✅ PyMySQL - MySQL connector
✅ PySide6 - GUI framework  
✅ Pandas - Data processing
✅ Requests - API functionality
✅ Structured exception handling
```

## 📈 Error Handling and Monitoring

### Exception Management System
- **Modular Exception Packages**: Organized by error type
- **Smart Error Recovery**: Automatic retry logic with exponential backoff
- **Contextual Error Information**: Detailed error context with recovery suggestions
- **Structured Logging**: JSON-structured logs with correlation IDs

### Monitoring Features
- **Real-time Progress Tracking**: GUI progress bars and status updates
- **Performance Metrics**: Memory usage monitoring
- **Connection Health**: Automatic database and API connectivity monitoring
- **Data Validation**: Schema validation with detailed reporting

Logs are stored in the `logs/` directory with structured JSON format.

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/Sylverose/Advanced-Python-ETL-Pipeline-with-GUI/blob/main/LICENSE) file for details.

## 📞 Contact
• Project Maintainer: Andy Sylvia Rosenvold
• Email: [andy.rosenvold@specialisterne.com](mailto:andy.rosenvold@specialisterne.com)
• Repository: [Repository URL](https://github.com/Sylverose/Advanced-Python-ETL-Pipeline-with-GUI)



## 🚀 Quick Command Reference

### Installation & Setup
```bash
pip install -r requirements.txt
python -c "import PySide6, pandas, pymysql; print('✅ Ready to go!')"
echo "DB_USER=root" > .env
echo "DB_PASSWORD=your_password" >> .env
echo "DB_HOST=127.0.0.1" >> .env
echo "DB_NAME=store_manager" >> .env
```

### GUI Interface
```bash
python gui/main_window.py
```

### Command Line
```bash
python src/main.py
python src/database/db_manager.py
python -c "from src.database.db_manager import DatabaseManager; print('DB OK:', DatabaseManager().test_connection())"
python -c "from src.database.data_from_api import APIDataFetcher; print('API OK:', len(APIDataFetcher().fetch_data('users')) > 0)"
```

### Testing
```bash
cd tests && python run_tests.py
python src/cache_cleaner.py
```



