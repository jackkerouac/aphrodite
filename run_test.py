#!/usr/bin/env python3
# Simple script to test the badge creation

import sys
import os

# Add the project root to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from aphrodite_helpers.apply_badge import save_test_badge

# Create a test badge with "DTS 5.1" text
success = save_test_badge(text="DTS 5.1")

if success:
    print("✅ Test badge created successfully")
    print(f"Badge saved to {os.path.join(script_dir, 'test_badge.png')}")
else:
    print("❌ Failed to create test badge")
