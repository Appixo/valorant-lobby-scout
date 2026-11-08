#!/usr/bin/env python3
"""
Launch the Valorant Lobby Scout with comprehensive logging enabled
"""

import sys
import logging
from logger_config import init_logging
from gui_app import main

def run_with_detailed_logging():
    """Run the application with detailed logging"""
    
    print("🎯 VALORANT LOBBY SCOUT")
    print("=" * 50)
    print("🔧 Initializing comprehensive logging system...")
    
    # Initialize logging with DEBUG level for maximum detail
    logger_system = init_logging(logging.DEBUG)
    logger = logger_system.logger
    
    logger.info("🚀 Starting Valorant Lobby Scout with detailed logging")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"💻 Platform: {sys.platform}")
    
    try:
        # Import and run the main GUI application
        logger.info("🖥️ Launching GUI application...")
        main()
        
    except KeyboardInterrupt:
        logger.info("⌨️ Application interrupted by user")
        print("\n👋 Application stopped by user")
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        logger.exception("Full exception details:")
        print(f"\n❌ Fatal error occurred: {e}")
        print("📋 Check the log files in the 'logs' directory for detailed information")
        
    finally:
        logger.info("🏁 Application shutdown complete")
        print("\n📁 Log files saved in 'logs' directory")
        print("🔍 Check the logs for detailed analysis of the session")

if __name__ == "__main__":
    run_with_detailed_logging()