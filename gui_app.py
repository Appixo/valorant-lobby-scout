import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import webbrowser
import urllib.parse
import os
from datetime import datetime
from valclient.client import Client
from player import Player
from game import Game
from streaming_services import StreamingChecker
from match_history import MatchHistory
from cache_manager import CacheManager
from notifications import NotificationManager
from logger_config import get_logger, init_logging
import game_data
from match_insights import (extract_players, presence_parties, number_parties, smurf_reasons,
                            find_encounters, describe_encounters, build_name_ledger, friend_names, time_ago)
from team_board import TeamBoard, pick_family, PARTY_LABELS

class ValorantDetectorGUI:
    def __init__(self, root):
        # Initialize logging first
        self.logger_system = init_logging()
        self.logger = get_logger('GUI')
        
        self.root = root
        self.root.title("Valorant Detector Pro")
        
        # Set application icon (must be set BEFORE overrideredirect for taskbar)
        # ICO format works better with borderless windows on Windows
        try:
            base_path = os.path.dirname(__file__) if __file__ else '.'
            ico_path = os.path.join(base_path, 'valorant_icon.ico')
            png_path = os.path.join(base_path, 'valorant_icon.png')
            
            # Prefer ICO format for better taskbar support with borderless windows
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
                self.logger.info("✅ Application icon loaded (ICO format)")
            elif os.path.exists(png_path):
                # Fallback to PNG (may not show in taskbar with borderless window)
                self._icon_image = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, self._icon_image)
                self.logger.info("✅ Application icon loaded (PNG format)")
                self.logger.info("💡 Tip: Convert to ICO for better taskbar support: python convert_icon_to_ico.py")
            else:
                self.logger.warning("⚠️ No icon file found (valorant_icon.ico or .png)")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load application icon: {e}")
        
        # Option: Remove borders (no taskbar icon) or keep borders (icon visible)
        # For taskbar icon visibility, comment out the overrideredirect line:
        # self.root.overrideredirect(True)  # Borderless but NO taskbar icon
        
        # Keep this for professional dark theme
        self.root.configure(bg='#0f1923')  # Dark theme background
        
        # Optional: Hide the default title bar on Windows (keeps taskbar icon)
        # Uncomment this if you want a semi-borderless look:
        # self.root.attributes('-toolwindow', False)
        
        # Window drag variables
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Variables
        self.client = None
        self.current_game = None
        self.settings = self.load_settings()
        self.auto_mode = self.settings.get('autoMode', True)

        # Match tracking (shared between the auto monitor and manual refreshes)
        self._match_lock = threading.Lock()
        self._stats_lock = threading.Lock()
        self._last_match_key = 'unset'
        self._current_match_id = None
        self._lobby_match_ids = set()   # Match IDs seen since leaving the menus
        self._player_cache = {}         # puuid -> Player, kept from agent select into the match
        self._current_players = []
        self._current_phase = None      # 'PREGAME' (agent select) or 'INGAME'
        self._presence_parties = []   # Parties seen in presences (you and friends)
        self._party_numbers = {}      # puuid -> party number (presences + recent matches)
        self._confirmed_party = set() # Players whose party comes from presences, not a guess
        self._encounters = {}
        self._stats_attempted = set()        # Rank stats tried
        self._match_stats_attempted = set()  # K/D + HS% tried
        self._stats_loading = False
        self._monitor_running = False
        self._connect_failures = 0

        # Session tracking
        self.session_start_time = time.time()
        self.session_stats = {
            'matches_detected': 0,
            'players_scanned': 0,
            'streamers_found': 0,
            'hidden_players_found': 0,
            'platforms_checked': 0,
            'cache_hits': 0,
            'notifications_sent': 0
        }
        
        # Initialize history and cache managers
        self.match_history = MatchHistory()
        self.cache_manager = CacheManager()
        self.notification_manager = NotificationManager()
        self._known_names = build_name_ledger(self.match_history.matches)
        
        # Initialize API clients for stats fetching
        self.init_api_clients()
        
        self.logger.info("🚀 GUI Application initialized")
        self.logger.debug(f"Settings loaded: {self.settings}")
        
        # Setup GUI
        self.setup_gui()
        
        # Auto-connect on startup
        self.root.after(1000, self.connect_client)
        
        # Setup cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind resize event for responsive design
        self.root.bind('<Configure>', self.on_resize)
    
    def init_api_clients(self):
        """Initialize API clients for stats fetching with direct PD API support"""
        try:
            from valorant_api_client import init_valorant_api
            
            # Initialize ValorantAPI with valclient for fast direct PD API access
            # This uses rank-yoinker's approach: direct local client API = NO rate limits!
            api_key = self.settings.get('henrikApiKey')

            # Pass valclient for direct PD API access (much faster!)
            valorant_api = init_valorant_api(api_key, valclient=self.client)
            self.logger.info("✅ ValorantAPI client initialized with direct PD API support")
            self.logger.info("🚀 Stats loading will be MUCH faster now!")
            
            # Initialize Tracker.gg API (optional fallback)
            # Uncomment and add API key if you have one
            # from tracker_api import init_tracker_api
            # tracker_api = init_tracker_api("YOUR_TRACKER_API_KEY")
            # self.logger.info("✅ Tracker.gg API client initialized")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize API clients: {e}")
    
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "region": None,
                "stateInterval": 5,
                "twitchReqDelay": 2.0,
                "ran": False,
                "skipTeamPlayers": False,
                "skipPartyPlayers": True
            }
    
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    # Window size per layout: (default size, minimum size); player cards shrink to fit
    LAYOUT_SIZES = {
        'horizontal': ((1460, 560), (1260, 480)),
        'vertical': ((760, 900), (700, 720)),
    }

    def setup_gui(self):
        # Valorant-inspired dark theme
        self.colors = {
            'bg_primary': '#0e1217',      # Window background
            'bg_secondary': '#151b22',    # Header / footer
            'bg_card': '#19202a',         # Panels
            'bg_elevated': '#232c38',     # Buttons, table headings
            'row_alt': '#1d2530',         # Striped table rows
            'accent_red': '#ff4655',      # Valorant red (attackers)
            'accent_blue': '#3d9bff',     # Defenders
            'accent_cyan': '#06b6d4',
            'accent_teal': '#17d4b0',
            'text_primary': '#e8edf2',
            'text_secondary': '#93a1b0',
            'text_muted': '#5f6d7c',
            'success': '#22c55e',
            'warning': '#f5a524',
            'danger': '#ff4655',
            'border': '#27313d',
            'border_light': '#334050',
            'hover': '#2b3542',
            'selected': '#2a3a4f',
            'attacker_bg': '#3d1e1f',
            'defender_bg': '#1e2d3d',
            'you': '#f5c451',             # Your own row
            'hidden_indicator': '#b197fc', # Players using incognito
            'panel': '#0e1217',           # Behind the player cards
            'row': '#1a212b',             # Player card
            'row_hover': '#253040',
            'ally': '#17d4b0',            # Your team's banner
            'enemy': '#ff4655',           # Enemy team's banner
        }
        self.font_display = pick_family('Bahnschrift SemiBold Condensed', 'Segoe UI Semibold')
        self.font_semibold = pick_family('Bahnschrift SemiBold', 'Segoe UI Semibold')
        self.font_regular = pick_family('Bahnschrift', 'Segoe UI')

        self.root.configure(bg=self.colors['bg_primary'], highlightthickness=0, bd=0)
        self.apply_dark_title_bar()

        style = ttk.Style()
        style.theme_use('clam')

        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_header_bar(main_frame)
        self.setup_session_footer(main_frame)

        content = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=(14, 12))

        self.setup_match_card(content)
        self.setup_players_section(content)
        self.setup_tooltips()

        self.apply_layout(self.settings.get('layout', 'horizontal'), resize=True)

    def apply_dark_title_bar(self):
        """Match the Windows title bar to the dark theme (Windows 10/11)"""
        try:
            import ctypes
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            dark = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark), ctypes.sizeof(dark))
            # Caption colour (Windows 11 only), COLORREF is 0x00BBGGRR
            caption = ctypes.c_int(0x00221b15)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption), ctypes.sizeof(caption))
        except Exception:
            pass

    def make_button(self, parent, text, command, primary=False, state=tk.NORMAL):
        """Create a flat button in the primary (red) or secondary (dark) style"""
        if primary:
            bg, hover, fg = self.colors['accent_red'], '#ff5f6c', 'white'
        else:
            bg, hover, fg = self.colors['bg_elevated'], self.colors['hover'], self.colors['text_primary']

        button = tk.Button(parent, text=text, command=command,
                           font=(self.font_semibold, 9),
                           bg=bg, fg=fg,
                           activebackground=hover, activeforeground=fg,
                           disabledforeground=self.colors['text_muted'],
                           relief=tk.FLAT, borderwidth=0, cursor='hand2',
                           padx=16, pady=7, state=state)
        self.add_button_hover_effect(button, bg, hover)
        return button

    def setup_header_bar(self, parent):
        """Header with title, connection status and actions"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=58)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        tk.Frame(parent, bg=self.colors['border'], height=1).pack(fill=tk.X)

        content_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=16)

        # Left side - brand
        left_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        left_frame.pack(side=tk.LEFT)

        tk.Frame(left_frame, bg=self.colors['accent_red'], width=4, height=26).pack(side=tk.LEFT, padx=(0, 12))

        title_box = tk.Frame(left_frame, bg=self.colors['bg_secondary'])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="VALORANT",
                 font=(self.font_semibold, 7),
                 bg=self.colors['bg_secondary'],
                 fg=self.colors['accent_red']).pack(anchor='w')
        tk.Label(title_box, text="PLAYER DETECTOR",
                 font=(self.font_display, 16, 'italic'),
                 bg=self.colors['bg_secondary'],
                 fg=self.colors['text_primary']).pack(anchor='w')

        # Right side - status and actions
        right_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        right_frame.pack(side=tk.RIGHT)

        status_pill = tk.Frame(right_frame, bg=self.colors['bg_elevated'], padx=10, pady=5)
        status_pill.pack(side=tk.LEFT, padx=(0, 12))
        self.status_dot = tk.Canvas(status_pill, width=10, height=10, bg=self.colors['bg_elevated'], highlightthickness=0)
        self.status_dot.create_oval(1, 1, 9, 9, fill=self.colors['text_muted'], outline='', tags='dot')
        self.status_dot.pack(side=tk.LEFT, padx=(0, 7))
        self.status_label = tk.Label(status_pill, text="Connecting...",
                                     font=(self.font_regular, 9),
                                     bg=self.colors['bg_elevated'],
                                     fg=self.colors['text_secondary'])
        self.status_label.pack(side=tk.LEFT)

        # Layout toggle (icon button)
        self.layout_btn = tk.Canvas(right_frame, width=34, height=31, cursor='hand2',
                                    bg=self.colors['bg_elevated'], highlightthickness=0)
        self.layout_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.layout_btn.bind('<Button-1>', lambda e: self.toggle_layout())
        self.layout_btn.bind('<Enter>', lambda e: self._draw_layout_icon(hover=True), add='+')
        self.layout_btn.bind('<Leave>', lambda e: self._draw_layout_icon(hover=False), add='+')

        self.auto_btn = self.make_button(right_frame, "", self.toggle_monitoring)
        self.auto_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._update_auto_button()

        self.load_stats_btn = self.make_button(right_frame, "Load Stats",
                                               self.load_player_stats_manual, state=tk.DISABLED)
        self.load_stats_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.refresh_btn = self.make_button(right_frame, "Refresh", self.refresh_match, primary=True)
        self.refresh_btn.pack(side=tk.LEFT)

    def _draw_layout_icon(self, hover=False):
        """Draw the icon for the layout you'd switch to"""
        canvas = self.layout_btn
        bg = self.colors['hover'] if hover else self.colors['bg_elevated']
        color = self.colors['text_primary'] if hover else self.colors['text_secondary']
        canvas.config(bg=bg)
        canvas.delete('all')
        if self.layout == 'horizontal':
            # Stacked panels
            canvas.create_rectangle(10, 8, 24, 14, outline=color, width=2)
            canvas.create_rectangle(10, 17, 24, 23, outline=color, width=2)
        else:
            # Side-by-side panels
            canvas.create_rectangle(8, 9, 15, 22, outline=color, width=2)
            canvas.create_rectangle(19, 9, 26, 22, outline=color, width=2)

    def setup_match_card(self, parent):
        """Map name as a title, the match phase as a chip, counts on the right"""
        bg = self.colors['bg_primary']
        strip = tk.Frame(parent, bg=bg)
        strip.pack(fill=tk.X, pady=(0, 10))

        self.match_map_value = tk.Label(strip, text="—", font=(self.font_display, 24, 'italic'),
                                        bg=bg, fg=self.colors['text_secondary'])
        self.match_map_value.pack(side=tk.LEFT, padx=(2, 14))
        self.match_status_value = tk.Label(strip, text="WAITING FOR CONNECTION", font=(self.font_semibold, 8),
                                           bg=self.colors['bg_elevated'], fg=self.colors['text_secondary'],
                                           padx=9, pady=3)
        self.match_status_value.pack(side=tk.LEFT, pady=(6, 0))

        def stat(label, value):
            box = tk.Frame(strip, bg=bg)
            box.pack(side=tk.RIGHT, padx=(22, 0))
            tk.Label(box, text=label, font=(self.font_semibold, 7),
                     bg=bg, fg=self.colors['text_muted']).pack(anchor='e')
            value_label = tk.Label(box, text=value, font=(self.font_display, 14),
                                   bg=bg, fg=self.colors['text_secondary'])
            value_label.pack(anchor='e')
            return value_label

        # Packed right to left
        self.match_session_value = stat("THIS SESSION", "0 matches")
        self.match_hidden_value = stat("HIDDEN NAMES", "0")
        self.match_players_value = stat("PLAYERS", "0")

    def setup_players_section(self, parent):
        """Attacker and defender tables, side by side or stacked"""
        self.players_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        self.players_frame.pack(fill=tk.BOTH, expand=True)

        self.attackers_frame = tk.Frame(self.players_frame, bg=self.colors['bg_primary'])
        self.defenders_frame = tk.Frame(self.players_frame, bg=self.colors['bg_primary'])

        self.setup_team_table(self.attackers_frame, "Attackers", self.colors['accent_red'])
        self.setup_team_table(self.defenders_frame, "Defenders", self.colors['accent_blue'])

    def apply_layout(self, layout, resize=False):
        """Place the team tables side by side ('horizontal') or stacked ('vertical')"""
        if layout not in self.LAYOUT_SIZES:
            layout = 'horizontal'
        self.layout = layout
        frame = self.players_frame

        self.attackers_frame.grid_forget()
        self.defenders_frame.grid_forget()
        if layout == 'horizontal':
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_rowconfigure(1, weight=0)
            frame.grid_columnconfigure(0, weight=1, uniform='team')
            frame.grid_columnconfigure(1, weight=1, uniform='team')
            self.attackers_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
            self.defenders_frame.grid(row=0, column=1, sticky='nsew', padx=(6, 0))
        else:
            frame.grid_rowconfigure(0, weight=1, uniform='team')
            frame.grid_rowconfigure(1, weight=1, uniform='team')
            frame.grid_columnconfigure(0, weight=1, uniform='')
            frame.grid_columnconfigure(1, weight=0, uniform='')
            self.attackers_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 6))
            self.defenders_frame.grid(row=1, column=0, sticky='nsew', pady=(6, 0))

        if layout == 'horizontal':
            self.footer_hint.pack(side=tk.RIGHT)
        else:
            self.footer_hint.pack_forget()

        (width, height), (min_w, min_h) = self.LAYOUT_SIZES[layout]
        self.root.minsize(min_w, min_h)
        if resize and self.root.state() != 'zoomed':
            height = min(height, self.root.winfo_screenheight() - 80)
            if self.root.winfo_ismapped():
                self.root.geometry(f"{width}x{height}+{max(self.root.winfo_x(), 0)}+{max(self.root.winfo_y(), 0)}")
            else:
                self.root.geometry(f"{width}x{height}")

        self._draw_layout_icon()

    def toggle_layout(self):
        """Switch between side-by-side and stacked team tables"""
        new_layout = 'vertical' if self.layout == 'horizontal' else 'horizontal'
        self.apply_layout(new_layout, resize=True)
        self.settings['layout'] = new_layout
        try:
            self.save_settings()
        except Exception as e:
            self.logger.warning(f"Could not save layout setting: {e}")

    def setup_team_table(self, parent, team_name, accent_color):
        """Team panel: coloured banner and one card per player"""
        board = TeamBoard(parent, self.colors, team_name, accent_color,
                          on_hover=self._on_row_hover, on_leave=self._hide_row_tooltip,
                          on_open=self.on_player_double_click)
        board.pack(fill=tk.BOTH, expand=True)

        if team_name == "Attackers":
            self.attackers_board = board
        else:
            self.defenders_board = board
        self.show_empty_state(board, "Waiting for match data...")

    def show_empty_state(self, board, message):
        """Clear a team panel and show a muted message"""
        board.set_rows([], message)

    def set_team_header(self, team, count, state=None):
        """Update a team's player count; state 'yours' or 'enemy' colours the banner"""
        board = self.attackers_board if team == 'attackers' else self.defenders_board
        board.set_banner(count, state)

    def setup_session_footer(self, parent):
        """Footer with session count, legend and version"""
        footer_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        tk.Frame(parent, bg=self.colors['border'], height=1).pack(fill=tk.X, side=tk.BOTTOM)

        footer_content = tk.Frame(footer_frame, bg=self.colors['bg_secondary'])
        footer_content.pack(fill=tk.BOTH, expand=True, padx=16)

        label_opts = {'font': (self.font_regular, 8), 'bg': self.colors['bg_secondary']}

        legend = (("★  You", self.colors['you']),
                  ("▌ Incognito", self.colors['hidden_indicator']),
                  ("▌ Party  (dashed = likely)", self.colors['ally']),
                  ("⚠  Possible smurf", self.colors['warning']),
                  ("↺  Met before", self.colors['text_secondary']))
        for text, color in legend:
            tk.Label(footer_content, text=text, fg=color, **label_opts).pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(footer_content, text="v2.2", fg=self.colors['text_muted'], **label_opts).pack(side=tk.RIGHT)
        self.footer_hint = tk.Label(footer_content, text="Hover a player for details  ·  Double-click opens Tracker.gg   ",
                                    fg=self.colors['text_muted'], **label_opts)
        self.footer_hint.pack(side=tk.RIGHT)

    def setup_tooltips(self):
        """Tooltips and keyboard shortcuts"""
        self.create_tooltip(self.refresh_btn, "Refresh current match (F5)")
        self.create_tooltip(self.load_stats_btn, "Load rank, peak, win rate, K/D and HS% for all players\nAuto mode does this for you")
        self.create_tooltip(self.auto_btn, lambda: "Auto mode is on: detects agent select and matches,\nthen loads stats automatically. Click to turn off."
                            if self.auto_mode else "Auto mode is off: use Refresh and Load Stats.\nClick to turn on.")
        self.create_tooltip(self.status_label, "Connection status to the Valorant client")
        self.create_tooltip(self.layout_btn, lambda: "Switch to stacked layout (Ctrl+L)" if self.layout == 'horizontal'
                            else "Switch to side-by-side layout (Ctrl+L)")

        self.root.bind('<F5>', lambda e: self.refresh_match())
        self.root.bind('<Control-r>', lambda e: self.refresh_match())
        self.root.bind('<Control-l>', lambda e: self.toggle_layout())
        self.root.bind('<Escape>', lambda e: self.on_closing())

    def create_tooltip(self, widget, text):
        """Show a tooltip while hovering a widget; text may be a string or a function returning one"""
        def show_tooltip(event):
            hide_tooltip(event)
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+12}+{event.y_root+14}")
            tk.Label(tooltip, text=text() if callable(text) else text,
                     background=self.colors['bg_elevated'],
                     foreground=self.colors['text_primary'],
                     justify=tk.LEFT,
                     font=('Segoe UI', 9),
                     padx=10, pady=6).pack()
            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')

        widget.bind('<Enter>', show_tooltip, add='+')
        widget.bind('<Leave>', hide_tooltip, add='+')
        widget.bind('<Button-1>', hide_tooltip, add='+')

    def add_button_hover_effect(self, button, normal_bg, hover_bg, normal_fg=None, hover_fg=None):
        """Change button colours on hover (skipped while disabled)"""
        def on_enter(e):
            if str(button['state']) == tk.DISABLED:
                return
            button['background'] = hover_bg
            if hover_fg:
                button['foreground'] = hover_fg

        def on_leave(e):
            button['background'] = normal_bg
            if normal_fg:
                button['foreground'] = normal_fg

        button.bind('<Enter>', on_enter, add='+')
        button.bind('<Leave>', on_leave, add='+')

    def update_footer_stats(self, player_count=0, hidden_count=0):
        """Update player counts in the match strip and session count in the footer"""
        matches = self.session_stats['matches_detected']
        self.match_session_value.config(text=f"{matches} match{'es' if matches != 1 else ''}")
        self.match_players_value.config(text=str(player_count),
                                        fg=self.colors['text_primary'] if player_count else self.colors['text_secondary'])
        self.match_hidden_value.config(text=str(hidden_count),
                                       fg=self.colors['hidden_indicator'] if hidden_count else self.colors['text_secondary'])

    def on_resize(self, event):
        """Handle window resize (grid handles the table layout)"""
        pass

    def log(self, message, level="Info"):
        """Simplified logging - console and file only"""
        # Log to file system
        clean_message = message.replace('🔗', '').replace('✅', '').replace('❌', '').replace('⚠️', '').strip()
        
        if level == "Error":
            self.logger.error(clean_message)
        elif level == "Warning":
            self.logger.warning(clean_message)
        else:
            self.logger.info(clean_message)
        
        # Also print to console for debugging
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def connect_client(self):
        def connect():
            start_time = time.time()
            self.logger.info("🔌 Starting Valorant client connection...")
            
            try:
                if not self.settings['ran']:
                    # First time setup
                    self.logger.info("🆕 First time setup detected")
                    region = self.ask_region()
                    if not region:
                        self.logger.warning("❌ Region selection cancelled")
                        return
                    
                    self.settings['region'] = region
                    self.settings['ran'] = True
                    self.save_settings()
                    self.logger.info(f"✅ Region set to: {region}")
                
                self.log(f"Connecting to Valorant client (Region: {self.settings['region']})...")
                self.logger.info(f"🌍 Connecting to region: {self.settings['region']}")
                
                self.client = Client(region=self.settings['region'])
                self.client.activate()
                
                connection_time = time.time() - start_time
                self.logger_system.log_performance_metric("Connection Time", f"{connection_time:.2f}", "s")
                
                # Test connection
                try:
                    test_start = time.time()
                    test_data = self.client.fetch_presence(self.client.puuid)
                    test_time = time.time() - test_start
                    
                    self.log("Connection test successful")
                    self.logger.info(f"✅ Connection test successful (PUUID: {self.client.puuid[:8]}...)")
                    self.logger_system.log_performance_metric("Connection Test", f"{test_time:.2f}", "s")
                    
                except Exception as e:
                    self.log(f"Connection test failed: {str(e)}", "Warning")
                    self.log("This is normal if you're not in a match yet")
                    self.logger.warning(f"⚠️ Connection test failed: {str(e)}")
                
                # Update UI
                self.root.after(0, self.update_connection_status, "Connected", "#28a745")
                self.root.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
                
                self._connect_failures = 0
                self.log("Successfully connected to Valorant client!")

                self.logger.info("🎯 Valorant client connection established successfully")
                self.logger_system.log_gui_action("Client Connected", f"Region: {self.settings['region']}")

                # Rebind Valorant API client with live valclient so direct PD API is enabled
                try:
                    from valorant_api_client import init_valorant_api
                    init_valorant_api(self.settings.get('henrikApiKey'), valclient=self.client)
                    self.logger.debug("🔁 Rebound Valorant API client with active valclient (Direct PD API enabled)")
                except Exception as rebind_err:
                    self.logger.debug(f"Could not rebind API client: {rebind_err}")
                
                # Try to get current match immediately
                if self.auto_mode:
                    self.start_monitoring()
                else:
                    self.refresh_match()

            except Exception as e:
                self._connect_failures += 1
                if self.auto_mode:
                    # Keep trying so the app can be started before Valorant
                    self.root.after(10000, self.connect_client)
                    self.root.after(0, self.update_connection_status, "Waiting for Valorant", None)
                if self._connect_failures > 1:
                    return  # Already reported

                connection_time = time.time() - start_time
                self.logger_system.log_error("Connection", e, f"Region: {self.settings.get('region', 'Unknown')}")
                self.logger_system.log_performance_metric("Failed Connection Time", f"{connection_time:.2f}", "s")
                
                self.log(f"Connection failed: {str(e)}", "Error")
                if not self.auto_mode:
                    self.root.after(0, self.update_connection_status, "Disconnected", "#ff6b6b")
                
                # Clear match data to show proper disconnected state
                self.root.after(0, self.set_disconnected_state)
                
                # More specific error messages
                error_msg = str(e).lower()
                if "lockfile" in error_msg:
                    suggestion = "Make sure Valorant is running and you're logged in."
                elif "connection" in error_msg:
                    suggestion = "Check if Valorant is fully loaded and try again."
                else:
                    suggestion = "Make sure Valorant is running."
                
                self.logger.error(f"💥 Connection failed: {suggestion}")
                self.log(f"Suggestion: {suggestion}")
        
        threading.Thread(target=connect, daemon=True).start()
    
    def update_connection_status(self, status, color):
        """Update status pill and button states"""
        connected = status == "Connected"
        if connected:
            dot_color = self.colors['success']
        elif status.startswith("Waiting"):
            dot_color = self.colors['warning']
        else:
            dot_color = self.colors['danger']
        self.status_dot.itemconfig('dot', fill=dot_color)
        self.status_label.config(text=status, fg=self.colors['text_primary'] if connected else self.colors['text_secondary'])
        self.refresh_btn.config(state=tk.NORMAL if connected else tk.DISABLED)

    def set_disconnected_state(self):
        """Set UI to proper disconnected state"""
        self.match_status_value.config(text="WAITING FOR CONNECTION", fg=self.colors['text_secondary'])
        self.match_map_value.config(text="—", fg=self.colors['text_secondary'])

        self.show_empty_state(self.attackers_board, "Waiting for match data...")
        self.show_empty_state(self.defenders_board, "Waiting for match data...")
        self.set_team_header('attackers', 0)
        self.set_team_header('defenders', 0)
        self.update_footer_stats(0, 0)

    def ask_region(self):
        """Professional region selection dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Region")
        dialog.geometry("420x340")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        result = [None]
        
        # Header with gradient feel
        header = tk.Frame(dialog, bg=self.colors['bg_secondary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['bg_secondary'])
        header_content.pack(expand=True)
        
        tk.Label(header_content, text="🌍", 
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary'], 
                font=('Segoe UI', 20)).pack()
        
        tk.Label(header_content, text="Select Your Region", 
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary'], 
                font=('Segoe UI', 16, 'bold')).pack()
        
        # Content
        content = tk.Frame(dialog, bg=self.colors['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=35, pady=25)
        
        tk.Label(content, text="Choose your Valorant server region:", 
                bg=self.colors['bg_primary'], 
                fg=self.colors['text_secondary'], 
                font=('Segoe UI', 10)).pack(pady=(0, 15))
        
        regions = [
            ("🌎 North America", "na"), 
            ("🌍 Europe", "eu"), 
            ("🌏 Asia Pacific", "ap"), 
            ("🇰🇷 Korea", "kr")
        ]
        
        var = tk.StringVar(value="na")
        
        # Create radio buttons with better spacing
        for text, value in regions:
            rb_frame = tk.Frame(content, bg=self.colors['bg_card'], 
                               relief=tk.FLAT, height=35)
            rb_frame.pack(fill=tk.X, pady=4)
            rb_frame.pack_propagate(False)
            
            rb = tk.Radiobutton(rb_frame, text=text, variable=var, value=value,
                          bg=self.colors['bg_card'], 
                          fg=self.colors['text_primary'],
                          selectcolor=self.colors['bg_elevated'],
                          activebackground=self.colors['bg_card'],
                          activeforeground=self.colors['accent_blue'],
                          font=('Segoe UI', 11),
                          relief=tk.FLAT,
                          indicatoron=True)
            rb.pack(side=tk.LEFT, padx=12, pady=5)
        
        def ok():
            result[0] = var.get()
            dialog.destroy()
        
        # Confirm button with hover effect
        confirm_btn = tk.Button(content, text="✓ CONFIRM", command=ok, 
                 bg=self.colors['accent_blue'], fg='white',
                 activebackground='#2563eb',
                 font=('Segoe UI', 11, 'bold'),
                 relief=tk.FLAT, padx=35, pady=13,
                 cursor='hand2')
        confirm_btn.pack(pady=(20, 0))
        
        self.add_button_hover_effect(confirm_btn, 
                                     self.colors['accent_blue'], 
                                     '#2563eb')
        
        # Keyboard shortcut
        dialog.bind('<Return>', lambda e: ok())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        dialog.wait_window()
        return result[0]
    
    def refresh_match(self):
        """Manually reload the current match with fresh rank data"""
        if not self.client:
            self.log("Not connected to Valorant client", "Error")
            return

        def refresh():
            try:
                self.log("Refreshing match information...")

                try:
                    from valorant_api_client import get_valorant_api
                    api_client = get_valorant_api()
                    if api_client:
                        api_client.invalidate_mmr_cache()
                except Exception as e:
                    self.logger.debug(f"Could not invalidate cache: {e}")

                self.handle_match_state(*self._fetch_current_match(), force=True)
            except Exception as e:
                self.log(f"Error refreshing match: {str(e)}", "Error")

        threading.Thread(target=refresh, daemon=True).start()

    def _fetch_current_match(self):
        """Return (match_info, match_id, phase) for agent select or a live match, else (None, None, None)"""
        try:
            pregame_player = self.client.pregame_fetch_player()
            if pregame_player and 'MatchID' in pregame_player:
                return self.client.pregame_fetch_match(), pregame_player['MatchID'], 'PREGAME'
        except Exception:
            pass

        try:
            coregame_player = self.client.coregame_fetch_player()
            if coregame_player and 'MatchID' in coregame_player:
                return self.client.coregame_fetch_match(), coregame_player['MatchID'], 'INGAME'
        except Exception:
            pass

        return None, None, None

    def handle_match_state(self, match_info, match_id, phase, force=False):
        """Update the UI when the match or phase changes (always when force is set)"""
        with self._match_lock:
            key = (match_id, phase)
            if key == self._last_match_key and not force:
                return
            self._last_match_key = key

            if force:
                # Keep the Player objects so names resolved during agent select
                # survive a Refresh; only the stats are dropped and re-fetched
                for player in self._player_cache.values():
                    player.stats_loaded = False
                    player.riot_stats_loaded = False
                    player.match_stats_loaded = False
                    player.stats = None
                self._stats_attempted.clear()
                self._match_stats_attempted.clear()

            if not match_info:
                # Back in the menus: forget this lobby
                self._current_match_id = None
                self._lobby_match_ids = set()
                self._player_cache = {}
                self._current_players = []
                self.log("No active match found")
                self.root.after(0, self.clear_match_data)
                return

            self.process_match_data(match_info, match_id, phase)

        if self.auto_mode:
            self.fetch_player_stats_background()

    def process_match_data(self, match_info, match_id, session_state):
        process_start = time.time()

        try:
            map_name = self.get_map_name(match_info.get('MapID', 'Unknown'))
            self.current_game = Game(match_id, map_name, session_state)
            previous_phase = self._current_phase
            self._current_phase = session_state
            self._refresh_known_names()

            players_list = extract_players(match_info)
            hidden_count = sum(1 for p in players_list if p.get('PlayerIdentity', {}).get('Incognito', False))

            if match_id != self._current_match_id:
                self._current_match_id = match_id
                self._lobby_match_ids.add(match_id)
                self._stats_attempted = set()
                self._match_stats_attempted = set()
                self.session_stats['matches_detected'] += 1
                self.session_stats['hidden_players_found'] += hidden_count
                self.logger_system.log_match_detection(match_id, map_name, len(players_list), hidden_count)

            self.root.after(0, lambda: self.update_match_status(session_state, map_name))

            players = self.process_players(players_list)
            self.current_game.players = players
            self._load_party_info(players)
            self._load_encounters(players)

            self._current_players = players
            self.root.after(0, self._update_player_display)
            self.root.after(0, lambda: self.load_stats_btn.config(state=tk.NORMAL))

            process_time = time.time() - process_start
            self.logger_system.log_performance_metric("Match Processing", f"{process_time:.2f}", "s")
            if session_state == 'INGAME' and previous_phase == 'PREGAME':
                self.log(f"Loading screen - opponents revealed ({map_name})")
            else:
                self.log(f"Match data updated - {map_name} ({session_state})")

            self.save_match_to_history(match_id, map_name, players)

        except Exception as e:
            self.logger_system.log_error("MatchProcessing", e, f"Match ID: {match_id}")
            self.log(f"Error processing match data: {str(e)}", "Error")

    def update_match_status(self, status, map_name):
        """Update match status strip"""
        phase = status.upper()
        if "INGAME" in phase:
            status_display, color = "In Game", self.colors['success']
        elif "PREGAME" in phase:
            status_display, color = "Agent Select", self.colors['warning']
        elif phase == "WAITING":
            status_display, color = "Waiting", self.colors['text_secondary']
        else:
            status_display, color = status.title(), self.colors['text_secondary']

        self.match_status_value.config(text=status_display.upper(), fg=color)
        self.match_map_value.config(text=map_name.upper(), fg=self.colors['text_primary'])

    def _is_me(self, puuid):
        return bool(self.client and puuid and puuid.lower() == self.client.puuid.lower())

    def _fetch_names(self, puuids):
        """Riot IDs for many players in one request — include all resolved names"""
        try:
            entries = self.client.put(endpoint="/name-service/v2/players", endpoint_type="pd", json_data=puuids)
            names = {}
            for e in entries:
                gn = (e.get('GameName') or '').strip()
                tl = (e.get('TagLine') or '').strip()
                if gn:
                    names[e['Subject'].lower()] = f"{gn}#{tl or '0000'}"
            return names
        except Exception as e:
            self.logger.debug(f"Batch name lookup failed: {e}")
            return {}

    def _refresh_known_names(self):
        """Rebuild the names you already hold, from your saved matches and friends list"""
        friends = []
        try:
            friends = friend_names(self.client.rnet_fetch_all_friends())
        except Exception as e:
            self.logger.debug(f"Could not read friends list: {e}")
        self._known_names = build_name_ledger(self.match_history.matches, friends)

    def _apply_known_name(self, player):
        """Reuse a Riot ID you already hold for this puuid; never asks Riot for a name it withheld"""
        entry = self._known_names.get(player.puuid)
        if not entry:
            return False

        name, _, tag = entry['name'].partition('#')
        player.name = player.filter_name(name)
        player.tag = tag or '0000'
        player.full_name = f"{player.name}#{player.tag}"
        player.privacy_hidden = False
        player.name_source = entry['source']
        player.name_timestamp = entry['timestamp']
        player.possibleNames = player.find_possible_names()
        return True

    def process_players(self, players_list):
        """Create Player objects (reusing ones from agent select) with you first"""
        players = []
        new_puuids = [p['Subject'] for p in players_list if p['Subject'].lower() not in self._player_cache]
        names = self._fetch_names(new_puuids) if new_puuids else {}
        
        for player_data in players_list:
            try:
                puuid = player_data['Subject'].lower()
                identity = player_data.get('PlayerIdentity', {})
                player = self._player_cache.get(puuid)

                if player is None:
                    player = Player(
                        client=self.client,
                        puuid=puuid,
                        agentID=(player_data.get('CharacterID') or '').lower(),
                        incognito=identity.get('Incognito', False),
                        team=player_data.get('TeamID'),
                        account_level=identity.get('AccountLevel', 0),
                        level_hidden=identity.get('HideAccountLevel', False),
                        display_name=names.get(puuid)
                    )
                    if self._is_me(puuid) and not player.player_level:
                        player.player_level = self._fetch_own_level()
                    self._player_cache[puuid] = player
                else:
                    player.agent = game_data.get_agent_name(player_data.get('CharacterID'), player.agent)
                    player.team = player.side(player_data.get('TeamID'))
                    # Re-resolve names for players whose name we couldn't get before
                    if getattr(player, 'privacy_hidden', False):
                        old = player.full_name
                        full = player.set_name(puuid)
                        if '#' in full and full != "Unknown#0000":
                            parts = full.split('#')
                            player.name = player.filter_name(parts[0])
                            player.tag = parts[1] if len(parts) > 1 else "0000"
                            player.full_name = f"{player.name}#{player.tag}"
                            player.is_hidden = player.incognito or player.privacy_hidden or player.name.startswith('Player_')
                            if old != player.full_name:
                                self.log(f"Resolved incognito name: {player.full_name}")

                if player.privacy_hidden and self._apply_known_name(player):
                    where = "friends list" if player.name_source == 'friend' else "saved matches"
                    self.log(f"{player.full_name} known from your {where}")

                if self._is_me(puuid):
                    players.insert(0, player)
                else:
                    players.append(player)

            except Exception as e:
                self.log(f"Error processing player: {str(e)}", "Warning")

        return players

    def _fetch_own_level(self):
        """Your own account level (the match data hides it when you hide your level)"""
        try:
            from valorant_api_client import riot_get
            status, data = riot_get(self.client, f"/account-xp/v1/players/{self.client.puuid}")
            return (data or {}).get('Progress', {}).get('Level', 0) if status == 200 else 0
        except Exception as e:
            self.logger.debug(f"Could not fetch own account level: {e}")
            return 0
    
    @staticmethod
    def _display_name(player):
        """Riot ID, or 'Hidden player (Agent)' when Riot withheld the name"""
        if getattr(player, 'privacy_hidden', False):
            agent = player.agent if player.agent and player.agent != "Unknown" else None
            return f"Hidden player ({agent})" if agent else "Hidden player"
        return player.full_name
    
    def _load_party_info(self, players):
        """Find who queued together from the chat presences the client can see (you and friends)"""
        try:
            presences = self.client.fetch_all_friend_presences()
            self._presence_parties = presence_parties(presences, [p.puuid for p in players])
        except Exception as e:
            self._presence_parties = []
            self.logger.debug(f"Could not load party info: {e}")
        self._recompute_parties(players)

    def _recompute_parties(self, players=None):
        """Combine presence parties with players who partied together in their recent matches"""
        players = players if players is not None else list(self._current_players)
        links = [(p.puuid, partner) for p in players for partner in getattr(p, 'recent_party_partners', ())]
        self._party_numbers, self._confirmed_party = number_parties(
            self._presence_parties, links, [p.puuid for p in players], self.client.puuid if self.client else None)

    def _load_encounters(self, players):
        """Look up earlier matches with these players in the saved match history"""
        me = next((p for p in players if self._is_me(p.puuid)), None)
        self._encounters = {
            p.puuid: find_encounters(self.match_history.matches, p.puuid, p.full_name if not p.full_name.startswith('Player_') else '',
                                     self._lobby_match_ids, self.client.puuid, me.full_name if me else None)
            for p in players if not self._is_me(p.puuid)
        }

    def load_player_stats_manual(self):
        """Manually load stats when user clicks the button (retries players that failed)"""
        if self._current_players:
            self._stats_attempted -= {p.puuid for p in self._current_players if not p.stats_loaded}
            self._match_stats_attempted -= {p.puuid for p in self._current_players if not p.match_stats_loaded}
            self.fetch_player_stats_background()
        else:
            self.log("No players to load stats for. Refresh the match first.")

    def fetch_player_stats_background(self):
        """Load stats for current players that don't have them yet, one at a time, updating the table as it goes"""
        with self._stats_lock:
            if self._stats_loading:
                return  # The running loader picks up new players
            self._stats_loading = True

        self.root.after(0, lambda: self.load_stats_btn.config(state=tk.DISABLED, text="Loading..."))

        def fetch_stats():
            loaded = 0
            while True:
                # Ranks for everyone come first (fast); K/D and HS% afterwards (slower)
                with self._stats_lock:
                    players = list(self._current_players)
                    rank_pending = [p for p in players
                                    if not p.stats_loaded and p.puuid not in self._stats_attempted]
                    match_pending = [p for p in players if p.stats_loaded and not p.match_stats_loaded
                                     and p.puuid not in self._match_stats_attempted]
                    if not rank_pending and not match_pending:
                        self._stats_loading = False
                        break
                    if rank_pending:
                        player, rank_pass = rank_pending[0], True
                        self._stats_attempted.add(player.puuid)
                    else:
                        player, rank_pass = match_pending[0], False
                        self._match_stats_attempted.add(player.puuid)

                try:
                    if rank_pass:
                        self.logger.info(f"📊 Fetching rank for {player.name}...")
                        player.get_competitive_stats(include_match_stats=False)
                        if player.stats_loaded:
                            loaded += 1
                    else:
                        player.load_match_stats()
                        self._recompute_parties()
                except Exception as e:
                    self.logger.warning(f"Could not fetch stats for {player.name}: {e}")

                self.root.after(0, self._update_player_display)

            self.root.after(0, lambda: self.load_stats_btn.config(state=tk.NORMAL, text="Load Stats"))
            self.log(f"Stats loading complete ({loaded} players)")

        threading.Thread(target=fetch_stats, daemon=True).start()

    def _update_player_display(self):
        """Update player display in main thread"""
        self.display_players_in_tables(self._current_players)

    def display_players_in_tables(self, players):
        """Display players in the appropriate team panels"""
        attackers = [p for p in players if p.team == "Attacking"]
        defenders = [p for p in players if p.team == "Defending"]
        hidden_count = sum(1 for p in players if p.incognito)

        for player in players:
            if player.team not in ("Attacking", "Defending"):
                self.logger.warning(f"  ⚠️ Player {player.full_name} has unknown team: {player.team}")

        mine_attacking = any(self._is_me(p.puuid) for p in attackers)
        mine_defending = any(self._is_me(p.puuid) for p in defenders)
        known = mine_attacking or mine_defending
        self.set_team_header('attackers', len(attackers),
                             'yours' if mine_attacking else ('enemy' if known else None))
        self.set_team_header('defenders', len(defenders),
                             'yours' if mine_defending else ('enemy' if known else None))
        self.update_footer_stats(len(players), hidden_count)

        self._hide_row_tooltip()
        # Riot only lists your own team until the loading screen, so an empty side
        # during agent select means "not revealed yet", not "nobody picked that side"
        waiting = self._current_phase == 'PREGAME'
        for board, team_players, empty_text in ((self.attackers_board, attackers,
                                                 "Opponents appear at the loading screen" if waiting else "No attackers yet"),
                                                (self.defenders_board, defenders,
                                                 "Opponents appear at the loading screen" if waiting else "No defenders yet")):
            ordered = self._group_by_party(team_players)
            board.set_rows([self._row_data(p, ordered) for p in ordered], empty_text)

        self.session_stats['players_scanned'] = len(players)
        self.logger.info(f"✅ Displayed {len(attackers)} attackers and {len(defenders)} defenders")

    def _group_by_party(self, team_players):
        """Keep the order (you first) but move party members next to each other"""
        first_seen = {}
        for index, player in enumerate(team_players):
            first_seen.setdefault(self._party_numbers.get(player.puuid) or ('solo', index), index)
        return sorted(team_players, key=lambda p: (
            first_seen[self._party_numbers.get(p.puuid) or ('solo', team_players.index(p))],
            team_players.index(p)))

    @staticmethod
    def _rank_text(rank, empty="—"):
        return rank if rank and rank != "Unranked" else empty

    def _stats_pending(self, player):
        """Rank stats will still be loaded for this player (auto mode or a running Load Stats)"""
        loading = self.auto_mode or self._stats_loading
        return loading and not player.stats_loaded and player.puuid not in self._stats_attempted

    def _match_stats_pending(self, player):
        loading = self.auto_mode or self._stats_loading
        return loading and not getattr(player, 'match_stats_loaded', False) and (
            self._stats_pending(player) or
            (player.stats_loaded and player.puuid not in self._match_stats_attempted))

    def _row_data(self, player, team_players):
        """Everything the team panel draws for one player"""
        is_you = self._is_me(player.puuid)
        if getattr(player, 'privacy_hidden', False):
            name, tag = "HIDDEN PLAYER", ""
        else:
            name, _, tag = player.full_name.partition('#')
            name = name.upper()

        level = getattr(player, 'player_level', 0) or 0
        level_hidden = not level and getattr(player, 'level_hidden', False)

        # Win rate and headshot rate are stored as fractions (0.55) by the stats APIs
        win_rate = getattr(player, 'win_rate', 0) or 0
        if 0 < win_rate <= 1:
            win_rate *= 100
        headshots = getattr(player, 'headshot_rate', 0) or 0
        if 0 < headshots <= 1:
            headshots *= 100
        kd = getattr(player, 'kd_ratio', 0) or 0

        # "…" = still loading, "—" = no data
        rank_none = "…" if self._stats_pending(player) else "—"
        match_none = "…" if self._match_stats_pending(player) else "—"

        party = None
        number = self._party_numbers.get(player.puuid)
        if number:
            size = sum(1 for p in team_players if self._party_numbers.get(p.puuid) == number)
            party = (number, player.puuid in self._confirmed_party, size)

        marks, _ = self._player_insights(player)
        agent = player.agent if player.agent and player.agent != "Unknown" else "—"
        return {
            'player': player,
            'name': name,
            'tag': tag,
            'agent': agent.upper(),
            'kind': 'you' if is_you else ('incognito' if player.incognito else 'normal'),
            'rank': self._rank_text(getattr(player, 'current_rank', None), rank_none),
            'peak': self._rank_text(getattr(player, 'peak_rank', None), rank_none),
            'level': str(level) if level > 0 else ("hidden" if level_hidden else "—"),
            'level_muted': not level,
            'win': (f"{win_rate:.0f}%", win_rate) if win_rate > 0 else (rank_none, None),
            'kd': (f"{kd:.2f}", kd) if kd > 0 else (match_none, None),
            'hs': (f"{headshots:.0f}%", headshots) if headshots > 0 else (match_none, None),
            'info': marks,
            'party': party,
        }

    def _player_insights(self, player):
        """Return (INFO column marks as (text, colour), detail lines for the hover tooltip)"""
        marks, lines = [], []

        party = self._party_numbers.get(player.puuid)
        if party:
            mates = [self._display_name(p) for p in self._current_players
                     if p is not player and self._party_numbers.get(p.puuid) == party]
            label = PARTY_LABELS.get(len(mates) + 1, "Party").title()
            if player.puuid in self._confirmed_party:
                lines.append(f"▌ {label}  ·  queued with {', '.join(mates)}")
            else:
                lines.append(f"▌ Likely {label.lower()}  ·  partied with {', '.join(mates)} in recent matches")

        if not self._is_me(player.puuid):
            if getattr(player, 'stats_loaded', False):
                win_rate = player.win_rate if player.win_rate <= 1 else player.win_rate / 100
                reasons = smurf_reasons(player.player_level, player.current_rank, player.peak_rank, win_rate,
                                        player.matches_played, player.kd_ratio, getattr(player, 'recent_matches', 0))
                if reasons:
                    marks.append(("⚠", self.colors['warning']))
                    lines.extend(f"⚠  {reason}" for reason in reasons)

            encounters = self._encounters.get(player.puuid)
            if encounters:
                marks.append((f"↺ {len(encounters)}×", self.colors['text_secondary']))
                lines.append(f"↺  {describe_encounters(encounters)}")

        if player.incognito and not self._is_me(player.puuid):
            source = getattr(player, 'name_source', None)
            if source == 'friend':
                lines.append("●  Incognito in-game — on your friends list")
            elif source == 'match':
                lines.append(f"●  Incognito in-game — name from your saved matches "
                             f"({time_ago(getattr(player, 'name_timestamp', ''))})")
            elif getattr(player, 'privacy_hidden', False):
                lines.append("●  Incognito — Riot does not expose this name")
            else:
                lines.append("●  Incognito mode enabled")

        return marks, lines

    def _on_row_hover(self, player, event):
        """Show party, smurf and history details for the player under the mouse"""
        if player is getattr(self, '_tooltip_row', None):
            if getattr(self, '_row_tooltip', None):
                self._row_tooltip.wm_geometry(f"+{event.x_root + 16}+{event.y_root + 18}")
            return

        self._hide_row_tooltip()
        self._tooltip_row = player
        if not player:
            return
        _, lines = self._player_insights(player)
        if not lines:
            return

        tooltip = tk.Toplevel(self.root)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 16}+{event.y_root + 18}")
        frame = tk.Frame(tooltip, bg=self.colors['bg_elevated'],
                         highlightthickness=1, highlightbackground=self.colors['border_light'])
        frame.pack()
        tk.Label(frame, text=self._display_name(player), font=(self.font_semibold, 9),
                 bg=self.colors['bg_elevated'], fg=self.colors['text_primary']).pack(anchor='w', padx=10, pady=(7, 2))
        for line in lines:
            color = self.colors['warning'] if line.startswith("⚠") else self.colors['text_secondary']
            tk.Label(frame, text=line, font=(self.font_regular, 9), justify=tk.LEFT,
                     bg=self.colors['bg_elevated'], fg=color).pack(anchor='w', padx=10)
        tk.Frame(frame, bg=self.colors['bg_elevated'], height=6).pack()
        self._row_tooltip = tooltip

    def _hide_row_tooltip(self):
        if getattr(self, '_row_tooltip', None):
            self._row_tooltip.destroy()
        self._row_tooltip = None
        self._tooltip_row = None

    def on_player_double_click(self, player):
        """Open the player's Tracker.gg profile (not possible without a Riot ID)"""
        if player and not getattr(player, 'privacy_hidden', False) and not player.full_name.startswith('Player_'):
            self.open_tracker_link(player.full_name)

    def open_tracker_link(self, player_name):
        """Open Tracker.gg profile for player"""
        try:
            raw = player_name.strip()
            encoded_name = urllib.parse.quote(raw)
            url = f"https://tracker.gg/valorant/profile/riot/{encoded_name}/overview"

            webbrowser.open(url)
            self.log(f"Opened Tracker.gg for {raw}")

        except Exception as e:
            self.log(f"Error opening Tracker.gg: {str(e)}", "Error")

    def _update_auto_button(self):
        if self.auto_mode:
            self.auto_btn.config(text="●  Auto", fg=self.colors['success'], activeforeground=self.colors['success'])
        else:
            self.auto_btn.config(text="○  Auto", fg=self.colors['text_secondary'], activeforeground=self.colors['text_secondary'])

    def toggle_monitoring(self):
        """Turn auto mode on or off"""
        self.auto_mode = not self.auto_mode
        self._update_auto_button()
        self.settings['autoMode'] = self.auto_mode
        try:
            self.save_settings()
        except Exception as e:
            self.logger.warning(f"Could not save auto mode setting: {e}")

        if self.auto_mode:
            self.log("Auto mode on")
            if self.client:
                self.start_monitoring()
            else:
                self.connect_client()
        else:
            self.log("Auto mode off")

    def start_monitoring(self):
        """Poll the client and update whenever agent select or a match starts or ends"""
        if self._monitor_running:
            return
        self._monitor_running = True

        def monitor():
            try:
                while self.auto_mode and self.client:
                    interval = max(2, self.settings.get('stateInterval', 5))
                    try:
                        match_info, match_id, phase = self._fetch_current_match()
                        # Agent select is short and the opponents only appear for a
                        # few seconds at the loading screen, so watch closely there
                        if phase == 'PREGAME':
                            interval = 1
                        self.handle_match_state(match_info, match_id, phase)
                    except Exception as e:
                        self.log(f"Monitoring error: {str(e)}", "Error")
                    time.sleep(interval)
            finally:
                self._monitor_running = False

        threading.Thread(target=monitor, daemon=True).start()

    def clear_match_data(self):
        self._current_phase = None
        self.match_status_value.config(text="NO ACTIVE MATCH", fg=self.colors['text_secondary'])
        self.match_map_value.config(text="—", fg=self.colors['text_secondary'])

        self.show_empty_state(self.attackers_board, "No active match")
        self.show_empty_state(self.defenders_board, "No active match")
        self.set_team_header('attackers', 0)
        self.set_team_header('defenders', 0)
        self.update_footer_stats(0, 0)

    def get_map_name(self, map_id):
        """Convert map ID to readable name"""
        return game_data.get_map_name(map_id)
    
    def save_match_to_history(self, match_id, map_name, players):
        """Save (or update) this match in the match history"""
        try:
            def team_color(player):
                return {'Attacking': 'Red', 'Defending': 'Blue'}.get(player.team, player.team)

            players_data = [{
                'puuid': p.puuid,
                'name': p.full_name if not p.full_name.startswith('Player_') else '',
                'agent': p.agent,
                'team': team_color(p),
                'hidden': p.incognito,
                'streaming_platforms': [],
                'social_platforms': []
            } for p in players]

            me = next((p for p in players if self._is_me(p.puuid)), None)
            self.match_history.upsert_match(match_id, map_name, players_data, team_color(me) if me else None)

        except Exception as e:
            self.log(f"Error saving match to history: {str(e)}", "Warning")

    def show_statistics(self):
        """Show statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Match Statistics")
        stats_window.geometry("600x500")
        stats_window.configure(bg='#f5f5f5')
        stats_window.transient(self.root)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Streamer stats tab
        streamer_frame = tk.Frame(notebook, bg='white')
        notebook.add(streamer_frame, text="Streamers")
        
        streamer_stats = self.match_history.get_streamer_stats()
        
        streamer_text = scrolledtext.ScrolledText(streamer_frame, bg='white', fg='#333333',
                                                font=('Consolas', 10), wrap=tk.WORD)
        streamer_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        streamer_info = f"""📊 STREAMER STATISTICS
{'='*50}
Total Matches: {streamer_stats['total_matches']}
Matches with Streamers: {streamer_stats['matches_with_streamers']}
Streamer Encounter Rate: {streamer_stats['streamer_encounter_rate']:.1%}

