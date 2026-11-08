#!/usr/bin/env python3
"""
Test automatic stat fetching when a player is created
Tests the new automatic loading of: player level, K/D, rank, peak rank, win rate, headshot %
"""

from valorant_api_client import init_valorant_api
from player import Player
import time

class MockClient:
    """Mock valclient for testing"""
    def __init__(self):
        self.region = 'eu'
    
    def put(self, endpoint, endpoint_type, json_data):
        """Mock put request - returns fake player data"""
        return [{
            'GameName': 'Appiezap',
            'TagLine': '0000',
            'DisplayName': 'Appiezap#0000'
        }]

def test_automatic_stats():
    print("[TEST] Automatic Stat Fetching")
    print("=" * 60)
    
    # Initialize ValorantAPI with the key
    api_key = "YOUR_HENRIK_API_KEY"
    init_valorant_api(api_key)
    
    print("\n[STEP 1] Creating Player object for Appiezap#0000")
    print("-" * 60)
    
    # Create a mock client
    mock_client = MockClient()
    
    # Create player with your account PUUID (fake for testing)
    fake_puuid = "c5a9ddc6-1930-537b-a58f-e8b0a0f7c76d"
    
    # Create Player object - this should automatically fetch stats
    player = Player(
        client=mock_client,
        puuid=fake_puuid,
        agentID="add6443a-41bd-e414-f6ad-e58d267f4e95",  # Jett
        incognito=False,
        team="Blue",
        display_name="Appiezap#0000"
    )
    
    print(f"\n[CREATED] Player: {player.full_name}")
    print(f"   Agent: {player.agent}")
    print(f"   Team: {player.team}")
    print(f"   Hidden: {player.is_hidden}")
    
    # Now trigger automatic stat loading
    print("\n[STEP 2] Triggering automatic stat loading...")
    print("-" * 60)
    
    player.get_enhanced_riot_stats()
    
    # Wait a bit for API calls to complete
    time.sleep(3)
    
    # Display results
    print("\n[RESULTS] Player Stats")
    print("=" * 60)
    
    results = {
        'Player Level': player.player_level if player.player_level > 0 else "Not loaded",
        'Current Rank': player.current_rank,
        'Current RR': f"{player.current_rr} RR" if player.current_rr > 0 else "N/A",
        'Peak Rank': player.peak_rank,
        'K/D Ratio': f"{player.kd_ratio:.2f}" if player.kd_ratio > 0 else "Not loaded",
        'Win Rate': f"{player.win_rate:.1%}" if player.win_rate > 0 else "Not loaded",
        'Headshot %': f"{player.headshot_rate:.1%}" if player.headshot_rate > 0 else "Not loaded",
        'Avg Score': f"{player.avg_score:.0f}" if player.avg_score > 0 else "Not loaded",
        'Matches Played': player.matches_played if player.matches_played > 0 else "Not loaded",
        'Stats Loaded': player.stats_loaded or player.riot_stats_loaded
    }
    
    for key, value in results.items():
        print(f"   {key}: {value}")
    
    # Verify all stats are loaded
    print("\n[VERIFICATION]")
    print("-" * 60)
    
    success_count = 0
    total_checks = 7
    
    checks = [
        ("Player Level", player.player_level > 0),
        ("Current Rank", player.current_rank != "Unranked"),
        ("K/D Ratio", player.kd_ratio > 0),
        ("Win Rate", player.win_rate > 0),
        ("Headshot %", player.headshot_rate > 0),
        ("Matches Played", player.matches_played > 0),
        ("Stats Loaded Flag", player.stats_loaded or player.riot_stats_loaded)
    ]
    
    for check_name, check_passed in checks:
        status = "[OK]" if check_passed else "[FAIL]"
        print(f"   {status} {check_name}")
        if check_passed:
            success_count += 1
    
    print(f"\n[SUMMARY] {success_count}/{total_checks} checks passed")
    
    if success_count >= 6:  # Allow one failure
        print("[SUCCESS] Automatic stat fetching is working!")
    else:
        print("[WARNING] Some stats failed to load automatically")
    
    # Display enhanced stats string
    print(f"\n[DISPLAY] Enhanced Stats String:")
    print(f"   {player.get_enhanced_stats_display()}")
    
    return player

if __name__ == "__main__":
    test_automatic_stats()

