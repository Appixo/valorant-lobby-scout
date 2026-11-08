"""
Quick Player Lookup - Simple stats checker
Usage: python quick_lookup.py PlayerName#TAG
"""

import json
import sys
from valclient.client import Client
from valorant_api_client import init_valorant_api, get_current_season_id


def lookup_player(username: str, tag: str):
    """Quick lookup of player stats"""
    try:
        print(f"\n🔍 Looking up: {username}#{tag}")
        print("-" * 60)
        
        # Connect to Valorant client
        print("📡 Connecting to Valorant client...")
        client = Client(region='eu')  # Change if needed: 'na', 'ap', 'kr'
        client.activate()
        print(f"✅ Connected! (Region: {client.region})\n")
        
        # Initialize API
        with open('settings.json') as f:
            api_key = json.load(f).get('henrikApiKey')
        api_client = init_valorant_api(api_key, valclient=client)
        season_id = get_current_season_id(client)
        
        # Try to get PUUID for fast method
        print(f"🔎 Fetching stats for {username}#{tag}...\n")
        
        try:
            # Get account info
            import requests
            response = requests.get(
                f"https://api.henrikdev.xyz/valorant/v1/account/{username}/{tag}",
                headers={'Authorization': api_key} if api_key else {},
                timeout=10
            )
            
            if response.status_code == 200:
                puuid = response.json().get('data', {}).get('puuid')
                
                if puuid:
                    # Use fast method
                    stats = api_client.get_player_stats_fast(puuid, season_id, username, tag)
                else:
                    # Fallback
                    stats = api_client.get_player_stats(username, tag)
            else:
                # Fallback
                stats = api_client.get_player_stats(username, tag)
                
        except Exception:
            # Fallback
            stats = api_client.get_player_stats(username, tag)
        
        if not stats:
            print(f"❌ No stats found for {username}#{tag}")
            print("   Player may not exist or has a private profile\n")
            return
        
        # Display results
        print("=" * 60)
        print(f"📊 STATS FOR {username}#{tag}")
        print("=" * 60)
        
        if hasattr(stats, 'player_level') and stats.player_level > 0:
            print(f"🎮 Level:         {stats.player_level}")
        
        if hasattr(stats, 'rank') and stats.rank != "Unranked":
            rank_display = stats.rank
            if hasattr(stats, 'rr') and stats.rr > 0:
                rank_display += f" ({stats.rr} RR)"
            print(f"🏆 Current Rank:  {rank_display}")
        else:
            print(f"🏆 Current Rank:  Unranked")
        
        if hasattr(stats, 'peak_rank') and stats.peak_rank != "Unranked":
            print(f"⭐ Peak Rank:     {stats.peak_rank}")
        
        if hasattr(stats, 'kd_ratio') and stats.kd_ratio > 0:
            print(f"💀 K/D Ratio:     {stats.kd_ratio:.2f}")
        
        if hasattr(stats, 'headshot_rate') and stats.headshot_rate > 0:
            print(f"🎯 Headshot %:    {stats.headshot_rate:.1%}")
        
        if hasattr(stats, 'win_rate') and stats.win_rate > 0:
            print(f"🏅 Win Rate:      {stats.win_rate:.1%}")
        
        if hasattr(stats, 'matches_played') and stats.matches_played > 0:
            win_loss = ""
            if hasattr(stats, 'wins') and hasattr(stats, 'losses'):
                win_loss = f" ({stats.wins}W - {stats.losses}L)"
            print(f"📈 Matches:       {stats.matches_played}{win_loss}")
        
        print("=" * 60)
        print("✅ Stats retrieved successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║          🎯 Quick Player Stats Lookup                 ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    if len(sys.argv) >= 2:
        # Command line argument
        full_name = sys.argv[1]
        if '#' in full_name:
            username, tag = full_name.split('#', 1)
            lookup_player(username, tag)
        else:
            print("\n❌ Error: Use format PlayerName#TAG")
            print("   Example: python quick_lookup.py TenZ#SEN\n")
    else:
        # Interactive mode
        print("\n📝 Enter player name (or 'quit' to exit)")
        print("   Format: PlayerName#TAG")
        print("   Example: TenZ#SEN\n")
        
        while True:
            full_name = input("👤 Player: ").strip()
            
            if not full_name or full_name.lower() == 'quit':
                print("\n👋 Goodbye!\n")
                break
            
            if '#' not in full_name:
                print("❌ Error: Use format PlayerName#TAG\n")
                continue
            
            username, tag = full_name.split('#', 1)
            lookup_player(username, tag)
            
            print("\n" + "─" * 60)
            print("Enter another player name or 'quit' to exit\n")


if __name__ == "__main__":
    main()

