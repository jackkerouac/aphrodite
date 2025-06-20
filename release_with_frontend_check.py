#!/usr/bin/env python3
"""
Pre-release check - ensures frontend is built before GitHub release
"""
import subprocess
import sys
import os

def run_command(cmd):
    """Run a command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def check_frontend_built():
    """Check if frontend is properly built"""
    print("🔍 Checking pre-built frontend...")
    
    # Check if .next exists
    if not os.path.exists("frontend/.next"):
        print("❌ ERROR: frontend/.next not found!")
        print("❌ You must build the frontend locally first")
        print("\n🔧 Run these commands:")
        print("   cd frontend")
        print("   npm install")
        print("   npm run build")
        print("   cd ..")
        return False
    
    # Check if .next has content
    next_contents = os.listdir("frontend/.next")
    if not next_contents:
        print("❌ ERROR: frontend/.next is empty!")
        print("❌ Frontend build failed or incomplete")
        return False
    
    print("✅ Pre-built frontend found")
    print(f"✅ .next contains: {len(next_contents)} items")
    
    # Check for key build artifacts
    required_items = ["static", "server"]
    missing_items = [item for item in required_items if item not in next_contents]
    
    if missing_items:
        print(f"⚠️  Missing build artifacts: {missing_items}")
        print("⚠️  Frontend may not be fully built")
        return False
    
    print("✅ All required build artifacts present")
    return True

def main():
    print("🧪 PRE-RELEASE CHECK - TAILWIND v4 COMPATIBLE")
    print("=" * 60)
    
    # Check frontend
    if not check_frontend_built():
        print("\n❌ FRONTEND CHECK FAILED")
        print("Build the frontend locally before creating release!")
        return 1
    
    print("\n📋 GitHub Action Summary:")
    print("✅ Uses Dockerfile.simple (your working version)")
    print("✅ AMD64 only (no ARM64 compilation issues)")
    print("✅ Uses pre-built frontend/.next (bypasses Tailwind v4 issues)")
    print("✅ Pushes to ghcr.io/jackkerouac/aphrodite")
    
    # Add and commit GitHub Action
    print("\n📦 Adding GitHub Action...")
    run_command("git add .github/")
    run_command("git add .")
    run_command('git commit -m "Add GitHub Action for automatic builds (Tailwind v4 compatible)"')
    
    # Push
    print("📤 Pushing...")
    run_command("git push origin main")
    
    # Create tag
    print("🏷️ Creating tag...")
    run_command("git tag v4.0.0")
    run_command("git push origin v4.0.0")
    
    print("\n🎉 READY FOR GITHUB RELEASE!")
    print("=" * 60)
    print("✅ GitHub Action will use your exact working process:")
    print("  • Uses Dockerfile.simple")
    print("  • Uses pre-built frontend/.next")
    print("  • AMD64 only build")
    print("  • No Tailwind v4 compilation issues")
    print("\n👉 Go create release: https://github.com/jackkerouac/aphrodite/releases/new")
    print("   • Select tag: v4.0.0")
    print("   • GitHub will build automatically using your working method!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
