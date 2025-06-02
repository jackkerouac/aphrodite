#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_imports():
    print("Testing Python imports...")
    
    try:
        # Test basic app import
        from app.main import create_app
        print("✅ App creation import works")
        
        # Test preview API import
        from app.api import preview
        print("✅ Preview API import works")
        print(f"   Preview blueprint: {preview.bp}")
        
        # Test creating the app
        app = create_app()
        print("✅ App created successfully")
        
        # List all registered blueprints
        print("\nRegistered blueprints:")
        for blueprint_name, blueprint in app.blueprints.items():
            print(f"  - {blueprint_name}: {blueprint}")
        
        # List all routes
        print("\nAll registered routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.methods} {rule.rule}")
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_imports()
