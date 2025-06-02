#!/usr/bin/env python3
import sys
import os

# Change to the web app directory
web_dir = os.path.join(os.getcwd(), 'aphrodite-web')
sys.path.insert(0, web_dir)
os.chdir(web_dir)

def test_imports():
    print(f"Testing Python imports from: {os.getcwd()}")
    
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
        
        # Check if preview blueprint is registered
        if 'preview' in app.blueprints:
            print("✅ Preview blueprint is registered!")
        else:
            print("❌ Preview blueprint is NOT registered!")
        
        # List all routes
        print("\nAll registered routes:")
        preview_routes = []
        for rule in app.url_map.iter_rules():
            route_info = f"  {list(rule.methods)} {rule.rule}"
            print(route_info)
            if 'preview' in rule.rule:
                preview_routes.append(rule.rule)
        
        print(f"\nPreview routes found: {preview_routes}")
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_imports()