🏆 MOST ENCOUNTERED STREAMERS:
{'-'*30}
"""
        for name, count in streamer_stats['most_encountered_streamers']:
            streamer_info += f"{name}: {count} times\n"
        
        streamer_info += f"\n📱 PLATFORM DISTRIBUTION:\n{'-'*30}\n"
        for platform, count in streamer_stats['platform_distribution'].items():
            streamer_info += f"{platform.title()}: {count} encounters\n"
        
        streamer_text.insert(1.0, streamer_info)
        streamer_text.config(state=tk.DISABLED)
        
        # Hidden players tab
        hidden_frame = tk.Frame(notebook, bg='white')
        notebook.add(hidden_frame, text="Hidden Players")
        
        hidden_stats = self.match_history.get_hidden_player_stats()
        
        hidden_text = scrolledtext.ScrolledText(hidden_frame, bg='white', fg='#333333',
                                              font=('Consolas', 10), wrap=tk.WORD)
        hidden_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        hidden_info = f"""🔍 HIDDEN PLAYER STATISTICS
{'='*50}
Total Matches: {hidden_stats['total_matches']}
Matches with Hidden Players: {hidden_stats['matches_with_hidden']}
Hidden Player Rate: {hidden_stats['hidden_player_rate']:.1%}

🏆 MOST ENCOUNTERED HIDDEN PLAYERS:
{'-'*30}
"""
        for name, count in hidden_stats['most_encountered_hidden']:
            hidden_info += f"{name}: {count} times\n"
        
        hidden_text.insert(1.0, hidden_info)
        hidden_text.config(state=tk.DISABLED)
        
        # Cache stats tab
        cache_frame = tk.Frame(notebook, bg='white')
        notebook.add(cache_frame, text="Cache")
        
        cache_stats = self.cache_manager.get_cache_stats()
        
        cache_text = scrolledtext.ScrolledText(cache_frame, bg='white', fg='#333333',
                                             font=('Consolas', 10), wrap=tk.WORD)
        cache_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        cache_info = f"""💾 CACHE STATISTICS
{'='*50}
Total Cached Entries: {cache_stats['total_entries']}
Cache File Size: {cache_stats['cache_file_size']} bytes

