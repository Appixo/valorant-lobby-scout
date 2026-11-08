#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discover what's actually available in the valo_api module
"""

import valo_api
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("Discovering valo_api module contents")
print("=" * 60)

# List all attributes
all_attrs = dir(valo_api)

# Filter for public methods/functions
public_methods = [attr for attr in all_attrs if not attr.startswith('_')]

print(f"\nTotal public attributes: {len(public_methods)}")
print("\nAvailable functions/methods:")
print("-" * 60)

for method in sorted(public_methods):
    attr = getattr(valo_api, method)
    if callable(attr):
        print(f"  {method}")

print("\n" + "=" * 60)
print("Testing module structure...")
print("=" * 60)

# Check if it's a class-based API
print(f"\nvalo_api type: {type(valo_api)}")
print(f"valo_api.__name__: {getattr(valo_api, '__name__', 'N/A')}")

# Check for common patterns
patterns = ['get_', 'fetch_', 'Account', 'Player', 'MMR', 'Match']
for pattern in patterns:
    matching = [m for m in public_methods if pattern in m]
    if matching:
        print(f"\nMethods containing '{pattern}':")
        for m in matching:
            print(f"  - {m}")

# Check if there are any classes
print("\n" + "=" * 60)
print("Classes in module:")
print("=" * 60)
for attr in public_methods:
    obj = getattr(valo_api, attr)
    if isinstance(obj, type):
        print(f"  Class: {attr}")
        # Show class methods
        class_methods = [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))]
        if class_methods:
            print(f"    Methods: {class_methods[:10]}")

print("\n" + "=" * 60)
print("Done!")

