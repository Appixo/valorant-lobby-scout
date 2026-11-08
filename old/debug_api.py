#!/usr/bin/env python3
"""
Debug script to test the Tracker.gg API key manually
"""

import requests

def test_api_key_raw():
    """Test the API key with manual requests"""
    app_id = "YOUR_TRACKER_API_KEY"  # This should be the App ID
    
    # Test endpoint from Tracker.gg docs - try the standard endpoint
    base_url = "https://public-api.tracker.gg/v2"
    
    # Test with the standard profile endpoint format
    test_endpoints = [
        f"{base_url}/valorant/standard/profile/riot/TenZ%23001",
        f"{base_url}/valorant/standard/profile/riot/shroud%23001",
    ]
    
    headers = {
        'TRN-Api-Key': app_id,  # Use App ID as per documentation
        'User-Agent': 'ValorantPlayerDetector/1.0',
        'Accept': 'application/json'
    }
    
    print("🔧 Testing App ID with standard endpoints...")
    print(f"App ID: {app_id}")
    print("-" * 50)
    
    for endpoint in test_endpoints:
        print(f"\n🔗 Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! API key is working")
                data = response.json()
                print(f"Data preview: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🧪 Testing alternative authentication...")
    # Test with Authorization header instead
    alt_headers = {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'ValorantPlayerDetector/1.0',
        'Accept': 'application/json'
    }
    
    endpoint = f"{base_url}/valorant/profile/riot/TenZ%23001"
    print(f"🔗 Testing with Authorization header: {endpoint}")
    try:
        response = requests.get(endpoint, headers=alt_headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS with Authorization header!")
            return True
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    test_api_key_raw()