#!/usr/bin/env python3
"""
Quick Manual Installation Script
For when automated scripts have issues
"""

import subprocess
import sys
import os

def manual_install():
    """Manual installation with step-by-step guidance"""
    
    print("🔧 Aphrodite v2 Manual Installation")
    print("=" * 40)
    print()
    
    # Check if in venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("❌ Not in virtual environment!")
        print()
        print("Please run these commands manually:")
        print("1. Deactivate current environment: deactivate")
        print("2. Remove old venv: rm -rf .venv  (or rmdir /s /q .venv on Windows)")
        print("3. Create new venv: python -m venv .venv")
        print("4. Activate: .venv\\Scripts\\activate  (Windows) or source .venv/bin/activate (Linux/Mac)")
        print("5. Run this script again")
        return
    
    print("✅ Virtual environment detected")
    print()
    
    # Install critical packages one by one
    critical_packages = [
        "pip",
        "setuptools",
        "wheel",
        "pydantic-settings==2.1.0",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0"
    ]
    
    print("📦 Installing critical packages one by one...")
    for package in critical_packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} - Error: {e}")
    
    print()
    print("🧪 Testing imports...")
    test_imports = [
        "fastapi",
        "pydantic_settings", 
        "uvicorn"
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
    
    print()
    print("🎯 If all imports work, try:")
    print("   python start_api.py")

if __name__ == "__main__":
    manual_install()
