import json
import time
import sys
from valclient.client import Client
from player import Player
from game import Game
from logger_config import init_logging, get_logger

def load_settings():
    """Load settings from settings.json"""
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ settings.json not found!")
        sys.exit(1)

def save_settings(data):
    """Save settings to settings.json"""
    with open('settings.json', 'w') as f:
        json.dump(data, f, indent=4)

def setup_client():
    """Initialize and setup the Valorant client"""
    data = load_settings()
    
    if not data['ran']:
        print("🎮 First time setup!")
        region = input("Enter your region (na, eu, ap, kr): ").lower()
        
        try:
            client = Client(region=region)
            client.activate()
            
            # Update settings
            data['ran'] = True
            data['region'] = region
            save_settings(data)
            
            print(f"✅ Setup complete! Region set to: {region}")
            return client, data
            
        except Exception as e:
            print(f"❌ Failed to connect to Valorant client: {e}")
            print("Make sure Valorant is running and try again.")
            sys.exit(1)
    else:
        try:
            client = Client(region=data['region'])
            client.activate()
            print(f"🔗 Connected to Valorant client (Region: {data['region']})")
            return client, data
            
        except Exception as e:
            print(f"❌ Failed to connect to Valorant client: {e}")
            print("Make sure Valorant is running and try again.")
            sys.exit(1)

def main():
    # Initialize logging
    logger_system = init_logging()
    logger = get_logger('Console')
    
    print("🎯 Valorant Lobby Scout")
    print("Created by: https://github.com/deadly")
    print("-" * 50)
    
    logger.info("🎯 Console application started")
    
    # Setup client and load settings
    client, settings = setup_client()
    
    # Extract settings
    stateInterval = settings['stateInterval']
    twitchReqDelay = settings['twitchReqDelay']
    skipTeamPlayers = settings['skipTeamPlayers']
    skipPartyPlayers = settings['skipPartyPlayers']
    
    running = True
    seenMatches = []
    
    print("⏳ Waiting for a match to begin...")
    print("Press Ctrl+C to stop")
    
    try:
        while running:
            time.sleep(stateInterval)
            
            try:
                # Check if in game
                presence = client.fetch_presence(client.puuid)
                if not presence:
                    continue
                    
                sessionState = presence.get('sessionLoopState')
                
                if sessionState == "INGAME":
                    # Get match info
                    player_info = client.coregame_fetch_player()
                    if not player_info:
                        continue
                        
                    matchID = player_info.get('MatchID')
                    if not matchID or matchID in seenMatches:
                        continue
                    
                    print("\n🎮 Match detected!")
                    seenMatches.append(matchID)
                    
                    # Fetch match details
                    matchInfo = client.coregame_fetch_match(matchID)
                    if not matchInfo or 'Players' not in matchInfo:
                        continue
                    
                    players = []
                    localPlayer = None
                    
                    # Process players
                    for player_data in matchInfo['Players']:
                        player_obj = Player(
                            client=client,
                            puuid=player_data['Subject'].lower(),
                            agentID=player_data['CharacterID'].lower(),
                            incognito=player_data['PlayerIdentity']['Incognito'],
                            team=player_data['TeamID']
                        )
                        
                        if client.puuid == player_data['Subject']:
                            localPlayer = player_obj
                        else:
                            players.append(player_obj)
                    
                    if not localPlayer:
                        print("❌ Could not identify local player")
                        continue
                    
                    # Create game instance
                    party = client.fetch_party()
                    currentGame = Game(
                        party=party,
                        matchID=matchID,
                        players=players,
                        localPlayer=localPlayer
                    )
                    
                    # Find hidden names
                    currentGame.find_hidden_names(players)
                    
                    # Find streamers
                    currentGame.find_streamers(
                        players, 
                        twitchReqDelay, 
                        skipTeamPlayers, 
                        skipPartyPlayers
                    )
                    
                    print("\n⏳ Monitoring for next match...")
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "core" not in error_msg and "nonetype" not in error_msg:
                    print(f"⚠️  Error occurred: {e}")
                # Continue running even if there's an error
                
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()