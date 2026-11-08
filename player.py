import requests
import time
from streaming_services import StreamingChecker
from tracker_api import get_tracker_api, PlayerStats
from game_data import get_agent_name


class Player:
    def __init__(self, client, puuid, agentID, incognito, team, display_name=None, account_level=0, level_hidden=False):
        self.client = client
        self.puuid = puuid
        self.display_name_hint = display_name  # Store the hint from match data
        
        # Debug agent ID and improve detection
        if agentID and agentID != "Unknown":
            # Normalize agent ID (remove any extra characters)
            normalized_agent_id = agentID.lower().strip()
            self.agent = get_agent_name(normalized_agent_id, f"Unknown({normalized_agent_id[:8]})")
            # Debug unknown agents
            if self.agent.startswith("Unknown"):
                print(f"Unknown agent ID: {agentID}")
        else:
            self.agent = "Unknown"
            
        self.incognito = incognito
        self.privacy_hidden = False  # Initialize privacy detection
        self.name_source = None      # 'match' or 'friend' when the name came from your own data
        self.team = self.side(team)
        
        # Get player name
        full_name = self.set_name(puuid)
        if '#' in full_name and full_name != "Unknown#0000":
            name_parts = full_name.split('#')
            self.name = self.filter_name(name_parts[0])
            self.tag = name_parts[1] if len(name_parts) > 1 else "0000"
        else:
            self.name = self.filter_name("Anonymous")
            self.tag = "0000"
        
        # Ensure we don't have empty names
        if not self.name or self.name.strip() == '':
            self.name = "Anonymous"
        if not self.tag or self.tag.strip() == '':
            self.tag = "0000"
            
        self.full_name = f"{self.name}#{self.tag}"
        
        # Enhanced hidden detection combining old and new methods
        self.is_hidden = self.incognito or self.privacy_hidden or self.name.startswith('Player_')
        
        self.possibleNames = self.find_possible_names()
        
        # Statistics attributes
        self.stats = None
        self.current_rank = "Unranked"
        self.peak_rank = "Unranked"
        self.kd_ratio = 0.0
        self.win_rate = 0.0
        self.avg_score = 0.0
        self.headshot_rate = 0.0
        self.matches_played = 0
        self.recent_matches = 0  # Matches behind kd_ratio / headshot_rate
        self.match_stats_loaded = False
        self.recent_party_partners = set()  # PUUIDs this player partied with in recent matches
        self.stats_loaded = False
        
        # Enhanced Riot API stats (account level comes straight from match data when available)
        self.player_level = account_level or 0
        self.level_hidden = level_hidden and not account_level  # Player chose to hide their account level
        self.current_rr = 0
        self.peak_rr = 0
        self.total_kills = 0
        self.total_headshots = 0
        self.account_created = None
        self.riot_stats_loaded = False

    def side(self, color):
        if color == "Blue":
            return "Defending"
        elif color == "Red":
            return "Attacking"
        else:
            # For pregame matches where team assignment is unknown
            return "Unknown"

    def set_name(self, puuid):
        # The name service is the only source that carries a real Riot ID for a
        # player the match data blanked. Since the October 2026 privacy changes it
        # returns an empty GameName for anyone with Incognito on, so a blank here
        # is expected rather than a failure to retry.
        try:
            playerData = self.client.put(
                endpoint="/name-service/v2/players",
                endpoint_type="pd",
                json_data=[puuid]
            )[0]
            game_name = (playerData.get('GameName') or '').strip()
            tag_line = (playerData.get('TagLine') or '').strip()

            if game_name:
                self.privacy_hidden = False
                return f"{game_name}#{tag_line or '0000'}"
        except Exception:
            pass

        # Name service returned empty or failed — use display_name hint as fallback
        hint = getattr(self, 'display_name_hint', None)
        if hint and hint.strip():
            hint = hint.strip()
            if '#' in hint:
                parts = hint.split('#', 1)
                if parts[0].strip():
                    self.privacy_hidden = False
                    return hint

        # Truly hidden — no name from any source
        self.privacy_hidden = True
        return f'Player_{puuid[:8]}#0000'

    def filter_name(self, name):
        if 'twitch' in name.lower():
            return name.lower().replace('twitch', '').strip()
        if 'ttv' in name.lower():
            return name.lower().replace('ttv', '').strip()
        return name

    def find_possible_names(self):
        self.name_u = self.name.replace(' ', '_')
        self.name = self.name.replace(' ', '')
        return list(set([
            self.name,
            self.name + self.tag,
            self.name_u,
            self.name_u + self.tag,
            self.tag + self.name,
            self.tag + self.name_u,
            f"{self.name}_{self.tag}",
            f"{self.tag}_{self.name}",
            f"{self.name_u}_{self.tag}",
            f"{self.tag}_{self.name_u}",
        ]))

    def is_live(self, delay):
        """Check if player is live on Twitch (legacy method for backward compatibility)"""
        for name in self.possibleNames:
            try:
                if delay > 0:
                    time.sleep(delay)
                response = requests.get(f'https://twitch.tv/{name}', timeout=5)
                if 'isLiveBroadcast' in response.text:
                    return name
            except requests.RequestException:
                continue
        return False
    
    def check_all_platforms(self, delay=1.0):
        """Check all streaming and social media platforms"""
        checker = StreamingChecker()
        return checker.check_all_platforms(self.possibleNames, delay)
    
    def get_enhanced_riot_stats(self, include_match_stats=True):
        """Automatically fetch player stats from APIs"""
        # Automatically fetch stats when player is detected
        if self.stats_loaded or self.riot_stats_loaded:
            return  # Already loaded
        
        # Skip for truly anonymous players (both name and tag are default)
        if self.name == "Anonymous" and self.tag == "0000":
            return
        
        # Riot no longer shares hidden names; stats still load by PUUID, name-based APIs are skipped

        # Fetch stats from available APIs
        try:
            success, message = self.get_tracker_stats_on_demand(include_match_stats)
            if success:
                self.riot_stats_loaded = True
                print(f"[OK] Auto-loaded stats for {self.full_name}")
        except Exception as e:
            print(f"[WARN] Could not auto-load stats for {self.full_name}: {e}")
    
    def get_tracker_stats_on_demand(self, include_match_stats=True):
        """Fetch stats from available APIs only when explicitly requested"""
        try:
            # Try ValorantAPI first (more reliable)
            success = self._try_valorant_api(include_match_stats)
            if success:
                return success
            
            # Fallback to Tracker.gg if ValorantAPI fails
            return self._try_tracker_gg_api()
            
        except Exception as e:
            error_msg = f"Error fetching stats: {e}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def _try_valorant_api(self, include_match_stats=True):
        """Try to get stats from ValorantAPI (using fast direct PD API)"""
        try:
            from valorant_api_client import get_valorant_api, get_current_season_id
            
            api_client = get_valorant_api()
            if not api_client:
                return False, "ValorantAPI not available"
            
            print(f"[VALORANT API] Fetching stats for {self.full_name}...")
            
            # Get current season ID
            season_id = None
            if self.client:
                season_id = get_current_season_id(self.client)
            
            # Try fast method first (direct PD API - rank-yoinker style); it copes with a missing season ID
            if self.client and getattr(self, 'puuid', None):
                print(f"[FAST] Trying direct PD API for {self.full_name}...")
                stats = api_client.get_player_stats_fast(
                    puuid=self.puuid,
                    season_id=season_id,
                    name=None if self.privacy_hidden else self.name,
                    tag=None if self.privacy_hidden else self.tag,
                    include_match_stats=include_match_stats
                )
            else:
                # Fallback to Henrik's API if no PUUID or season ID
                print(f"[FALLBACK] Using Henrik's API for {self.full_name}...")
                stats = api_client.get_player_stats(self.name, self.tag)
            
            if stats:
                # Update player attributes with ValorantAPI data
                self.player_level = stats.player_level if stats.player_level > 0 else self.player_level
                self.current_rank = stats.rank if stats.rank != "Unranked" else "Unranked"
                self.peak_rank = stats.peak_rank if stats.peak_rank != "Unranked" else "Unranked"
                self.current_rr = stats.rr
                self.kd_ratio = stats.kd_ratio
                self.win_rate = stats.win_rate
                self.avg_score = stats.avg_score
                self.headshot_rate = stats.headshot_rate
                self.matches_played = stats.matches_played
                self.recent_matches = getattr(stats, 'recent_matches', 0)
                self.match_stats_loaded = include_match_stats
                
                # Store the stats object
                self.stats = stats
                self.stats_loaded = True
                
                # Generate display string
                parts = []
                if self.current_rank != "Unranked":
                    rank_display = self.current_rank
                    if self.current_rr > 0:
                        rank_display += f" ({self.current_rr} RR)"
                    parts.append(rank_display)
                if self.peak_rank != "Unranked" and self.peak_rank != self.current_rank:
                    parts.append(f"Peak: {self.peak_rank}")
                if self.kd_ratio > 0:
                    parts.append(f"K/D: {self.kd_ratio:.2f}")
                if self.headshot_rate > 0:
                    parts.append(f"HS: {self.headshot_rate:.1%}")
                if self.win_rate > 0:
                    parts.append(f"WR: {self.win_rate:.1%}")
                
                display_str = " | ".join(parts) if parts else "Basic stats"
                print(f"[OK] ValorantAPI stats loaded for {self.full_name}: {display_str}")
                
                return True, display_str
            else:
                return False, "Player may have private profile or limited API coverage"
                
        except ImportError:
            return False, "ValorantAPI client not available"
        except Exception as e:
            if "Route not found" in str(e):
                return False, "Player not found in ValorantAPI database (may be private)"
            else:
                print(f"[WARN] ValorantAPI error: {e}")
                return False, f"ValorantAPI error: {e}"
    
    def _try_tracker_gg_api(self):
        """Try to get stats from Tracker.gg API (fallback)"""
        if self.privacy_hidden:
            return False, "Hidden name: no Riot ID to look up"
        try:
            from tracker_api import get_tracker_api
            
            api_client = get_tracker_api()
            if not api_client:
                return False, "Tracker.gg API not available"
            
            print(f"[TRACKER.GG] Fetching stats for {self.full_name}...")
            
            # Fetch stats from Tracker.gg API
            stats = api_client.get_player_stats(self.name, self.tag)
            
            if stats:
                # Update player attributes with Tracker.gg data
                self.current_rank = stats.rank if stats.rank != "Unranked" else "Unranked"
                self.peak_rank = stats.peak_rank if stats.peak_rank != "Unranked" else "Unranked"
                self.current_rr = stats.rr
                self.kd_ratio = stats.kd_ratio
                self.win_rate = stats.win_rate
                self.avg_score = stats.avg_score
                self.headshot_rate = stats.headshot_rate
                self.matches_played = stats.matches_played
                
                # Store the tracker stats object
                self.stats = stats
                self.stats_loaded = True
                
                # Generate display string
                parts = []
                if self.current_rank != "Unranked":
                    rank_display = self.current_rank
                    if self.current_rr > 0:
                        rank_display += f" ({self.current_rr} RR)"
                    parts.append(rank_display)
                if self.peak_rank != "Unranked" and self.peak_rank != self.current_rank:
                    parts.append(f"Peak: {self.peak_rank}")
                if self.kd_ratio > 0:
                    parts.append(f"K/D: {self.kd_ratio:.2f}")
                if self.headshot_rate > 0:
                    parts.append(f"HS: {self.headshot_rate:.1%}")
                if self.win_rate > 0:
                    parts.append(f"WR: {self.win_rate:.1%}")
                
                display_str = " | ".join(parts) if parts else "Basic stats"
                print(f"[OK] Tracker.gg stats loaded for {self.full_name}: {display_str}")
                
                return True, display_str
            else:
                return False, "No Tracker.gg data found"
                
        except ImportError:
            return False, "Tracker.gg API client not available"
        except Exception as e:
            print(f"[WARN] Tracker.gg error: {e}")
            return False, f"Tracker.gg error: {e}"
    

    

    

    
    def load_match_stats(self):
        """K/D and HS% over recent competitive matches (the slower part of the stats)"""
        from valorant_api_client import get_valorant_api
        api_client = get_valorant_api()
        match_stats = api_client.get_player_match_stats_direct(self.puuid) if api_client else None
        if match_stats:
            self.kd_ratio = match_stats["kd"]
            self.headshot_rate = match_stats["headshot_rate"] / 100.0
            self.recent_matches = match_stats.get("matches", 0)
            self.recent_party_partners = set(match_stats.get("party_partners", []))
            self.match_stats_loaded = True
        return bool(match_stats)

    def get_competitive_stats(self, include_match_stats=True):
        """Fetch competitive statistics - now integrated with enhanced stats"""
        if self.stats_loaded or self.riot_stats_loaded:
            return  # Already loaded via enhanced system
        
        # If enhanced stats haven't run yet, try the enhanced approach
        if not self.riot_stats_loaded:
            self.get_enhanced_riot_stats(include_match_stats)
            return
        
        # Legacy fallback for direct Tracker.gg API call
        try:
            from tracker_api import get_tracker_api
            
            api_client = get_tracker_api()
            if not api_client:
                print("Tracker.gg API not initialized")
                return
            
            # Fetch stats from API
            stats = api_client.get_player_stats(self.name, self.tag)
            
            if stats:
                self.stats = stats
                self.current_rank = stats.rank
                self.peak_rank = stats.peak_rank
                self.kd_ratio = stats.kd_ratio
                self.win_rate = stats.win_rate
                self.avg_score = stats.avg_score
                self.headshot_rate = stats.headshot_rate
                self.matches_played = stats.matches_played
                self.stats_loaded = True
                
                print(f"[OK] Loaded Tracker.gg stats for {self.full_name}: {self.current_rank}, K/D: {self.kd_ratio:.2f}")
            else:
                print(f"[INFO] No stats found for {self.full_name}")
                
        except Exception as e:
            print(f"Error fetching stats for {self.full_name}: {e}")
    
    def get_rank_name(self) -> str:
        """Get formatted rank name"""
        if self.current_rank and self.current_rank != "Unranked":
            return self.current_rank
        return "Unranked"
    
    def get_stats_summary(self) -> dict:
        """Get a comprehensive summary of player statistics"""
        return {
            'name': self.full_name,
            'player_level': self.player_level if self.player_level > 0 else "N/A",
            'rank': self.get_rank_name(),
            'current_rr': f"{self.current_rr} RR" if self.current_rr > 0 else "N/A",
            'peak_rank': self.peak_rank if self.peak_rank != "Unranked" else "N/A",
            'peak_rr': f"{self.peak_rr} RR" if self.peak_rr > 0 else "N/A",
            'kd_ratio': f"{self.kd_ratio:.2f}" if self.kd_ratio > 0 else "N/A",
            'win_rate': f"{self.win_rate:.1%}" if self.win_rate > 0 else "N/A",
            'avg_score': f"{self.avg_score:.0f}" if self.avg_score > 0 else "N/A",
            'headshot_rate': f"{self.headshot_rate:.1%}" if self.headshot_rate > 0 else "N/A",
            'total_kills': self.total_kills if self.total_kills > 0 else "N/A",
            'total_headshots': self.total_headshots if self.total_headshots > 0 else "N/A",
            'matches_played': self.matches_played if self.matches_played > 0 else "N/A",
            'agent': self.agent,
            'team': self.team,
            'hidden': self.incognito,
            'riot_stats_loaded': self.riot_stats_loaded,
            'stats_loaded': self.stats_loaded
        }
    
    def get_enhanced_stats_display(self) -> str:
        """Get a formatted string for displaying enhanced stats"""
        if not self.riot_stats_loaded and not self.stats_loaded:
            return "No stats available"
        
        parts = []
        
        if self.player_level > 0:
            parts.append(f"Level {self.player_level}")
        
        if self.current_rank != "Unranked":
            rank_display = self.current_rank
            if self.current_rr > 0:
                rank_display += f" ({self.current_rr} RR)"
            parts.append(rank_display)
        
        if self.peak_rank != "Unranked" and self.peak_rank != self.current_rank:
            peak_display = f"Peak: {self.peak_rank}"
            if self.peak_rr > 0:
                peak_display += f" ({self.peak_rr} RR)"
            parts.append(peak_display)
        
        if self.headshot_rate > 0:
            parts.append(f"HS: {self.headshot_rate:.1%}")
        
        if self.kd_ratio > 0:
            parts.append(f"K/D: {self.kd_ratio:.2f}")
        
        if self.win_rate > 0:
            parts.append(f"WR: {self.win_rate:.1%}")
        
        return " | ".join(parts) if parts else "Stats loading..."
    
    def get_level_display_name(self) -> str:
        """Get player name with level display: PlayerName (Lv.45)"""
        if self.player_level > 0:
            return f"{self.name} (Lv.{self.player_level})"
        return self.name
    
    def get_server_region(self) -> str:
        """Get the server region the player is on"""
        # Try to determine server region from client region
        if hasattr(self, 'client') and self.client:
            region = getattr(self.client, 'region', 'Unknown')
            region_map = {
                'eu': '🇪🇺 Europe',
                'na': '🇺🇸 N. America', 
                'ap': '🌏 Asia Pacific',
                'kr': '🇰🇷 Korea'
            }
            return region_map.get(region, f'🌍 {region.upper()}')
        return '🌍 Unknown'


