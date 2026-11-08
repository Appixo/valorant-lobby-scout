#!/usr/bin/env python3
"""
Quick test to verify API is working with known public accounts
"""

import valo_api
import time

def test_api():
    print("[TEST] Verifying API Access")
    print("=" * 60)
    
    # Set API key
    api_key = "YOUR_HENRIK_API_KEY"
    valo_api.set_api_key(api_key)
    
    # Test with known public accounts
    test_accounts = [
        ("TenZ", "001", "TenZ (Known Pro Player)"),
        ("Shroud", "1337", "Shroud (Known Streamer)"),
        ("Appiezap", "0000", "Your Account"),
    ]
    
    for name, tag, description in test_accounts:
        print(f"\n[TEST] {description}: {name}#{tag}")
        print("-" * 60)
        
        # Try account details (with player level)
        try:
            result = valo_api.get_account_details_by_name(name, tag)
            if result and hasattr(result, 'data'):
                data = result.data
                print(f"   [OK] Account found!")
                if hasattr(data, 'account_level'):
                    print(f"   [LEVEL] Level: {data.account_level}")
                if hasattr(data, 'region'):
                    print(f"   [REGION] Region: {data.region}")
                if hasattr(data, 'puuid'):
                    print(f"   [PUUID] PUUID: {data.puuid[:20]}...")
            else:
                print(f"   [FAIL] No account data")
        except Exception as e:
            print(f"   [ERROR] {e}")
        
        time.sleep(1.5)
        
        # Try MMR details
        try:
            result = valo_api.get_mmr_details_by_name(name, tag)
            if result and hasattr(result, 'data'):
                data = result.data
                print(f"   [OK] MMR data found!")
                if hasattr(data, 'current_data') and data.current_data:
                    current = data.current_data
                    if hasattr(current, 'currenttierpatched'):
                        print(f"   [RANK] Rank: {current.currenttierpatched}")
                    if hasattr(current, 'ranking_in_tier'):
                        print(f"   [RR] RR: {current.ranking_in_tier}")
            else:
                print(f"   [FAIL] No MMR data")
        except Exception as e:
            print(f"   [ERROR] {e}")
        
        time.sleep(1.5)

if __name__ == "__main__":
    test_api()

