import json
import os
from datetime import datetime
from typing import List, Dict, Any

class MatchHistory:
    """Manages match history and player statistics"""
    
    def __init__(self, history_file='match_history.json'):
        self.history_file = history_file
        self.matches = self.load_history()
    
    def load_history(self) -> List[Dict]:
        """Load match history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading match history: {e}")
        return []
    
    def save_history(self):
        """Save match history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.matches, f, indent=2)
        except Exception as e:
            print(f"Error saving match history: {e}")
    
    def add_match(self, match_id: str, map_name: str, players: List[Dict]):
        """Add a new match to history"""
        match_data = {
            'match_id': match_id,
            'timestamp': datetime.now().isoformat(),
            'map_name': map_name,
            'players': players,
            'hidden_players': [p for p in players if p.get('hidden', False)],
            'streamers': [p for p in players if p.get('streaming_platforms')],
            'social_media': [p for p in players if p.get('social_platforms')]
        }
        
        # Check if match already exists
        existing_match = next((m for m in self.matches if m['match_id'] == match_id), None)
        if not existing_match:
            self.matches.append(match_data)
            self.save_history()
            return True
        return False
    
    def upsert_match(self, match_id: str, map_name: str, players: List[Dict], my_team: str = None):
        """Add a match, or update it when it was first saved during agent select (only your team known)"""
        existing = next((m for m in self.matches if m['match_id'] == match_id), None)
        if existing is None:
            self.add_match(match_id, map_name, players)
            existing = self.matches[-1]
        elif len(players) >= len(existing['players']):
            existing.update({
                'map_name': map_name,
                'players': players,
                'hidden_players': [p for p in players if p.get('hidden', False)],
            })
        else:
            return
        existing['my_team'] = my_team
        self.save_history()
    
    def get_player_history(self, player_name: str) -> List[Dict]:
        """Get all matches where a specific player was encountered"""
        player_matches = []
        
        for match in self.matches:
            for player in match['players']:
                if player['name'].lower() == player_name.lower():
                    player_matches.append({
                        'match_id': match['match_id'],
                        'timestamp': match['timestamp'],
                        'map_name': match['map_name'],
                        'player_data': player
                    })
                    break
        
        return player_matches
    
    def get_streamer_stats(self) -> Dict[str, Any]:
        """Get statistics about encountered streamers"""
        total_matches = len(self.matches)
        matches_with_streamers = len([m for m in self.matches if m['streamers']])
        
        streamer_encounters = {}
        platform_stats = {}
        
        for match in self.matches:
            for streamer in match['streamers']:
                name = streamer['name']
                streamer_encounters[name] = streamer_encounters.get(name, 0) + 1
                
                for platform in streamer.get('streaming_platforms', []):
                    platform_name = platform['platform']
                    platform_stats[platform_name] = platform_stats.get(platform_name, 0) + 1
        
        return {
            'total_matches': total_matches,
            'matches_with_streamers': matches_with_streamers,
            'streamer_encounter_rate': matches_with_streamers / total_matches if total_matches > 0 else 0,
            'most_encountered_streamers': sorted(streamer_encounters.items(), key=lambda x: x[1], reverse=True)[:10],
            'platform_distribution': platform_stats
        }
    
    def get_hidden_player_stats(self) -> Dict[str, Any]:
        """Get statistics about hidden players"""
        total_matches = len(self.matches)
        matches_with_hidden = len([m for m in self.matches if m['hidden_players']])
        
        hidden_encounters = {}
        
        for match in self.matches:
            for hidden_player in match['hidden_players']:
                name = hidden_player['name']
                hidden_encounters[name] = hidden_encounters.get(name, 0) + 1
        
        return {
            'total_matches': total_matches,
            'matches_with_hidden': matches_with_hidden,
            'hidden_player_rate': matches_with_hidden / total_matches if total_matches > 0 else 0,
            'most_encountered_hidden': sorted(hidden_encounters.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def export_to_csv(self, filename: str = None):
        """Export match history to CSV"""
        if not filename:
            filename = f"valorant_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['match_id', 'timestamp', 'map_name', 'player_name', 'agent', 'team', 
                             'hidden', 'streaming_platforms', 'social_platforms']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for match in self.matches:
                    for player in match['players']:
                        writer.writerow({
                            'match_id': match['match_id'],
                            'timestamp': match['timestamp'],
                            'map_name': match['map_name'],
                            'player_name': player['name'],
                            'agent': player.get('agent', ''),
                            'team': player.get('team', ''),
                            'hidden': player.get('hidden', False),
                            'streaming_platforms': '; '.join([p['platform'] for p in player.get('streaming_platforms', [])]),
                            'social_platforms': '; '.join([p['platform'] for p in player.get('social_platforms', [])])
                        })
            
            return filename
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return None