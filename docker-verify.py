#!/usr/bin/env python3
"""
Docker Container Verification Script

Verifies that logging, directories, and permissions are working correctly
inside the Docker container.
"""

import sys
import os
import logging
from pathlib import Path

def check_environment():
    """Check basic environment setup"""
    print("=== Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"User ID: {os.getuid() if hasattr(os, 'getuid') else 'N/A'}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print()

def check_directories():
    """Check required directories exist and are writable"""
    print("=== Directory Check ===")
    
    required_dirs = [
        "/app",
        "/app/logs",
        "/app/data", 
        "/app/media",
        "/app/api/static",
        "/app/api/static/originals",
        "/app/api/static/processed",
        "/app/api/static/preview"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        exists = path.exists()
        is_dir = path.is_dir() if exists else False
        writable = False
        
        if exists and is_dir:
            try:
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()
                writable = True
            except Exception as e:
                writable = f"Error: {e}"
        
        status = "✅" if exists and is_dir and writable else "❌"
        print(f"{status} {dir_path} - Exists: {exists}, Dir: {is_dir}, Writable: {writable}")
    
    print()

def check_logging():
    """Check logging system"""
    print("=== Logging System Check ===")
    
    try:
        # Test basic Python logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("test")
        logger.info("Basic Python logging works")
        print("✅ Basic Python logging: OK")
        
        # Test Aphrodite logging system
        sys.path.insert(0, "/app")
        from aphrodite_logging import setup_logging, get_logger
        
        print("✅ Aphrodite logging import: OK")
        
        # Test production setup
        setup_logging("production")
        aphrodite_logger = get_logger("test.docker")
        aphrodite_logger.info("Aphrodite logging system works in Docker")
        print("✅ Aphrodite production logging: OK")
        
        # Test with potential permission issues
        try:
            setup_logging("production", {
                "handlers": {
                    "file": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "filename": "/app/logs/container-test.log",
                        "level": "INFO"
                    }
                }
            })
            test_logger = get_logger("test.file")
            test_logger.info("File logging test")
            print("✅ File logging: OK")
        except Exception as e:
            print(f"⚠️  File logging: {e}")
        
    except Exception as e:
        print(f"❌ Logging system error: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def check_imports():
    """Check critical imports"""
    print("=== Import Check ===")
    
    critical_imports = [
        "sys",
        "os", 
        "pathlib",
        "logging",
        "uvicorn",
        "fastapi",
        "psycopg2",
        "redis",
        "celery"
    ]
    
    for module_name in critical_imports:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: OK")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
    
    print()

def main():
    """Run all verification checks"""
    print("Docker Container Verification")
    print("=" * 50)
    
    check_environment()
    check_directories()
    check_imports()
    check_logging()
    
    print("=" * 50)
    print("Verification complete!")

if __name__ == "__main__":
    main()
