#!/usr/bin/env python3
"""
Clean up all the temporary scripts and files before release
"""
import os
import sys

def delete_files(file_list, description):
    """Delete a list of files if they exist"""
    print(f"\n🧹 Cleaning up {description}...")
    deleted = []
    not_found = []
    
    for file in file_list:
        if os.path.exists(file):
            try:
                os.remove(file)
                deleted.append(file)
                print(f"  ✅ Deleted: {file}")
            except Exception as e:
                print(f"  ❌ Failed to delete {file}: {e}")
        else:
            not_found.append(file)
    
    if not_found:
        print(f"  ℹ️  Not found (already clean): {len(not_found)} files")
    
    return len(deleted)

def main():
    print("🧹 CLEANING UP TEMPORARY FILES")
    print("=" * 50)
    
    # Test and debug scripts
    test_scripts = [
        "test_release.py",
        "test_docker.py", 
        "test_frontend.py",
        "quick_test.py",
        "quick_build.py",
        "quick_fix.py",
        "debug_deployment.py",
        "final_validation.py",
        "fix_frontend_css.py"
    ]
    
    # Build scripts (keep only the working one)
    build_scripts = [
        "build_amd64_only.py",  # Keep this one - it works
        "build_multiplatform.py",
        "clean_reset.py"
    ]
    
    # Registry push scripts
    push_scripts = [
        "push_to_dockerhub.py",
        "push_to_github.py", 
        "github_push_fixed.py",
        "simple_release.py",
        "release_now.py"
    ]
    
    # Old Dockerfiles
    old_dockerfiles = [
        "Dockerfile.original",
        "Dockerfile.simply",  # typo version
        "Dockerfile.backend-only",
        "Dockerfile.frontend-only"
    ]
    
    # Temporary env files
    temp_env_files = [
        ".env.backup",
        ".env.test",
        ".env.debug"
    ]
    
    total_deleted = 0
    
    # Clean each category
    total_deleted += delete_files(test_scripts, "test and debug scripts")
    total_deleted += delete_files(build_scripts[1:], "extra build scripts (keeping build_amd64_only.py)")  # Skip first one
    total_deleted += delete_files(push_scripts, "registry push scripts")
    total_deleted += delete_files(old_dockerfiles, "old Dockerfiles")
    total_deleted += delete_files(temp_env_files, "temporary env files")
    
    print(f"\n📋 KEEPING THESE ESSENTIAL FILES:")
    essential_files = [
        "build_amd64_only.py",  # Working local build script
        "Dockerfile.simple",   # Working Dockerfile
        "docker-compose.yml",  # Production deployment
        ".env.example",        # User template
        "RELEASE_NOTES_v4.0.0.md",  # Release documentation
        "release_with_frontend_check.py"  # This release script
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
    
    print(f"\n🎉 CLEANUP COMPLETE")
    print(f"✅ Deleted {total_deleted} temporary files")
    print("✅ Repository ready for clean release")
    
    print(f"\n📋 FINAL REPOSITORY STRUCTURE:")
    print("Essential files only:")
    print("  • .github/workflows/docker-build.yml  # Auto-build on release")
    print("  • Dockerfile.simple                   # Working build")
    print("  • docker-compose.yml                  # User deployment")
    print("  • .env.example                        # User config template")
    print("  • build_amd64_only.py                 # Local development build")
    print("  • RELEASE_NOTES_v4.0.0.md            # Release docs")
    print("  • frontend/.next/                     # Pre-built frontend")
    print("  • api/, shared/, etc.                 # Application code")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
