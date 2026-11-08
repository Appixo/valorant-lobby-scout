"""
ValorantAPI client for fetching player statistics
Supports both Henrik's unofficial API and direct local Valorant client API
Uses rank-yoinker's approach for faster, rate-limit-free stats fetching
"""

import time
from concurrent.futures import ThreadPoolExecutor
import requests
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import valo_api
from cache_manager import CacheManager
from game_data import normalize_tier, latest_season_id

@dataclass
class ValorantPlayerStats:
    """Player statistics from ValorantAPI"""
    name: str = ""
    player_level: int = 0
    rank: str = "Unranked"
    rr: int = 0
    peak_rank: str = "Unranked"
    kd_ratio: float = 0.0
    win_rate: float = 0.0
    avg_score: float = 0.0
    headshot_rate: float = 0.0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    last_updated: str = ""

RECENT_MATCH_COUNT = 5  # Competitive matches used for K/D and HS%


def riot_get(valclient, endpoint: str, endpoint_type: str = "pd") -> Tuple[int, Optional[Any]]:
    """GET a Riot pd/glz/shared endpoint with the client's auth; returns (status code, JSON or None)"""
    base = {
        "pd": valclient.base_url,
        "glz": valclient.base_url_glz,
        "shared": valclient.base_url_shared,
    }[endpoint_type]
    for attempt in range(3):
        response = requests.get(f"{base}{endpoint}", headers=valclient.headers, timeout=10)
        if response.status_code != 429:
            break
        # Rate limited: wait as long as Riot asks (or back off) and try again
        wait = float(response.headers.get("Retry-After") or 2 ** (attempt + 1))
        print(f"[WARN] Rate limited, retrying in {wait:.0f}s")
        time.sleep(min(wait, 10))
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, None