📱 CACHED PLATFORMS:
{'-'*30}
"""
        for platform, count in cache_stats['platforms'].items():
            cache_info += f"{platform.title()}: {count} entries\n"
        
        cache_text.insert(1.0, cache_info)
        cache_text.config(state=tk.DISABLED)
        
        # Clear cache button
        clear_btn = tk.Button(cache_frame, text="Clear Cache", 
                            command=lambda: self.clear_cache_and_refresh(cache_text),
                            bg='#dc3545', fg='white', font=('Segoe UI', 10, 'bold'))
        clear_btn.pack(pady=10)
    
    def clear_cache_and_refresh(self, cache_text):
        """Clear cache and refresh display"""
        self.cache_manager.cache = {}
        self.cache_manager.save_cache()
        cache_text.config(state=tk.NORMAL)
        cache_text.delete(1.0, tk.END)
        cache_text.insert(1.0, "Cache cleared successfully!")
        cache_text.config(state=tk.DISABLED)
        self.log("Cache cleared")
    
    def show_team_analysis(self):
        """Show team analysis window with smurf detection and recommendations"""
        if not self.current_game:
            messagebox.showinfo("No Match", "No active match to analyze.")
            return
        
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Team Analysis & Smurf Detection")
        analysis_window.geometry("800x600")
        analysis_window.configure(bg='#f5f5f5')
        analysis_window.transient(self.root)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(analysis_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Overall analysis tab
        overall_frame = tk.Frame(notebook, bg='white')
        notebook.add(overall_frame, text="Overall Analysis")
        
        # Get all players from current match
        all_players = []
        for player in self.current_game.players if hasattr(self.current_game, 'players') else []:
            try:
                player.get_competitive_stats()
                if hasattr(player, 'player_stats') and player.player_stats:
                    all_players.append(player.player_stats)
            except:
                continue
        
        if all_players:
            from player_stats import PlayerStatisticsManager
            stats_manager = PlayerStatisticsManager()
            team_analysis = stats_manager.get_team_analysis(all_players)
            
            # Display analysis
            analysis_text = scrolledtext.ScrolledText(overall_frame, bg='white', fg='#333333',
                                                    font=('Consolas', 11), wrap=tk.WORD)
            analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            analysis_info = f"""🔍 TEAM ANALYSIS & SMURF DETECTION
{'='*60}

