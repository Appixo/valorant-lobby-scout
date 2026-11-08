#!/usr/bin/env python3
"""
Test Enhanced Riot API Player Statistics
Demonstrates the new player level, rank, and headshot percentage features
"""

import sys
import json
from valclient.client import Client
from player import Player

def load_settings():
    """Load settings from settings.json"""
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ settings.json not found!")
        return None

def test_enhanced_stats():
    """Test the enhanced Riot API statistics"""
    print("🎮 Testing Enhanced Riot API Player Statistics")
    print("=" * 50)
    
    # Load settings
    settings = load_settings()
    if not settings:
        return
    
    try:
        # Initialize client
        print("🔌 Connecting to Valorant client...")
        client = Client(region=settings.get('region', 'na'))
        client.activate()
        print("✅ Connected successfully!")
        
        # Get current player info
        presence = client.fetch_presence(client.puuid)
        if not presence:
            print("❌ Could not fetch player presence")
            return
        
        print(f"👤 Testing with local player: {client.puuid}")
        
        # Create a test player instance
        test_player = Player(
            client=client,
            puuid=client.puuid,
            agentID=None,
            incognito=False,
            team="Unknown"
        )
        
        print(f"📋 Player: {test_player.full_name}")
        print("🔄 Fetching enhanced statistics...")
        
        # Test enhanced Riot API stats
        test_player.get_enhanced_riot_stats()
        
        # Display results
        print("\n📊 Enhanced Statistics Results:")
        print("-" * 30)
        
        stats = test_player.get_stats_summary()
        for key, value in stats.items():
            if key not in ['agent', 'team', 'hidden']:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print(f"\n🎯 Enhanced Display String:")
        print(f"   {test_player.get_enhanced_stats_display()}")
        
        # Test fallback to Tracker.gg if needed
        print(f"\n🔄 Testing Tracker.gg fallback...")
        test_player.get_competitive_stats()
        
        print(f"\n✅ Test completed!")
        print(f"   - Riot API Stats Loaded: {test_player.riot_stats_loaded}")
        print(f"   - Tracker.gg Stats Loaded: {test_player.stats_loaded}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_stats()