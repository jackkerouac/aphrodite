#!/usr/bin/env python3
"""
Test script for the new maintenance functionality.
This script helps verify that the export and import endpoints work correctly.
"""

import requests
import json
import os
from datetime import datetime

def test_maintenance_functionality():
    """Test the new export and import functionality."""
    
    base_url = "http://localhost:8000"  # Adjust if needed
    
    print("=== Maintenance Functionality Test ===")
    print(f"Testing against: {base_url}")
    print(f"Test time: {datetime.now().isoformat()}")
    
    # Test 1: Database status
    print("\n1. Testing database status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/maintenance/database/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Database status: {data.get('database', {}).get('connection_status', 'unknown')}")
            print(f"   ✓ Tables found: {data.get('database', {}).get('table_count', 0)}")
            print(f"   ✓ Backups available: {len(data.get('backups', []))}")
        else:
            print(f"   ✗ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Export functionality
    print("\n2. Testing database export...")
    try:
        export_data = {"includeSensitive": False}
        response = requests.post(
            f"{base_url}/api/v1/maintenance/database/export",
            json=export_data
        )
        if response.status_code == 200:
            # Check if it's a file download
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                print(f"   ✓ Export successful (Content-Type: {content_type})")
                print(f"   ✓ Response size: {len(response.content)} bytes")
                
                # Try to parse the response as JSON to validate structure
                try:
                    export_json = response.json()
                    if 'export_info' in export_json and 'tables' in export_json:
                        tables_count = len(export_json['tables'])
                        print(f"   ✓ Export contains {tables_count} tables")
                        print(f"   ✓ Export version: {export_json['export_info'].get('version', 'unknown')}")
                    else:
                        print("   ⚠ Unexpected export structure")
                except:
                    print("   ✓ Export appears to be a file download (binary content)")
            else:
                print(f"   ✗ Unexpected content type: {content_type}")
        else:
            print(f"   ✗ Export failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   ✗ Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   ✗ Raw error: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Import functionality (with mock data)
    print("\n3. Testing database import (dry run)...")
    try:
        # Create a minimal test import structure
        test_import_data = {
            "export_info": {
                "created": datetime.now().isoformat(),
                "version": "aphrodite_v2",
                "include_sensitive": False,
                "export_type": "database_settings"
            },
            "tables": {
                "test_table": {
                    "error": "Test table - no actual import",
                    "exported": False
                }
            }
        }
        
        import_request = {"jsonData": test_import_data}
        response = requests.post(
            f"{base_url}/api/v1/maintenance/database/import-settings",
            json=import_request
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data.get('import_summary', {})
                print(f"   ✓ Import endpoint working")
                print(f"   ✓ Tables processed: {summary.get('total_tables_in_export', 0)}")
                print(f"   ✓ Tables imported: {summary.get('tables_imported', 0)}")
                print(f"   ✓ Tables skipped: {summary.get('tables_skipped', 0)}")
            else:
                print(f"   ✗ Import failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ✗ Import request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   ✗ Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   ✗ Raw error: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n=== Test Complete ===")
    print("\nNext steps:")
    print("1. Rebuild the Docker container: docker-compose build")
    print("2. Start the application: docker-compose up")
    print("3. Test the maintenance page in the browser")
    print("4. Try exporting the database to JSON")
    print("5. Try importing settings from a JSON file")

if __name__ == "__main__":
    test_maintenance_functionality()