class ValorantAPIClient:
    """
    Client for both Henrik's ValorantAPI and direct local Valorant client API
    Uses rank-yoinker's approach for faster stats fetching
    """
    
    def __init__(self, api_key: Optional[str] = None, valclient=None):
        self.api_key = api_key
        if api_key:
            valo_api.set_api_key(api_key)
        
        # Store valclient for direct PD API access
        self.valclient = valclient
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1.5  # 1.5 seconds between requests
        
        # Caching (rank-yoinker style)
        self.cache_manager = CacheManager()
        self.cache_duration = 3600  # 1 hour cache for Henrik's API
        self.mmr_cache = {}  # In-memory cache for MMR data (faster)
        self.match_cache = {}  # In-memory cache for per-player recent match stats
        self.match_details_cache = {}  # Match ID -> match details (never invalidated)
        
        # Rate limit handling with exponential backoff
        self.rate_limit_backoff = 5  # Start with 5 seconds
        
    def _rate_limit(self):
        """Apply rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        self.last_request_time = time.time()
    
    def invalidate_mmr_cache(self):
        """Invalidate cached MMR data (call when returning to menu)"""
        self.mmr_cache = {}
        self.match_cache = {}
        print("[CACHE] MMR and match caches invalidated")
    
    def get_mmr_data_direct(self, puuid: str, season_id: str) -> Optional[Dict[str, Any]]:
        """
        Get MMR data directly from local Valorant client API (rank-yoinker style)
        This is MUCH faster and has higher rate limits than Henrik's API
        
        Args:
            puuid: Player PUUID
            season_id: Current season ID
            
        Returns:
            Dict with rank, rr, leaderboard, peak_rank, win_rate, etc.
        """
        if not self.valclient:
            print("[WARN] No valclient available for direct PD API access")
            return None
        
        try:
            # Check cache first (rank-yoinker style)
            if puuid in self.mmr_cache:
                print(f"[CACHE HIT] Using cached MMR data for {puuid[:8]}")
                return self.mmr_cache[puuid]
            
            # Fetch from PD API: /mmr/v1/players/{puuid}
            print(f"[PD API] Fetching MMR data for {puuid[:8]}...")
            status, data = riot_get(self.valclient, f"/mmr/v1/players/{puuid}")

            if status != 200 or not data:
                print(f"[WARN] MMR fetch failed: HTTP {status}")
                return None
            
            # Parse MMR data (same logic as rank-yoinker)
            result = {
                "rank": 0,
                "rr": 0,
                "leaderboard": 0,
                "peak_rank": 0,
                "win_rate": 0,
                "matches_played": 0,
                "peak_rank_act": None,
                "peak_rank_episode": None,
            }
            
            try:
                seasonal_info = data["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]
                current_season = seasonal_info.get(season_id)
                # Fallback: if season_id is None or missing, use the latest season available
                if not current_season:
                    try:
                        latest_season = latest_season_id(seasonal_info.keys())
                        current_season = seasonal_info.get(latest_season, {})
                        print(f"[WARN] Season ID missing; using latest season {latest_season}")
                    except Exception:
                        current_season = {}
                
                # Current rank and RR
                rank_tier = current_season.get("CompetitiveTier", 0)
                result["rank"] = int(rank_tier)
                result["rr"] = current_season.get("RankedRating", 0)
                result["leaderboard"] = current_season.get("LeaderboardRank", 0)
                
                # Win rate calculation
                wins = current_season.get("NumberOfWinsWithPlacements", 0)
                total_games = current_season.get("NumberOfGames", 0)
                result["matches_played"] = total_games
                
                if total_games > 0:
                    result["win_rate"] = int((wins / total_games) * 100)
                else:
                    result["win_rate"] = 0
                
                # Peak rank across all seasons
                max_rank = result["rank"]
                for season in seasonal_info:
                    wins_by_tier = seasonal_info[season].get("WinsByTier")
                    if wins_by_tier:
                        for tier in wins_by_tier:
                            tier_int = normalize_tier(int(tier), season)
                            if tier_int > max_rank:
                                max_rank = tier_int
                
                result["peak_rank"] = max_rank
                
                print(f"[OK] MMR data: Rank={result['rank']}, RR={result['rr']}, Peak={result['peak_rank']}, WR={result['win_rate']}%")
                
            except (KeyError, TypeError) as e:
                print(f"[WARN] Error parsing MMR data: {e}")
                return None
            
            # Cache the result
            self.mmr_cache[puuid] = result
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch MMR data: {e}")
            return None
    
    def get_player_match_stats_direct(self, puuid: str, match_count: int = RECENT_MATCH_COUNT) -> Optional[Dict[str, Any]]:
        """
        Get K/D and HS% over the player's last few competitive matches
        
        Args:
            puuid: Player PUUID
            match_count: How many recent competitive matches to include
            
        Returns:
            Dict with kd, headshot_rate, rr_change and matches (number of matches counted)
        """
        if not self.valclient:
            return None
        
        try:
            if puuid in self.match_cache:
                print(f"[CACHE HIT] Using cached match stats for {puuid[:8]}")
                return self.match_cache[puuid]
            
            print(f"[PD API] Fetching match history for {puuid[:8]}...")
            status, updates = riot_get(
                self.valclient,
                f"/mmr/v1/players/{puuid}/competitiveupdates?startIndex=0&endIndex={match_count}&queue=competitive"
            )
            if status != 200 or not updates:
                return None
            
            matches = updates.get("Matches", [])
            rr_change = matches[0].get("RankedRatingEarned", 0) if matches else 0

            # Download the match details in parallel; each takes about half a second
            match_ids = [m.get("MatchID") for m in matches]
            with ThreadPoolExecutor(max_workers=3) as pool:
                details = list(pool.map(self._get_match_details, match_ids))

            total_kills = total_deaths = total_headshots = total_hits = 0
            counted = 0
            party_partners = set()  # Players who were in this player's party in these matches

            for match_data in details:
                if match_data is None:
                    break  # Rate limited or unavailable; use what we have
                
                player = next((p for p in match_data.get("players", []) if p.get("subject") == puuid), None)
                if not player or not player.get("stats"):
                    continue

                if player.get("partyId"):
                    party_partners.update(p["subject"].lower() for p in match_data.get("players", [])
                                          if p.get("partyId") == player["partyId"] and p.get("subject") != puuid)
                
                total_kills += player["stats"].get("kills", 0)
                total_deaths += player["stats"].get("deaths", 0)
                for round_result in match_data.get("roundResults") or []:
                    for player_stat in round_result.get("playerStats", []):
                        if player_stat.get("subject") == puuid:
                            for damage in player_stat.get("damage", []):
                                headshots = damage.get("headshots", 0)
                                total_headshots += headshots
                                total_hits += headshots + damage.get("bodyshots", 0) + damage.get("legshots", 0)
                counted += 1
            
            kd = round(total_kills / total_deaths, 2) if total_deaths > 0 else float(total_kills)
            headshot_rate = int((total_headshots / total_hits) * 100) if total_hits > 0 else 0
            
            result = {
                "kd": kd,
                "headshot_rate": headshot_rate,
                "rr_change": rr_change,
                "matches": counted,
                "party_partners": sorted(party_partners)
            }
            
            self.match_cache[puuid] = result
            print(f"[OK] Match stats over {counted} matches: K/D={kd}, HS={headshot_rate}%")
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch match stats: {e}")
            return None
    
    def _get_match_details(self, match_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Fetch full match details; finished matches never change, so they're cached for the session"""
        if not match_id:
            return None
        if match_id in self.match_details_cache:
            return self.match_details_cache[match_id]
        
        print(f"[PD API] Fetching match details for {match_id[:8]}...")
        status, data = riot_get(self.valclient, f"/match-details/v1/matches/{match_id}")
        if status == 429:
            print("[WARN] Rate limited while fetching match details")
            return None
        if status != 200 or not data:
            return None
        
        self.match_details_cache[match_id] = data
        return data
    
    def get_player_stats_fast(self, puuid: str, season_id: str, name: str = None, tag: str = None,
                              include_match_stats: bool = True) -> Optional[ValorantPlayerStats]:
        """
        Fast stats fetching using direct PD API (rank-yoinker approach)
        Falls back to Henrik's API if valclient is not available
        
        Args:
            puuid: Player PUUID
            season_id: Current season ID
            name: Player name (optional, for Henrik's API fallback)
            tag: Player tag (optional, for Henrik's API fallback)
            
        Returns:
            ValorantPlayerStats object or None
        """
        try:
            # Try direct PD API first (FAST!)
            mmr_data = self.get_mmr_data_direct(puuid, season_id)
            match_stats = self.get_player_match_stats_direct(puuid) if include_match_stats else None
            
            if mmr_data:
                # Map rank numbers to names
                rank_names = {
                    0: "Unranked", 1: "Unranked", 2: "Unranked",
                    3: "Iron 1", 4: "Iron 2", 5: "Iron 3",
                    6: "Bronze 1", 7: "Bronze 2", 8: "Bronze 3",
                    9: "Silver 1", 10: "Silver 2", 11: "Silver 3",
                    12: "Gold 1", 13: "Gold 2", 14: "Gold 3",
                    15: "Platinum 1", 16: "Platinum 2", 17: "Platinum 3",
                    18: "Diamond 1", 19: "Diamond 2", 20: "Diamond 3",
                    21: "Ascendant 1", 22: "Ascendant 2", 23: "Ascendant 3",
                    24: "Immortal 1", 25: "Immortal 2", 26: "Immortal 3",
                    27: "Radiant"
                }
                
                stats = ValorantPlayerStats(
                    name=f"{name}#{tag}" if name and tag else "Unknown",
                    rank=rank_names.get(mmr_data["rank"], "Unranked"),
                    rr=mmr_data["rr"],
                    peak_rank=rank_names.get(mmr_data["peak_rank"], "Unranked"),
                    win_rate=mmr_data["win_rate"] / 100.0,  # Convert to decimal
                    matches_played=mmr_data["matches_played"],
                    wins=int((mmr_data["win_rate"] / 100.0) * mmr_data["matches_played"]),
                    losses=mmr_data["matches_played"] - int((mmr_data["win_rate"] / 100.0) * mmr_data["matches_played"]),
                    last_updated=time.strftime('%Y-%m-%d %H:%M:%S')
                )
                
                # Add match stats if available
                if match_stats:
                    stats.kd_ratio = match_stats["kd"]
                    stats.headshot_rate = match_stats["headshot_rate"] / 100.0  # Convert to decimal
                    stats.recent_matches = match_stats.get("matches", 0)
                
                print(f"[OK] Fast stats loaded via PD API: {stats.rank} ({stats.rr} RR), K/D: {stats.kd_ratio:.2f}")
                return stats
            
            # Fallback to Henrik's API if PD API fails
            if name and tag:
                print("[FALLBACK] Using Henrik's API...")
                return self.get_player_stats(name, tag)
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Fast stats fetch failed: {e}")
            return None
    
    def get_player_stats(self, player_name: str, tag: str) -> Optional[ValorantPlayerStats]:
        """
        Get comprehensive player statistics using ValorantAPI
        
        Args:
            player_name: Player's display name
            tag: Player's tag (without #)
            
        Returns:
            ValorantPlayerStats object or None if not found
        """
        try:
            # Check cache first
            cache_key = f"valorant_api_{player_name}_{tag}"
            cached_stats = self.cache_manager.get_cached_data(cache_key, self.cache_duration)
            if cached_stats:
                return ValorantPlayerStats(**cached_stats)
            
            # Apply rate limiting
            self._rate_limit()
            
            full_name = f"{player_name}#{tag}"
            stats = ValorantPlayerStats(name=full_name)
            
            print(f"[VALORANT API] Fetching stats for {full_name}...")
            
            # Get player level from account endpoint (direct HTTP request)
            try:
                print(f"[VALORANT API] Fetching account level for {full_name}...")
                account_url = f"https://api.henrikdev.xyz/valorant/v1/account/{player_name}/{tag}"
                headers = {}
                if self.api_key:
                    headers['Authorization'] = self.api_key
                
                account_response = requests.get(account_url, headers=headers, timeout=10)
                if account_response.status_code == 200:
                    account_data = account_response.json()
                    if 'data' in account_data:
                        stats.player_level = account_data['data'].get('account_level', 0)
                        print(f"[OK] Player level: {stats.player_level}")
                else:
                    print(f"[WARN] Could not fetch account level: HTTP {account_response.status_code}")
            except Exception as e:
                print(f"[WARN] Error fetching account level: {e}")
            
            # Get MMR data (rank information) - using direct HTTP
            try:
                print(f"[VALORANT API] Attempting to fetch MMR data for {full_name}...")
                # Use direct HTTP request with region (try EU first, fallback to other regions)
                mmr_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/eu/{player_name}/{tag}"
                headers = {}
                if self.api_key:
                    headers['Authorization'] = self.api_key
                
                mmr_response = requests.get(mmr_url, headers=headers, timeout=10)
                print(f"[INFO] MMR Response: HTTP {mmr_response.status_code}")
                
                if mmr_response.status_code == 200:
                    mmr_data = mmr_response.json()
                    if 'data' in mmr_data:
                        current_data = mmr_data['data'].get('current_data', {})
                        if current_data:
                            print(f"[OK] Found current MMR data")
                            stats.rank = current_data.get('currenttierpatched', 'Unranked')
                            stats.rr = current_data.get('ranking_in_tier', 0)
                            elo = current_data.get('elo', 0)
                            print(f"[INFO] Rank: {stats.rank}, RR: {stats.rr}, ELO: {elo}")
                        
                        # Get highest rank from this season
                        highest_rank = mmr_data['data'].get('highest_rank', {})
                        if highest_rank:
                            stats.peak_rank = highest_rank.get('patched_tier', stats.rank)
                            print(f"[INFO] Peak Rank: {stats.peak_rank}")
                    else:
                        print("[WARN] No MMR data in response")
                else:
                    print(f"[WARN] MMR request failed: HTTP {mmr_response.status_code}")
            except Exception as e:
                print(f"[WARN] Failed to get MMR data: {e}")
            
            # Get match history for win rate and K/D calculation - using direct HTTP
            try:
                print(f"[VALORANT API] Attempting to fetch match history for {full_name}...")
                match_url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{player_name}/{tag}"
                headers = {}
                if self.api_key:
                    headers['Authorization'] = self.api_key
                
                match_response = requests.get(match_url, headers=headers, timeout=10)
                print(f"[INFO] Match History Response: HTTP {match_response.status_code}")
                
                if match_response.status_code == 200:
                    match_data = match_response.json()
                    if 'data' in match_data:
                        matches = match_data['data'][:20]  # Last 20 matches
                        print(f"[INFO] Found {len(matches)} matches")
                        
                        if matches:
                            wins = 0
                            total_kills = 0
                            total_deaths = 0
                            total_headshots = 0
                            
                            for i, match in enumerate(matches):
                                # Find player data in match - players is a direct list
                                all_players = match.get('players', [])
                                if isinstance(all_players, dict):
                                    # Sometimes players might be a dict with 'all_players' key
                                    all_players = all_players.get('all_players', [])
                                
                                for player in all_players:
                                    if (player.get('name', '').lower() == player_name.lower() and
                                        player.get('tag', '').lower() == tag.lower()):
                                        
                                        # Get stats
                                        player_stats = player.get('stats', {})
                                        total_kills += player_stats.get('kills', 0)
                                        total_deaths += player_stats.get('deaths', 0)
                                        total_headshots += player_stats.get('headshots', 0)
                                        
                                        # Check if won
                                        player_team = player.get('team', '').lower()
                                        teams = match.get('teams', {})
                                        if player_team == 'red' and teams.get('red', {}).get('has_won', False):
                                            wins += 1
                                        elif player_team == 'blue' and teams.get('blue', {}).get('has_won', False):
                                            wins += 1
                                        break
                            
                            # Calculate statistics
                            stats.matches_played = len(matches)
                            stats.wins = wins
                            stats.losses = stats.matches_played - wins
                            stats.win_rate = wins / stats.matches_played if stats.matches_played > 0 else 0.0
                            stats.kd_ratio = total_kills / total_deaths if total_deaths > 0 else 0.0
                            stats.headshot_rate = total_headshots / total_kills if total_kills > 0 else 0.0
                            
                            print(f"[OK] Calculated stats: {stats.matches_played} matches, {stats.win_rate:.1%} WR, {stats.kd_ratio:.2f} K/D")
                    else:
                        print("[WARN] No match data in response")
                else:
                    print(f"[WARN] Match history request failed: HTTP {match_response.status_code}")
                        
            except Exception as e:
                print(f"[WARN] Failed to get match history: {e}")
            
            # Set last updated time
            stats.last_updated = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Cache the results
            stats_dict = {
                'name': stats.name,
                'player_level': stats.player_level,
                'rank': stats.rank,
                'rr': stats.rr,
                'peak_rank': stats.peak_rank,
                'kd_ratio': stats.kd_ratio,
                'win_rate': stats.win_rate,
                'avg_score': stats.avg_score,
                'headshot_rate': stats.headshot_rate,
                'matches_played': stats.matches_played,
                'wins': stats.wins,
                'losses': stats.losses,
                'last_updated': stats.last_updated
            }
            self.cache_manager.cache_data(cache_key, stats_dict)
            
            # Return stats even if only level is available
            if stats.player_level > 0 or stats.rank != "Unranked" or stats.matches_played > 0:
                print(f"[OK] Retrieved ValorantAPI stats for {full_name}: Level {stats.player_level}, {stats.rank}, K/D: {stats.kd_ratio:.2f}, WR: {stats.win_rate:.1%}")
                return stats
            else:
                print(f"[INFO] No data found for {full_name} via ValorantAPI")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error fetching ValorantAPI stats for {player_name}#{tag}: {e}")
            return None
    
    def test_api_connection(self) -> bool:
        """Test if the ValorantAPI is accessible"""
        try:
            # Test with a simple API call
            self._rate_limit()
            test_result = valo_api.get_version_info()
            if test_result:
                print("[OK] ValorantAPI connection successful!")
                return True
            else:
                print("[ERROR] ValorantAPI connection failed")
                return False
        except Exception as e:
            print(f"[ERROR] ValorantAPI connection test error: {e}")
            return False

