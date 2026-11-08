import logging
import os
from datetime import datetime
import json
import sys

class ValorantLogger:
    """Comprehensive logging system for Valorant detector"""
    
    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create timestamp for log files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Configure root logger
        self.logger = logging.getLogger('ValorantDetector')
        self.logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(f'logs/valorant_detector_{timestamp}.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # File handler for errors only
        error_handler = logging.FileHandler(f'logs/errors_{timestamp}.log', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # Create specialized loggers
        self.setup_specialized_loggers()
        
        self.logger.info("=" * 80)
        self.logger.info("🎯 VALORANT MULTI-PLATFORM DETECTOR STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Log Level: {logging.getLevelName(self.log_level)}")
        self.logger.info(f"Log Files: logs/valorant_detector_{timestamp}.log")
        self.logger.info(f"Error Log: logs/errors_{timestamp}.log")
        
    def setup_specialized_loggers(self):
        """Setup specialized loggers for different components"""
        
        # Match detection logger
        self.match_logger = logging.getLogger('ValorantDetector.Match')
        
        # Platform checking logger
        self.platform_logger = logging.getLogger('ValorantDetector.Platform')
        
        # Cache logger
        self.cache_logger = logging.getLogger('ValorantDetector.Cache')
        
        # GUI logger
        self.gui_logger = logging.getLogger('ValorantDetector.GUI')
        
        # Performance logger
        self.perf_logger = logging.getLogger('ValorantDetector.Performance')
        
        # Statistics logger
        self.stats_logger = logging.getLogger('ValorantDetector.Statistics')
    
    def log_match_detection(self, match_id, map_name, player_count, hidden_count):
        """Log match detection details"""
        self.match_logger.info(f"🎮 MATCH DETECTED")
        self.match_logger.info(f"   Match ID: {match_id}")
        self.match_logger.info(f"   Map: {map_name}")
        self.match_logger.info(f"   Players: {player_count}")
        self.match_logger.info(f"   Hidden Players: {hidden_count}")
    
    def log_player_processing(self, player_name, agent, team, is_hidden):
        """Log individual player processing"""
        status = "HIDDEN" if is_hidden else "VISIBLE"
        self.match_logger.debug(f"👤 Player: {player_name} | {agent} | {team} | {status}")
    
    def log_platform_check_start(self, player_name, platforms):
        """Log start of platform checking"""
        self.platform_logger.info(f"🔍 Checking {player_name} on {len(platforms)} platforms")
        self.platform_logger.debug(f"   Platforms: {', '.join(platforms)}")
    
    def log_platform_result(self, player_name, platform, result, cached=False, duration=None):
        """Log platform check result"""
        cache_status = " (CACHED)" if cached else ""
        duration_str = f" ({duration:.2f}s)" if duration else ""
        
        if result:
            self.platform_logger.info(f"✅ {player_name} found on {platform.title()}{cache_status}{duration_str}")
            self.platform_logger.debug(f"   URL: {result}")
        else:
            self.platform_logger.debug(f"❌ {player_name} not found on {platform}{cache_status}{duration_str}")
    
    def log_cache_operation(self, operation, key=None, hit_rate=None):
        """Log cache operations"""
        if operation == "hit":
            self.cache_logger.debug(f"💾 Cache HIT: {key}")
        elif operation == "miss":
            self.cache_logger.debug(f"💾 Cache MISS: {key}")
        elif operation == "store":
            self.cache_logger.debug(f"💾 Cache STORE: {key}")
        elif operation == "stats" and hit_rate is not None:
            self.cache_logger.info(f"📊 Cache Hit Rate: {hit_rate:.1%}")
    
    def log_performance_metric(self, metric_name, value, unit="ms"):
        """Log performance metrics"""
        self.perf_logger.info(f"⚡ {metric_name}: {value}{unit}")
    
    def log_gui_action(self, action, details=None):
        """Log GUI actions"""
        if details:
            self.gui_logger.info(f"🖱️ GUI: {action} - {details}")
        else:
            self.gui_logger.info(f"🖱️ GUI: {action}")
    
    def log_error(self, component, error, context=None):
        """Log errors with context"""
        error_msg = f"❌ ERROR in {component}: {str(error)}"
        if context:
            error_msg += f" | Context: {context}"
        
        self.logger.error(error_msg)
        
        # Also log the full exception if available
        if hasattr(error, '__traceback__'):
            self.logger.exception("Full exception details:")
    
    def log_statistics(self, stats_type, data):
        """Log statistics data"""
        self.stats_logger.info(f"📊 {stats_type} Statistics:")
        
        if isinstance(data, dict):
            for key, value in data.items():
                self.stats_logger.info(f"   {key}: {value}")
        else:
            self.stats_logger.info(f"   {data}")
    
    def log_notification(self, notification_type, title, message):
        """Log notifications sent"""
        self.logger.info(f"🔔 NOTIFICATION [{notification_type}]: {title} - {message}")
    
    def log_session_summary(self, session_data):
        """Log session summary at the end"""
        self.logger.info("=" * 80)
        self.logger.info("📋 SESSION SUMMARY")
        self.logger.info("=" * 80)
        
        for key, value in session_data.items():
            self.logger.info(f"   {key}: {value}")
        
        self.logger.info("=" * 80)
    
    def get_logger(self, component=None):
        """Get logger for specific component"""
        if component:
            return logging.getLogger(f'ValorantDetector.{component}')
        return self.logger

# Global logger instance
valorant_logger = None

def get_logger(component=None):
    """Get the global logger instance"""
    global valorant_logger
    if valorant_logger is None:
        valorant_logger = ValorantLogger()
    
    if component:
        return valorant_logger.get_logger(component)
    return valorant_logger.logger

def init_logging(log_level=logging.INFO):
    """Initialize the logging system"""
    global valorant_logger
    valorant_logger = ValorantLogger(log_level)
    return valorant_logger