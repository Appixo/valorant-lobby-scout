#!/usr/bin/env python3
"""
Test script for the multi-platform streaming checker
"""

from streaming_services import StreamingChecker
import time

def test_streaming_checker():
    """Test the streaming checker with some known usernames"""
    
    print("🧪 Testing Multi-Platform Streaming Checker")
    print("=" * 50)
    
    checker = StreamingChecker()
    
    # Test with some common/known usernames
    test_names = [
        "ninja",           # Known Twitch streamer
        "pewdiepie",       # Known YouTuber
        "shroud",          # Known streamer
        "valorant",        # Official accounts
        "riotgames",       # Official Riot
        "nonexistentuser123456789"  # Should not exist
    ]
    
    for name in test_names:
        print(f"\n🔍 Testing username: {name}")
        print("-" * 30)
        
        try:
            results = checker.check_all_platforms([name], delay=0.5)
            
            if results:
                for result in results:
                    platform = result['platform']
                    url = result['url']
                    status = result['status']
                    print(f"✅ Found on {platform.title()}: {url} ({status})")
            else:
                print("❌ Not found on any platform")
                
        except Exception as e:
            print(f"⚠️ Error testing {name}: {e}")
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_streaming_checker()