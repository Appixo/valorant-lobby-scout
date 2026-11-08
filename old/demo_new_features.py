#!/usr/bin/env python3
"""
Demo: New Valorant API Features
Demonstrates how to implement the newly discovered features
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import valo_api

@dataclass
class StoreItem:
    """Store item information"""
    name: str
    price: int
    category: str
    expires_at: str

@dataclass
class EsportsMatch:
    """Esports match information"""
    team1: str
    team2: str
    date: str
    league: str
    status: str

class NewFeaturesDemo:
    """Demonstration of new Valorant API features"""
    
    def __init__(self):
        self.henrik_api_key = "YOUR_HENRIK_API_KEY"
        self.henrik_base = "https://api.henrikdev.xyz"
        self.valorant_api_base = "https://valorant-api.com/v1"
        
        # Initialize Henrik's API
        valo_api.set_api_key(self.henrik_api_key)
        
        print("🚀 Valorant API New Features Demo")
        print("=" * 40)
    
    def demo_store_integration(self):
        """Demo: Store integration and notifications"""
        print("\n🛒 DEMO: Store Integration")
        print("-" * 30)
        
        try:
            # Get featured store items
            store_data = valo_api.get_store_featured_v2()
            if store_data:
                print("✅ Store data retrieved successfully!")
                print(f"📦 Found {len(store_data)} featured items")
                
                # Process store items
                featured_items = []
                for item in store_data[:3]:  # Show first 3 items
                    if hasattr(item, 'display_name') and hasattr(item, 'cost'):
                        featured_items.append(StoreItem(
                            name=getattr(item, 'display_name', 'Unknown'),
                            price=getattr(item, 'cost', 0),
                            category=getattr(item, 'category', 'Unknown'),
                            expires_at=getattr(item, 'expires_at', 'Unknown')
                        ))
                
                # Display featured items
                for item in featured_items:
                    print(f"   🎯 {item.name} - {item.price} VP ({item.category})")
                
                print("\n💡 Feature Ideas:")
                print("   - Notify users when favorite skins appear")
                print("   - Track store rotation patterns")
                print("   - Price history tracking")
                print("   - Wishlist with auto-notifications")
                
            else:
                print("⚠️ No store data available")
                
        except Exception as e:
            print(f"❌ Store demo error: {e}")
    
    def demo_leaderboard_integration(self):
        """Demo: Leaderboard integration"""
        print("\n🏆 DEMO: Leaderboard Integration")
        print("-" * 35)
        
        try:
            # Get leaderboard data
            leaderboard = valo_api.get_leaderboard_v2("eu")
            if leaderboard and hasattr(leaderboard, 'data'):
                players = leaderboard.data[:5]  # Top 5 players
                print("✅ Leaderboard data retrieved!")
                print("🥇 Top 5 EU Players:")
                
                for i, player in enumerate(players, 1):
                    name = getattr(player, 'game_name', 'Unknown')
                    tag = getattr(player, 'tag_line', 'Unknown')
                    rank = getattr(player, 'current_tier_patched', 'Unknown')
                    rr = getattr(player, 'ranking_in_tier', 0)
                    
                    print(f"   {i}. {name}#{tag} - {rank} ({rr} RR)")
                
                print("\n💡 Feature Ideas:")
                print("   - Track your position relative to leaderboard")
                print("   - Alert when friends appear on leaderboard")
                print("   - Regional ranking comparisons")
                print("   - Leaderboard history tracking")
                
            else:
                print("⚠️ No leaderboard data available")
                
        except Exception as e:
            print(f"❌ Leaderboard demo error: {e}")
    
    def demo_esports_integration(self):
        """Demo: Esports schedule integration"""
        print("\n🎮 DEMO: Esports Integration")
        print("-" * 30)
        
        try:
            # Get esports schedule
            headers = {
                'Authorization': self.henrik_api_key,
                'User-Agent': 'ValorantNewFeaturesDemo/1.0'
            }
            
            response = requests.get(
                f"{self.henrik_base}/valorant/v1/esports/schedule",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200 and data.get('data'):
                    matches = data['data'][:5]  # Next 5 matches
                    print("✅ Esports schedule retrieved!")
                    print("📅 Upcoming Matches:")
                    
                    for match in matches:
                        if isinstance(match, dict):
                            date = match.get('date', 'Unknown')
                            state = match.get('state', 'Unknown')
                            league = match.get('league', {}).get('name', 'Unknown League')
                            
                            # Try to get team names if available
                            teams = match.get('teams', [])
                            if len(teams) >= 2:
                                team1 = teams[0].get('name', 'Team 1')
                                team2 = teams[1].get('name', 'Team 2')
                            else:
                                team1, team2 = 'TBD', 'TBD'
                            
                            print(f"   🆚 {team1} vs {team2}")
                            print(f"      📍 {league} - {date} ({state})")
                    
                    print("\n💡 Feature Ideas:")
                    print("   - Match notifications and reminders")
                    print("   - Live score updates")
                    print("   - Player stats from pro matches")
                    print("   - Team performance tracking")
                    
                else:
                    print("⚠️ No esports data in response")
            else:
                print(f"❌ Esports API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Esports demo error: {e}")
    
    def demo_game_assets(self):
        """Demo: Game assets and rich data"""
        print("\n🎨 DEMO: Game Assets Integration")
        print("-" * 35)
        
        try:
            # Get agents data
            response = requests.get(f"{self.valorant_api_base}/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    agents = [a for a in data['data'] if a.get('isPlayableCharacter')][:5]
                    print("✅ Agent data retrieved!")
                    print("🎭 Sample Agents:")
                    
                    for agent in agents:
                        name = agent.get('displayName', 'Unknown')
                        role = agent.get('role', {}).get('displayName', 'Unknown')
                        abilities = [a.get('displayName', 'Unknown') for a in agent.get('abilities', [])]
                        
                        print(f"   🎯 {name} ({role})")
                        print(f"      Abilities: {', '.join(abilities[:3])}")
                        
                        # Show asset URLs
                        if agent.get('displayIcon'):
                            print(f"      🖼️ Icon: Available")
                        if agent.get('fullPortrait'):
                            print(f"      🖼️ Portrait: Available")
            
            # Get maps data
            response = requests.get(f"{self.valorant_api_base}/maps", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    maps = data['data'][:3]
                    print(f"\n🗺️ Sample Maps:")
                    
                    for map_data in maps:
                        name = map_data.get('displayName', 'Unknown')
                        coordinates = map_data.get('coordinates', 'Unknown')
                        callouts = [c.get('regionName', 'Unknown') for c in map_data.get('callouts', [])]
                        
                        print(f"   🗺️ {name} ({coordinates})")
                        if callouts:
                            print(f"      Callouts: {', '.join(callouts[:5])}")
                        if map_data.get('splash'):
                            print(f"      🖼️ Map image: Available")
            
            print("\n💡 Feature Ideas:")
            print("   - Rich agent selection interface")
            print("   - Interactive map callouts overlay")
            print("   - Agent ability guides and tips")
            print("   - Map-specific strategy suggestions")
            
        except Exception as e:
            print(f"❌ Game assets demo error: {e}")
    
    def demo_server_status(self):
        """Demo: Server status monitoring"""
        print("\n🔧 DEMO: Server Status Monitoring")
        print("-" * 35)
        
        try:
            # Get server status
            status = valo_api.get_status_v1("eu")
            if status and hasattr(status, 'data'):
                print("✅ Server status retrieved!")
                
                # Check for maintenances
                maintenances = getattr(status.data, 'maintenances', [])
                incidents = getattr(status.data, 'incidents', [])
                
                print(f"🔧 Maintenances: {len(maintenances)}")
                print(f"⚠️ Incidents: {len(incidents)}")
                
                if maintenances:
                    print("   Scheduled maintenances found")
                if incidents:
                    print("   Active incidents detected")
                
                if not maintenances and not incidents:
                    print("✅ All systems operational!")
                
                print("\n💡 Feature Ideas:")
                print("   - Server status notifications")
                print("   - Maintenance schedule alerts")
                print("   - Regional server comparison")
                print("   - Downtime history tracking")
                
            else:
                print("⚠️ No status data available")
                
        except Exception as e:
            print(f"❌ Server status demo error: {e}")
    
    def demo_implementation_examples(self):
        """Demo: Code examples for implementation"""
        print("\n💻 DEMO: Implementation Examples")
        print("-" * 35)
        
        print("🔧 Enhanced Player Class Example:")
        print("""
