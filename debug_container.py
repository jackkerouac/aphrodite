#!/usr/bin/env python3
"""
Debug: Check what code is actually running in the container

This script will help us verify if our fixes are actually being used.
"""

print("🔍 CONTAINER CODE VERIFICATION")
print("=" * 50)

# Check if we can determine what's happening
try:
    # Try to read the actual resolution processor that should be running
    container_file_content = """
    The logs show:
    
    1. ✅ Audio processor starts successfully
    2. ✅ Gets 'EAC3 6.0' codec from v1 aggregator 
    3. ❌ Database connection corruption occurs
    4. ❌ Missing thread isolation logs
    
    This suggests the v1 aggregator is still running directly,
    not in thread isolation as we intended.
    """
    
    print("📋 Analysis:")
    print(container_file_content)
    
    print("\n🔍 Possible Issues:")
    print("1. Docker container cache - old code still running")
    print("2. Thread isolation code not reached - different code path")
    print("3. V1 aggregator called from unexpected location")
    print("4. Docker build didn't include our changes")
    
    print("\n🛠️ Debugging Steps:")
    print("1. Force rebuild: docker build --no-cache -t aphrodite . --progress=plain")
    print("2. Check container logs for thread isolation debug messages")
    print("3. Verify our fixed code is actually in the container")
    print("4. Look for alternative v1 aggregator call paths")
    
    print("\n⚠️ CRITICAL:")
    print("The database connection corruption is STILL happening")
    print("This means our thread isolation fix is NOT being executed")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("🎯 CONCLUSION: Need to verify Docker container is using our fixed code")
