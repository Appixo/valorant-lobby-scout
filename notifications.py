import tkinter as tk
from tkinter import messagebox
import threading
import time
try:
    import plyer
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class NotificationManager:
    """Manages desktop notifications for the Valorant detector"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.notification_history = []
    
    def show_notification(self, title, message, notification_type="info"):
        """Show a desktop notification"""
        if not self.enabled:
            return
        
        # Add to history
        self.notification_history.append({
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': time.time()
        })
        
        # Try to use plyer for cross-platform notifications
        if PLYER_AVAILABLE:
            try:
                plyer.notification.notify(
                    title=title,
                    message=message,
                    timeout=5
                )
                return
            except Exception as e:
                print(f"Plyer notification failed: {e}")
        
        # Fallback to tkinter messagebox (will be blocking)
        threading.Thread(target=self._show_tkinter_notification, 
                        args=(title, message, notification_type), 
                        daemon=True).start()
    
    def _show_tkinter_notification(self, title, message, notification_type):
        """Show notification using tkinter (fallback)"""
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            if notification_type == "info":
                messagebox.showinfo(title, message)
            elif notification_type == "warning":
                messagebox.showwarning(title, message)
            elif notification_type == "error":
                messagebox.showerror(title, message)
            
            root.destroy()
        except Exception as e:
            print(f"Notification error: {e}")
    
    def notify_streamer_found(self, player_name, platform, is_live=True):
        """Notify when a streamer is found"""
        if is_live:
            title = "🔴 Live Streamer Detected!"
            message = f"{player_name} is streaming live on {platform.title()}"
        else:
            title = "📱 Content Creator Found!"
            message = f"{player_name} has a {platform.title()} profile"
        
        self.show_notification(title, message, "info")
    
    def notify_hidden_player(self, player_count):
        """Notify when hidden players are found"""
        title = "🔍 Hidden Players Detected!"
        if player_count == 1:
            message = "1 player is using incognito mode"
        else:
            message = f"{player_count} players are using incognito mode"
        
        self.show_notification(title, message, "warning")
    
    def notify_match_start(self, map_name):
        """Notify when a new match starts"""
        title = "🎮 New Match Detected!"
        message = f"Starting scan on {map_name}"
        
        self.show_notification(title, message, "info")
    
    def get_notification_history(self):
        """Get recent notification history"""
        return self.notification_history[-10:]  # Last 10 notifications
    
    def clear_history(self):
        """Clear notification history"""
        self.notification_history.clear()
    
    def toggle_notifications(self):
        """Toggle notifications on/off"""
        self.enabled = not self.enabled
        return self.enabled