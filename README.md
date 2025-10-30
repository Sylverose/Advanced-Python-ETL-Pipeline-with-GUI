# Python ETL Project

A high-performance Python-based Extract, Transform, Load (ETL) pipeline
featuring modern PySide6 GUI interface, robust MySQL connectivity, and comprehensive data processing capabilities. Built with Python 3.13, MySQL 8.0, and professional-grade error handling.

## ✨ Key Features

- 🖥️ **Professional GUI** - PySide6 interface, icon-free design, dual themes
- 🗄️ **Complete Database** - All 9 tables, 1,289+ records loaded successfully  
- 🔄 **Direct API Integration** - Real-time API-to-MySQL processing
- ⚡ **Multi-threaded** - Non-blocking operations with progress tracking
- 🛡️ **Robust Data Handling** - Pandas 2.3.3 compatible, NaN→NULL conversion
- 🎯 **Zero Cache** - Clean project structure, no __pycache__ files

## 📊 Current Status: ✅ FULLY OPERATIONAL

```
✅ Database Connection: PyMySQL + MySQL 8.0.43 working
✅ Schema Alignment: STOCKS (store_name FK), STAFFS (correct columns)  
✅ Data Loading: 1,289 CSV records across 6 tables
✅ GUI Interface: Professional design, all functions working
✅ API Integration: Direct API-to-MySQL insertion operational
✅ Error Handling: NaN values, pandas compatibility resolved
```

## 🖥️ GUI Interface

Launch with `python demo_gui.py` for:

| Section | Features |
|---------|----------|
| **Database** | Test connection, create all 9 tables |
| **File Management** | Select → Load workflow for CSV files |
| **Data Loading** | Import CSV data, load API data |
| **Testing** | Validate CSV access, test API export |
| **Themes** | Toggle between dark cyan/light blue |

## 🛠️ Technical Stack

| Component | Version | Status |
|-----------|---------|--------|
| Python | 3.13.7 | ✅ Optimized |
| MySQL | 8.0.43 | ✅ Connected |
| PyMySQL | 1.1.2 | ✅ Primary driver |
| PySide6 | 6.10.0 | ✅ GUI framework |
| Pandas | 2.3.3+ | ✅ Compatible |

## 🔧 Recent Fixes (October 2025)

### Major Issues Resolved ✅

1. **Schema Mismatch**: Updated both `db_manager.py` and `schema_manager.py` to match CSV structure
2. **Pandas Compatibility**: Fixed `fillna()` issues with `df.where(pd.notna(df), None)`  
3. **Database Connection**: Migrated to PyMySQL for Python 3.13 compatibility
4. **Complete Data Loading**: All 1,289 CSV records now loading successfully

### Performance Optimizations
- **Direct API-to-MySQL**: No intermediate CSV files required
- **Multi-threaded GUI**: Operations never block the interface
- **Intelligent NaN Handling**: Proper NULL conversion for MySQL
- **Cache Prevention**: System-wide `__pycache__` elimination

## 🎯 Usage Workflows

### CSV Data Import
1. Launch GUI → Test DB Connection → Create Tables
2. Select CSV Files → Load Selected Files  
3. Import CSV Data → Monitor progress

### API Data Processing
1. Configure API URL → Test connection
2. Create database tables → Load API data
3. Direct insertion to MySQL (no CSV files)

### Testing & Validation
- **GUI Testing**: Use built-in test buttons for comprehensive validation
- **Command Line**: `python tests/run_tests.py` for automated testing

## 📁 Project Structure

```
ETL/
├── data/           # Data storage
│   ├── CSV/        # Original CSV data sources
│   └── API/        # API-generated CSV exports
├── gui/            # PySide6 GUI Interface
│   └── main_window.py  # Main GUI application
├── src/            # Source code modules
│   ├── connect.py      # Database connection utilities
│   ├── data_from_api.py # API client for data retrieval
│   ├── db_manager.py   # Core ETL engine with unified API methods
│   ├── main.py         # Main application entry point
│   └── database/       # Modular database components
│       ├── connection_manager.py # Enhanced connection wrapper
│       └── schema_manager.py     # Table schema definitions
├── tests/          # Test files and demonstrations
│   ├── test_*.py           # Various test modules
│   └── run_tests.py        # Test runner script
├── run_gui.py      # GUI launcher with demo information
├── data_model.md   # Mermaid ER diagram documentation
├── .venv/          # Virtual environment (not tracked in git)
├── .gitignore      # Git ignore rules
└── README.md       # This file
```

## 🚀 Getting Started

### Prerequisites
  
- **Python 3.13.7** (tested and optimized)
- **MySQL Server 8.0.43** (running and accessible)
- **pip package manager**

