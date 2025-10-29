# Python ETL Pipeline# Python ETL Project



**Production-ready ETL system** with modern GUI, complete MySQL integration, and robust data processing capabilities.A high-performance Python-based Extract, Transform, Load (ETL) pipeline featuring **modern PySide6 GUI interface**, **robust MySQL connectivity**, and **comprehensive data processing capabilities**. Built with Python 3.13, MySQL 8.0, and professional-grade error handling.



## 🚀 Quick Start## ✨ Key Features



```bash- 🖥️ **Modern PySide6 GUI Interface** with clean, icon-free professional design

# 1. Install dependencies- �️ **Complete MySQL Integration** with PyMySQL connector (Python 3.13 compatible)

pip install pandas pymysql cryptography PySide6 qt-material requests python-dotenv- 📊 **All 9 Database Tables** automatically created with proper schema

- 📁 **Smart File Management** - select files first, then load to data folder

# 2. Configure database (.env file)- � **Direct API-to-MySQL** insertion with comprehensive error handling

DB_USER=root- � **Dual Theme Support** - Dark cyan and Light blue themes

DB_PASSWORD=your_mysql_password  - ⚡ **Multi-threaded Operations** - UI never freezes during processing  

DB_HOST=127.0.0.1- 🛡️ **Data Validation** - NaN values properly handled for MySQL compatibility

DB_NAME=store_manager- 🔄 **Real-time Progress** tracking with detailed status messages

- 🎯 **Zero Cache Policy** - no __pycache__ files created

# 3. Launch GUI interface

python demo_gui.py## 📁 Project Structure

```

```

## ✨ Key FeaturesETL/

├── data/           # Data storage

- 🖥️ **Professional GUI** - PySide6 interface, icon-free design, dual themes│   ├── CSV/        # Original CSV data sources

- 🗄️ **Complete Database** - All 9 tables, 1,289+ records loaded successfully  │   └── API/        # API-generated CSV exports

- 🔄 **Direct API Integration** - Real-time API-to-MySQL processing├── gui/            # PySide6 GUI Interface

- ⚡ **Multi-threaded** - Non-blocking operations with progress tracking│   └── interface.py    # Main GUI application

- 🛡️ **Robust Data Handling** - Pandas 2.3.3 compatible, NaN→NULL conversion├── src/            # Source code modules

- 🎯 **Zero Cache** - Clean project structure, no __pycache__ files│   ├── connect.py      # Database connection utilities

│   ├── data_from_api.py # API client for data retrieval

## 📊 Current Status: ✅ FULLY OPERATIONAL│   ├── db_manager.py   # Core ETL engine with unified API methods

│   ├── main.py         # Main application entry point

```│   └── database/       # Modular database components

✅ Database Connection: PyMySQL + MySQL 8.0.43 working│       ├── connection_manager.py # Enhanced connection wrapper

✅ Schema Alignment: STOCKS (store_name FK), STAFFS (correct columns)  │       └── schema_manager.py     # Table schema definitions

✅ Data Loading: 1,289 CSV records across 6 tables├── tests/          # Test files and demonstrations

✅ GUI Interface: Professional design, all functions working│   ├── test_*.py           # Various test modules

✅ API Integration: Direct API-to-MySQL insertion operational│   └── run_tests.py        # Test runner script

✅ Error Handling: NaN values, pandas compatibility resolved├── demo_gui.py     # GUI demonstration script

```├── data_model.md   # Mermaid ER diagram documentation

├── .venv/          # Virtual environment (not tracked in git)

## 🖥️ GUI Interface├── .gitignore      # Git ignore rules

└── README.md       # This file

Launch with `python demo_gui.py` for:```



| Section | Features |## 🚀 Getting Started

|---------|----------|

| **Database** | Test connection, create all 9 tables |### Prerequisites

| **File Management** | Select → Load workflow for CSV files |  

| **Data Loading** | Import CSV data, load API data |- **Python 3.13.7** (tested and optimized)

| **Testing** | Validate CSV access, test API export |- **MySQL Server 8.0.43** (running and accessible)

| **Themes** | Toggle between dark cyan/light blue |- **pip package manager**



## 🔧 Command Line Usage### Required Packages

```bash

```bash# Database connectivity (Python 3.13 compatible)

# Complete ETL pipeline (CSV + API)PyMySQL>=1.1.2                 # Primary MySQL driver

