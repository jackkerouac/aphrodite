#!/usr/bin/env python3
"""
Quick test runner for Phase 4 verification
"""
import subprocess
import sys

def main():
    """Run the Phase 4 test and report results"""
    print("🧪 Running Phase 4 Verification Test...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "test_phase4_results.py"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Phase 4 test PASSED")
        else:
            print("❌ Phase 4 test FAILED")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
