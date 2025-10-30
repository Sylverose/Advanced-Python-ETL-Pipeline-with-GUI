"""
Cache Cleaner Utility
Automatically clears application cache when run
"""

import os
import shutil
import sys
from pathlib import Path


class CacheCleaner:
    def __init__(self):
        # Get the root project directory (parent of gui folder)
        self.project_root = Path(__file__).parent.parent
        
        # Cache directories to clean
        self.cache_dirs = [
            self.project_root / "__pycache__",
            self.project_root / "gui" / "__pycache__",
            self.project_root / "src" / "__pycache__",
            self.project_root / "src" / "database" / "__pycache__",
            self.project_root / "tests" / "__pycache__",
        ]
        
        # Cache file patterns to remove
        self.cache_patterns = [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".pytest_cache",
            ".coverage",
            "*.log"
        ]
    
    def clear_pycache_dirs(self):
        """Remove __pycache__ directories"""
        removed_dirs = []
        
        for cache_dir in self.cache_dirs:
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                    removed_dirs.append(str(cache_dir))
                except Exception as e:
                    print(f"Warning: Could not remove {cache_dir}: {e}")
        
        return removed_dirs
    
    def clear_cache_files(self):
        """Remove cache files by pattern"""
        removed_files = []
        
        # Search recursively through project
        for pattern in self.cache_patterns:
            for file_path in self.project_root.rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        removed_files.append(str(file_path))
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        removed_files.append(str(file_path))
                except Exception as e:
                    print(f"Warning: Could not remove {file_path}: {e}")
        
        return removed_files
    
    def clean_all(self, verbose=True):
        """Clean all cache files and directories"""
        if verbose:
            print("Starting cache cleanup...")
        
        # Clear __pycache__ directories
        removed_dirs = self.clear_pycache_dirs()
        
        # Clear cache files
        removed_files = self.clear_cache_files()
        
        total_removed = len(removed_dirs) + len(removed_files)
        
        if verbose:
            if total_removed > 0:
                print(f"Cache cleanup completed: {total_removed} items removed")
                if removed_dirs:
                    print(f"Directories removed: {len(removed_dirs)}")
                if removed_files:
                    print(f"Files removed: {len(removed_files)}")
            else:
                print("Cache cleanup completed: No cache files found")
        
        return total_removed


def main():
    """Run cache cleaner from command line"""
    cleaner = CacheCleaner()
    cleaner.clean_all(verbose=True)


if __name__ == "__main__":
    main()