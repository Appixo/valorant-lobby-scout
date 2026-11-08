"""
Tracker.gg API Client for Valorant Player Statistics
Provides efficient, authenticated API access for player stats and ranks.
"""

import requests
import time
from typing import Dict, Optional, Any
import json
from dataclasses import dataclass
from cache_manager import CacheManager

@dataclass
class PlayerStats:
    """Player statistics data structure"""
    name: str = ""
    rank: str = "Unranked"
    rr: int = 0
    peak_rank: str = "Unranked"
    kd_ratio: float = 0.0
    win_rate: float = 0.0
    avg_score: float = 0.0
    headshot_rate: float = 0.0
    matches_played: int = 0
    last_updated: str = ""

class TrackerGGAPI:
    """Official Tracker.gg API client for Valorant statistics"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://public-api.tracker.gg/v2/valorant/standard"  # Use standard endpoint
        self.session = requests.Session()
        self.session.headers.update({
            'TRN-Api-Key': api_key,  # This should be the App ID
            'User-Agent': 'ValorantLobbyScout/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1.0  # 1 second between requests
        
        # Caching
        self.cache_manager = CacheManager()
        self.cache_duration = 3600  # 1 hour cache
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated API request with rate limiting"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_delay:
                time.sleep(self.min_delay - time_since_last)
            
            self.last_request_time = time.time()
            
            # Make request
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Player not found: {endpoint}")
                return None
            elif response.status_code == 429:
                print("Rate limited by Tracker.gg API")
                time.sleep(5)  # Wait 5 seconds and try again
                return None
            else:
                print(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error making API request: {e}")
            return None
    
    def get_player_stats(self, player_name: str, tag: str) -> Optional[PlayerStats]:
        """
        Get comprehensive player statistics using official API
        
        Args:
            player_name: Player's display name
            tag: Player's tag (without #)
            
        Returns:
            PlayerStats object or None if not found
        """
        try:
            # Check cache first
            cache_key = f"tracker_api_{player_name}_{tag}"
            cached_stats = self.cache_manager.get_cached_data(cache_key, self.cache_duration)
            if cached_stats:
                return PlayerStats(**cached_stats)
            
            # Make API request - use standard endpoint format
            endpoint = f"profile/riot/{player_name}%23{tag}"
            data = self._make_request(endpoint)
            
            if not data:
                return None
            
            stats = PlayerStats(name=f"{player_name}#{tag}")
            
            # Parse player data
            if 'data' in data:
                player_data = data['data']
                
                # Extract segments (different game modes)
                segments = player_data.get('segments', [])
                
                for segment in segments:
                    segment_type = segment.get('type', '')
                    attributes = segment.get('attributes', {})
                    segment_stats = segment.get('stats', {})
                    
                    # Competitive/Ranked data
                    if segment_type == 'overview' and attributes.get('mode') == 'competitive':
                        # Current rank
                        if 'tier' in segment_stats:
                            tier_data = segment_stats['tier']
                            if tier_data.get('displayValue'):
                                stats.rank = tier_data['displayValue']
                        
                        # Ranked Rating
                        if 'rankedRating' in segment_stats:
                            rr_data = segment_stats['rankedRating']
                            if rr_data.get('displayValue'):
                                try:
                                    stats.rr = int(rr_data['displayValue'].replace(',', ''))
                                except:
                                    pass
                        
                        # Peak rank
                        if 'peakTier' in segment_stats:
                            peak_data = segment_stats['peakTier']
                            if peak_data.get('displayValue'):
                                stats.peak_rank = peak_data['displayValue']
                        
                        # K/D Ratio
                        if 'kDRatio' in segment_stats:
                            kd_data = segment_stats['kDRatio']
                            if kd_data.get('displayValue'):
                                try:
                                    stats.kd_ratio = float(kd_data['displayValue'])
                                except:
                                    pass
                        
                        # Win Rate
                        if 'winRate' in segment_stats:
                            wr_data = segment_stats['winRate']
                            if wr_data.get('displayValue'):
                                try:
                                    # Remove % sign and convert
                                    wr_str = wr_data['displayValue'].replace('%', '')
                                    stats.win_rate = float(wr_str) / 100.0
                                except:
                                    pass
                        
                        # Average Score
                        if 'avgScore' in segment_stats:
                            score_data = segment_stats['avgScore']
                            if score_data.get('displayValue'):
                                try:
                                    stats.avg_score = float(score_data['displayValue'].replace(',', ''))
                                except:
                                    pass
                        
                        # Headshot Rate
                        if 'headshotRate' in segment_stats:
                            hs_data = segment_stats['headshotRate']
                            if hs_data.get('displayValue'):
                                try:
                                    hs_str = hs_data['displayValue'].replace('%', '')
                                    stats.headshot_rate = float(hs_str) / 100.0
                                except:
                                    pass
                        
                        # Matches Played
                        if 'matchesPlayed' in segment_stats:
                            matches_data = segment_stats['matchesPlayed']
                            if matches_data.get('displayValue'):
                                try:
                                    stats.matches_played = int(matches_data['displayValue'].replace(',', ''))
                                except:
                                    pass
                
                # Set last updated time
                stats.last_updated = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Cache the results
                stats_dict = {
                    'name': stats.name,
                    'rank': stats.rank,
                    'rr': stats.rr,
                    'peak_rank': stats.peak_rank,
                    'kd_ratio': stats.kd_ratio,
                    'win_rate': stats.win_rate,
                    'avg_score': stats.avg_score,
                    'headshot_rate': stats.headshot_rate,
                    'matches_played': stats.matches_played,
                    'last_updated': stats.last_updated
                }
                self.cache_manager.cache_data(cache_key, stats_dict)
                
                print(f"✅ Retrieved stats for {player_name}#{tag}: {stats.rank}, K/D: {stats.kd_ratio:.2f}, WR: {stats.win_rate:.1%}")
                return stats
            
            return None
            
        except Exception as e:
            print(f"Error fetching stats for {player_name}#{tag}: {e}")
            return None
    
    def test_api_connection(self) -> bool:
        """Test if the API key is valid and working"""
        try:
            # Test with a known profile using standard endpoint
            test_data = self._make_request("profile/riot/TenZ%23001")
            if test_data and 'data' in test_data:
                print("✅ Tracker.gg API connection successful!")
                return True
            else:
                print("❌ Tracker.gg API test failed - check API key")
                return False
        except Exception as e:
            print(f"❌ API connection test error: {e}")
            return False

# Initialize global API client (will be configured with key)
tracker_api = None

def init_tracker_api(api_key: str) -> TrackerGGAPI:
    """Initialize the global Tracker.gg API client"""
    global tracker_api
    tracker_api = TrackerGGAPI(api_key)
    return tracker_api

def get_tracker_api() -> Optional[TrackerGGAPI]:
    """Get the global API client instance"""
    return tracker_api