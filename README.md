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

- Python 3.11+ (recommended: 3.13.7)
- MySQL Server 8.0+
- Dependencies: `pip install -r requirements.txt`

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
├── data/           # Data storage
│   ├── CSV/        # Original CSV data sources
│   ├── API/        # API-generated CSV exports  
│   ├── data_model.md       # Mermaid ER diagram documentation
│   └── etl_data_model_diagram.mmd  # Database schema diagram
├── gui/            # PySide6 GUI Interface
│   ├── main_window.py      # Main GUI application
│   └── themes/             # Theme system (dark/light modes)
├── src/            # Source code modules
│   ├── connect.py          # Database connection management
│   ├── cache_cleaner.py    # Cache management
│   ├── logging_system.py   # Structured logging system
│   ├── main.py             # Main application entry point
│   ├── api/                # Async API client package
│   │   ├── api_client.py   # Core HTTP client
│   │   ├── api_models.py   # Request/response models
│   │   ├── rate_limiter.py # Rate limiting functionality
│   │   ├── retry_handler.py # Retry logic
│   │   ├── data_processor.py # Response processing
│   │   └── convenience.py  # Helper functions
│   ├── exceptions/         # ETL exception handling package
│   │   ├── base_exceptions.py      # Core exception classes
│   │   ├── database_exceptions.py  # Database-related errors
│   │   ├── validation_exceptions.py # Data validation errors
│   │   ├── api_exceptions.py       # API and HTTP errors
│   │   ├── processing_exceptions.py # Data processing errors
│   │   ├── system_exceptions.py    # System and config errors
│   │   ├── exception_factories.py  # Exception factory functions
│   │   └── decorators.py          # Exception handling decorators
│   ├── config/             # Configuration modules
│   │   ├── api.py          # API configuration
│   │   ├── database.py     # Database configuration
│   │   └── environments.py # Environment management
│   └── database/           # Database modules
│       ├── __init__.py             # Module exports
│       ├── db_manager.py           # Core ETL engine
│       ├── connection_manager.py   # Connection handling
│       ├── schema_manager.py       # Schema definitions
│       ├── data_validator.py       # Data validation
│       ├── data_from_api.py       # API client
│       └── pandas_optimizer.py    # Pandas operations
├── tests/          # Test files and demonstrations
│   ├── test_*.py           # Various test modules
│   └── run_tests.py        # Test runner script
├── logs/           # Application logs (auto-generated)
├── run_gui.py      # GUI launcher with demo information
├── .env.example    # Environment configuration template
├── .venv/          # Virtual environment (not tracked in git)
├── .gitignore      # Git ignore rules
├── requirements.txt # Dependency specifications
└── README.md       # This file
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
- **Modular Architecture**: ✅ API client and exceptions packages fully modularized
- **GUI Interface**: ✅ Professional PySide6 interface with theme system
- **Data Processing**: ✅ Pandas with proper NaN→NULL conversion for MySQL
- **API Integration**: ✅ Smart endpoint detection with multiple server support
- **Error Handling**: ✅ Comprehensive exception system with recovery suggestions

### Quick Start - GUI Mode
Launch the modern PySide6 interface for easy ETL management:

```bash
# Start the GUI interface  
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
# Run the main ETL pipeline
python src/main.py

# Direct database operations
python src/database/db_manager.py

# Test database connectivity
python -c "from src.database.db_manager import DatabaseManager; db = DatabaseManager(); print('Connection:', db.test_connection())"
```

### API Client Usage
```bash
# Test API connectivity
python -c "from src.database.data_from_api import APIDataFetcher; api = APIDataFetcher('https://jsonplaceholder.typicode.com'); print('Data:', len(api.fetch_data('users')))"

# Export API data to CSV
python -c "from src.database.data_from_api import export_api_data_to_csv; export_api_data_to_csv()"
```

### Architecture Benefits
```
✅ MODULAR:     API Package → Database Package → Exception Handling
✅ RESILIENT:   Smart endpoint detection with automatic fallbacks  
✅ COMPATIBLE:  Works with multiple API server architectures
⚡ EFFICIENT:   Direct pandas DataFrame to MySQL with NaN handling
```

### Project Components
• Extract: Direct API data retrieval with error handling
• Transform: Pandas-based data cleaning and validation
• Load: Multiple MySQL insertion strategies for optimal performance

