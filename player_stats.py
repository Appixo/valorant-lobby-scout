import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict

@dataclass
class PlayerStats:
    """Data class for player statistics"""
    name: str
    puuid: str
    current_rank: str = "Unranked"
    peak_rank: str = "Unranked"
    current_rr: int = 0
    peak_rr: int = 0
    win_rate: float = 0.0
    kd_ratio: float = 0.0
    headshot_percentage: float = 0.0
    average_score: float = 0.0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    last_updated: str = ""
    account_age_days: int = 0
    is_smurf_risk: bool = False
    smurf_indicators: List[str] = None
    rank_history: List[Dict] = None
    recent_performance: List[Dict] = None
    
    def __post_init__(self):
        if self.smurf_indicators is None:
            self.smurf_indicators = []
        if self.rank_history is None:
            self.rank_history = []
        if self.recent_performance is None:
            self.recent_performance = []

class PlayerStatisticsManager:
    """Manages player statistics and smurf detection"""
    
    def __init__(self, stats_file='player_stats.json', cache_duration_hours=24):
        self.stats_file = stats_file
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.player_stats = self.load_stats()
        self.lock = threading.Lock()
        
        # Smurf detection thresholds
        self.smurf_thresholds = {
            'win_rate_threshold': 0.65,  # 65% win rate
            'kd_ratio_threshold': 1.5,   # 1.5 K/D ratio
            'rank_disparity_threshold': 3,  # 3 rank tiers difference
            'account_age_threshold': 30,  # 30 days
            'recent_performance_threshold': 0.7  # 70% recent win rate
        }
    
    def load_stats(self) -> Dict[str, PlayerStats]:
        """Load player statistics from file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    return {name: PlayerStats(**stats) for name, stats in data.items()}
        except Exception as e:
            print(f"Error loading player stats: {e}")
        return {}
    
    def save_stats(self):
        """Save player statistics to file"""
        try:
            with self.lock:
                data = {name: asdict(stats) for name, stats in self.player_stats.items()}
                with open(self.stats_file, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving player stats: {e}")
    
    def get_player_stats(self, player_name: str, puuid: str, client=None) -> PlayerStats:
        """Get or fetch player statistics"""
        # Check if we have cached stats
        if player_name in self.player_stats:
            stats = self.player_stats[player_name]
            last_updated = datetime.fromisoformat(stats.last_updated)
            
            # Check if cache is still valid
            if datetime.now() - last_updated < self.cache_duration:
                return stats
        
        # Fetch new stats
        if client:
            stats = self.fetch_player_stats(player_name, puuid, client)
            if stats:
                self.player_stats[player_name] = stats
                self.save_stats()
                return stats
        
        # Return default stats if fetch failed
        return PlayerStats(name=player_name, puuid=puuid)
    
    def fetch_player_stats(self, player_name: str, puuid: str, client) -> Optional[PlayerStats]:
        """Fetch player statistics from Valorant API and Tracker.gg"""
        try:
            stats = PlayerStats(name=player_name, puuid=puuid)
            
            # Fetch from Valorant API
            self.fetch_valorant_stats(stats, client)
            
            # Fetch from Tracker.gg (if available)
            self.fetch_tracker_stats(stats, player_name)
            
            # Analyze for smurf indicators
            self.analyze_smurf_indicators(stats)
            
            stats.last_updated = datetime.now().isoformat()
            return stats
            
        except Exception as e:
            print(f"Error fetching stats for {player_name}: {e}")
            return None
    
    def fetch_valorant_stats(self, stats: PlayerStats, client):
        """Fetch statistics from Valorant API"""
        try:
            # Fetch MMR data
            mmr_data = client.fetch_mmr(stats.puuid)
            if mmr_data:
                stats.current_rank = self.get_rank_name(mmr_data.get('currenttier', 0))
                stats.current_rr = mmr_data.get('rankedrating', 0)
                
                # Get peak rank from seasonal data
                if 'QueueSkills' in mmr_data and 'competitive' in mmr_data['QueueSkills']:
                    seasonal_info = mmr_data['QueueSkills']['competitive'].get('SeasonalInfoBySeasonID', {})
                    if seasonal_info:
                        latest_season = max(seasonal_info.keys()) if seasonal_info else None
                        if latest_season:
                            season_data = seasonal_info[latest_season]
                            stats.peak_rank = self.get_rank_name(season_data.get('PeakTier', 0))
                            stats.peak_rr = season_data.get('PeakRankedRating', 0)
                            
                            # Store rank history
                            for season_id, season_info in seasonal_info.items():
                                stats.rank_history.append({
                                    'season': season_id,
                                    'rank': self.get_rank_name(season_info.get('PeakTier', 0)),
                                    'rr': season_info.get('PeakRankedRating', 0)
                                })
            
            # Fetch match history for win rate calculation
            self.fetch_match_history(stats, client)
            
        except Exception as e:
            print(f"Error fetching Valorant stats: {e}")
    
    def fetch_match_history(self, stats: PlayerStats, client):
        """Fetch match history to calculate win rate and performance"""
        try:
            # Try to fetch match history - this may fail due to API limitations
            match_history = client.fetch_match_history(stats.puuid)
            
            if not match_history:
                return
            
            # Handle different response formats
            matches = []
            if isinstance(match_history, dict):
                # Check common keys for match data
                for key in ['History', 'matches', 'data']:
                    if key in match_history:
                        potential_matches = match_history[key]
                        if isinstance(potential_matches, list):
                            matches = potential_matches
                            break
            elif isinstance(match_history, list):
                matches = match_history
            
            if not matches:
                print(f"No matches found in history for {stats.name}")
                return
            
            # Limit to most recent 20 matches for better performance
            if len(matches) > 20:
                matches = matches[:20]
                wins = 0
                total_kills = 0
                total_deaths = 0
                total_score = 0
                recent_wins = 0
                recent_matches = 0
                
                for i, match in enumerate(matches):
                    # Check if player won
                    player_team = None
                    for player in match.get('players', []):
                        if player.get('puuid') == stats.puuid:
                            player_team = player.get('teamId')
                            break
                    
                    if player_team:
                        # Determine if team won
                        for team in match.get('teams', []):
                            if team.get('teamId') == player_team:
                                if team.get('won'):
                                    wins += 1
                                    if i < 10:  # Recent matches
                                        recent_wins += 1
                                break
                    
                    # Get player performance
                    for player in match.get('players', []):
                        if player.get('puuid') == stats.puuid:
                            stats_data = player.get('stats', {})
                            total_kills += stats_data.get('kills', 0)
                            total_deaths += stats_data.get('deaths', 0)
                            total_score += stats_data.get('score', 0)
                            break
                    
                    if i < 10:
                        recent_matches += 1
                
                # Calculate statistics
                stats.matches_played = len(matches)
                stats.wins = wins
                stats.losses = stats.matches_played - wins
                stats.win_rate = wins / stats.matches_played if stats.matches_played > 0 else 0.0
                
                if total_deaths > 0:
                    stats.kd_ratio = total_kills / total_deaths
                
                stats.average_score = total_score / stats.matches_played if stats.matches_played > 0 else 0.0
                
                # Recent performance (last 10 matches)
                if recent_matches > 0:
                    stats.recent_performance.append({
                        'recent_win_rate': recent_wins / recent_matches,
                        'recent_matches': recent_matches
                    })
        
        except Exception as e:
            print(f"Error fetching match history for {stats.name}: {e}")
            # Set default values when match history fails
            stats.matches_played = 0
            stats.wins = 0
            stats.losses = 0
            stats.win_rate = 0.0
            stats.kd_ratio = 0.0
    
    def fetch_tracker_stats(self, stats: PlayerStats, player_name: str):
        """Fetch additional statistics from Tracker.gg"""
        try:
            # Note: Tracker.gg doesn't have a public API, so this would require web scraping
            # For now, we'll implement a basic structure for future enhancement
            
            # This could be enhanced with web scraping or if Tracker.gg provides an API
            pass
            
        except Exception as e:
            print(f"Error fetching Tracker.gg stats: {e}")
    
    def analyze_smurf_indicators(self, stats: PlayerStats):
        """Analyze player for smurf indicators"""
        indicators = []
        
        # High win rate with low account age
        if stats.win_rate > self.smurf_thresholds['win_rate_threshold']:
            indicators.append(f"High win rate ({stats.win_rate:.1%})")
        
        # High K/D ratio
        if stats.kd_ratio > self.smurf_thresholds['kd_ratio_threshold']:
            indicators.append(f"High K/D ratio ({stats.kd_ratio:.2f})")
        
        # Rank disparity (current vs peak)
        current_tier = self.rank_to_tier(stats.current_rank)
        peak_tier = self.rank_to_tier(stats.peak_rank)
        if abs(current_tier - peak_tier) >= self.smurf_thresholds['rank_disparity_threshold']:
            indicators.append(f"Rank disparity (Current: {stats.current_rank}, Peak: {stats.peak_rank})")
        
        # Recent performance spike
        if stats.recent_performance:
            recent_win_rate = stats.recent_performance[0].get('recent_win_rate', 0)
            if recent_win_rate > self.smurf_thresholds['recent_performance_threshold']:
                indicators.append(f"Recent performance spike ({recent_win_rate:.1%} win rate)")
        
        # Account age
        if stats.account_age_days < self.smurf_thresholds['account_age_threshold']:
            indicators.append(f"New account ({stats.account_age_days} days old)")
        
        stats.smurf_indicators = indicators
        stats.is_smurf_risk = len(indicators) >= 2  # At least 2 indicators
    
    def get_rank_name(self, tier: int) -> str:
        """Convert tier number to rank name"""
        ranks = {
            0: "Unranked", 3: "Iron 1", 4: "Iron 2", 5: "Iron 3",
            6: "Bronze 1", 7: "Bronze 2", 8: "Bronze 3",
            9: "Silver 1", 10: "Silver 2", 11: "Silver 3",
            12: "Gold 1", 13: "Gold 2", 14: "Gold 3",
            15: "Platinum 1", 16: "Platinum 2", 17: "Platinum 3",
            18: "Diamond 1", 19: "Diamond 2", 20: "Diamond 3",
            21: "Ascendant 1", 22: "Ascendant 2", 23: "Ascendant 3",
            24: "Immortal 1", 25: "Immortal 2", 26: "Immortal 3",
            27: "Radiant"
        }
        return ranks.get(tier, "Unknown")
    
    def rank_to_tier(self, rank_name: str) -> int:
        """Convert rank name to tier number"""
        rank_tiers = {
            "Unranked": 0, "Iron 1": 3, "Iron 2": 4, "Iron 3": 5,
            "Bronze 1": 6, "Bronze 2": 7, "Bronze 3": 8,
            "Silver 1": 9, "Silver 2": 10, "Silver 3": 11,
            "Gold 1": 12, "Gold 2": 13, "Gold 3": 14,
            "Platinum 1": 15, "Platinum 2": 16, "Platinum 3": 17,
            "Diamond 1": 18, "Diamond 2": 19, "Diamond 3": 20,
            "Ascendant 1": 21, "Ascendant 2": 22, "Ascendant 3": 23,
            "Immortal 1": 24, "Immortal 2": 25, "Immortal 3": 26,
            "Radiant": 27
        }
        return rank_tiers.get(rank_name, 0)
    
    def get_smurf_risk_level(self, stats: PlayerStats) -> str:
        """Get smurf risk level description"""
        if not stats.is_smurf_risk:
            return "Low"
        
        indicator_count = len(stats.smurf_indicators)
        if indicator_count >= 4:
            return "Very High"
        elif indicator_count >= 3:
            return "High"
        else:
            return "Medium"
    
    def get_player_summary(self, stats: PlayerStats) -> Dict[str, Any]:
        """Get a summary of player statistics"""
        return {
            'name': stats.name,
            'current_rank': stats.current_rank,
            'peak_rank': stats.peak_rank,
            'win_rate': f"{stats.win_rate:.1%}",
            'kd_ratio': f"{stats.kd_ratio:.2f}",
            'matches_played': stats.matches_played,
            'smurf_risk': self.get_smurf_risk_level(stats),
            'smurf_indicators': stats.smurf_indicators,
            'last_updated': stats.last_updated
        }
    
    def get_team_analysis(self, players: List[PlayerStats]) -> Dict[str, Any]:
        """Analyze a team of players for overall risk assessment"""
        if not players:
            return {}
        
        total_players = len(players)
        smurf_players = [p for p in players if p.is_smurf_risk]
        high_risk_players = [p for p in players if self.get_smurf_risk_level(p) in ["High", "Very High"]]
        
        avg_win_rate = sum(p.win_rate for p in players) / total_players
        avg_kd_ratio = sum(p.kd_ratio for p in players) / total_players
        
        return {
            'total_players': total_players,
            'smurf_players': len(smurf_players),
            'high_risk_players': len(high_risk_players),
            'smurf_percentage': len(smurf_players) / total_players,
            'avg_win_rate': avg_win_rate,
            'avg_kd_ratio': avg_kd_ratio,
            'team_risk_level': self.calculate_team_risk_level(players),
            'recommendation': self.get_team_recommendation(players)
        }
    
    def calculate_team_risk_level(self, players: List[PlayerStats]) -> str:
        """Calculate overall team risk level"""
        high_risk_count = len([p for p in players if self.get_smurf_risk_level(p) in ["High", "Very High"]])
        total_players = len(players)
        
        if high_risk_count >= total_players * 0.4:  # 40% or more high risk
            return "Very High"
        elif high_risk_count >= total_players * 0.2:  # 20% or more high risk
            return "High"
        elif high_risk_count > 0:
            return "Medium"
        else:
            return "Low"
    
    def get_team_recommendation(self, players: List[PlayerStats]) -> str:
        """Get recommendation based on team analysis"""
        risk_level = self.calculate_team_risk_level(players)
        
        if risk_level == "Very High":
            return "Consider dodging - High chance of smurfs or unfair match"
        elif risk_level == "High":
            return "Be cautious - Multiple suspicious players detected"
        elif risk_level == "Medium":
            return "Proceed with caution - Some suspicious players"
        else:
            return "Safe to proceed - No significant risks detected"
