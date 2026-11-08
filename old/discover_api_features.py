#!/usr/bin/env python3
"""
Quick Valorant API Feature Discovery
Tests available endpoints and features from different APIs
"""

import requests
import json
import time

def test_henrik_api_endpoints():
    """Test what endpoints are available in Henrik's API"""
    print("🔍 Testing Henrik's Valorant API Endpoints")
    print("=" * 45)
    
    api_key = "YOUR_HENRIK_API_KEY"
    base_url = "https://api.henrikdev.xyz"
    headers = {
        'Authorization': api_key,
        'User-Agent': 'ValorantAPIDiscovery/1.0'
    }
    
    # Test basic endpoints
    endpoints_to_test = [
        # Account/Player endpoints
        ("/valorant/v1/account/TenZ/001", "Account Info"),
        ("/valorant/v2/mmr/eu/TenZ/001", "MMR Data"),
        ("/valorant/v1/mmr-history/eu/TenZ/001", "MMR History"),
        
        # Match endpoints  
        ("/valorant/v3/matches/eu/TenZ/001?size=3", "Match History"),
        
        # Leaderboard endpoints
        ("/valorant/v2/leaderboard/eu", "Leaderboard"),
        
        # Store endpoints (if available)
        ("/valorant/v1/store-featured", "Featured Store"),
        ("/valorant/v1/store-offers", "Store Offers"),
        
        # Esports endpoints (if available)
        ("/valorant/v1/esports/schedule", "Esports Schedule"),
        
        # Status endpoints
        ("/valorant/v1/status/eu", "Server Status"),
        ("/valorant/v1/version", "Game Version"),
    ]
    
    working_endpoints = []
    
    for endpoint, description in endpoints_to_test:
        try:
            print(f"Testing: {description} ({endpoint})")
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ SUCCESS - Status: {data.get('status', 'unknown')}")
                working_endpoints.append((endpoint, description, data))
                
                # Show sample data structure
                if 'data' in data and isinstance(data['data'], dict):
                    keys = list(data['data'].keys())[:5]  # First 5 keys
                    print(f"     Data keys: {keys}")
                elif 'data' in data and isinstance(data['data'], list) and data['data']:
                    if isinstance(data['data'][0], dict):
                        keys = list(data['data'][0].keys())[:5]
                        print(f"     Item keys: {keys}")
                    print(f"     Array length: {len(data['data'])}")
                    
            elif response.status_code == 404:
                print(f"  ⚠️ NOT FOUND (404) - Endpoint may not exist")
            elif response.status_code == 403:
                print(f"  🔒 FORBIDDEN (403) - May need different permissions")
            elif response.status_code == 429:
                print(f"  ⏳ RATE LIMITED (429) - Too many requests")
                time.sleep(2)
            else:
                print(f"  ❌ ERROR {response.status_code}")
                
        except Exception as e:
            print(f"  💥 EXCEPTION: {e}")
        
        time.sleep(1)  # Rate limiting
        print()
    
    return working_endpoints

def test_valorant_api_com():
    """Test what's available from Valorant-API.com"""
    print("🎨 Testing Valorant-API.com Endpoints")
    print("=" * 40)
    
    base_url = "https://valorant-api.com/v1"
    
    endpoints_to_test = [
        ("/agents", "All Agents"),
        ("/agents?isPlayableCharacter=true", "Playable Agents"),
        ("/maps", "All Maps"),
        ("/weapons", "All Weapons"),
        ("/gear", "Gear/Armor"),
        ("/buddies", "Gun Buddies"),
        ("/cards", "Player Cards"),
        ("/sprays", "Sprays"),
        ("/titles", "Player Titles"),
        ("/currencies", "In-game Currencies"),
        ("/gamemodes", "Game Modes"),
        ("/seasons", "Seasons"),
        ("/competitivetiers", "Competitive Tiers/Ranks"),
        ("/contenttiers", "Content Tiers"),
        ("/contracts", "Contracts"),
        ("/events", "Events"),
        ("/ceremonies", "Ceremonies"),
        ("/levelborders", "Level Borders"),
    ]
    
    working_endpoints = []
    
    for endpoint, description in endpoints_to_test:
        try:
            print(f"Testing: {description} ({endpoint})")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ SUCCESS - Status: {data.get('status', 'unknown')}")
                working_endpoints.append((endpoint, description, data))
                
                # Show data structure
                if 'data' in data and isinstance(data['data'], list) and data['data']:
                    print(f"     Items count: {len(data['data'])}")
                    if isinstance(data['data'][0], dict):
                        keys = list(data['data'][0].keys())[:5]
                        print(f"     Sample keys: {keys}")
                elif 'data' in data and isinstance(data['data'], dict):
                    keys = list(data['data'].keys())[:5]
                    print(f"     Data keys: {keys}")
                    
            else:
                print(f"  ❌ ERROR {response.status_code}")
                
        except Exception as e:
            print(f"  💥 EXCEPTION: {e}")
        
        time.sleep(0.5)  # Small delay
        print()
    
    return working_endpoints