📊 OVERALL STATISTICS:
{'-'*30}
Total Players: {team_analysis['total_players']}
Smurf Risk Players: {team_analysis['smurf_players']}
High Risk Players: {team_analysis['high_risk_players']}
Smurf Percentage: {team_analysis['smurf_percentage']:.1%}

📈 PERFORMANCE METRICS:
{'-'*30}
Average Win Rate: {team_analysis['avg_win_rate']:.1%}
Average K/D Ratio: {team_analysis['avg_kd_ratio']:.2f}

⚠️ RISK ASSESSMENT:
{'-'*30}
Team Risk Level: {team_analysis['team_risk_level']}

💡 RECOMMENDATION:
{'-'*30}
{team_analysis['recommendation']}

🎯 DETAILED PLAYER ANALYSIS:
{'-'*30}
"""
            
            # Add individual player analysis
            for player in all_players:
                player_summary = stats_manager.get_player_summary(player)
                analysis_info += f"""
{player_summary['name']}:
  • Current Rank: {player_summary['current_rank']}
  • Peak Rank: {player_summary['peak_rank']}
  • Win Rate: {player_summary['win_rate']}
  • K/D Ratio: {player_summary['kd_ratio']}
  • Smurf Risk: {player_summary['smurf_risk']}
  • Indicators: {', '.join(player_summary['smurf_indicators']) if player_summary['smurf_indicators'] else 'None'}
