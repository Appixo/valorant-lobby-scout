"""
Test script for fast stats loading
Allows testing player stats lookup by username#tag without being in a game
"""

import sys
import time
from valclient.client import Client
from valorant_api_client import init_valorant_api, get_current_season_id


def test_player_stats(username: str, tag: str):
    """
    Test stats fetching for a specific player
    
    Args:
        username: Player name (e.g., "PlayerName")
        tag: Player tag (e.g., "TAG" or "1234")
    """
    print("=" * 80)
    print(f"🔍 Testing Fast Stats System")
    print(f"   Player: {username}#{tag}")
    print("=" * 80)
    print()
    
    try:
        # Initialize Valorant client
        print("📡 Connecting to Valorant client...")
        client = Client(region='eu')  # Change region if needed: 'na', 'ap', 'kr'
        client.activate()
        print(f"✅ Connected! Region: {client.region}")
        print()
        
        # Get current season ID
        print("📅 Fetching current season...")
        season_id = get_current_season_id(client)
        print(f"✅ Season ID: {season_id}")
        print()
        
        # Initialize API with valclient for direct PD API access
        print("🔧 Initializing API clients...")
        api_key = "YOUR_HENRIK_API_KEY"
        api_client = init_valorant_api(api_key, valclient=client)
        print()
        
        # Get player PUUID from name
        print(f"🔎 Looking up PUUID for {username}#{tag}...")
        
        # Use the name service to get PUUID
        try:
            # Try to get account info
            response = client.fetch(
                endpoint=f"https://api.henrikdev.xyz/valorant/v1/account/{username}/{tag}",
                endpoint_type="custom"
            )
            
            if response and response.status_code == 200:
                data = response.json()
                puuid = data.get('data', {}).get('puuid')
                
                if puuid:
                    print(f"✅ Found PUUID: {puuid}")
                    print()
                else:
                    print("❌ Player not found")
                    return
            else:
                print(f"❌ Failed to look up player: HTTP {response.status_code if response else 'None'}")
                print("   Trying fallback method...")
                
                # Fallback: Use Henrik's API without PUUID
                print()
                print("🔄 Using fallback method (Henrik's API)...")
                stats = api_client.get_player_stats(username, tag)
                
                if stats:
                    display_stats(stats, username, tag, method="Henrik's API (Fallback)")
                else:
                    print("❌ No stats found via fallback method")
                return
                
        except Exception as e:
            print(f"⚠️ Error looking up PUUID: {e}")
            print("   Trying fallback method...")
            
            # Fallback: Use Henrik's API without PUUID
            print()
            print("🔄 Using fallback method (Henrik's API)...")
            stats = api_client.get_player_stats(username, tag)
            
            if stats:
                display_stats(stats, username, tag, method="Henrik's API (Fallback)")
            else:
                print("❌ No stats found via fallback method")
            return
        
        # Test 1: Fast method with direct PD API
        print("=" * 80)
        print("🚀 TEST 1: Direct PD API (Fast Method)")
        print("=" * 80)
        start_time = time.time()
        
        stats_fast = api_client.get_player_stats_fast(
            puuid=puuid,
            season_id=season_id,
            name=username,
            tag=tag
        )
        
        elapsed_fast = time.time() - start_time
        
        if stats_fast:
            display_stats(stats_fast, username, tag, elapsed_fast, "Direct PD API")
        else:
            print("❌ Fast method failed")
        
        print()
        
        # Test 2: Cached retrieval (should be instant)
        print("=" * 80)
        print("🎯 TEST 2: Cached Retrieval (Should be instant)")
        print("=" * 80)
        start_time = time.time()
        
        stats_cached = api_client.get_player_stats_fast(
            puuid=puuid,
            season_id=season_id,
            name=username,
            tag=tag
        )
        
        elapsed_cached = time.time() - start_time
        
        if stats_cached:
            print(f"⚡ Cached retrieval time: {elapsed_cached:.3f}s")
            print("✅ Cache is working! (Should be < 0.1s)")
            print()
            display_stats(stats_cached, username, tag, elapsed_cached, "Cached (Direct PD API)")
        else:
            print("❌ Cached method failed")
        
        print()
        
        # Test 3: Henrik's API comparison (fallback)
        print("=" * 80)
        print("📊 TEST 3: Henrik's API (Fallback Comparison)")
        print("=" * 80)
        start_time = time.time()
        
        stats_henrik = api_client.get_player_stats(username, tag)
        
        elapsed_henrik = time.time() - start_time
        
        if stats_henrik:
            display_stats(stats_henrik, username, tag, elapsed_henrik, "Henrik's API")
        else:
            print("❌ Henrik's API method failed")
        
        print()
        
        # Performance comparison
        print("=" * 80)
        print("📈 PERFORMANCE COMPARISON")
        print("=" * 80)
        print(f"Direct PD API (1st):  {elapsed_fast:.3f}s")
        print(f"Cached (2nd):         {elapsed_cached:.3f}s  (🚀 {elapsed_fast/elapsed_cached:.1f}x faster!)")
        print(f"Henrik's API:         {elapsed_henrik:.3f}s")
        print()
        
        speedup_vs_henrik = elapsed_henrik / elapsed_fast
        speedup_cached = elapsed_fast / elapsed_cached
        
        print(f"✅ Direct PD API is {speedup_vs_henrik:.1f}x faster than Henrik's API")
        print(f"✅ Cached retrieval is {speedup_cached:.1f}x faster than first load")
        print()
        
        # Invalidate cache test
        print("=" * 80)
        print("🗑️ TEST 4: Cache Invalidation")
        print("=" * 80)
        api_client.invalidate_mmr_cache()
        print("✅ Cache invalidated successfully")
        print()
        
        # Test after invalidation
        print("🔄 Fetching after cache invalidation...")
        start_time = time.time()
        
        stats_after_clear = api_client.get_player_stats_fast(
            puuid=puuid,
            season_id=season_id,
            name=username,
            tag=tag
        )
        
        elapsed_after_clear = time.time() - start_time
        
        if stats_after_clear:
            print(f"✅ Fetched after clear: {elapsed_after_clear:.3f}s")
            print("   (Should be similar to first load time)")
        
        print()
        print("=" * 80)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