python src/db_manager.pycryptography>=46.0.3           # Required for MySQL authentication



# API-only operations  # Core ETL dependencies  

python src/db_manager.py --api-direct    # Fastest methodpandas>=2.0.0                  # Data processing

python src/db_manager.py --api-streaming # Large datasetsrequests>=2.28.0               # API communication

python src/db_manager.py --api-csv       # Export to CSVpython-dotenv>=1.0.0          # Environment configuration



# Testing# GUI framework

cd tests && python run_tests.pyPySide6>=6.10.0               # Modern Qt6 interface

```qt-material                    # Material design themes



## 📁 Data Architecture# Optional (fallback)

mysql-connector-python>=9.5.0  # Alternative MySQL driver

### Database Schema (9 Tables)```

- **CSV Tables**: brands, categories, stores, staffs, products, stocks

- **API Tables**: customers, orders, order_items### Installation

- **Total Records**: 1,289+ successfully loaded

1. Clone this repository:

### Key Schema Updates ✅```bash

- **STOCKS**: Uses `store_name` (FK, not PK) instead of `store_id`git clone <repository-url>

- **STAFFS**: Columns aligned with CSV (`name`, `store_name`, `street`)cd ETL

```

## 🛠️ Technical Stack

2. Create and activate a virtual environment:

| Component | Version | Status |```bash

|-----------|---------|--------|# Create virtual environment

| **Python** | 3.13.7 | ✅ Optimized |python -m venv .venv

| **MySQL** | 8.0.43 | ✅ Connected |

| **PyMySQL** | 1.1.2 | ✅ Primary driver |# Activate virtual environment (Windows)

| **PySide6** | 6.10.0 | ✅ GUI framework |.venv\Scripts\activate

| **Pandas** | 2.3.3+ | ✅ Compatible |

# Activate virtual environment (macOS/Linux)

## 🔧 Recent Fixes (October 2025)source .venv/bin/activate

```

### Major Issues Resolved ✅

1. **Schema Mismatch**: Updated both `db_manager.py` and `schema_manager.py` to match CSV structure3. Install required dependencies:

2. **Pandas Compatibility**: Fixed `fillna()` issues with `df.where(pd.notna(df), None)`  ```bash

3. **Database Connection**: Migrated to PyMySQL for Python 3.13 compatibility# Install all dependencies at once

4. **Complete Data Loading**: All 1,289 CSV records now loading successfullypip install -r requirements.txt



### Performance Optimizations# Or install individually

- **Direct API-to-MySQL**: No intermediate CSV files requiredpip install pandas mysql-connector-python requests python-dotenv PySide6

- **Multi-threaded GUI**: Operations never block the interface```

- **Intelligent NaN Handling**: Proper NULL conversion for MySQL

- **Cache Prevention**: System-wide `__pycache__` elimination4. Configure database connection:

```bash

## 🎯 Usage Workflows# Edit .env file with your MySQL credentials

# Example .env content:

### CSV Data ImportDB_USER=root

1. Launch GUI → Test DB Connection → Create TablesDB_PASSWORD=your_mysql_password

2. Select CSV Files → Load Selected Files  DB_HOST=127.0.0.1

3. Import CSV Data → Monitor progressDB_NAME=store_manager



### API Data Processing  # The application will create the database if it doesn't exist

1. Configure API URL → Test connection```

2. Create database tables → Load API data

3. Direct insertion to MySQL (no CSV files)## ⚡ Quick Start



### Testing & Validation### Option 1: GUI Interface (Recommended)

- **GUI Testing**: Use built-in test buttons for comprehensive validation```bash

- **Command Line**: `python tests/run_tests.py` for automated testing# Launch the modern PySide6 GUI interface

python demo_gui.py

## 📞 Support

# Direct GUI launch (alternative)

- **Project**: Advanced Python ETL Pipeline with GUIpython gui/interface.py

- **Maintainer**: Andy Sylvia Rosenvold  ```

- **Status**: Production ready, all major issues resolved

- **Last Updated**: October 29, 2025### Current Status: ✅ FULLY OPERATIONAL

- **Database Connection**: ✅ Working (PyMySQL + MySQL 8.0.43)

---- **All 9 Tables**: ✅ Created with correct schema (1,289 CSV rows loaded)

- **Schema Updates**: ✅ STOCKS uses store_name (not store_id), STAFFS has correct columns

**🎉 System fully operational with 1,289+ records successfully processed!**- **GUI Interface**: ✅ Icon-free professional design with material themes
- **Data Processing**: ✅ Pandas 2.3.3 compatibility, NaN→NULL conversion working
- **API Integration**: ✅ Direct API-to-MySQL insertion operational

### Option 2: Command Line (Advanced)
```bash
# Database table creation
python src/db_manager.py

