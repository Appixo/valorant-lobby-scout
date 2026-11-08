#!/usr/bin/env python3
"""
Test script for specific player: Titot#5158
Tests both ValorantAPI and Tracker.gg API
"""

import sys
import time

def test_player_titot():
    """Test the specific player Titot#5158"""
    player_name = "Titot"
    tag = "5158"
    
    print(f"🎯 Testing Player: {player_name}#{tag}")
    print("=" * 50)
    
    # Test 1: ValorantAPI
    print("\n🎮 Testing ValorantAPI...")
    try:
        from valorant_api_client import init_valorant_api
        
        api = init_valorant_api()
        if api:
            print("✅ ValorantAPI client initialized")
            stats = api.get_player_stats(player_name, tag)
            if stats:
                print(f"✅ ValorantAPI Success!")
                print(f"   Rank: {stats.rank}")
                print(f"   RR: {stats.rr}")
                print(f"   Peak: {stats.peak_rank}")
                print(f"   K/D: {stats.kd_ratio:.2f}")
                print(f"   Win Rate: {stats.win_rate:.1%}")
                print(f"   Headshot Rate: {stats.headshot_rate:.1%}")
                print(f"   Matches: {stats.matches_played}")
            else:
                print("⚠️ ValorantAPI: No data found")
        else:
            print("❌ ValorantAPI: Failed to initialize")
    except Exception as e:
        print(f"❌ ValorantAPI Error: {e}")
    
    # Test 2: Tracker.gg API
    print("\n🔗 Testing Tracker.gg API...")
    try:
        from tracker_api import init_tracker_api
        
        api_key = "YOUR_TRACKER_API_KEY"
        api = init_tracker_api(api_key)
        if api:
            print("✅ Tracker.gg client initialized")
            stats = api.get_player_stats(player_name, tag)
            if stats:
                print(f"✅ Tracker.gg Success!")
                print(f"   Rank: {stats.rank}")
                print(f"   RR: {stats.rr}")
                print(f"   Peak: {stats.peak_rank}")
                print(f"   K/D: {stats.kd_ratio:.2f}")
                print(f"   Win Rate: {stats.win_rate:.1%}")
                print(f"   Headshot Rate: {stats.headshot_rate:.1%}")
                print(f"   Matches: {stats.matches_played}")
            else:
                print("⚠️ Tracker.gg: No data found")
        else:
            print("❌ Tracker.gg: Failed to initialize")
    except Exception as e:
        print(f"❌ Tracker.gg Error: {e}")
    
    # Test 3: Player class integration
    print("\n👤 Testing Player Class Integration...")
    try:
        from player import Player
        
        # Create a mock client (we don't need real Valorant client for stats testing)
        class MockClient:
            def put(self, endpoint, endpoint_type, json_data):
                return [{"GameName": player_name, "TagLine": tag}]
        
        mock_client = MockClient()
        
        # Create player instance
        test_player = Player(
            client=mock_client,
            puuid="test-uuid",
            agentID="test-agent",
            incognito=False,
            team="Unknown"
        )
        
        print(f"✅ Player created: {test_player.full_name}")
        
        # Test stats fetching
        print("🔄 Testing on-demand stats...")
        success, result = test_player.get_tracker_stats_on_demand()
        
        if success:
            print(f"✅ Stats Success: {result}")
        else:
            print(f"⚠️ Stats Failed: {result}")
            
    except Exception as e:
        print(f"❌ Player Class Error: {e}")
    
    print(f"\n🎉 Test completed for {player_name}#{tag}")

if __name__ == "__main__":
    test_player_titot()