"""
            
            analysis_text.insert(1.0, analysis_info)
            analysis_text.config(state=tk.DISABLED)
        else:
            # No players to analyze
            no_data_label = tk.Label(overall_frame, text="No player data available for analysis.\nRefresh the match to load player statistics.", 
                                   font=('Segoe UI', 12), bg='white', fg='#666666')
            no_data_label.pack(expand=True)
        
        # Risk breakdown tab
        risk_frame = tk.Frame(notebook, bg='white')
        notebook.add(risk_frame, text="Risk Breakdown")
        
        risk_text = scrolledtext.ScrolledText(risk_frame, bg='white', fg='#333333',
                                            font=('Consolas', 11), wrap=tk.WORD)
        risk_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        risk_info = """🔍 SMURF DETECTION CRITERIA
{'='*60}

The system analyzes players based on the following indicators:

📊 PERFORMANCE INDICATORS:
{'-'*30}
• Win Rate > 65% (suspicious for new accounts)
• K/D Ratio > 1.5 (unusually high performance)
• Recent performance spike (>70% win rate in last 10 matches)

🏆 RANK INDICATORS:
{'-'*30}
• Large rank disparity (3+ tiers difference between current and peak)
• Sudden rank improvements
• Inconsistent rank progression

📅 ACCOUNT INDICATORS:
{'-'*30}
• New account (<30 days old)
• Limited match history
• Suspicious account creation patterns