## 📊 Data Sources

### API Integration
- **Smart Endpoint Detection**: Automatically detects and maps API endpoints
- **Multiple Server Support**: Works with different API architectures
  - JSONPlaceholder API (`/users`, `/posts`, `/comments`)  
  - ETL Server API (`/customers`, `/orders`, `/products`)
- **Fallback Logic**: Tries multiple endpoint variations (`/api/orders`, `/order`, etc.)
- **Error Recovery**: Graceful handling of 404s and server errors

### CSV Data Processing
- **Products**: Product catalog with categories and brands
- **Stores**: Store locations and contact information
- **Staff**: Employee and management data
- **Inventory**: Stock levels and availability tracking
- **NaN Handling**: Automatic conversion of pandas NaN to MySQL NULL

### MySQL Database Schema
- **Engine**: InnoDB with foreign key constraints
- **Tables**: 9 tables with proper relationships and indexes
- **Performance**: Batch processing and connection pooling
- **Validation**: Automatic schema alignment and data validation

## 🛠️ Development

### Setting Up Development Environment
1. Follow the installation steps above
2. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # if you have dev dependencies
```

### Code Structure
• Place reusable modules in the `src/` directory
• Keep data processing scripts in the `data/` directory
• Follow PEP 8 style guidelines

### Testing
Run comprehensive tests:
```bash
# All tests and demonstrations
cd tests
python run_tests.py

# Individual test categories
python test_simplification.py      # Code improvement validation
python test_api_direct_mysql.py    # API-to-MySQL method testing
python api_mysql_examples.py       # Usage examples
python complete_api_overview.py    # Full capabilities demo
```

## 📋 Configuration
Create configuration files for different environments:

• `config/dev.ini` - Development settings
• `config/prod.ini` - Production settings

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
- **Primary Driver**: PyMySQL (with mysql-connector-python fallback)
- **Database**: `store_manager` (auto-created if missing)
- **Schema**: 9 tables with proper foreign key relationships
- **Authentication**: MySQL 8.0+ caching_sha2_password support
- **Connection Pooling**: Configurable connection management
- **Error Recovery**: Automatic reconnection with exponential backoff

### Dependencies Management
```
✅ PyMySQL - Primary MySQL connector
✅ PySide6 - Modern GUI framework  
✅ Pandas - Data processing and transformation
✅ Requests/aiohttp - API client functionality
✅ Structured exception handling system
```

## 📈 Error Handling and Monitoring

### Exception Management System
The ETL pipeline features a comprehensive exception handling system:

- **Modular Exception Packages**: Organized by error type (database, API, validation, system)
- **Smart Error Recovery**: Automatic retry logic with exponential backoff
- **Contextual Error Information**: Detailed error context with recovery suggestions
- **Structured Logging**: JSON-structured logs with correlation IDs

### Monitoring Features
- **Real-time Progress Tracking**: GUI progress bars and status updates
- **Performance Metrics**: Memory usage monitoring and optimization suggestions
- **Connection Health**: Automatic database and API connectivity monitoring
- **Data Validation**: Schema validation with detailed mismatch reporting

Logs are stored in the `logs/` directory with structured JSON format for easy parsing.

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
# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import PySide6, pandas, pymysql; print('✅ Ready to go!')"

# Configure database connection (create .env file)
echo "DB_USER=root" > .env
echo "DB_PASSWORD=your_password" >> .env
echo "DB_HOST=127.0.0.1" >> .env
echo "DB_NAME=store_manager" >> .env
```

### GUI Interface (Recommended)
```bash
python gui/main_window.py       # Launch modern ETL GUI interface
```

### Command Line Interface
```bash
python src/main.py              # Main ETL pipeline entry point
python src/database/db_manager.py  # Direct database operations

# Test specific components
python -c "from src.database.db_manager import DatabaseManager; print('DB OK:', DatabaseManager().test_connection())"
python -c "from src.database.data_from_api import APIDataFetcher; print('API OK:', len(APIDataFetcher().fetch_data('users')) > 0)"
```

### Testing & Verification
```bash
cd tests && python run_tests.py  # Run comprehensive test suite
python src/cache_cleaner.py      # Clean project cache files

# Individual component tests
python -c "from src.exceptions import ETLException, DatabaseError; print('Exception system loaded')"
python -c "from src.api import AsyncAPIClient; print('API client loaded')"
```



