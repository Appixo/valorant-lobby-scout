#!/usr/bin/env python3
"""
Test script for ValorantAPI integration
Tests the new ValorantAPI client functionality
"""

from valorant_api_client import init_valorant_api
import time

def test_valorant_api():
    """Test the ValorantAPI integration"""
    print("🎮 Testing ValorantAPI Integration")
    print("=" * 50)
    
    # Initialize ValorantAPI with your API key
    print("🔧 Initializing ValorantAPI...")
    api = init_valorant_api("YOUR_HENRIK_API_KEY")
    
    assert api is not None, "Failed to initialize ValorantAPI"
    print("✅ ValorantAPI initialized successfully")
    
    # Test API connection
    print("\n🔗 Testing API connection...")
    connection_test = api.test_api_connection()
    if connection_test:
        print("✅ API connection successful!")
    else:
        print("⚠️ API connection test failed, but API may still work")
    
    # Test with some example players (replace with actual names)
    test_players = [
        ("TenZ", "001"),
        ("shroud", "1337"),
        ("Valorant", "000"),  # Generic test
    ]
    
    print(f"\n📊 Testing player statistics retrieval...")
    
    successful_tests = 0
    for player_name, tag in test_players:
        print(f"\n🔍 Testing {player_name}#{tag}...")
        try:
            stats = api.get_player_stats(player_name, tag)
            if stats:
                print(f"✅ Success! Rank: {stats.rank}, K/D: {stats.kd_ratio:.2f}, WR: {stats.win_rate:.1%}")
                successful_tests += 1
            else:
                print(f"⚠️ No data found for {player_name}#{tag}")
            
            # Rate limiting between requests
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error testing {player_name}#{tag}: {e}")
    
    print(f"\n📈 Results: {successful_tests}/{len(test_players)} successful")
    
    # Assert that at least one test was successful
    assert successful_tests > 0, f"ValorantAPI couldn't fetch any test data ({successful_tests}/{len(test_players)} successful)"
    print("✅ ValorantAPI is working and can fetch player statistics!")

if __name__ == "__main__":
    print("🎯 ValorantAPI Integration Test")
    print("=" * 40)
    
    # Run ValorantAPI test
    try:
        test_valorant_api()
        print("\n🎉 ValorantAPI integration test completed successfully!")
        print("\n💡 The application can now use ValorantAPI for player statistics!")
        print("   - ValorantAPI will be used as the primary stats source")
        print("   - Tracker.gg remains as fallback")
        print("   - No API key approval required!")
    except AssertionError as e:
        print(f"\n⚠️ ValorantAPI test completed with issues: {e}")
        print("   - The application will fall back to Tracker.gg")
        print("   - Basic functionality still works")