class EnhancedPlayer(Player):
    def get_store_notifications(self):
        '''Check for favorite skins in store'''
        store_items = valo_api.get_store_featured_v2()
        favorites = self.get_favorite_skins()
        return [item for item in store_items 
                if item.name in favorites]
    
    def get_leaderboard_position(self, region='eu'):
        '''Find player position on leaderboard'''
        leaderboard = valo_api.get_leaderboard_v2(region)
        for i, player in enumerate(leaderboard.data):
            if (player.game_name == self.name and 
                player.tag_line == self.tag):
                return i + 1
        return None
    
    def get_agent_recommendations(self, map_name):
        '''AI-powered agent recommendations'''
        # Combine player history + map data + meta
        performance = self.get_agent_performance()
        map_meta = self.get_map_meta(map_name)
        return self.calculate_best_agents(performance, map_meta)
        """)
        
        print("\n🎨 UI Enhancement Examples:")
        print("""
# Rich agent display with portraits
def display_player_with_agent(player):
    agent_data = get_agent_data(player.agent)
    portrait_url = agent_data['fullPortrait']
    abilities = agent_data['abilities']
    
    # Show agent portrait + abilities in GUI
    
# Map callouts overlay
def show_map_callouts(map_name):
    map_data = get_map_data(map_name)
    callouts = map_data['callouts']
    
    # Overlay callout names on minimap
        """)
        
        print("\n📊 Analytics Examples:")
        print("""