# Global client instance
valorant_api_client = None

def init_valorant_api(api_key: Optional[str] = None, valclient=None) -> ValorantAPIClient:
    """
    Initialize the global ValorantAPI client
    
    Args:
        api_key: Henrik's API key (optional)
        valclient: Local Valorant client instance for direct PD API access (recommended for speed)
    """
    global valorant_api_client
    valorant_api_client = ValorantAPIClient(api_key, valclient)
    print(f"[INIT] ValorantAPI client initialized (Direct PD API: {'✓' if valclient else '✗'})")
    return valorant_api_client

def get_valorant_api() -> Optional[ValorantAPIClient]:
    """Get the global ValorantAPI client"""
    return valorant_api_client

_season_cache = {"id": None, "time": 0}


def get_current_season_id(valclient) -> Optional[str]:
    """
    Get the current competitive act ID from the Valorant client (cached for 10 minutes)
    
    Args:
        valclient: Valorant client instance
        
    Returns:
        Current season ID string or None
    """
    if _season_cache["id"] and time.time() - _season_cache["time"] < 600:
        return _season_cache["id"]
    try:
        status, seasons_data = riot_get(valclient, "/content-service/v3/content", "shared")
        if status == 200 and seasons_data:
            for season in seasons_data.get("Seasons", []):
                # Only acts carry competitive ranks; episodes are active at the same time
                if season.get("IsActive") and season.get("Type") in (None, "act"):
                    _season_cache.update(id=season.get("ID"), time=time.time())
                    print(f"[INFO] Current season ID: {_season_cache['id']}")
                    return _season_cache["id"]
        print(f"[WARN] Could not determine current season (HTTP {status})")
    except Exception as e:
        print(f"[ERROR] Failed to get season ID: {e}")
    return None
