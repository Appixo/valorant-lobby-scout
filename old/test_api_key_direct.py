#!/usr/bin/env python3
"""
Test API key directly with HTTP requests (bypassing valo_api library)
"""

import requests
import time

def test_henrik_api_direct():
    print("[TEST] Testing Henrik's ValorantAPI Directly")
    print("=" * 60)
    
    api_key = "YOUR_HENRIK_API_KEY"
    base_url = "https://api.henrikdev.xyz"
    
    headers = {
        'Authorization': api_key,
        'User-Agent': 'ValorantPlayerDetector/1.0'
    }
    
    # Test 1: Status endpoint (should work without player name)
    print("\n[TEST 1] Testing /valorant/v1/status")
    try:
        response = requests.get(f"{base_url}/valorant/v1/status", headers=headers, timeout=10)
        print(f"   [STATUS] HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Status: {data}")
        else:
            print(f"   [FAIL] Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    time.sleep(1)
    
    # Test 2: Account endpoint with TenZ
    print("\n[TEST 2] Testing /valorant/v1/account/TenZ/001")
    try:
        response = requests.get(f"{base_url}/valorant/v1/account/TenZ/001", headers=headers, timeout=10)
        print(f"   [STATUS] HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Account found!")
            if 'data' in data:
                print(f"   [PUUID] {data['data'].get('puuid', 'N/A')[:20]}...")
                print(f"   [REGION] {data['data'].get('region', 'N/A')}")
                print(f"   [LEVEL] {data['data'].get('account_level', 'N/A')}")
        else:
            print(f"   [FAIL] Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    time.sleep(1)
    
    # Test 3: MMR endpoint with TenZ
    print("\n[TEST 3] Testing /valorant/v2/mmr/na/TenZ/001")
    try:
        response = requests.get(f"{base_url}/valorant/v2/mmr/na/TenZ/001", headers=headers, timeout=10)
        print(f"   [STATUS] HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] MMR data found!")
            if 'data' in data:
                current = data['data'].get('current_data', {})
                print(f"   [RANK] {current.get('currenttierpatched', 'N/A')}")
                print(f"   [RR] {current.get('ranking_in_tier', 'N/A')}")
                print(f"   [ELO] {current.get('elo', 'N/A')}")
        else:
            print(f"   [FAIL] Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    time.sleep(1)
    
    # Test 4: Your account - Appiezap#0000
    print("\n[TEST 4] Testing /valorant/v1/account/Appiezap/0000")
    try:
        response = requests.get(f"{base_url}/valorant/v1/account/Appiezap/0000", headers=headers, timeout=10)
        print(f"   [STATUS] HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Account found!")
            if 'data' in data:
                print(f"   [PUUID] {data['data'].get('puuid', 'N/A')[:20]}...")
                print(f"   [REGION] {data['data'].get('region', 'N/A')}")
                print(f"   [LEVEL] {data['data'].get('account_level', 'N/A')}")
                print(f"   [NAME] {data['data'].get('name', 'N/A')}#{data['data'].get('tag', 'N/A')}")
        elif response.status_code == 404:
            print(f"   [NOT FOUND] Account not found or private")
            print(f"   [INFO] Response: {response.text[:300]}")
        else:
            print(f"   [FAIL] Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 5: Try with eu region for Appiezap
    time.sleep(1)
    print("\n[TEST 5] Testing MMR /valorant/v2/mmr/eu/Appiezap/0000")
    try:
        response = requests.get(f"{base_url}/valorant/v2/mmr/eu/Appiezap/0000", headers=headers, timeout=10)
        print(f"   [STATUS] HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] MMR data found!")
            if 'data' in data:
                current = data['data'].get('current_data', {})
                print(f"   [RANK] {current.get('currenttierpatched', 'N/A')}")
                print(f"   [RR] {current.get('ranking_in_tier', 'N/A')}")
        elif response.status_code == 404:
            print(f"   [NOT FOUND] No MMR data or private profile")
        else:
            print(f"   [FAIL] Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] {e}")

if __name__ == "__main__":
    test_henrik_api_direct()

