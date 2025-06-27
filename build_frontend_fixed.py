#!/usr/bin/env python3
"""
Build script to ensure frontend uses correct environment for production deployment
Python version for Windows/PowerShell development
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        print(f"🔄 Running: {cmd}")
        result = subprocess.run(cmd, shell=shell, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {cmd}")
        print(f"   Exit code: {e.returncode}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def main():
    print("🔧 Building Aphrodite frontend for production deployment...")
    print("=" * 60)
    
    # Get script directory and frontend path
    script_dir = Path(__file__).parent
    frontend_dir = script_dir / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)
    
    print(f"📁 Working in: {frontend_dir}")
    os.chdir(frontend_dir)
    
    # Check if package.json exists
    if not (frontend_dir / "package.json").exists():
        print("❌ Error: package.json not found in frontend directory")
        sys.exit(1)
    
    print("\n📦 Installing dependencies...")
    if not run_command("npm ci", cwd=frontend_dir):
        print("⚠️  npm ci failed, trying npm install...")
        if not run_command("npm install", cwd=frontend_dir):
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    print("\n🧹 Cleaning previous build...")
    next_dir = frontend_dir / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("✅ Removed .next directory")
        except Exception as e:
            print(f"⚠️  Could not remove .next directory: {e}")
    
    print("\n🏗️ Building frontend with production environment...")
    
    # Set environment variables for the build
    env = os.environ.copy()
    env['NODE_ENV'] = 'production'
    
    # Run the build with environment
    try:
        result = subprocess.run(
            "npm run build:docker", 
            shell=True, 
            cwd=frontend_dir, 
            env=env,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        print("✅ Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code: {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        sys.exit(1)
    
    print("\n📋 Verifying build...")
    
    # Check if .next directory was created
    if not next_dir.exists():
        print("❌ Error: .next directory not found after build")
        sys.exit(1)
    
    # Check if static directory exists
    static_dir = next_dir / "static"
    if not static_dir.exists():
        print("❌ Error: .next/static directory not found")
        sys.exit(1)
    
    print("✅ Frontend build completed successfully!")
    print("🚀 Ready for Docker deployment")
    
    # Show build info
    print("\n📊 Build info:")
    try:
        # Count files in static directory
        static_files = list(static_dir.rglob("*"))
        file_count = len([f for f in static_files if f.is_file()])
        print(f"   Static files: {file_count} files")
        
        # Get build size
        def get_dir_size(path):
            total = 0
            for f in path.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
            return total
        
        build_size = get_dir_size(next_dir)
        build_size_mb = build_size / (1024 * 1024)
        print(f"   Build size: {build_size_mb:.1f} MB")
        
    except Exception as e:
        print(f"   Could not calculate build stats: {e}")
    
    print("\n🔗 API URL configuration:")
    print("   Development: http://localhost:8000")
    print("   Production: Dynamic (uses window.location.origin)")
    
    print("\n✅ The frontend will now work correctly on remote machines!")
    print("\n🚀 Next steps:")
    print("   1. Commit and push changes to GitHub")
    print("   2. GitHub will build the Docker image")
    print("   3. Deploy to remote machine (192.168.0.110)")
    print("   4. Test that Dashboard shows 'Online' status")

if __name__ == "__main__":
    main()
