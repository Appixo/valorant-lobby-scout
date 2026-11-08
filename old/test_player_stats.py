#!/usr/bin/env python3
"""
Test script for player statistics and smurf detection features
"""

import json
from player_stats import PlayerStatisticsManager, PlayerStats

def test_player_stats():
    """Test the player statistics system"""
    print("🧪 Testing Player Statistics System")
    print("=" * 50)
    
    # Initialize the statistics manager
    stats_manager = PlayerStatisticsManager()
    
    # Create some test player data
    test_players = [
        {
            'name': 'TestPlayer1#1234',
            'puuid': 'test-uuid-1',
            'current_rank': 'Gold 2',
            'peak_rank': 'Platinum 1',
            'win_rate': 0.72,
            'kd_ratio': 1.8,
            'matches_played': 45,
            'account_age_days': 15
        },
        {
            'name': 'TestPlayer2#5678',
            'puuid': 'test-uuid-2',
            'current_rank': 'Silver 3',
            'peak_rank': 'Silver 3',
            'win_rate': 0.48,
            'kd_ratio': 0.9,
            'matches_played': 120,
            'account_age_days': 180
        },
        {
            'name': 'TestPlayer3#9999',
            'puuid': 'test-uuid-3',
            'current_rank': 'Bronze 1',
            'peak_rank': 'Diamond 2',
            'win_rate': 0.85,
            'kd_ratio': 2.1,
            'matches_played': 12,
            'account_age_days': 5
        }
    ]
    
    # Create PlayerStats objects
    player_stats_list = []
    for player_data in test_players:
        stats = PlayerStats(
            name=player_data['name'],
            puuid=player_data['puuid'],
            current_rank=player_data['current_rank'],
            peak_rank=player_data['peak_rank'],
            win_rate=player_data['win_rate'],
            kd_ratio=player_data['kd_ratio'],
            matches_played=player_data['matches_played'],
            account_age_days=player_data['account_age_days']
        )
        
        # Analyze for smurf indicators
        stats_manager.analyze_smurf_indicators(stats)
        player_stats_list.append(stats)
        
        # Display individual player analysis
        print(f"\n👤 Player: {stats.name}")
        print(f"   Current Rank: {stats.current_rank}")
        print(f"   Peak Rank: {stats.peak_rank}")
        print(f"   Win Rate: {stats.win_rate:.1%}")
        print(f"   K/D Ratio: {stats.kd_ratio:.2f}")
        print(f"   Matches Played: {stats.matches_played}")
        print(f"   Account Age: {stats.account_age_days} days")
        print(f"   Smurf Risk: {stats_manager.get_smurf_risk_level(stats)}")
        print(f"   Indicators: {', '.join(stats.smurf_indicators) if stats.smurf_indicators else 'None'}")
    
    # Test team analysis
    print(f"\n🏆 TEAM ANALYSIS")
    print("=" * 50)
    
    team_analysis = stats_manager.get_team_analysis(player_stats_list)
    
    print(f"Total Players: {team_analysis['total_players']}")
    print(f"Smurf Risk Players: {team_analysis['smurf_players']}")
    print(f"High Risk Players: {team_analysis['high_risk_players']}")
    print(f"Smurf Percentage: {team_analysis['smurf_percentage']:.1%}")
    print(f"Average Win Rate: {team_analysis['avg_win_rate']:.1%}")
    print(f"Average K/D Ratio: {team_analysis['avg_kd_ratio']:.2f}")
    print(f"Team Risk Level: {team_analysis['team_risk_level']}")
    print(f"Recommendation: {team_analysis['recommendation']}")
    
    # Test player summary
    print(f"\n📊 PLAYER SUMMARIES")
    print("=" * 50)
    
    for stats in player_stats_list:
        summary = stats_manager.get_player_summary(stats)
        print(f"\n{summary['name']}:")
        print(f"  Rank: {summary['current_rank']} (Peak: {summary['peak_rank']})")
        print(f"  Performance: {summary['win_rate']} WR, {summary['kd_ratio']} K/D")
        print(f"  Risk: {summary['smurf_risk']}")
        print(f"  Last Updated: {summary['last_updated']}")

def test_smurf_detection():
    """Test smurf detection logic"""
    print(f"\n🔍 SMURF DETECTION TEST")
    print("=" * 50)
    
    stats_manager = PlayerStatisticsManager()
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'Obvious Smurf',
            'win_rate': 0.85,
            'kd_ratio': 2.5,
            'current_rank': 'Bronze 1',
            'peak_rank': 'Diamond 3',
            'account_age_days': 10,
            'matches_played': 8
        },
        {
            'name': 'Legitimate Player',
            'win_rate': 0.52,
            'kd_ratio': 1.1,
            'current_rank': 'Gold 2',
            'peak_rank': 'Gold 3',
            'account_age_days': 365,
            'matches_played': 200
        },
        {
            'name': 'Suspicious Player',
            'win_rate': 0.68,
            'kd_ratio': 1.6,
            'current_rank': 'Silver 1',
            'peak_rank': 'Platinum 2',
            'account_age_days': 45,
            'matches_played': 30
        }
    ]
    
    for scenario in scenarios:
        stats = PlayerStats(
            name=f"{scenario['name']}#TEST",
            puuid=f"test-{scenario['name'].lower().replace(' ', '-')}",
            win_rate=scenario['win_rate'],
            kd_ratio=scenario['kd_ratio'],
            current_rank=scenario['current_rank'],
            peak_rank=scenario['peak_rank'],
            account_age_days=scenario['account_age_days'],
            matches_played=scenario['matches_played']
        )
        
        stats_manager.analyze_smurf_indicators(stats)
        risk_level = stats_manager.get_smurf_risk_level(stats)
        
        print(f"\n{scenario['name']}:")
        print(f"  Win Rate: {scenario['win_rate']:.1%}")
        print(f"  K/D Ratio: {scenario['kd_ratio']:.2f}")
        print(f"  Rank: {scenario['current_rank']} → {scenario['peak_rank']}")
        print(f"  Account Age: {scenario['account_age_days']} days")
        print(f"  Matches: {scenario['matches_played']}")
        print(f"  Risk Level: {risk_level}")
        print(f"  Indicators: {len(stats.smurf_indicators)}")
        for indicator in stats.smurf_indicators:
            print(f"    • {indicator}")

if __name__ == "__main__":
    test_player_stats()
    test_smurf_detection()
    print(f"\n✅ Testing completed!")
