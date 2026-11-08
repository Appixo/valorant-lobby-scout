# Valorant Player Detector

A desktop tool that shows who you're playing with and against: ranks, recent performance, parties and possible smurfs.

## Features

- 🔍 **Hidden names**: marks who uses incognito mode and still loads their stats. Riot no longer hands out those names, so a real Riot ID only appears when you already know it — from your own saved matches or your friends list
- 🤖 **Auto mode**: detects agent select, the loading screen and matches by itself and loads everyone's stats; start the app before Valorant and it waits for the game
- 📊 **Player stats**: current rank, peak rank, account level, win rate this act, K/D and headshot % over the last 5 competitive matches
- 👥 **Parties**: players who queued together get the same number (①, ②, …)
- ⚠️ **Possible smurfs**: flags low-level accounts at high ranks, big gaps between peak and current rank, very high win rates and K/Ds
- ↺ **Met before**: remembers players from earlier matches (when, which map, teammate or opponent)
- 🖱️ **Hover a player** for the reasons behind these markers; **double-click** to open their Tracker.gg profile
- ↔️ **Side-by-side or stacked** team tables (layout button or Ctrl+L), remembered between sessions
- 🗺️ **Always up to date**: agent and map names come from valorant-api.com, so new agents and maps work without updates

## Requirements

- Windows with Python 3.8+
- Valorant installed (the tool reads the running game client)

## Installation

1. Clone or download this repository
2. Copy `settings.example.json` to `settings.json` and fill in your [Henrik API key](https://docs.henrikdev.xyz) (`henrikApiKey`); it's only used as a fallback for stats
3. Double-click `start_detector.bat` (it installs missing requirements the first time), or run:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

## Usage

With **auto mode** on (the default), just leave the app open: it fills in both teams during agent select and the match, and loads stats automatically.

With auto mode off, click **Refresh** (F5) in agent select or in game, then **Load Stats**.

| Marker | Meaning |
|---|---|
| ★ (gold row) | You |
| ● (purple row) | Player using a hidden name |
| ①②③ | Players in the same party |
| ⚠ | Possible smurf (hover to see why) |
| ↺ | You've played with or against this player before |

Party detection depends on which players' presence the game client shares, so not every party may show up.

## Configuration

`settings.json` (created from `settings.example.json`; not tracked by git):

| Setting | Meaning |
|---|---|
| `region` | Your region: `na`, `eu`, `ap` or `kr` (asked on first run) |
| `henrikApiKey` | Henrik API key, used when the game client can't provide stats |
| `autoMode` | `true` to detect matches and load stats automatically |
| `stateInterval` | Seconds between auto mode checks |
| `layout` | `horizontal` (side by side) or `vertical` (stacked) |

## How It Works

1. **Game client**: reads agent select and live match data from the running Valorant client (via [valclient](https://github.com/colinhartigan/valclient-python))
2. **Stats**: rank, peak and win rate come from Riot's MMR data; K/D and HS% from each player's last 5 competitive matches (match details are cached so shared matches are only downloaded once)
3. **Parties**: read from the chat presences the client can see
4. **History**: every match is saved to `match_history.json`, which powers the "met before" marker
5. **Names**: agent, map and season data come from valorant-api.com and are cached for a day in `game_data_cache.json`

## Project Structure

```
📁 Valorant Player Detector
├── main.py                 # Entry point
├── start_detector.bat      # Windows launcher (also used by the desktop shortcut)
├── gui_app.py              # GUI (Tkinter)
├── main_console.py         # Console version (legacy)
├── quick_lookup.py         # Command-line stats lookup: python quick_lookup.py Name#TAG
│
├── player.py               # Player data and stats loading
├── game.py                 # Current match
├── match_insights.py       # Parties, smurf flags, earlier encounters
├── match_history.py        # Saved matches
├── game_data.py            # Agent, map and season names (valorant-api.com)
├── valorant_api_client.py  # Riot client APIs + Henrik API fallback
├── tracker_api.py          # Tracker.gg (optional)
├── cache_manager.py, logger_config.py, notifications.py, player_stats.py, streaming_services.py
│
├── settings.example.json   # Copy to settings.json
└── old/                    # Earlier experiments and test scripts (not used by the app)
```

## AI Agent System

This project is enhanced with **5 specialized AI agents** for efficient development:

- 🎨 **UI/GUI Agent** - Handles interface design and user experience
- 🔧 **API Integration Agent** - Manages all external API connections
- 📊 **Data & Statistics Agent** - Handles data management and analytics
- 🐛 **Testing & QA Agent** - Maintains tests and ensures quality
- 📝 **Documentation Agent** - Keeps documentation up-to-date

Each agent has specific expertise and responsibilities. See `.cursorrules` and `.cursor/agents/` for detailed configurations.

## Legal Notice

This tool uses the Valorant client API for educational purposes. Use responsibly and in accordance with Riot Games' Terms of Service.

## Recent Updates

### Version 2.2 (November 2026)
- ✅ Auto mode: detects agent select and matches, loads stats, reconnects when Valorant starts
- ✅ Party numbers, possible-smurf flags and "met before" markers with hover details
- ✅ K/D and headshot % over the last 5 competitive matches (was: last match only)
- ✅ Fixed fast stats loading from the game client (was silently falling back to the slower Henrik API)
- ✅ Fixed agent select showing no players, wrong win %, old-season peak ranks and missing account levels
- ✅ New agents and maps loaded automatically; fixed maps showing as "Unknown Map" and Viper showing as Vyse
- ✅ Redesigned UI with Peak, Level, Win %, K/D and HS% columns and a side-by-side / stacked layout toggle
- ✅ API key moved to `settings.json`; old scripts moved to `old/`

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

### Development
- Review `.cursorrules` for project guidelines
- Check `.cursor/agents/` for specialized agent roles
- Follow PEP 8 style guidelines

## Credits

- Original concept inspired by various Valorant community tools
- Progress bar implementation from Stack Overflow
- Built with [valclient](https://github.com/colinhartigan/valclient-python) library

## Disclaimer

This tool is for educational purposes only. The authors are not responsible for any misuse or violations of Terms of Service.