### Required Packages

```bash
# Database connectivity (Python 3.13 compatible)
PyMySQL>=1.1.2                 # Primary MySQL driver
cryptography>=46.0.3           # Required for MySQL authentication

# Core ETL dependencies  
pandas>=2.0.0                  # Data processing
requests>=2.28.0               # API communication
python-dotenv>=1.0.0          # Environment configuration

# GUI framework
PySide6>=6.10.0               # Modern Qt6 interface
qt-material>=2.17             # Material design themes

# Optional (fallback)
mysql-connector-python>=9.5.0  # Alternative MySQL driver
```

> **Important**: If you have multiple Python installations, use `python -m pip install` instead of just `pip install` to ensure packages are installed in the correct Python environment.

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd ETL
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate
```

3. Install required dependencies:
```bash
# Install all dependencies at once
pip install -r requirements.txt

# Or install individually (recommended for multiple Python installations)
python -m pip install PySide6 pandas PyMySQL requests python-dotenv qt-material cryptography
```

4. Configure database connection:
```bash
# Edit .env file with your MySQL credentials
# Example .env content:
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_NAME=store_manager

# The application will create the database if it doesn't exist
```

## ⚡ Quick Start

### Option 1: GUI Interface (Recommended)
```bash
# Launch with demo information and usage guide
python run_gui.py

# Direct GUI launch (no demo information)
python gui/main_window.py
```

> **Note**: If you encounter "No module named 'PySide6'" errors, install the required packages:
> ```bash
> python -m pip install PySide6 pandas PyMySQL requests python-dotenv qt-material cryptography
> ```

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
# Start the GUI interface with demo information
python run_gui.py

# Or launch GUI directly
python gui/main_window.py 
```

### Current Status: ✅ FULLY OPERATIONAL

- **Database Connection**: ✅ Working (PyMySQL + MySQL 8.0.43)
- **All 9 Tables**: ✅ Created with correct schema (1,289 CSV rows loaded)
- **Schema Updates**: ✅ STOCKS uses store_name (not store_id), STAFFS has correct columns
- **GUI Interface**: ✅ Icon-free professional design with material themes
- **Data Processing**: ✅ Pandas 2.3.3 compatibility, NaN→NULL conversion working
- **API Integration**: ✅ Direct API-to-MySQL insertion operational

**🎉 System fully operational with 1,289+ records successfully processed!**

### GUI Features

The ETL Pipeline Manager provides a professional interface with:

