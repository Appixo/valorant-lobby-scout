# Player Statistics & Smurf Detection System

## Overview

Valorant Lobby Scout now includes advanced player statistics and smurf detection capabilities to help you make informed decisions about your matches. This system analyzes player performance, rank history, and account patterns to identify potential smurfs or problematic players.

## Features

### 📊 Player Statistics
- **Current Rank & Peak Rank**: Track player's current and highest achieved ranks
- **Win Rate**: Calculate win percentage from recent matches
- **K/D Ratio**: Average kills to deaths ratio
- **Match History**: Number of matches played and performance trends
- **Account Age**: How long the account has been active

### 🔍 Smurf Detection
The system uses multiple indicators to identify potential smurfs:

#### Performance Indicators
- **High Win Rate**: >65% win rate (suspicious for new accounts)
- **High K/D Ratio**: >1.5 K/D ratio (unusually high performance)
- **Recent Performance Spike**: >70% win rate in last 10 matches

#### Rank Indicators
- **Rank Disparity**: 3+ tier difference between current and peak rank
- **Sudden Rank Improvements**: Inconsistent rank progression
- **Rank History Analysis**: Seasonal rank patterns

#### Account Indicators
- **New Account**: <30 days old
- **Limited Match History**: Few matches played
- **Suspicious Patterns**: Unusual account creation or activity

### ⚠️ Risk Levels
- **Low**: 0-1 indicators (safe to proceed)
- **Medium**: 2 indicators (proceed with caution)
- **High**: 3 indicators (be very cautious)
- **Very High**: 4+ indicators (consider dodging)

## Usage

### In-Game Interface

1. **Connect to Valorant**: Click "Connect" to establish connection
2. **Refresh Match**: Click "Refresh" when in agent select or in-game
3. **View Player Stats**: Each player row shows:
   - Player name and agent
   - Current rank
   - Win rate percentage
   - K/D ratio
   - Risk level (color-coded)
   - Hidden/Visible status

### Team Analysis

1. **Click "Team Analysis"**: Opens detailed analysis window
2. **Overall Analysis Tab**: Shows team-wide statistics and recommendations
3. **Risk Breakdown Tab**: Explains detection criteria and risk levels

### Key Information Displayed

```
Player Name    Agent    Rank    Win Rate    K/D    Risk    Status    Tracker
JohnDoe#1234   Jett     Gold 2   65%       1.8    ⚠️ High  Visible   Open
```

## Data Sources

### Valorant API
- **MMR Data**: Current rank, peak rank, RR points
- **Match History**: Win/loss records, performance metrics
- **Seasonal Data**: Rank progression over time

### Tracker.gg Integration (Future)
- Additional statistics and verification
- Cross-platform data validation
- Enhanced accuracy for smurf detection

## Configuration

### Smurf Detection Thresholds
You can adjust detection sensitivity in `player_stats.py`:

```python
self.smurf_thresholds = {
    'win_rate_threshold': 0.65,      # 65% win rate
    'kd_ratio_threshold': 1.5,       # 1.5 K/D ratio
    'rank_disparity_threshold': 3,   # 3 rank tiers difference
    'account_age_threshold': 30,     # 30 days
    'recent_performance_threshold': 0.7  # 70% recent win rate
}
```

### Cache Settings
- **Cache Duration**: 24 hours (configurable)
- **Storage**: `player_stats.json` file
- **Auto-refresh**: Automatically updates stale data

## Recommendations

### Based on Risk Level

#### Very High Risk
- **Action**: Consider dodging the match
- **Reason**: High chance of smurfs or unfair match
- **Indicators**: Multiple high-risk players, suspicious patterns

#### High Risk
- **Action**: Be very cautious, monitor closely
- **Reason**: Multiple suspicious players detected
- **Strategy**: Play defensively, communicate with team

#### Medium Risk
- **Action**: Proceed with caution
- **Reason**: Some suspicious players
- **Strategy**: Normal gameplay, stay alert

#### Low Risk
- **Action**: Safe to proceed normally
- **Reason**: No significant risks detected
- **Strategy**: Standard competitive play

## Technical Details

### Data Storage
- **Player Statistics**: Stored in `player_stats.json`
- **Match History**: Stored in `match_history.json`
- **Cache Management**: Automatic cleanup and updates

### Performance
- **API Calls**: Minimized through intelligent caching
- **Update Frequency**: 24-hour cache duration
- **Background Processing**: Non-blocking data fetching

### Error Handling
- **Graceful Degradation**: Works with partial data
- **Fallback Values**: Default statistics when API fails
- **Logging**: Comprehensive error tracking

## Privacy & Ethics

### Data Collection
- **Public Data Only**: Only collects publicly available information
- **No Personal Data**: No private account information stored
- **Transparent**: All data sources clearly documented

### Fair Use
- **Educational Purpose**: Help understand match dynamics
- **No Harassment**: Not intended for player targeting
- **Respectful Use**: Use responsibly and ethically

## Troubleshooting

### Common Issues

#### "No player data available"
- **Solution**: Refresh the match data
- **Cause**: API connection issues or no active match

#### "Statistics not updating"
- **Solution**: Check internet connection
- **Cause**: Valorant API rate limiting

#### "Incorrect risk assessment"
- **Solution**: Adjust thresholds in configuration
- **Cause**: Default thresholds may not suit your region/rank

### Performance Tips
- **Regular Updates**: Keep the application updated
- **Cache Management**: Clear cache if data seems stale
- **Network Stability**: Ensure stable internet connection

## Future Enhancements

### Planned Features
- **Machine Learning**: Improved detection accuracy
- **Regional Analysis**: Region-specific patterns
- **Behavioral Analysis**: Playstyle pattern recognition
- **Real-time Updates**: Live statistics during matches

### API Improvements
- **Tracker.gg Integration**: Enhanced data validation
- **Multiple Sources**: Cross-reference with other platforms
- **Historical Analysis**: Long-term trend analysis

## Support

For issues or questions about the player statistics system:
1. Check the troubleshooting section
2. Review the configuration options
3. Test with the provided test script
4. Report bugs with detailed information

---

**Note**: This system provides indicators, not definitive proof. Always use your judgment and respect other players. The goal is to improve match quality, not to harass or unfairly target players.
