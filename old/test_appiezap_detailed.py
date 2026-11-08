#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed test for Appiezap account with various API approaches
"""

import valo_api
import time
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_known_account():
    """First test with a known working account"""
    print("\n" + "=" * 60)
    print("Testing with known account (TenZ#001)...")
    print("=" * 60)
    
    try:
        # Test account details
        account = valo_api.get_account_details_by_name("TenZ", "001")
        if account and hasattr(account, 'data'):
            print("[OK] API is working - TenZ account found")
            data = account.data
            attrs = [attr for attr in dir(data) if not attr.startswith('_')]
            print(f"Available attributes: {attrs[:15]}")
            
            # Check for account level
            for attr in attrs:
                if 'level' in attr.lower() or 'account' in attr.lower():
                    value = getattr(data, attr, None)
                    print(f"  {attr}: {value}")
            return True
        else:
            print("[FAIL] API not working properly")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_appiezap_variations():
    """Try different variations of the Appiezap account"""
    print("\n" + "=" * 60)
    print("Testing Appiezap account variations...")
    print("=" * 60)
    
    # Different possible tag variations
    test_cases = [
        ("Appiezap", "0000"),
        ("Appiezap", "000"),
        ("Appiezap", "EUW"),
        ("appiezap", "0000"),
    ]
    
    for name, tag in test_cases:
        print(f"\nTrying {name}#{tag}...")
        try:
            time.sleep(1.5)  # Rate limiting
            
            # Try account details
            account = valo_api.get_account_details_by_name(name, tag)
            if account and hasattr(account, 'data'):
                print(f"  [SUCCESS] Found account!")
                data = account.data
                print(f"  Name: {getattr(data, 'name', 'N/A')}")
                print(f"  Tag: {getattr(data, 'tag', 'N/A')}")
                print(f"  Region: {getattr(data, 'region', 'N/A')}")
                
                # Look for level
                for attr in dir(data):
                    if 'level' in attr.lower():
                        print(f"  {attr}: {getattr(data, attr, 'N/A')}")
                
                return (name, tag, data)
        except Exception as e:
            print(f"  [FAIL] {e}")
            continue
    
    print("\n[INFO] Could not find account with tried variations")
    return None

def test_with_region():
    """Try with explicit region parameter"""
    print("\n" + "=" * 60)
    print("Testing with explicit region...")
    print("=" * 60)
    
    regions = ['eu', 'na', 'ap', 'kr']
    
    for region in regions:
        print(f"\nTrying region: {region}")
        try:
            time.sleep(1.5)
            # Try MMR with region
            mmr = valo_api.get_mmr_details_by_name("Appiezap", "0000", region)
            if mmr and hasattr(mmr, 'data'):
                print(f"  [SUCCESS] Found in region {region}!")
                return region
        except Exception as e:
            print(f"  [FAIL] {e}")
    
    return None

def test_alternative_methods():
    """Test if there are alternative methods to get account info"""
    print("\n" + "=" * 60)
    print("Available valo_api methods...")
    print("=" * 60)
    
    # List all available methods
    methods = [method for method in dir(valo_api) if not method.startswith('_') and callable(getattr(valo_api, method))]
    
    print("Account-related methods:")
    for method in methods:
        if any(keyword in method.lower() for keyword in ['account', 'player', 'profile', 'level']):
            print(f"  - {method}")
    
    print("\nMMR-related methods:")
    for method in methods:
        if 'mmr' in method.lower():
            print(f"  - {method}")

def main():
    """Main test function"""
    print("Detailed API Test for Appiezap Account")
    print("=" * 60)
    
    # Set API key
    valo_api.set_api_key("YOUR_HENRIK_API_KEY")
    
    # Step 1: Verify API works with known account
    api_working = test_known_account()
    
    if not api_working:
        print("\n[ERROR] API is not working properly. Check API key.")
        return
    
    # Step 2: Try different variations of Appiezap account
    result = test_appiezap_variations()
    
    if result:
        name, tag, data = result
        print(f"\n[SUCCESS] Found Appiezap account as {name}#{tag}")
    else:
        print("\n[INFO] Account not found with standard method")
        
        # Step 3: Try with explicit regions
        region = test_with_region()
        if region:
            print(f"\n[INFO] Account found in region: {region}")
        
    # Step 4: Show available methods
    test_alternative_methods()
    
    # Final conclusion
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("\nPossible reasons for 'Route not found':")
    print("1. Account tag might not be '0000'")
    print("2. Account might be new/not indexed in Henrik's API yet")
    print("3. Account might be private or hidden from external APIs")
    print("4. Region might need to be specified")
    print("\nWhat we DO have access to:")
    print("- Current Rank & RR (if account is found)")
    print("- Peak Rank (via MMR history)")
    print("- K/D, Win Rate, Headshot % (via match history)")
    print("- Account details (when available)")
    print("\n[NOTE] Player level might need to be fetched from")
    print("       the local Valorant client instead of external APIs")

if __name__ == "__main__":
    main()

