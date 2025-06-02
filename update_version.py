#!/usr/bin/env python3
"""
Simple script to update the Aphrodite version across all files
Usage: python update_version.py 1.4.4
"""

import sys
import yaml
import json
from pathlib import Path

def update_version(new_version):
    """Update version in all relevant files"""
    
    # Base directory (root of the project)
    base_dir = Path(__file__).parent
    
    files_updated = []
    
    # 1. Update version.yml
    version_file = base_dir / 'version.yml'
    try:
        with open(version_file, 'w') as f:
            yaml.dump({'version': new_version}, f, default_flow_style=False)
        files_updated.append(str(version_file))
        print(f"✅ Updated {version_file}")
    except Exception as e:
        print(f"❌ Failed to update {version_file}: {e}")
    
    # 2. Update package.json
    package_file = base_dir / 'package.json'
    try:
        with open(package_file, 'r') as f:
            package_data = json.load(f)
        
        package_data['version'] = new_version
        
        with open(package_file, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        files_updated.append(str(package_file))
        print(f"✅ Updated {package_file}")
    except Exception as e:
        print(f"❌ Failed to update {package_file}: {e}")
    
    # 3. Update frontend package.json
    frontend_package_file = base_dir / 'aphrodite-web' / 'frontend' / 'package.json'
    try:
        if frontend_package_file.exists():
            with open(frontend_package_file, 'r') as f:
                frontend_package_data = json.load(f)
            
            frontend_package_data['version'] = new_version
            
            with open(frontend_package_file, 'w') as f:
                json.dump(frontend_package_data, f, indent=2)
            
            files_updated.append(str(frontend_package_file))
            print(f"✅ Updated {frontend_package_file}")
    except Exception as e:
        print(f"❌ Failed to update {frontend_package_file}: {e}")
    
    print(f"\n🎉 Version updated to {new_version}")
    print(f"📁 Files updated: {len(files_updated)}")
    
    print("\n📋 Next steps:")
    print("1. Test the application to ensure version is displayed correctly")
    print("2. Commit changes: git add . && git commit -m 'chore: bump version to v{}'".format(new_version))
    print("3. Create GitHub release: git tag v{} && git push origin v{}".format(new_version, new_version))
    
    return files_updated

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        print("Example: python update_version.py 1.4.4")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Basic version validation
    if not new_version.replace('.', '').replace('-', '').replace('rc', '').replace('beta', '').replace('alpha', '').isalnum():
        print(f"❌ Invalid version format: {new_version}")
        print("Expected format: x.y.z (e.g., 1.4.4)")
        sys.exit(1)
    
    print(f"🔄 Updating Aphrodite version to {new_version}")
    print("=" * 50)
    
    update_version(new_version)

if __name__ == "__main__":
    main()
