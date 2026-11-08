#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test which endpoints actually work with the valo_api library
"""

import valo_api
import time
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_mmr_endpoint():
    """Test MMR endpoint with known player"""
    print("\n[TEST] MMR Details Endpoint")
    print("-" * 60)
    
    try:
        # Try with TenZ first
        result = valo_api.get_mmr_by_name("TenZ", "001")
        if result:
            print("[SUCCESS] MMR endpoint works!")
            print(f"Type: {type(result)}")
            
            # Show attributes
            attrs = [attr for attr in dir(result) if not attr.startswith('_')]
            print(f"Attributes: {attrs[:15]}")
            
            # Show some data
            for attr in ['currenttierpatched', 'ranking_in_tier', 'elo']:
                if hasattr(result, attr):
                    print(f"  {attr}: {getattr(result, attr)}")
            
            return True
        else:
            print("[FAIL] No data returned")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_mmr_details_endpoint():
    """Test MMR Details endpoint"""
    print("\n[TEST] MMR Details (Extended) Endpoint")
    print("-" * 60)
    
    try:
        result = valo_api.get_mmr_details_by_name("TenZ", "001")
        if result and hasattr(result, 'data'):
            print("[SUCCESS] MMR Details endpoint works!")
            data = result.data
            
            # Show structure
            attrs = [attr for attr in dir(data) if not attr.startswith('_')]
            print(f"Data attributes: {attrs[:15]}")
            
            # Current data
            if hasattr(data, 'current_data') and data.current_data:
                current = data.current_data
                print(f"\nCurrent Rank Info:")
                print(f"  Rank: {getattr(current, 'currenttierpatched', 'N/A')}")
                print(f"  RR: {getattr(current, 'ranking_in_tier', 'N/A')}")
            
            # Highest rank
            if hasattr(data, 'highest_rank') and data.highest_rank:
                peak = data.highest_rank
                print(f"\nPeak Rank Info:")
                print(f"  Rank: {getattr(peak, 'patched_tier', 'N/A')}")
            
            return True
        else:
            print("[FAIL] No data returned")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_match_history_endpoint():
    """Test match history endpoint"""
    print("\n[TEST] Match History Endpoint")
    print("-" * 60)
    
    try:
        result = valo_api.get_match_history_by_name("TenZ", "001")
        if result and hasattr(result, 'data'):
            print("[SUCCESS] Match History endpoint works!")
            matches = result.data
            
            if matches and len(matches) > 0:
                print(f"Found {len(matches)} matches")
                
                # Show first match structure
                first_match = matches[0]
                attrs = [attr for attr in dir(first_match) if not attr.startswith('_')]
                print(f"Match attributes: {attrs[:15]}")
                
                return True
            else:
                print("[WARN] No matches found")
                return False
        else:
            print("[FAIL] No data returned")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_appiezap_with_working_endpoints():
    """Test Appiezap account with endpoints that work"""
    print("\n" + "=" * 60)
    print("Testing Appiezap#0000 with working endpoints")
    print("=" * 60)
    
    player_name = "Appiezap"
    tag = "0000"
    
    # Test MMR
    print(f"\n[TEST] MMR for {player_name}#{tag}")
    print("-" * 60)
    try:
        time.sleep(1.5)
        result = valo_api.get_mmr_by_name(player_name, tag)
        if result:
            print("[SUCCESS] Found MMR data!")
            print(f"  Rank: {getattr(result, 'currenttierpatched', 'N/A')}")
            print(f"  RR: {getattr(result, 'ranking_in_tier', 'N/A')}")
            print(f"  ELO: {getattr(result, 'elo', 'N/A')}")
            
            # Check all attributes for level/account info
            attrs = [attr for attr in dir(result) if not attr.startswith('_')]
            print(f"\nAll attributes: {attrs}")
            
        else:
            print("[FAIL] No MMR data found")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Test Match History
    print(f"\n[TEST] Match History for {player_name}#{tag}")
    print("-" * 60)
    try:
        time.sleep(1.5)
        result = valo_api.get_match_history_by_name(player_name, tag)
        if result and hasattr(result, 'data'):
            matches = result.data
            if matches and len(matches) > 0:
                print(f"[SUCCESS] Found {len(matches)} matches!")
                
                # Calculate K/D from recent matches
                total_kills = 0
                total_deaths = 0
                
                for match in matches[:10]:
                    if hasattr(match, 'players') and match.players:
                        for player in match.players:
                            if (hasattr(player, 'name') and 
                                player.name.lower() == player_name.lower() and
                                hasattr(player, 'tag') and 
                                player.tag.lower() == tag.lower()):
                                
                                if hasattr(player, 'stats'):
                                    stats = player.stats
                                    total_kills += getattr(stats, 'kills', 0)
                                    total_deaths += getattr(stats, 'deaths', 0)
                
                if total_deaths > 0:
                    kd = total_kills / total_deaths
                    print(f"  K/D Ratio (last 10 games): {kd:.2f}")
                    print(f"  Total K/D: {total_kills}/{total_deaths}")
            else:
                print("[FAIL] No matches found")
        else:
            print("[FAIL] No match data")
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    """Main function"""
    print("Testing Valo-API Working Endpoints")
    print("=" * 60)
    
    # Set API key
    valo_api.set_api_key("YOUR_HENRIK_API_KEY")
    
    # Test which endpoints work
    print("\n[PHASE 1] Testing endpoints with known player (TenZ)...")
    mmr_works = test_mmr_endpoint()
    time.sleep(1.5)
    
    mmr_details_works = test_mmr_details_endpoint()
    time.sleep(1.5)
    
    match_history_works = test_match_history_endpoint()
    
    # Summary of working endpoints
    print("\n" + "=" * 60)
    print("Working Endpoints Summary")
    print("=" * 60)
    print(f"MMR (basic): {'[OK]' if mmr_works else '[FAIL]'}")
    print(f"MMR Details: {'[OK]' if mmr_details_works else '[FAIL]'}")
    print(f"Match History: {'[OK]' if match_history_works else '[FAIL]'}")
    
    if mmr_works or mmr_details_works or match_history_works:
        print("\n[PHASE 2] Testing your account...")
        test_appiezap_with_working_endpoints()
        
        print("\n" + "=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)
        print("\n[YES] We have API access to:")
        if mmr_works or mmr_details_works:
            print("  - Current Rank & RR")
            print("  - Peak Rank (from MMR history)")
        if match_history_works:
            print("  - K/D Ratio (calculated from match history)")
            print("  - Win Rate (from match history)")
            print("  - Headshot % (from match history)")
        
        print("\n[MAYBE] Player Level:")
        print("  - Not available in external API endpoints tested")
        print("  - May need to be fetched from local Valorant client")
        print("  - Alternative: Use valclient library to get from game")
    else:
        print("\n[ERROR] No endpoints working - API might be down or key invalid")

if __name__ == "__main__":
    main()

