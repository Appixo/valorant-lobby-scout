#!/usr/bin/env python3
"""
Simple direct test of API calls
"""

import requests

api_key = "YOUR_HENRIK_API_KEY"
player_name = "Appiezap"
tag = "0000"

headers = {'Authorization': api_key}

# Test MMR
print("[TEST] MMR Data")
mmr_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/eu/{player_name}/{tag}"
response = requests.get(mmr_url, headers=headers, timeout=10)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Keys: {data.keys()}")
    if 'data' in data:
        print(f"Rank: {data['data'].get('current_data', {}).get('currenttierpatched', 'N/A')}")
        print(f"RR: {data['data'].get('current_data', {}).get('ranking_in_tier', 'N/A')}")
    else:
        print(f"No 'data' key, got: {data}")
else:
    print(f"Error: {response.text[:200]}")

print("\n[TEST] Match History")
match_url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{player_name}/{tag}"
response = requests.get(match_url, headers=headers, timeout=10)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Keys: {data.keys()}")
    if 'data' in data:
        matches = data['data']
        print(f"Matches: {len(matches)}")
        if matches:
            first_match = matches[0]
            print(f"First match keys: {first_match.keys()}")
    else:
        print(f"No 'data' key")
else:
    print(f"Error: {response.text[:200]}")

