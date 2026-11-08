# Enhanced Riot API Player Statistics

## Overview

The Valorant Lobby Scout now features **enhanced player statistics** directly from Riot's API, providing comprehensive player insights including player level, current rank, peak rank, and headshot percentage.

## New Features

### 🆕 Enhanced Player Statistics

**Available Data:**
- ✅ **Player Level** - Account level from Riot API
- ✅ **Current Rank + RR** - Real-time competitive rank and rating
- ✅ **Peak Rank + RR** - Highest achieved rank across all seasons  
- ✅ **Headshot Percentage** - Calculated from recent match performance
- ✅ **K/D Ratio** - Kill/Death ratio from match history
- ✅ **Win Rate** - Win percentage from recent matches
- ✅ **Match Statistics** - Total kills, headshots, and matches played

### 🎮 Enhanced GUI Display

**Player Tables:**
- Player names now show level: `PlayerName (Lv.45)`
- Enhanced tooltips on profile buttons with full stats
- Real-time statistics loading during agent select
- Improved visual indicators for hidden players

**Stats Display Format:**
```
Level 45 | Gold 2 (85 RR) | Peak: Diamond 1 (120 RR) | HS: 23.4% | K/D: 1.65 | WR: 68.2%
```

## Implementation Details

### Direct Riot API Integration

**Primary Data Sources:**
1. **Account API** - Player level and account information
2. **MMR API** - Current and peak rank data with RR points
3. **Match History API** - Performance statistics and headshot calculations

**Fallback System:**
- Primary: Direct Riot API calls (faster, more accurate)
- Fallback: Tracker.gg API (if Riot API fails)
- Graceful degradation with partial data display

### Performance Optimizations

**Intelligent Loading:**
- Stats loaded only when needed (during match detection)
- Caching prevents redundant API calls
- Background processing doesn't block UI
- Timeout handling for API reliability

**Memory Management:**
- Per-player stat caching
- Automatic cleanup of old data
- Efficient data structures

## Usage

### Automatic Loading
Statistics are automatically loaded when:
1. **New match detected** - All players get enhanced stats
2. **Agent select phase** - Real-time stat loading
3. **Profile button hover** - Tooltip with full statistics

### Manual Testing
Use the test script to verify functionality:
```bash
python test_enhanced_stats.py
```

### Configuration
Settings are automatically managed, but you can adjust:
- Cache duration in `player.py`
- API timeout values
- Stat calculation parameters

## API Endpoints Used

### Riot API Endpoints
```
GET /account/v1/accounts/by-puuid/{puuid}     # Account level
GET /mmr/v1/players/{puuid}                   # Rank data  
GET /match-history/v1/history/{puuid}         # Match stats
```

### Data Processing
- **Headshot %**: Calculated from damage events in recent matches
- **Win Rate**: Percentage from last 20 competitive matches
- **Peak Rank**: Highest tier across all seasons
- **Account Level**: Direct from account API

## Troubleshooting

### Common Issues

**"No stats available"**
- Check Valorant client connection
- Verify API accessibility
- Player may have no competitive history

**"Stats loading..."**
- API calls in progress (normal)
- May take 2-3 seconds for full data
- Check network connectivity

**Level shows 0**
- Alternative API endpoint will be tried
- Some accounts may not expose level data
- Fallback to other stat sources

### Debug Information
Enable debug logging to see:
- API call success/failure
- Data parsing results  
- Fallback mechanism activation
- Performance timing

## Benefits

### For Players
- **Better Match Insights** - Know opponent skill levels instantly
- **Team Composition** - Understand team strengths/weaknesses
- **Skill Assessment** - Accurate rank and performance data
- **Smurf Detection** - Enhanced detection with more data points

### For Development
- **Reliable Data** - Direct from official Riot API
- **Real-time Updates** - Fresh data every match
- **Comprehensive Stats** - Multiple data points for analysis
- **Future Expansion** - Foundation for advanced features

## Future Enhancements

### Planned Features
- **Agent Performance** - Stats per agent played
- **Seasonal Trends** - Rank progression over time
- **Team Synergy** - Composition analysis
- **Performance Predictions** - Match outcome insights

### API Expansion
- **Esports Data** - Professional player identification
- **Tournament Stats** - Competitive scene integration
- **Real-time Events** - Live match data streaming
- **Cross-Region** - Global player database

---

## Implementation Notes

The enhanced statistics system maintains backward compatibility while adding powerful new features. The dual-API approach ensures reliability, and the caching system provides optimal performance.

**Key Benefits:**
- ⚡ **Faster loading** with direct Riot API
- 🎯 **More accurate** than third-party sources
- 📊 **Comprehensive data** including headshot percentages
- 🔄 **Real-time updates** during matches
- 🛡️ **Fallback protection** with Tracker.gg