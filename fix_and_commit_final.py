#!/usr/bin/env python3
"""
Final fix: Ensure the proper source code changes are committed to GitHub
This fixes the root cause so GitHub Actions builds the correct frontend
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return success status"""
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def main():
    print("🚀 Final fix: Committing source code changes to GitHub")
    print("=" * 60)
    
    # Verify the fixes are in place locally
    print("\n📋 Verifying local fixes...")
    try:
        with open("frontend/src/services/api.ts", "r") as f:
            api_content = f.read()
            if "buildApiUrl" in api_content and "window.location.origin" in api_content:
                print("✅ API service fixes are present locally")
            else:
                print("❌ API service fixes are missing - please apply the fixes first")
                return False
                
        with open("frontend/next.config.ts", "r") as f:
            config_content = f.read()
            if "NODE_ENV === 'production'" in config_content:
                print("✅ Next.js config fixes are present locally")
            else:
                print("❌ Next.js config fixes are missing")
                return False
                
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return False
    
    # Git status
    if not run_command("git status --porcelain", "Checking git status"):
        return False
    
    # Add the critical files
    critical_files = [
        "frontend/src/services/api.ts",
        "frontend/next.config.ts", 
        "frontend/.env.production"
    ]
    
    for file in critical_files:
        if not run_command(f"git add {file}", f"Adding {file}"):
            print(f"⚠️ Could not add {file} - it may not exist or have changes")
    
    # Commit with clear message
    commit_msg = "Fix API URL resolution for remote deployments - use dynamic URLs instead of localhost hardcoding"
    if not run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
        print("❌ Failed to commit - there may be no changes to commit")
        return False
    
    # Push to GitHub
    if not run_command("git push", "Pushing to GitHub"):
        return False
    
    print("\n✅ Successfully pushed source code fixes to GitHub!")
    print("\n🏗️ Now GitHub Actions will build with the correct frontend")
    print("\n🚀 Next steps:")
    print("   1. Wait for GitHub Actions to build new Docker image")
    print("   2. Create new release (v4.0.31+)")
    print("   3. Update remote machine with new release")
    print("   4. Test that API calls work without manual patching")
    
    print("\n💡 Key insight:")
    print("   The emergency patch proved the fix works!")
    print("   Now we've committed the source code so it's permanent.")

if __name__ == "__main__":
    main()
