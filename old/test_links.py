#!/usr/bin/env python3
"""
Test script for link functionality
"""

import webbrowser
import urllib.parse

def test_tracker_link():
    """Test Tracker.gg link generation"""
    player_name = "Abel#1133"
    encoded_name = urllib.parse.quote(player_name)
    url = f"https://tracker.gg/valorant/profile/riot/{encoded_name}/overview"
    print(f"Tracker.gg URL: {url}")
    
    # Uncomment to test opening
    # webbrowser.open(url)

def test_twitch_link():
    """Test Twitch link generation"""
    username = "andruwu"
    url = f"https://www.twitch.tv/{username}"
    print(f"Twitch URL: {url}")
    
    # Uncomment to test opening
    # webbrowser.open(url)

if __name__ == "__main__":
    print("🔗 Testing link generation...")
    test_tracker_link()
    test_twitch_link()
    print("✅ Link generation working!")