def display_stats(stats, username: str, tag: str, elapsed: float = None, method: str = "Unknown"):
    """Display player stats in a formatted way"""
    print()
    if elapsed:
        print(f"⏱️  Fetch time: {elapsed:.3f} seconds")
    print(f"📡 Method: {method}")
    print()
    print(f"👤 Player: {username}#{tag}")
    print("-" * 60)
    
    if hasattr(stats, 'player_level') and stats.player_level > 0:
        print(f"   Level:          {stats.player_level}")
    
    if hasattr(stats, 'rank'):
        print(f"   Current Rank:   {stats.rank}", end="")
        if hasattr(stats, 'rr') and stats.rr > 0:
            print(f" ({stats.rr} RR)")
        else:
            print()
    
    if hasattr(stats, 'peak_rank') and stats.peak_rank != "Unranked":
        print(f"   Peak Rank:      {stats.peak_rank}")
    
    if hasattr(stats, 'kd_ratio') and stats.kd_ratio > 0:
        print(f"   K/D Ratio:      {stats.kd_ratio:.2f}")
    
    if hasattr(stats, 'headshot_rate') and stats.headshot_rate > 0:
        print(f"   Headshot %:     {stats.headshot_rate:.1%}")
    
    if hasattr(stats, 'win_rate') and stats.win_rate > 0:
        print(f"   Win Rate:       {stats.win_rate:.1%}")
    
    if hasattr(stats, 'matches_played') and stats.matches_played > 0:
        print(f"   Matches:        {stats.matches_played} played", end="")
        if hasattr(stats, 'wins') and hasattr(stats, 'losses'):
            print(f" ({stats.wins}W - {stats.losses}L)")
        else:
            print()
    
    print("-" * 60)
    print()


def main():
    """Main entry point"""
    print()
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                    🚀 FAST STATS SYSTEM TEST TOOL                          ║")
    print("║                      (Rank-Yoinker Approach)                               ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Get player name from command line or prompt
    if len(sys.argv) >= 2:
        # Format: python test_fast_stats.py PlayerName#TAG
        full_name = sys.argv[1]
        if '#' in full_name:
            username, tag = full_name.split('#', 1)
        else:
            print("❌ Error: Please use format PlayerName#TAG")
            print("   Example: python test_fast_stats.py TenZ#SEN")
            return
    else:
        # Interactive mode
        print("📝 Enter player name to test")
        print("   Format: PlayerName#TAG")
        print("   Example: TenZ#SEN")
        print()
        full_name = input("👤 Player name: ").strip()
        
        if not full_name:
            print("❌ No name provided. Exiting.")
            return
        
        if '#' not in full_name:
            print("❌ Error: Please use format PlayerName#TAG")
            return
        
        username, tag = full_name.split('#', 1)
    
    print()
    
    # Run the test
    test_player_stats(username, tag)
    
    print()
    print("🎉 Test complete! Press Enter to exit...")
    input()


if __name__ == "__main__":
    main()

