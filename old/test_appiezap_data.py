#!/usr/bin/env python3
"""
Test script to verify API access for Appiezap#0000
Tests both ValorantAPI and Tracker.gg to see what data we can actually get
"""

import valo_api
import json
import time

def test_appiezap_account():
    """Test fetching data for Appiezap#0000"""
    print("[TEST] Testing API Access for Appiezap#0000")
    print("=" * 60)
    
    # Set API key from test file
    api_key = "YOUR_HENRIK_API_KEY"
    valo_api.set_api_key(api_key)
    
    player_name = "Appiezap"
    tag = "0000"
    
    print(f"\n[TARGET] Account: {player_name}#{tag}")
    print("-" * 60)
    
    results = {
        "account": player_name,
        "tag": tag,
        "tests": {}
    }
    
    # Test 1: Account Details (includes player level!)
    print("\n[TEST 1] Testing Account Details (Player Level)")
    try:
        account_data = valo_api.get_account_details_by_name(player_name, tag)
        if account_data and hasattr(account_data, 'data'):
            data = account_data.data
            print(f"   [OK] SUCCESS - Account data retrieved!")
            
            # Extract account details
            details = {}
            if hasattr(data, 'account_level'):
                details['level'] = data.account_level
                print(f"   [LEVEL] Account Level: {data.account_level}")
            if hasattr(data, 'card'):
                details['card'] = data.card
            if hasattr(data, 'region'):
                details['region'] = data.region
                print(f"   [REGION] Region: {data.region}")
            if hasattr(data, 'puuid'):
                details['puuid'] = data.puuid[:20] + "..."
                
            results['tests']['account_details'] = {
                'success': True,
                'data': details
            }
        else:
            print(f"   [FAIL] No account data returned")
            results['tests']['account_details'] = {'success': False}
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        results['tests']['account_details'] = {'success': False, 'error': str(e)}
    
    time.sleep(1.5)  # Rate limiting
    
    # Test 2: MMR Details (Current Rank, RR, Peak Rank)
    print("\n[TEST 2] Testing MMR Details (Rank & RR)")
    try:
        mmr_data = valo_api.get_mmr_details_by_name(player_name, tag)
        if mmr_data and hasattr(mmr_data, 'data'):
            data = mmr_data.data
            print(f"   [OK] SUCCESS - MMR data retrieved!")
            
            # Extract MMR details
            mmr_info = {}
            if hasattr(data, 'current_data') and data.current_data:
                current = data.current_data
                if hasattr(current, 'currenttierpatched'):
                    mmr_info['current_rank'] = current.currenttierpatched
                    print(f"   [RANK] Current Rank: {current.currenttierpatched}")
                if hasattr(current, 'ranking_in_tier'):
                    mmr_info['current_rr'] = current.ranking_in_tier
                    print(f"   [RR] Current RR: {current.ranking_in_tier}")
                if hasattr(current, 'elo'):
                    mmr_info['elo'] = current.elo
                    print(f"   [ELO] ELO: {current.elo}")
            
            if hasattr(data, 'highest_rank') and data.highest_rank:
                peak = data.highest_rank
                if hasattr(peak, 'patched_tier'):
                    mmr_info['peak_rank'] = peak.patched_tier
                    print(f"   [PEAK] Peak Rank: {peak.patched_tier}")
                if hasattr(peak, 'season'):
                    mmr_info['peak_season'] = peak.season
            
            results['tests']['mmr_details'] = {
                'success': True,
                'data': mmr_info
            }
        else:
            print(f"   [FAIL] No MMR data returned")
            results['tests']['mmr_details'] = {'success': False}
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        results['tests']['mmr_details'] = {'success': False, 'error': str(e)}
    
    time.sleep(1.5)  # Rate limiting
    
    # Test 3: Match History (K/D, Win Rate)
    print("\n[TEST 3] Testing Match History (K/D & Win Rate)")
    try:
        match_data = valo_api.get_match_history_by_name(player_name, tag)
        if match_data and hasattr(match_data, 'data'):
            matches = match_data.data
            print(f"   [OK] SUCCESS - Match history retrieved!")
            print(f"   [MATCHES] Found {len(matches)} recent matches")
            
            # Calculate stats from recent matches
            if matches:
                total_kills = 0
                total_deaths = 0
                total_headshots = 0
                wins = 0
                
                for i, match in enumerate(matches[:10]):  # Last 10 matches
                    if hasattr(match, 'players') and match.players:
                        for player in match.players:
                            # Find the target player
                            if (hasattr(player, 'name') and 
                                player.name.lower() == player_name.lower() and
                                hasattr(player, 'tag') and 
                                player.tag == tag):
                                
                                if hasattr(player, 'stats'):
                                    stats = player.stats
                                    total_kills += getattr(stats, 'kills', 0)
                                    total_deaths += getattr(stats, 'deaths', 0)
                                    total_headshots += getattr(stats, 'headshots', 0)
                                
                                # Check win/loss
                                if hasattr(player, 'team') and player.team == 'Red':
                                    team_color = 'Red'
                                else:
                                    team_color = 'Blue'
                                    
                                # Find if team won
                                if hasattr(match, 'teams') and match.teams:
                                    for team in match.teams:
                                        if (hasattr(team, 'team_id') and 
                                            team.team_id.lower() == team_color.lower() and
                                            hasattr(team, 'has_won') and team.has_won):
                                            wins += 1
                
                # Calculate derived stats
                kd_ratio = total_kills / total_deaths if total_deaths > 0 else 0.0
                win_rate = wins / len(matches[:10]) if len(matches[:10]) > 0 else 0.0
                hs_rate = total_headshots / total_kills if total_kills > 0 else 0.0
                
                match_stats = {
                    'matches_analyzed': len(matches[:10]),
                    'kd_ratio': round(kd_ratio, 2),
                    'win_rate': f"{win_rate:.1%}",
                    'headshot_rate': f"{hs_rate:.1%}",
                    'total_kills': total_kills,
                    'total_deaths': total_deaths,
                    'wins': wins
                }
                
                print(f"   [K/D] K/D Ratio: {kd_ratio:.2f}")
                print(f"   [WR] Win Rate: {win_rate:.1%}")
                print(f"   [HS] Headshot Rate: {hs_rate:.1%}")
                
                results['tests']['match_history'] = {
                    'success': True,
                    'data': match_stats
                }
            else:
                print(f"   [WARN] No matches found")
                results['tests']['match_history'] = {'success': False}
        else:
            print(f"   [FAIL] No match data returned")
            results['tests']['match_history'] = {'success': False}
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        results['tests']['match_history'] = {'success': False, 'error': str(e)}
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY]")
    print("=" * 60)
    
    successful_tests = sum(1 for test in results['tests'].values() if test.get('success', False))
    total_tests = len(results['tests'])
    
    print(f"[OK] Successful Tests: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        print("\n[DATA] Available Data for Appiezap#0000:")
        for test_name, test_data in results['tests'].items():
            if test_data.get('success'):
                print(f"\n   {test_name.replace('_', ' ').title()}:")
                if 'data' in test_data:
                    for key, value in test_data['data'].items():
                        print(f"      • {key}: {value}")
    else:
        print("\n[FAIL] No data could be retrieved. Possible reasons:")
        print("   - Player profile may be private")
        print("   - Account may not exist or tag is incorrect")
        print("   - API key may be invalid or rate limited")
    
    # Save results
    with open('appiezap_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[SAVE] Full results saved to: appiezap_test_results.json")
    
    return results

if __name__ == "__main__":
    test_appiezap_account()

