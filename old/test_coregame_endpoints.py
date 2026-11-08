"""
Test script to discover available coregame API endpoints
This will help us find the endpoint that provides all match data
"""

from valclient import Client
from valclient.exceptions import HandshakeError

def test_coregame_endpoints():
    """Test various coregame endpoints to find comprehensive match data"""
    
    try:
        # Initialize client
        client = Client(region="eu")
        client.activate()
        print("[OK] Connected to Valorant client")
        
        # Get current match info
        try:
            player_info = client.coregame_fetch_player()
            match_id = player_info.get('MatchID')
            print(f"[MATCH] Current match ID: {match_id}")
        except Exception as e:
            print(f"[ERROR] No active match: {e}")
            return
        
        # Test endpoints
        endpoints_to_test = [
            f"/coregame/v1/matches/{match_id}/allplayers",
            f"/coregame/v1/matches/{match_id}/loadouts",
            f"/coregame/v1/matches/{match_id}/teamprogress",
            f"/coregame/v1/matches/{match_id}/competitive",
            f"/coregame/v1/players/{client.puuid}/coregame",
        ]
        
        print("\n[TESTING] Testing coregame endpoints...")
        
        for endpoint in endpoints_to_test:
            try:
                print(f"\n[TEST] Testing: {endpoint}")
                response = client.fetch(endpoint=f"/{endpoint.lstrip('/')}", endpoint_type="glz")
                
                if response and response.status_code == 200:
                    data = response.json()
                    print(f"[SUCCESS] Keys: {list(data.keys())}")
                    
                    # Show some sample data
                    if isinstance(data, dict):
                        for key, value in list(data.items())[:5]:
                            if isinstance(value, (dict, list)):
                                print(f"  {key}: {type(value).__name__} with {len(value)} items")
                            else:
                                print(f"  {key}: {value}")
                else:
                    print(f"[FAIL] HTTP {response.status_code if response else 'None'}")
                    
            except Exception as e:
                print(f"[ERROR] {str(e)[:100]}")
        
    except HandshakeError:
        print("[ERROR] Valorant client not running")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_coregame_endpoints()

