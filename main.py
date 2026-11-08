#!/usr/bin/env python3
"""
Valorant Player Detector - Main Entry Point
Launches the professional GUI application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_app import main as gui_main
    
    if __name__ == "__main__":
        print("=" * 60)
        print("🎯 Valorant Player Detector Pro")
        print("=" * 60)
        print("✨ Launching professional UI...")
        print("🔍 Hidden player detection enabled")
        print("📊 Real-time match analysis ready")
        print("-" * 60)
        gui_main()
        
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("\n💡 Please install requirements:")
    print("   pip install -r requirements.txt")
    input("\nPress Enter to exit...")
except KeyboardInterrupt:
    print("\n\n👋 Application stopped by user")
except Exception as e:
    print(f"\n❌ Error starting application: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")