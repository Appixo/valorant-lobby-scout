#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test different API versions to find which ones work
"""

import valo_api
import time
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_method_versions(method_base, player_name, tag):
    """Test different versions of a method"""
    versions = ['', '_v1', '_v2', '_v3']
    
    for version in versions:
        method_name = f"{method_base}{version}"
        
        # Check if method exists
        if not hasattr(valo_api, method_name):
            continue
            
        print(f"\n  Testing: {method_name}")
        try:
            method = getattr(valo_api, method_name)
            result = method(player_name, tag)
            
            if result:
                print(f"    [SUCCESS] {method_name} works!")
                
                # Show structure
                if hasattr(result, 'data'):
                    data = result.data
                    attrs = [attr for attr in dir(data) if not attr.startswith('_')]
                    print(f"    Data attributes: {attrs[:10]}")
                    
                    # Try to extract useful info
                    for attr in ['name', 'tag', 'region', 'account_level', 'card']:
                        if hasattr(data, attr):
                            value = getattr(data, attr)
                            print(f"      {attr}: {value}")
                else:
                    attrs = [attr for attr in dir(result) if not attr.startswith('_')]
                    print(f"    Result attributes: {attrs[:10]}")
                    
                    # Try to extract useful info
                    for attr in ['currenttierpatched', 'ranking_in_tier', 'elo']:
                        if hasattr(result, attr):
                            value = getattr(result, attr)
                            print(f"      {attr}: {value}")
                
                return True
            else:
                print(f"    [FAIL] No data")
                
        except Exception as e:
            error_msg = str(e)
            if "Route not found" in error_msg:
                print(f"    [FAIL] Route not found")
            else:
                print(f"    [ERROR] {error_msg}")
        
        time.sleep(1.2)  # Rate limiting
    
    return False

def main():
    """Main test function"""
    print("Testing API Versions for Data Access")
    print("=" * 60)
    
    # Set API key
    valo_api.set_api_key("YOUR_HENRIK_API_KEY")
    
    # Test with known player first
    test_player = ("TenZ", "001")
    print(f"\n[PHASE 1] Testing with {test_player[0]}#{test_player[1]}")
    print("=" * 60)
    
    # Test Account Details versions
    print("\n[1] Account Details (for player level):")
    account_works = test_method_versions("get_account_details_by_name", test_player[0], test_player[1])
    
    # Test MMR versions
    print("\n[2] MMR Details (for rank):")
    mmr_works = test_method_versions("get_mmr_details_by_name", test_player[0], test_player[1])
    
    # Test Match History versions
    print("\n[3] Match History (for K/D):")
    match_works = test_method_versions("get_match_history_by_name", test_player[0], test_player[1])
    
    # Now test with user's account
    user_player = ("Appiezap", "0000")
    print(f"\n\n[PHASE 2] Testing with {user_player[0]}#{user_player[1]}")
    print("=" * 60)
    
    if account_works:
        print("\n[1] Account Details:")
        test_method_versions("get_account_details_by_name", user_player[0], user_player[1])
    
    if mmr_works:
        print("\n[2] MMR Details:")
        test_method_versions("get_mmr_details_by_name", user_player[0], user_player[1])
    
    if match_works:
        print("\n[3] Match History:")
        test_method_versions("get_match_history_by_name", user_player[0], user_player[1])
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if account_works or mmr_works or match_works:
        print("\n[OK] We have API access!")
        print("\nAvailable data:")
        if account_works:
            print("  - Account details (potentially includes level)")
        if mmr_works:
            print("  - Current Rank & RR")
            print("  - Peak Rank")
        if match_works:
            print("  - Match History")
            print("  - K/D Ratio (calculated)")
            print("  - Win Rate (calculated)")
            print("  - Headshot % (calculated)")
    else:
        print("\n[WARN] No API endpoints working")
        print("This could mean:")
        print("  1. API is temporarily down")
        print("  2. API endpoints have changed")
        print("  3. API key needs different permissions")
        print("\nAlternative: Use local Valorant client (valclient) for data")

if __name__ == "__main__":
    main()

