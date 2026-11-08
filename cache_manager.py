import json
import time
from datetime import datetime, timedelta
import os

class CacheManager:
    """Manages caching of platform check results to improve performance"""
    
    def __init__(self, cache_file='player_cache.json', cache_duration_hours=24):
        self.cache_file = cache_file
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
        return {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get_cached_result(self, player_name, platform):
        """Get cached result for player on specific platform"""
        cache_key = f"{player_name.lower()}_{platform}"
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            
            # Check if cache is still valid
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data['result']
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        
        return None
    
    def cache_result(self, player_name, platform, result):
        """Cache result for player on specific platform"""
        cache_key = f"{player_name.lower()}_{platform}"
        
        self.cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'player_name': player_name,
            'platform': platform
        }
        
        # Save cache periodically
        self.save_cache()
    
    def clear_expired_cache(self):
        """Remove all expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, data in self.cache.items():
            cached_time = datetime.fromisoformat(data['timestamp'])
            if current_time - cached_time >= self.cache_duration:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.save_cache()
            print(f"Cleared {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        total_entries = len(self.cache)
        platforms = {}
        
        for data in self.cache.values():
            platform = data['platform']
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            'total_entries': total_entries,
            'platforms': platforms,
            'cache_file_size': os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        }
    
    def get_cached_data(self, cache_key, max_age_seconds):
        """Get cached data for tracker API (compatible method)"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            
            # Check if cache is still valid
            age_seconds = (datetime.now() - cached_time).total_seconds()
            if age_seconds < max_age_seconds:
                return cached_data.get('data')
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        
        return None
    
    def cache_data(self, cache_key, data):
        """Cache data for tracker API (compatible method)"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save cache periodically
        self.save_cache()