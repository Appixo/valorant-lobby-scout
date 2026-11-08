#!/usr/bin/env python3
"""
Test script for Tracker.gg API integration
Tests the API with the provided key and validates functionality
"""

from tracker_api import init_tracker_api, TrackerGGAPI
import time

def test_api_integration():
    """Test the complete API integration"""
    print("🧪 Testing Tracker.gg API Integration")
    print("=" * 50)
    
    # Initialize API with your new key
    api_key = "YOUR_TRACKER_API_KEY"
    
    # Initialize the API
    print("🔧 Initializing Tracker.gg API...")
    api = init_tracker_api(api_key)
    
    assert api is not None, "Failed to initialize API"
    print("✅ API initialized successfully")
    
    # Test API connection
    print("\n🔗 Testing API connection...")
    connection_success = api.test_api_connection()
    print("✅ API connection successful!" if connection_success else "❌ API connection failed")
    assert connection_success, "API connection failed"
    
    # Test with a known player (you can replace with actual player names)
    test_players = [
        ("TenZ", "001"),  # Known public profile
        ("Shroud", "1337"),  # Another known profile
    ]
    
    print(f"\n📊 Testing player statistics retrieval...")
    
    stats_retrieved = False
    for player_name, tag in test_players:
        print(f"\n🎯 Testing: {player_name}#{tag}")
        print("-" * 30)
        
        try:
            stats = api.get_player_stats(player_name, tag)
            
            if stats:
                print(f"✅ SUCCESS! Retrieved stats:")
                print(f"   Name: {stats.name}")
                print(f"   Rank: {stats.rank}")
                print(f"   Peak Rank: {stats.peak_rank}")
                print(f"   K/D Ratio: {stats.kd_ratio:.2f}")
                print(f"   Win Rate: {stats.win_rate:.1%}")
                print(f"   Avg Score: {stats.avg_score:.0f}")
                print(f"   Matches: {stats.matches_played}")
                stats_retrieved = True
            else:
                print(f"⚠️ No stats found for {player_name}#{tag}")
                
        except Exception as e:
            print(f"❌ Error testing {player_name}#{tag}: {e}")
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\n" + "=" * 50)
    print("🏁 API integration test completed!")
    
    # Assert that we successfully retrieved stats for at least one player
    assert stats_retrieved, "Failed to retrieve stats for any test players"

def test_caching():
    """Test the caching functionality"""
    print("\n🗄️ Testing caching functionality...")
    
    api_key = "YOUR_TRACKER_API_KEY"
    api = TrackerGGAPI(api_key)
    
    # Test same player twice to verify caching
    test_player = ("TenZ", "001")
    
    print(f"First request for {test_player[0]}#{test_player[1]}:")
    start_time = time.time()
    stats1 = api.get_player_stats(test_player[0], test_player[1])
    first_duration = time.time() - start_time
    
    print(f"Second request (should be cached):")
    start_time = time.time()
    stats2 = api.get_player_stats(test_player[0], test_player[1])
    second_duration = time.time() - start_time
    
    print(f"First request: {first_duration:.2f}s")
    print(f"Second request: {second_duration:.2f}s")
    
    if second_duration < first_duration * 0.5:
        print("✅ Caching appears to be working!")
    else:
        print("⚠️ Caching may not be working optimally")
    
    # Assert that caching is working (second request should be significantly faster)
    assert second_duration < first_duration * 0.5, f"Caching not working optimally: {second_duration:.2f}s vs {first_duration:.2f}s"

if __name__ == "__main__":
    print("🎯 Valorant Tracker.gg API Integration Test")
    print("==========================================")
    
    # Run API integration test
    try:
        test_api_integration()
        # Test caching if API works
        test_caching()
        print("\n🎉 All tests completed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    
    print("\n💡 You can now use the application with Tracker.gg statistics!")
    print("   - Open the GUI with: python main.py")
    print("   - The application will now fetch real player statistics")
    print("   - Statistics are cached for 1 hour to improve performance")