# Test specific functionality
cd tests && python run_tests.py
```

## 🖥️ GUI Interface Usage

### Quick Start - GUI Mode

Launch the modern PySide6 interface for easy ETL management:

```bash
# Start the GUI interface
python gui/interface.py

# Or run the demo
python demo_gui.py
```

### GUI Features

The **ETL Pipeline Manager** provides a professional interface with:

| Section | Features | Description |
|---------|----------|-------------|
| **API Configuration** | URL input + Test button | Test API connections (default: https://etl-server.fly.dev) |
| **Database Operations** | Connection test + Table creation | Validate MySQL connection and create all 9 tables |
| **File Management** | Select → Load workflow | Choose CSV files, then click "Load Selected Files" |
| **Data Loading** | CSV + API data import | Multi-threaded loading with progress feedback |
| **Test Operations** | CSV access + API export | Comprehensive testing and validation |
| **Theme Settings** | Dark/Light toggle | Switch between dark cyan and light blue themes |

### GUI Workflow (Updated)

1. **Test Database Connection**: ✅ Should work immediately with your configured MySQL
2. **Create Tables**: ✅ Creates all 9 tables with proper foreign key relationships  
3. **Select CSV Files**: Choose files from computer (NOT copied yet)
4. **Load Selected Files**: Click "Load" button to copy files to `data/CSV/`
5. **Import Data**: Use "Load CSV Data" to insert into database
6. **Monitor Progress**: Real-time status updates in output window

### Recent Improvements ✨ (October 2025)

- **✅ Schema Alignment**: Updated STOCKS (store_name FK) and STAFFS (name, store_name, street columns) 
- **✅ Pandas 2.3.3 Compatibility**: Fixed `fillna()` issues with `df.where(pd.notna(df), None)`
- **✅ Complete Data Loading**: All 1,289 CSV records loading successfully
- **✅ Modular Schema Manager**: Both db_manager.py and schema_manager.py synchronized
- **✅ Professional GUI**: Icon-free design with dark cyan/light blue themes
- **✅ Zero Cache Policy**: Automatic __pycache__ prevention system-wide

## 🔧 Command Line Usage

### Quick Start - Direct API-to-MySQL

Your ETL pipeline **already does direct API-to-MySQL insertion**! No CSV conversion needed.

```bash
# Standard method (current default)
python src/db_manager.py --api-only

# High-performance streaming (for large datasets)
python src/db_manager.py --api-streaming

# Maximum speed direct JSON insertion
python src/db_manager.py --api-direct

# Get help with all options
python src/db_manager.py --help
```

### Available Insertion Methods

| Method | Command | Performance | Memory Usage | Use Case |
|--------|---------|-------------|--------------|----------|
| **Standard** | `--api-only` | ⭐⭐⭐ Good | Moderate | Development, general use |
| **Streaming** | `--api-streaming` | ⭐⭐⭐⭐ Great | Low | Large datasets (>10K records) |
| **Direct JSON** | `--api-direct` | ⭐⭐⭐⭐⭐ Fastest | Minimal | Production, maximum speed |

### Data Flow Options

```
❌ INEFFICIENT: API → CSV File → Read CSV → DataFrame → MySQL
✅ YOUR SETUP:  API → DataFrame → MySQL (Direct!)
⚡ OPTIMIZED:   API → Raw JSON → MySQL (Even faster!)
```

### Project Components

- **Extract**: Direct API data retrieval with error handling
- **Transform**: Pandas-based data cleaning and validation
- **Load**: Multiple MySQL insertion strategies for optimal performance

## 📊 Data Sources

### API Endpoints
- **Customers API**: Customer information and profiles
- **Orders API**: Order transactions and details  
- **Order Items API**: Individual order line items

### CSV Data Files
- **Products**: Product catalog with categories and brands
- **Stores**: Store locations and information
- **Staff**: Employee and staff data
- **Inventory**: Stock levels and availability

### MySQL Database
- **Schema**: `store_manager` with InnoDB engine
- **Tables**: Automated creation for all data sources
- **Performance**: Optimized indexes and constraints

## 🛠️ Development

### Setting Up Development Environment

1. Follow the installation steps above
2. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # if you have dev dependencies
```