def explore_specific_data(working_henrik_endpoints, working_valorant_endpoints):
    """Explore specific interesting data from working endpoints"""
    print("🔍 Exploring Specific Data")
    print("=" * 30)
    
    # Explore agents data
    for endpoint, desc, data in working_valorant_endpoints:
        if "agents" in endpoint and "?isPlayableCharacter=true" not in endpoint:
            print("🎭 Agent Information:")
            agents = data.get('data', [])
            for agent in agents[:3]:  # First 3 agents
                if agent.get('isPlayableCharacter', False):
                    print(f"   - {agent.get('displayName', 'Unknown')}: {agent.get('role', {}).get('displayName', 'Unknown role')}")
                    abilities = agent.get('abilities', [])
                    if abilities:
                        print(f"     Abilities: {[a.get('displayName', 'Unknown') for a in abilities[:3]]}")
            print()
            break
    
    # Explore maps data
    for endpoint, desc, data in working_valorant_endpoints:
        if "maps" in endpoint:
            print("🗺️ Map Information:")
            maps = data.get('data', [])
            for map_data in maps[:3]:  # First 3 maps
                print(f"   - {map_data.get('displayName', 'Unknown')}: {map_data.get('coordinates', 'No coordinates')}")
                callouts = map_data.get('callouts', [])
                if callouts:
                    print(f"     Callouts: {[c.get('regionName', 'Unknown') for c in callouts[:3]]}")
            print()
            break
    
    # Explore match data if available
    for endpoint, desc, data in working_henrik_endpoints:
        if "matches" in endpoint:
            print("🎮 Match Data Structure:")
            matches = data.get('data', [])
            if matches:
                match = matches[0]
                metadata = match.get('metadata', {})
                print(f"   Map: {metadata.get('map', 'Unknown')}")
                print(f"   Mode: {metadata.get('mode', 'Unknown')}")
                print(f"   Rounds: {metadata.get('rounds_played', 0)}")
                
                players = match.get('players', {}).get('all_players', [])
                if players:
                    player = players[0]
                    print(f"   Player example: {player.get('name', 'Unknown')}#{player.get('tag', 'Unknown')}")
                    print(f"   Agent: {player.get('character', 'Unknown')}")
                    stats = player.get('stats', {})
                    print(f"   Stats: {stats.get('kills', 0)}/{stats.get('deaths', 0)}/{stats.get('assists', 0)}")
                    
                    # Check for additional data
                    economy = player.get('economy', {})
                    if economy:
                        print(f"   Economy data available: {list(economy.keys())}")
                    
                    abilities = player.get('ability_casts', {})
                    if abilities:
                        print(f"   Ability casts: {abilities}")
            print()
            break

def generate_feature_summary(henrik_endpoints, valorant_endpoints):
    """Generate a summary of available features"""
    print("📋 Available Features Summary")
    print("=" * 35)
    
    print("🔥 Henrik's API Features:")
    for endpoint, desc, _ in henrik_endpoints:
        print(f"   ✅ {desc}")
    
    print(f"\n🎨 Valorant-API.com Features:")
    for endpoint, desc, _ in valorant_endpoints:
        print(f"   ✅ {desc}")
    
    print(f"\n💡 Implementation Suggestions:")
    print("   1. Enhanced Player Profiles (combine rank + agent data)")
    print("   2. Map-specific performance tracking")
    print("   3. Agent recommendation system")
    print("   4. Weapon usage analytics")
    print("   5. Live match overlay with callouts")
    print("   6. Competitive tier progression tracking")
    print("   7. Store rotation notifications")
    print("   8. Esports schedule integration")

def main():
    """Main discovery function"""
    print("🚀 Valorant API Feature Discovery")
    print("=" * 50)
    print("Discovering what additional features are available...\n")
    
    # Test Henrik's API
    henrik_endpoints = test_henrik_api_endpoints()
    print()
    
    # Test Valorant-API.com
    valorant_endpoints = test_valorant_api_com()
    print()
    
    # Explore specific data
    explore_specific_data(henrik_endpoints, valorant_endpoints)
    
    # Generate summary
    generate_feature_summary(henrik_endpoints, valorant_endpoints)
    
    # Save results
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'henrik_api_endpoints': [{'endpoint': e, 'description': d} for e, d, _ in henrik_endpoints],
        'valorant_api_endpoints': [{'endpoint': e, 'description': d} for e, d, _ in valorant_endpoints]
    }
    
    with open('api_feature_discovery.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to api_feature_discovery.json")
    print("🎉 Feature discovery completed!")

if __name__ == "__main__":
    main()