⚠️ RISK LEVELS:
{'-'*30}
• Low: 0-1 indicators
• Medium: 2 indicators  
• High: 3 indicators
• Very High: 4+ indicators

💡 RECOMMENDATIONS:
{'-'*30}
• Very High Risk: Consider dodging the match
• High Risk: Be very cautious, monitor closely
• Medium Risk: Proceed with caution
• Low Risk: Safe to proceed normally

Note: These are indicators, not definitive proof. Use your judgment!
"""
        
        risk_text.insert(1.0, risk_info)
        risk_text.config(state=tk.DISABLED)
    
    def export_data(self):
        """Export match data to CSV"""
        try:
            filename = self.match_history.export_to_csv()
            if filename:
                self.log(f"Data exported to {filename}")
            else:
                self.log("Export failed", "Error")
        except Exception as e:
            self.log(f"Export error: {str(e)}", "Error")
    
    def toggle_notifications(self):
        """Toggle desktop notifications"""
        enabled = self.notification_manager.toggle_notifications()
        if enabled:
            self.notify_btn.config(text="Notifications", bg='#28a745')
            self.log("Notifications enabled")
        else:
            self.notify_btn.config(text="Notifications", bg='#e1e1e1')
            self.log("Notifications disabled")
    
    def start_drag(self, event):
        """Start dragging the window"""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
    
    def on_drag(self, event):
        """Drag the window"""
        x = self.root.winfo_x() - self._drag_start_x + event.x
        y = self.root.winfo_y() - self._drag_start_y + event.y
        self.root.geometry(f"+{x}+{y}")
    
    def minimize_window(self):
        """Minimize the window (workaround for borderless windows)"""
        # Store current state
        self._minimized = True
        # Temporarily enable window manager for minimize
        self.root.overrideredirect(False)
        self.root.iconify()
        # Restore borderless when window is restored
        self.root.bind('<Map>', self._on_restore)
    
    def _on_restore(self, event=None):
        """Restore borderless mode after minimize"""
        if hasattr(self, '_minimized') and self._minimized:
            self.root.after(10, lambda: self.root.overrideredirect(True))
            self._minimized = False
            self.root.unbind('<Map>')
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Calculate session duration
            session_duration = time.time() - self.session_start_time
            
            # Prepare session summary
            session_summary = {
                'Session Duration': f"{session_duration/60:.1f} minutes",
                'Matches Detected': self.session_stats['matches_detected'],
                'Players Scanned': self.session_stats['players_scanned'],
                'Streamers Found': self.session_stats['streamers_found'],
                'Hidden Players Found': self.session_stats['hidden_players_found'],
                'Platforms Checked': self.session_stats['platforms_checked'],
                'Cache Hits': self.session_stats['cache_hits'],
                'Cache Hit Rate': f"{(self.session_stats['cache_hits'] / max(1, self.session_stats['platforms_checked'])) * 100:.1f}%",
                'Notifications Sent': self.session_stats['notifications_sent']
            }
            
            # Log session summary
            self.logger_system.log_session_summary(session_summary)
            
            self.logger.info("👋 Application closing gracefully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        
        finally:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = ValorantDetectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()