### Code Structure

- Place reusable modules in the `src/` directory
- Keep data processing scripts in the `data/` directory
- Follow PEP 8 style guidelines

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
- `config/dev.ini` - Development settings
- `config/prod.ini` - Production settings

**Note**: Configuration files are ignored by git to protect sensitive information.

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
- **Driver**: PyMySQL (primary), mysql-connector-python (fallback)
- **Database**: `store_manager` (auto-created if missing)
- **Tables**: 9 tables with proper foreign key relationships
- **Authentication**: Supports MySQL 8.0 caching_sha2_password

### Current Connection Status ✅
```
✅ MySQL 8.0.43 - Running
✅ PyMySQL 1.1.2 - Installed  
✅ Database 'store_manager' - Ready
✅ All 9 tables - Created
✅ Password authentication - Working
```

## 📈 Monitoring and Logging

The ETL pipeline includes:
- Detailed logging for debugging and monitoring
- Error handling and recovery mechanisms
- Performance metrics tracking

Logs are stored in the `logs/` directory (ignored by git).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Project Maintainer**: Andy Sylvia Rosenvold
- **Email**: [andy.rosenvold@specialisterne.com]
- **Repository**: [Repository URL](https://github.com/Sylverose)

### Insertion Method Performance
| Method | Speed | Memory | Recommended For |
|--------|-------|--------|-----------------|
| Standard | Good | Moderate | Development, testing |
| Streaming | Great | Low | Large datasets, production |
| Direct JSON | Fastest | Minimal | High-performance scenarios |

## 🚀 Quick Command Reference

```bash
# GUI Interface (Recommended)
python gui/interface.py          # Launch GUI interface
python demo_gui.py               # Run GUI demo with instructions

# Command Line Interface
python src/db_manager.py --help  # Show all available options
python src/db_manager.py         # Complete ETL pipeline (CSV + API)
python src/db_manager.py --api-direct    # API-to-MySQL only (fastest)
python src/db_manager.py --api-csv       # Export API data to CSV files
python src/db_manager.py --api-streaming # Streaming insertion for large data

# Testing
cd tests && python run_tests.py  # Run all core functionality tests
```

## 🔧 Recent Fixes & Updates

### Schema Mismatch Issues - RESOLVED ✅ (Latest Fix)
- **Issue**: "Unknown column 'name'" errors during data insertion
- **Root Cause**: CSV files had different column structure than database schema
- **Solution**: Updated both db_manager.py and schema_manager.py schemas:
  - STAFFS: `first_name → name`, `store_id → store_name`, added `street` column
  - STOCKS: `store_id → store_name` (FK only, not PK), updated primary key structure
- **Result**: All 1,289 CSV rows loading successfully (9+7+3+10+321+939 records)

### Pandas 2.3.3 Compatibility - RESOLVED ✅
- **Issue**: `fillna(value=None)` failing with "Must specify a fill 'value' or 'method'"
- **Solution**: Replaced with `df.where(pd.notna(df), None)` for proper NaN→NULL conversion
- **Result**: Clean data processing without pandas version conflicts

### Database Connection Issues - RESOLVED ✅
- **Issue**: MySQL connection failures with Python 3.13
- **Solution**: Migrated to PyMySQL driver with cryptography support
- **Result**: Stable connection to MySQL 8.0.43

### Complete Table Creation - RESOLVED ✅  
- **Issue**: Only 4/9 tables being created, schema mismatches
- **Solution**: Updated `create_all_tables_from_csv()` + synchronized modular schemas
- **Result**: All 9 tables created with correct column mappings

### GUI File Management - IMPROVED ✅
- **Issue**: Files copied immediately upon selection
- **Solution**: Separated "Select" and "Load" operations
- **Result**: Better user control over file operations

### Cache Management - OPTIMIZED ✅
- **Feature**: Automatic __pycache__ prevention
- **Implementation**: `sys.dont_write_bytecode = True`
- **Result**: Clean project directory

---

*Last updated: October 29, 2025 - All major issues resolved, ETL pipeline fully operational*