# Performance trend analysis
def analyze_recent_form(player, matches=20):
    history = get_detailed_match_history(player)
    
    trends = {
        'kd_trend': calculate_kd_trend(history),
        'win_rate_trend': calculate_winrate_trend(history),
        'agent_performance': group_by_agent(history),
        'map_performance': group_by_map(history)
    }
    
    return generate_insights(trends)
        """)

def main():
    """Run all feature demos"""
    demo = NewFeaturesDemo()
    
    # Run all demos
    demo.demo_store_integration()
    demo.demo_leaderboard_integration() 
    demo.demo_esports_integration()
    demo.demo_game_assets()
    demo.demo_server_status()
    demo.demo_implementation_examples()
    
    print(f"\n" + "=" * 50)
    print("🎉 NEW FEATURES DEMO COMPLETED!")
    print("=" * 50)
    
    print("\n🚀 Ready to Implement:")
    print("   1. ✅ Store Integration - Skin notifications")
    print("   2. ✅ Leaderboard Tracking - Competitive rankings") 
    print("   3. ✅ Esports Integration - Match schedules")
    print("   4. ✅ Rich Game Assets - Agent portraits, maps")
    print("   5. ✅ Server Monitoring - Status notifications")
    
    print("\n💡 Next Steps:")
    print("   - Choose which features to implement first")
    print("   - Design UI mockups for new features")
    print("   - Set up data storage for enhanced analytics")
    print("   - Create notification system for real-time alerts")
    
    print("\n📈 Your app can now offer 10x more value to users!")

if __name__ == "__main__":
    main()