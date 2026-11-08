#!/usr/bin/env python3
"""
Discover what methods are actually available in valo_api
"""

import valo_api

def list_available_methods():
    print("[INFO] Available valo_api methods:")
    print("=" * 60)
    
    # Get all public methods (not starting with _)
    methods = [method for method in dir(valo_api) if not method.startswith('_')]
    
    for i, method in enumerate(methods, 1):
        print(f"{i:2}. {method}")
    
    return methods

def test_simple_methods():
    print("\n[TEST] Testing simple methods (no parameters needed):")
    print("=" * 60)
    
    api_key = "YOUR_HENRIK_API_KEY"
    valo_api.set_api_key(api_key)
    
    # Try methods that don't require player parameters
    simple_methods = [
        'get_status',
        'get_version_info',
        'get_content',
    ]
    
    for method_name in simple_methods:
        if hasattr(valo_api, method_name):
            print(f"\n[TEST] {method_name}:")
            try:
                method = getattr(valo_api, method_name)
                result = method()
                if result:
                    print(f"   [OK] Works! Type: {type(result)}")
                    if hasattr(result, 'data'):
                        print(f"   [DATA] Has .data attribute")
                else:
                    print(f"   [FAIL] No result")
            except Exception as e:
                print(f"   [ERROR] {str(e)[:100]}")

if __name__ == "__main__":
    methods = list_available_methods()
    test_simple_methods()
    
    print(f"\n[INFO] Total methods found: {len(methods)}")

