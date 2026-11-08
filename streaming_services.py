import requests
import time
import re
from urllib.parse import quote
import json
from cache_manager import CacheManager
from logger_config import get_logger

class StreamingChecker:
    """Multi-platform streaming and social media checker with caching"""
    
    def __init__(self, use_cache=True):
        self.platforms = {
            'twitch': self.check_twitch,
            'youtube': self.check_youtube,
            'kick': self.check_kick,
            'tiktok': self.check_tiktok,
            'rumble': self.check_rumble,
            'facebook': self.check_facebook
        }
        
        # Headers to avoid bot detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Initialize cache manager and logger
        self.use_cache = use_cache
        self.cache_manager = CacheManager() if use_cache else None
        self.logger = get_logger('Platform')
    
    def check_all_platforms(self, possible_names, delay=1.0):
        """Check all platforms for live streams/content with caching"""
        found_streams = []
        
        for platform_name, check_func in self.platforms.items():
            for name in possible_names:
                try:
                    # Check cache first
                    if self.use_cache and self.cache_manager:
                        cached_result = self.cache_manager.get_cached_result(name, platform_name)
                        if cached_result is not None:
                            self.logger.debug(f"💾 Cache HIT: {name} on {platform_name}")
                            if cached_result:  # If cached result is not empty/None
                                found_streams.append({
                                    'platform': platform_name,
                                    'username': name,
                                    'url': cached_result,
                                    'status': 'live' if platform_name in ['twitch', 'youtube', 'kick'] else 'active',
                                    'cached': True
                                })
                            continue  # Skip actual check, use cached result
                        else:
                            self.logger.debug(f"💾 Cache MISS: {name} on {platform_name}")
                    
                    if delay > 0:
                        time.sleep(delay)
                    
                    check_start = time.time()
                    result = check_func(name)
                    check_duration = time.time() - check_start
                    
                    # Log the result
                    if result:
                        self.logger.debug(f"✅ {name} found on {platform_name} ({check_duration:.2f}s)")
                    else:
                        self.logger.debug(f"❌ {name} not found on {platform_name} ({check_duration:.2f}s)")
                    
                    # Cache the result
                    if self.use_cache and self.cache_manager:
                        self.cache_manager.cache_result(name, platform_name, result)
                        self.logger.debug(f"💾 Cached result for {name} on {platform_name}")
                    
                    if result:
                        found_streams.append({
                            'platform': platform_name,
                            'username': name,
                            'url': result,
                            'status': 'live' if platform_name in ['twitch', 'youtube', 'kick'] else 'active',
                            'cached': False
                        })
                        break  # Found on this platform, no need to check other names
                        
                except Exception as e:
                    self.logger.error(f"❌ Error checking {platform_name} for {name}: {e}")
                    continue
        
        return found_streams
    
    def check_twitch(self, username):
        """Check if user is live on Twitch"""
        try:
            url = f'https://twitch.tv/{username}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Check for live broadcast indicators
                if 'isLiveBroadcast' in response.text or '"isLive":true' in response.text:
                    return url
                # Check for channel existence (but don't return URL if not live)
                elif ('channel does not exist' not in response.text.lower() and 
                      'followers' in response.text.lower()):
                    return url  # Channel exists
            return None
        except Exception:
            return None
    
    def check_youtube(self, username):
        """Check YouTube for live streams or recent activity"""
        try:
            # Try different YouTube URL formats
            urls_to_check = [
                f'https://youtube.com/@{username}',
                f'https://youtube.com/c/{username}',
                f'https://youtube.com/user/{username}',
                f'https://youtube.com/channel/{username}'
            ]
            
            for url in urls_to_check:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        # Check for live stream indicators
                        if '"isLiveContent":true' in response.text or 'LIVE' in response.text:
                            return url
                        # Check if channel exists and is active
                        elif 'channel' in response.text.lower() and 'subscribe' in response.text.lower():
                            return url  # Channel exists
                except Exception:
                    continue
            return None
        except Exception:
            return None
    
    def check_kick(self, username):
        """Check if user is live on Kick"""
        try:
            url = f'https://kick.com/{username}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Check for live stream indicators
                if '"is_live":true' in response.text or 'LIVE' in response.text:
                    return url
                # Check if channel exists
                elif 'channel' in response.text.lower() and 'follow' in response.text.lower():
                    return url
            return None
        except Exception:
            return None
    
    def check_tiktok(self, username):
        """Check TikTok profile"""
        try:
            url = f'https://tiktok.com/@{username}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # More specific checks for TikTok profile existence
                if ('uniqueId' in response.text and 'followers' in response.text.lower()):
                    return url
                elif 'user-page' in response.text and 'tiktok' in response.text.lower():
                    return url
            return None
        except Exception:
            return None
    
    def check_rumble(self, username):
        """Check Rumble for user profile"""
        try:
            url = f'https://rumble.com/user/{username}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Check if profile exists
                if 'subscribers' in response.text.lower() or 'videos' in response.text.lower():
                    return url
                # Check for live stream
                elif 'live' in response.text.lower():
                    return url
            return None
        except Exception:
            return None
    
    def check_facebook(self, username):
        """Check Facebook profile/page"""
        try:
            # Try different Facebook URL formats
            urls_to_check = [
                f'https://facebook.com/{username}',
                f'https://facebook.com/profile.php?id={username}',
                f'https://facebook.com/pages/{username}'
            ]
            
            for url in urls_to_check:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        # Check if profile/page exists
                        if 'facebook' in response.text.lower() and ('profile' in response.text.lower() or 'page' in response.text.lower()):
                            return url
                except Exception:
                    continue
            return None
        except Exception:
            return None

# Convenience function for backward compatibility
def check_streaming_platforms(possible_names, delay=1.0):
    """Check all streaming platforms for the given names"""
    checker = StreamingChecker()
    return checker.check_all_platforms(possible_names, delay)