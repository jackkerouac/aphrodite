#!/usr/bin/env python3
"""
Quick Test: Check for hardcoded Windows paths in resolution applicator
"""

import re
from pathlib import Path

def check_windows_paths():
    """Check for hardcoded Windows paths that would break in Docker"""
    
    # Files to check
    files_to_check = [
        "E:/programming/aphrodite/api/app/services/badge_processing/resolution_applicator.py",
        "E:/programming/aphrodite/api/app/services/badge_processing/resolution_processor.py",
        "E:/programming/aphrodite/api/app/services/badge_processing/review_applicator.py",
        "E:/programming/aphrodite/api/app/services/badge_processing/review_processor.py",
        "E:/programming/aphrodite/api/app/services/badge_processing/audio_processor.py",
        "E:/programming/aphrodite/api/app/services/badge_processing/awards_processor.py"
    ]
    
    # Patterns that indicate Windows paths
    windows_patterns = [
        r'[A-Z]:/.*',  # Drive letters like E:/
        r'\\\\.*',     # UNC paths
        r'aphrodite-v2',  # Old project name paths
    ]
    
    print("🔍 Checking for hardcoded Windows paths...")
    print("=" * 50)
    
    issues_found = 0
    
    for file_path in files_to_check:
        file_obj = Path(file_path)
        if not file_obj.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n📁 Checking: {file_obj.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            for pattern in windows_patterns:
                if re.search(pattern, line) and not line.strip().startswith('#'):
                    print(f"   ❌ Line {line_num}: {line.strip()}")
                    issues_found += 1
    
    print(f"\n📊 Summary: {issues_found} potential Windows path issues found")
    
    if issues_found == 0:
        print("✅ No hardcoded Windows paths detected!")
        print("🐳 Should work correctly in Docker container")
    else:
        print("⚠️  Found hardcoded paths that may cause Docker issues")
        print("💡 Consider using relative paths or container-appropriate paths")

if __name__ == "__main__":
    check_windows_paths()