| Section | Features | Description |
|---------|----------|-------------|
| API Configuration | URL input + Test button | Test API connections (default: https://etl-server.fly.dev) |
| Database Operations | Connection test + Table creation | Validate MySQL connection and create all 9 tables |
| File Management | Select → Load workflow | Choose CSV files, then click "Load Selected Files" |
| Data Loading | CSV + API data import | Multi-threaded loading with progress feedback |
| Test Operations | CSV access + API export | Comprehensive testing and validation |
| Theme Settings | Dark/Light toggle | Switch between dark cyan and light blue themes |

### GUI Workflow (Updated)
1. Test Database Connection: ✅ Should work immediately with your configured MySQL
2. Create Tables: ✅ Creates all 9 tables with proper foreign key relationships
3. Select CSV Files: Choose files from computer (NOT copied yet)
4. Load Selected Files: Click "Load" button to copy files to `data/CSV/`
5. Import Data: Use "Load CSV Data" to insert into database
6. Monitor Progress: Real-time status updates in output window

### Recent Improvements ✨ (October 2025)
• ✅ Schema Alignment: Updated STOCKS (store_name FK) and STAFFS (name, store_name, street columns)
• ✅ Pandas 2.3.3 Compatibility: Fixed `fillna()` issues with `df.where(pd.notna(df), None)`
• ✅ Complete Data Loading: All 1,289 CSV records loading successfully
• ✅ Modular Schema Manager: Both db_manager.py and schema_manager.py synchronized
• ✅ Professional GUI: Icon-free design with dark cyan/light blue themes
• ✅ Zero Cache Policy: Automatic pycache prevention system-wide

## 🔧 Command Line Usage

### Quick Start - Direct API-to-MySQL
Your ETL pipeline already does direct API-to-MySQL insertion! No CSV conversion needed.

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

| Method | Flag | Performance | Memory Usage | Best For |
|--------|------|-------------|--------------|----------|
| Standard | --api-only | ⭐⭐⭐ Good | Moderate | Development, general use |
| Streaming | --api-streaming | ⭐⭐⭐⭐ Great | Low | Large datasets (>10K records) |
| Direct JSON | --api-direct | ⭐⭐⭐⭐⭐ Fastest | Minimal | Production, maximum speed |

### Data Flow Options
```
❌ INEFFICIENT: API → CSV File → Read CSV → DataFrame → MySQL
✅ YOUR SETUP:  API → DataFrame → MySQL (Direct!)
⚡ OPTIMIZED:   API → Raw JSON → MySQL (Even faster!)
```

### Project Components
• Extract: Direct API data retrieval with error handling
• Transform: Pandas-based data cleaning and validation
• Load: Multiple MySQL insertion strategies for optimal performance

## 📊 Data Sources

### API Endpoints
• Customers API: Customer information and profiles
• Orders API: Order transactions and details
• Order Items API: Individual order line items

### CSV Data Files
• Products: Product catalog with categories and brands
• Stores: Store locations and information
• Staff: Employee and staff data
• Inventory: Stock levels and availability

### MySQL Database
• Schema: `store_manager` with InnoDB engine
• Tables: Automated creation for all data sources
• Performance: Optimized indexes and constraints

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
• Driver: PyMySQL (primary), mysql-connector-python (fallback)
• Database: `store_manager` (auto-created if missing)
• Tables: 9 tables with proper foreign key relationships
• Authentication: Supports MySQL 8.0 caching_sha2_password

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

• Detailed logging for debugging and monitoring
• Error handling and recovery mechanisms
• Performance metrics tracking

Logs are stored in the `logs/` directory (ignored by git).

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
• Repository: [Repository URL](https://github.com/Sylverose)

### Insertion Method Performance
| Method | Performance | Memory | Best Use Case |
|--------|-------------|--------|---------------|
| Standard | Good | Moderate | Development, testing |
| Streaming | Great | Low | Large datasets, production |
| Direct JSON | Fastest | Minimal | High-performance scenarios |

## 🚀 Quick Command Reference
```bash
# GUI Interface (Recommended)
python run_gui.py               # Launch with demo information and usage guide
python gui/main_window.py        # Direct GUI launch (no demo info)

# Command Line Interface
python src/db_manager.py --help  # Show all available options
python src/db_manager.py         # Complete ETL pipeline (CSV + API)
python src/db_manager.py --api-direct    # API-to-MySQL only (fastest)
python src/db_manager.py --api-csv       # Export API data to CSV files
python src/db_manager.py --api-streaming # Streaming insertion for large data

# Testing
cd tests && python run_tests.py  # Run all core functionality tests
```

## 🔧 Troubleshooting Multiple Python Installations

If you encounter module import errors, you likely have multiple Python installations:

```bash
# Check which Python you're using
python -c "import sys; print(sys.executable)"

# Use python -m pip instead of pip to install in the correct Python
python -m pip install PySide6

# Test if PySide6 is available
python -c "import PySide6; print('PySide6 works!')"
```

## 🔧 Recent Fixes & Updates

### Schema Mismatch Issues - RESOLVED ✅ (Latest Fix)
• Issue: "Unknown column 'name'" errors during data insertion
• Root Cause: CSV files had different column structure than database schema
• Solution: Updated both db_manager.py and schema_manager.py schemas:
  ◦ STAFFS: `first_name → name`, `store_id → store_name`, added `street` column
  ◦ STOCKS: `store_id → store_name` (FK only, not PK), updated primary key structure
• Result: All 1,289 CSV rows loading successfully (9+7+3+10+321+939 records)

### Pandas 2.3.3 Compatibility - RESOLVED ✅
• Issue: `fillna(value=None)` failing with "Must specify a fill 'value' or 'method'"
• Solution: Replaced with `df.where(pd.notna(df), None)` for proper NaN→NULL conversion
• Result: Clean data processing without pandas version conflicts

### Database Connection Issues - RESOLVED ✅
• Issue: MySQL connection failures with Python 3.13
• Solution: Migrated to PyMySQL driver with cryptography support
• Result: Stable connection to MySQL 8.0.43

### Complete Table Creation - RESOLVED ✅
• Issue: Only 4/9 tables being created, schema mismatches
• Solution: Updated `create_all_tables_from_csv()` + synchronized modular schemas
• Result: All 9 tables created with correct column mappings

### GUI File Management - IMPROVED ✅
• Issue: Files copied immediately upon selection
• Solution: Separated "Select" and "Load" operations
• Result: Better user control over file operations

### Cache Management - OPTIMIZED ✅
• Feature: Automatic pycache prevention
• Implementation: `sys.dont_write_bytecode = True`
• Result: Clean project directory

---

Last updated: October 30, 2025 - All major issues resolved, ETL pipeline fully operational
