#!/usr/bin/env python3
"""
AMD64-only build - no ARM64 compilation bullshit
"""
import subprocess
import sys

def run_command(cmd, check=True):
    """Run a command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0

def main():
    print("🔥 FUCK ARM64 - AMD64 ONLY BUILD")
    print("=" * 50)
    
    # Step 1: Build locally for AMD64 only
    print("Building for AMD64 only...")
    if not run_command("docker build -f Dockerfile.simple -t jackkerouac/aphrodite:4.0.0 ."):
        print("❌ Build failed")
        return 1
    
    # Tag as latest
    run_command("docker tag jackkerouac/aphrodite:4.0.0 jackkerouac/aphrodite:latest")
    
    # Step 2: Login
    print("\n🔐 Login to Docker Hub:")
    if not run_command("docker login -u jackkerouac"):
        print("❌ Login failed")
        return 1
    
    # Step 3: Push
    print("\n📤 Pushing to Docker Hub...")
    if not run_command("docker push jackkerouac/aphrodite:4.0.0"):
        print("❌ Push failed")
        return 1
    
    if not run_command("docker push jackkerouac/aphrodite:latest"):
        print("❌ Push failed")
        return 1
    
    print("\n🎉 SUCCESS!")
    print("✅ AMD64 image published to Docker Hub")
    print("✅ jackkerouac/aphrodite:4.0.0")
    print("✅ jackkerouac/aphrodite:latest")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
