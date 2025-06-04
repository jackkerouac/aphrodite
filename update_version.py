#!/usr/bin/env python3
"""
Update all version files to match a target version.
This ensures consistency across the project.
"""

import yaml
import sys
import os
import re
from pathlib import Path

def get_current_version():
    """Get the current version from version.yml."""
    base_dir = Path(__file__).parent
    version_file = base_dir / "version.yml"
    
    if version_file.exists():
        try:
            with open(version_file, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('version', 'unknown')
        except Exception:
            pass
    return 'unknown'

def update_version_files(new_version):
    """Update all version-related files to the specified version."""
    
    base_dir = Path(__file__).parent
    
    # Files to update
    version_files = [
        base_dir / "version.yml",
        base_dir / "config" / "version.yml"
    ]
    
    print(f"Updating all version files to: {new_version}")
    
    # Update YAML version files
    for version_file in version_files:
        try:
            # Create directory if it doesn't exist
            version_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(version_file, 'w') as f:
                yaml.dump({'version': new_version}, f, default_flow_style=False)
            print(f"✅ Updated {version_file}")
        except Exception as e:
            print(f"❌ Failed to update {version_file}: {e}")
    
    print(f"\n🎉 Version update complete!")
    print(f"📝 Next steps:")
    print(f"   1. Update docker-compose.yml image tag to: ghcr.io/jackkerouac/aphrodite:{new_version}")
    print(f"   2. Commit changes: git add . && git commit -m 'Release v{new_version}'")
    print(f"   3. Create and push tag: git tag v{new_version} && git push --tags")
    print(f"   4. Create GitHub release to trigger Docker build")
    print(f"   5. Test the published image")

def update_docker_compose(new_version):
    """Update docker-compose.yml with new version."""
    base_dir = Path(__file__).parent
    compose_file = base_dir / "docker-compose.yml"
    
    if not compose_file.exists():
        print(f"⚠️  {compose_file} not found")
        return
    
    try:
        with open(compose_file, 'r') as f:
            content = f.read()
        
        # Replace the image tag
        pattern = r'(image: ghcr\.io/jackkerouac/aphrodite:)([^\s]+)'
        replacement = f'\\1{new_version}'
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(compose_file, 'w') as f:
                f.write(new_content)
            print(f"✅ Updated {compose_file}")
        else:
            print(f"⚠️  No image tag found to update in {compose_file}")
            
    except Exception as e:
        print(f"❌ Failed to update {compose_file}: {e}")

def show_current_version():
    """Show the current version."""
    current = get_current_version()
    print(f"Current version: {current}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Aphrodite Version Management")
        print("Usage:")
        print("  python update_version.py <version>    # Update to specific version")
        print("  python update_version.py current      # Show current version")
        print("  python update_version.py auto         # Auto-increment patch version")
        print("")
        print("Examples:")
        print("  python update_version.py 2.3.0")
        print("  python update_version.py current")
        print("  python update_version.py auto")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "current":
        show_current_version()
    elif command == "auto":
        current = get_current_version()
        if current == 'unknown':
            print("❌ Cannot auto-increment unknown version. Please specify a version.")
            sys.exit(1)
        
        try:
            # Parse semantic version and increment patch
            parts = current.split('.')
            if len(parts) >= 3:
                major, minor, patch = parts[0], parts[1], parts[2]
                new_patch = str(int(patch) + 1)
                new_version = f"{major}.{minor}.{new_patch}"
                print(f"Auto-incrementing: {current} → {new_version}")
                update_version_files(new_version)
                update_docker_compose(new_version)
            else:
                print(f"❌ Cannot parse version '{current}' for auto-increment")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Auto-increment failed: {e}")
            sys.exit(1)
    else:
        version = command.lstrip('v')  # Remove 'v' prefix if present
        update_version_files(version)
        update_docker_compose(version)
