#!/usr/bin/env python3
"""
Advanced Valorant API Explorer
Tests and demonstrates additional features available from various Valorant APIs
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import valo_api
from valorant_api_client import init_valorant_api

@dataclass
class EnhancedMatchData:
    """Enhanced match data structure"""
    match_id: str
    map_name: str
    game_mode: str
    rounds_played: int
    game_length_minutes: float
    player_performance: Dict[str, Any]
    round_details: List[Dict[str, Any]]
    economy_data: Dict[str, Any]
    ability_usage: Dict[str, int]

@dataclass
class AgentPerformance:
    """Agent-specific performance metrics"""
    agent_name: str
    matches_played: int
    win_rate: float
    avg_kills: float
    avg_deaths: float
    avg_assists: float
    ability_efficiency: Dict[str, Any]

class ValorantAPIExplorer:
    """Explorer for advanced Valorant API features"""
    
    def __init__(self, henrik_api_key: str):
        self.henrik_api_key = henrik_api_key
        self.henrik_base_url = "https://api.henrikdev.xyz"
        self.valorant_api_base = "https://valorant-api.com/v1"
        
        # Initialize Henrik's API client
        init_valorant_api(henrik_api_key)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1.0
    
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_henrik_request(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated request to Henrik's API"""
        try:
            self._rate_limit()
            headers = {
                'Authorization': self.henrik_api_key,
                'User-Agent': 'ValorantAPIExplorer/1.0'
            }
            response = requests.get(f"{self.henrik_base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Henrik API error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Error making Henrik API request: {e}")
            return None
    
    def _make_valorant_api_request(self, endpoint: str) -> Optional[Dict]:
        """Make request to Valorant-API.com (no auth required)"""
        try:
            response = requests.get(f"{self.valorant_api_base}{endpoint}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Valorant-API error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Error making Valorant-API request: {e}")
            return None
    
    def get_detailed_match_history(self, name: str, tag: str, region: str = "eu", size: int = 5) -> Optional[List[EnhancedMatchData]]:
        """Get detailed match history with enhanced data"""
        print(f"🔍 Getting detailed match history for {name}#{tag}...")
        
        endpoint = f"/valorant/v3/matches/{region}/{name}/{tag}?size={size}"
        data = self._make_henrik_request(endpoint)
        
        if not data or data.get('status') != 200:
            return None
        
        enhanced_matches = []
        for match in data.get('data', []):
            try:
                metadata = match.get('metadata', {})
                players = match.get('players', {})
                
                # Find the player in the match
                player_data = None
                for player in players.get('all_players', []):
                    if (player.get('name', '').lower() == name.lower() and 
                        player.get('tag', '').lower() == tag.lower()):
                        player_data = player
                        break
                
                if player_data:
                    enhanced_match = EnhancedMatchData(
                        match_id=metadata.get('matchid', ''),
                        map_name=metadata.get('map', ''),
                        game_mode=metadata.get('mode', ''),
                        rounds_played=metadata.get('rounds_played', 0),
                        game_length_minutes=metadata.get('game_length', 0) / 60000,  # Convert to minutes
                        player_performance={
                            'kills': player_data.get('stats', {}).get('kills', 0),
                            'deaths': player_data.get('stats', {}).get('deaths', 0),
                            'assists': player_data.get('stats', {}).get('assists', 0),
                            'score': player_data.get('stats', {}).get('score', 0),
                            'headshots': player_data.get('stats', {}).get('headshots', 0),
                            'bodyshots': player_data.get('stats', {}).get('bodyshots', 0),
                            'legshots': player_data.get('stats', {}).get('legshots', 0)
                        },
                        round_details=match.get('rounds', []),
                        economy_data=player_data.get('economy', {}),
                        ability_usage=player_data.get('ability_casts', {})
                    )
                    enhanced_matches.append(enhanced_match)
                    
            except Exception as e:
                print(f"Error processing match: {e}")
                continue
        
        return enhanced_matches
    
    def analyze_agent_performance(self, name: str, tag: str, region: str = "eu") -> Dict[str, AgentPerformance]:
        """Analyze performance with different agents"""
        print(f"🎯 Analyzing agent performance for {name}#{tag}...")
        
        matches = self.get_detailed_match_history(name, tag, region, size=20)
        if not matches:
            return {}
        
        agent_stats = {}
        
        for match in matches:
            # We need to get the full match data to see which agent was played
            match_details = self.get_match_details(match.match_id)
            if not match_details:
                continue
            
            # Find player's agent in this match
            agent_name = self._find_player_agent(match_details, name, tag)
            if not agent_name:
                continue
            
            if agent_name not in agent_stats:
                agent_stats[agent_name] = {
                    'matches': [],
                    'wins': 0,
                    'total_kills': 0,
                    'total_deaths': 0,
                    'total_assists': 0,
                    'ability_casts': {}
                }
            
            # Add match data
            agent_stats[agent_name]['matches'].append(match)
            
            # Check if won (this requires team data from match details)
            if self._did_player_win(match_details, name, tag):
                agent_stats[agent_name]['wins'] += 1
            
            # Add performance stats
            perf = match.player_performance
            agent_stats[agent_name]['total_kills'] += perf.get('kills', 0)
            agent_stats[agent_name]['total_deaths'] += perf.get('deaths', 0)
            agent_stats[agent_name]['total_assists'] += perf.get('assists', 0)
            
            # Add ability usage
            for ability, casts in match.ability_usage.items():
                if ability not in agent_stats[agent_name]['ability_casts']:
                    agent_stats[agent_name]['ability_casts'][ability] = 0
                agent_stats[agent_name]['ability_casts'][ability] += casts
        
        # Convert to AgentPerformance objects
        result = {}
        for agent_name, stats in agent_stats.items():
            matches_count = len(stats['matches'])
            if matches_count > 0:
                result[agent_name] = AgentPerformance(
                    agent_name=agent_name,
                    matches_played=matches_count,
                    win_rate=stats['wins'] / matches_count,
                    avg_kills=stats['total_kills'] / matches_count,
                    avg_deaths=stats['total_deaths'] / matches_count,
                    avg_assists=stats['total_assists'] / matches_count,
                    ability_efficiency=stats['ability_casts']
                )
        
        return result
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed match information by match ID"""
        endpoint = f"/valorant/v2/match/{match_id}"
        return self._make_henrik_request(endpoint)
    
    def _find_player_agent(self, match_data: Dict, name: str, tag: str) -> Optional[str]:
        """Find which agent a player used in a match"""
        if not match_data or match_data.get('status') != 200:
            return None
        
        players = match_data.get('data', {}).get('players', {}).get('all_players', [])
        for player in players:
            if (player.get('name', '').lower() == name.lower() and 
                player.get('tag', '').lower() == tag.lower()):
                return player.get('character', '')
        
        return None
    
    def _did_player_win(self, match_data: Dict, name: str, tag: str) -> bool:
        """Check if player won the match"""
        if not match_data or match_data.get('status') != 200:
            return False
        
        data = match_data.get('data', {})
        players = data.get('players', {}).get('all_players', [])
        teams = data.get('teams', {})
        
        # Find player's team
        player_team = None
        for player in players:
            if (player.get('name', '').lower() == name.lower() and 
                player.get('tag', '').lower() == tag.lower()):
                player_team = player.get('team', '').lower()
                break
        
        if not player_team or player_team not in teams:
            return False
        
        return teams[player_team].get('has_won', False)
    
    def get_map_statistics(self, name: str, tag: str, region: str = "eu") -> Dict[str, Dict]:
        """Get performance statistics by map"""
        print(f"🗺️ Analyzing map performance for {name}#{tag}...")
        
        matches = self.get_detailed_match_history(name, tag, region, size=20)
        if not matches:
            return {}
        
        map_stats = {}
        
        for match in matches:
            map_name = match.map_name
            if map_name not in map_stats:
                map_stats[map_name] = {
                    'matches': 0,
                    'wins': 0,
                    'total_kills': 0,
                    'total_deaths': 0,
                    'total_score': 0,
                    'total_rounds': 0
                }
            
            # Get full match details to determine win/loss
            match_details = self.get_match_details(match.match_id)
            
            map_stats[map_name]['matches'] += 1
            if match_details and self._did_player_win(match_details, name, tag):
                map_stats[map_name]['wins'] += 1
            
            perf = match.player_performance
            map_stats[map_name]['total_kills'] += perf.get('kills', 0)
            map_stats[map_name]['total_deaths'] += perf.get('deaths', 0)
            map_stats[map_name]['total_score'] += perf.get('score', 0)
            map_stats[map_name]['total_rounds'] += match.rounds_played
        
        # Calculate averages
        for map_name, stats in map_stats.items():
            matches = stats['matches']
            if matches > 0:
                stats['win_rate'] = stats['wins'] / matches
                stats['avg_kills'] = stats['total_kills'] / matches
                stats['avg_deaths'] = stats['total_deaths'] / matches
                stats['avg_score'] = stats['total_score'] / matches
                stats['kd_ratio'] = stats['total_kills'] / max(stats['total_deaths'], 1)
        
        return map_stats
    
    def get_game_assets(self) -> Dict[str, Any]:
        """Get game assets from Valorant-API.com"""
        print("🎨 Fetching game assets...")
        
        assets = {}
        
        # Get agents
        agents_data = self._make_valorant_api_request("/agents")
        if agents_data and agents_data.get('status') == 200:
            assets['agents'] = agents_data.get('data', [])
        
        # Get maps
        maps_data = self._make_valorant_api_request("/maps")
        if maps_data and maps_data.get('status') == 200:
            assets['maps'] = maps_data.get('data', [])
        
        # Get weapons
        weapons_data = self._make_valorant_api_request("/weapons")
        if weapons_data and weapons_data.get('status') == 200:
            assets['weapons'] = weapons_data.get('data', [])
        
        # Get game modes
        modes_data = self._make_valorant_api_request("/gamemodes")
        if modes_data and modes_data.get('status') == 200:
            assets['gamemodes'] = modes_data.get('data', [])
        
        return assets
    
    def generate_performance_report(self, name: str, tag: str, region: str = "eu") -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print(f"📊 Generating comprehensive performance report for {name}#{tag}...")
        
        report = {
            'player': f"{name}#{tag}",
            'region': region,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'match_history': [],
            'agent_performance': {},
            'map_statistics': {},
            'summary': {}
        }
        
        # Get detailed match history
        matches = self.get_detailed_match_history(name, tag, region, size=10)
        if matches:
            report['match_history'] = [asdict(match) for match in matches]
        
        # Get agent performance
        agent_perf = self.analyze_agent_performance(name, tag, region)
        report['agent_performance'] = {k: asdict(v) for k, v in agent_perf.items()}
        
        # Get map statistics
        map_stats = self.get_map_statistics(name, tag, region)
        report['map_statistics'] = map_stats
        
        # Generate summary
        if matches:
            total_kills = sum(m.player_performance.get('kills', 0) for m in matches)
            total_deaths = sum(m.player_performance.get('deaths', 0) for m in matches)
            total_rounds = sum(m.rounds_played for m in matches)
            
            report['summary'] = {
                'matches_analyzed': len(matches),
                'total_rounds_played': total_rounds,
                'overall_kd_ratio': total_kills / max(total_deaths, 1),
                'avg_kills_per_match': total_kills / len(matches),
                'most_played_agent': max(agent_perf.keys(), key=lambda a: agent_perf[a].matches_played) if agent_perf else "Unknown",
                'best_map': max(map_stats.keys(), key=lambda m: map_stats[m]['win_rate']) if map_stats else "Unknown"
            }
        
        return report

def test_advanced_features():
    """Test the advanced API features"""
    print("🚀 Testing Advanced Valorant API Features")
    print("=" * 50)
    
    # Initialize with your API key
    api_key = "YOUR_HENRIK_API_KEY"  # Replace with your actual key
    explorer = ValorantAPIExplorer(api_key)
    
    # Test players (replace with actual player names)
    test_players = [
        ("TenZ", "001", "na"),
        ("Henrik3", "EUW3", "eu"),
    ]
    
    for name, tag, region in test_players:
        print(f"\n🎯 Testing advanced features for {name}#{tag}")
        print("-" * 40)
        
        try:
            # Test detailed match history
            print("📚 Getting detailed match history...")
            matches = explorer.get_detailed_match_history(name, tag, region, size=3)
            if matches:
                print(f"✅ Retrieved {len(matches)} detailed matches")
                for i, match in enumerate(matches[:2]):  # Show first 2
                    print(f"   Match {i+1}: {match.map_name} ({match.game_mode}) - {match.rounds_played} rounds")
                    print(f"   Performance: {match.player_performance['kills']}/{match.player_performance['deaths']}/{match.player_performance['assists']}")
            else:
                print("⚠️ No detailed match data found")
            
            # Test agent performance
            print("\n🎭 Analyzing agent performance...")
            agent_perf = explorer.analyze_agent_performance(name, tag, region)
            if agent_perf:
                print(f"✅ Found performance data for {len(agent_perf)} agents")
                for agent_name, perf in list(agent_perf.items())[:3]:  # Show top 3
                    print(f"   {agent_name}: {perf.matches_played} matches, {perf.win_rate:.1%} WR, {perf.avg_kills:.1f} avg kills")
            else:
                print("⚠️ No agent performance data found")
            
            # Test map statistics
            print("\n🗺️ Analyzing map performance...")
            map_stats = explorer.get_map_statistics(name, tag, region)
            if map_stats:
                print(f"✅ Found performance data for {len(map_stats)} maps")
                for map_name, stats in list(map_stats.items())[:3]:  # Show top 3
                    print(f"   {map_name}: {stats['matches']} matches, {stats['win_rate']:.1%} WR, {stats['kd_ratio']:.2f} K/D")
            else:
                print("⚠️ No map performance data found")
            
            # Generate comprehensive report
            print("\n📊 Generating comprehensive report...")
            report = explorer.generate_performance_report(name, tag, region)
            
            # Save report to file
            report_filename = f"performance_report_{name}_{tag}.json"
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Comprehensive report saved to {report_filename}")
            
            if report['summary']:
                summary = report['summary']
                print(f"   Summary: {summary['matches_analyzed']} matches, {summary['overall_kd_ratio']:.2f} K/D")
                print(f"   Best agent: {summary['most_played_agent']}, Best map: {summary['best_map']}")
            
        except Exception as e:
            print(f"❌ Error testing {name}#{tag}: {e}")
        
        time.sleep(3)  # Rate limiting between players
    
    # Test game assets
    print(f"\n🎨 Testing game assets from Valorant-API.com...")
    try:
        assets = explorer.get_game_assets()
        if assets:
            print(f"✅ Retrieved game assets:")
            if 'agents' in assets:
                print(f"   - {len(assets['agents'])} agents")
            if 'maps' in assets:
                print(f"   - {len(assets['maps'])} maps")
            if 'weapons' in assets:
                print(f"   - {len(assets['weapons'])} weapons")
            if 'gamemodes' in assets:
                print(f"   - {len(assets['gamemodes'])} game modes")
        else:
            print("⚠️ No game assets retrieved")
    except Exception as e:
        print(f"❌ Error getting game assets: {e}")
    
    print(f"\n" + "=" * 50)
    print("🎉 Advanced features testing completed!")
    print("\n💡 New features demonstrated:")
    print("   - Detailed match history with round data")
    print("   - Agent-specific performance analysis")
    print("   - Map-specific statistics")
    print("   - Economy and ability usage tracking")
    print("   - Comprehensive performance reports")
    print("   - Game assets and metadata")

if __name__ == "__main__":
    test_advanced_features()