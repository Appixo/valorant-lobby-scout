#!/usr/bin/env python3
"""
Demo script showing the multi-platform detection capabilities
"""

from streaming_services import StreamingChecker
import time

def demo_multiplatform():
    """Demonstrate the multi-platform checking functionality"""
    
    print("🎯 VALORANT MULTI-PLATFORM DETECTOR DEMO")
    print("=" * 60)
    print("This demo shows how the tool checks multiple platforms")
    print("for streaming and social media presence.")
    print("=" * 60)
    
    # Simulate some Valorant player names
    demo_players = [
        {
            'name': 'TwitchStreamer',
            'tag': '1234',
            'possible_names': ['twitchstreamer', 'ttv_twitchstreamer', 'twitchstreamer1234']
        },
        {
            'name': 'YouTubeGamer',
            'tag': '5678', 
            'possible_names': ['youtubegamer', 'yt_youtubegamer', 'youtubegamer5678']
        },
        {
            'name': 'SocialPlayer',
            'tag': '9999',
            'possible_names': ['socialplayer', 'socialplayer9999', 'social_player']
        }
    ]
    
    checker = StreamingChecker()
    
    print("\n🔍 SCANNING PLAYERS...")
    print("-" * 40)
    
    for i, player in enumerate(demo_players, 1):
        full_name = f"{player['name']}#{player['tag']}"
        print(f"\n[{i}/3] 👤 Checking {full_name}")
        print(f"      Possible names: {', '.join(player['possible_names'])}")
        
        # Check all platforms
        results = checker.check_all_platforms(player['possible_names'], delay=0.5)
        
        if results:
            streaming_found = []
            social_found = []
            
            for result in results:
                platform = result['platform']
                url = result['url']
                status = result['status']
                
                if platform in ['twitch', 'youtube', 'kick'] and status == 'live':
                    streaming_found.append(f"🔴 {platform.title()}: {url}")
                else:
                    social_found.append(f"📱 {platform.title()}: {url}")
            
            if streaming_found:
                print("      🎥 LIVE STREAMS:")
                for stream in streaming_found:
                    print(f"         {stream}")
            
            if social_found:
                print("      📱 SOCIAL MEDIA:")
                for social in social_found:
                    print(f"         {social}")
            
            if not streaming_found and not social_found:
                print("      ❌ No presence found on any platform")
        else:
            print("      ❌ No presence found on any platform")
    
    print("\n" + "=" * 60)
    print("✅ SCAN COMPLETE!")
    print("\nIn a real Valorant match, this would:")
    print("• Detect hidden player names")
    print("• Check all platforms for each player")
    print("• Show results in the GUI with clickable links")
    print("• Allow you to watch streams or view profiles")
    print("=" * 60)

if __name__ == "__main__":
    demo_multiplatform()