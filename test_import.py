#!/usr/bin/env python3
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing preview API import...")
    from app.api import preview
    print("✅ Preview API imported successfully")
    print(f"Preview blueprint: {preview.bp}")
    print(f"Preview routes: {[rule.rule for rule in preview.bp.url_map.iter_rules()]}")
except Exception as e:
    print(f"❌ Failed to import preview API: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nTesting individual functions...")
    from app.api.preview import get_badge_types, get_poster_types
    print("✅ Preview functions imported successfully")
except Exception as e:
    print(f"❌ Failed to import preview functions: {e}")
    import traceback
    traceback.print_exc()
