#!/usr/bin/env python3
"""
Test script to explore all available valo_api methods
Discovers what additional data we can get from Henrik's API through the Python library
"""

import valo_api
import json
import time

def test_valo_api_methods():
    """Test various valo_api methods to see what data is available"""
    print("🔍 Testing valo_api Python Library Methods")
    print("=" * 50)
    
    # Set API key
    valo_api.set_api_key("YOUR_HENRIK_API_KEY")
    
    # Test players
    test_players = [
        ("TenZ", "001"),
        ("Shroud", "1337"),
    ]
    
    # List of methods to test
    methods_to_test = [
        # Account methods
        ("get_account_details_by_name", "Account Details"),
        
        # MMR methods
        ("get_mmr_details_by_name", "MMR Details"),
        ("get_mmr_history_by_name", "MMR History"),
        
        # Match methods
        ("get_match_history_by_name", "Match History"),
        ("get_lifetime_matches_by_name", "Lifetime Matches"),
        
        # Content methods
        ("get_content", "Game Content"),
        ("get_crosshair", "Crosshair"),
        
        # General methods
        ("get_leaderboard", "Leaderboard"),
        ("get_status", "Server Status"),
        ("get_store_featured", "Featured Store"),
        ("get_version_info", "Version Info"),
        ("get_website", "Website Info"),
    ]
    
    successful_methods = []
    
    for method_name, description in methods_to_test:
        print(f"\n🧪 Testing: {description} ({method_name})")
        print("-" * 40)
        
        try:
            method = getattr(valo_api, method_name)
            
            # Methods that need player parameters
            if any(x in method_name for x in ['by_name', 'by_puuid']):
                for name, tag in test_players:
                    try:
                        print(f"  Testing with {name}#{tag}...")
                        
                        # Different methods need different parameters
                        if 'leaderboard' in method_name:
                            result = method("eu")  # region parameter
                        elif 'mmr_history' in method_name:
                            result = method(name, tag, "eu")  # name, tag, region
                        else:
                            result = method(name, tag)  # name, tag
                        
                        if result:
                            print(f"    ✅ SUCCESS - Data type: {type(result)}")
                            
                            # Show sample data structure
                            if hasattr(result, '__dict__'):
                                attrs = [attr for attr in dir(result) if not attr.startswith('_')][:5]
                                print(f"    Attributes: {attrs}")
                            elif hasattr(result, 'data') and hasattr(result.data, '__dict__'):
                                attrs = [attr for attr in dir(result.data) if not attr.startswith('_')][:5]
                                print(f"    Data attributes: {attrs}")
                            
                            successful_methods.append((method_name, description, result))
                            break  # Success with first player, move to next method
                        else:
                            print(f"    ⚠️ No data returned")
                            
                    except Exception as e:
                        print(f"    ❌ Error with {name}#{tag}: {e}")
                        continue
                        
            # Methods that don't need player parameters
            else:
                try:
                    if 'leaderboard' in method_name:
                        result = method("eu")  # region parameter
                    elif 'crosshair' in method_name:
                        result = method("0;P;o;1;f;0;0t;1;0l;2;0o;2;0a;1;0f;0;1b;0")  # sample crosshair
                    else:
                        result = method()  # no parameters
                    
                    if result:
                        print(f"  ✅ SUCCESS - Data type: {type(result)}")
                        
                        # Show sample data structure
                        if hasattr(result, '__dict__'):
                            attrs = [attr for attr in dir(result) if not attr.startswith('_')][:5]
                            print(f"  Attributes: {attrs}")
                        elif hasattr(result, 'data') and hasattr(result.data, '__dict__'):
                            attrs = [attr for attr in dir(result.data) if not attr.startswith('_')][:5]
                            print(f"  Data attributes: {attrs}")
                        
                        successful_methods.append((method_name, description, result))
                    else:
                        print(f"  ⚠️ No data returned")
                        
                except Exception as e:
                    print(f"  ❌ Error: {e}")
            
            time.sleep(1)  # Rate limiting
            
        except AttributeError:
            print(f"  ❌ Method {method_name} not found")
        except Exception as e:
            print(f"  💥 Unexpected error: {e}")
    
    # Assert that we found at least one working method
    assert len(successful_methods) > 0, "No valo_api methods returned data successfully"
    print(f"\n✅ Successfully tested {len(successful_methods)} methods")
    
    # For integration with main(), we'll call the exploration functions here
    explore_successful_methods(successful_methods)
    documentation = create_method_documentation(successful_methods)
    suggest_new_features(documentation)

def explore_successful_methods(successful_methods):
    """Explore the structure of successful method results"""
    print(f"\n🔍 Exploring Successful Methods")
    print("=" * 35)
    
    for method_name, description, result in successful_methods:
        print(f"\n📊 {description} ({method_name}):")
        
        try:
            # Different ways to explore the data structure
            if hasattr(result, 'data'):
                data = result.data
                print(f"  Has .data attribute: {type(data)}")
                
                if hasattr(data, '__dict__'):
                    # It's an object with attributes
                    attrs = {k: type(v).__name__ for k, v in data.__dict__.items() if not k.startswith('_')}
                    print(f"  Data attributes: {attrs}")
                    
                    # Show some sample values for interesting attributes
                    for attr_name, attr_type in list(attrs.items())[:3]:
                        try:
                            value = getattr(data, attr_name)
                            if isinstance(value, (str, int, float, bool)):
                                print(f"    {attr_name}: {value}")
                            elif isinstance(value, list) and value:
                                print(f"    {attr_name}: [{len(value)} items] - {type(value[0]).__name__}")
                            else:
                                print(f"    {attr_name}: {type(value).__name__}")
                        except:
                            pass
                
                elif isinstance(data, list) and data:
                    print(f"  List with {len(data)} items")
                    if hasattr(data[0], '__dict__'):
                        attrs = {k: type(v).__name__ for k, v in data[0].__dict__.items() if not k.startswith('_')}
                        print(f"  Item attributes: {list(attrs.keys())[:5]}")
                    
            elif hasattr(result, '__dict__'):
                # Direct object attributes
                attrs = {k: type(v).__name__ for k, v in result.__dict__.items() if not k.startswith('_')}
                print(f"  Object attributes: {attrs}")
                
        except Exception as e:
            print(f"  Error exploring: {e}")

def create_method_documentation(successful_methods):
    """Create documentation for available methods"""
    print(f"\n📚 Creating Method Documentation")
    print("=" * 35)
    
    documentation = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "successful_methods": [],
        "method_details": {}
    }
    
    for method_name, description, result in successful_methods:
        documentation["successful_methods"].append({
            "method": method_name,
            "description": description,
            "data_type": type(result).__name__
        })
        
        # Try to document the data structure
        method_info = {
            "description": description,
            "returns": type(result).__name__,
            "data_structure": {}
        }
        
        try:
            if hasattr(result, 'data'):
                data = result.data
                if hasattr(data, '__dict__'):
                    method_info["data_structure"] = {
                        k: type(v).__name__ for k, v in data.__dict__.items() 
                        if not k.startswith('_')
                    }
                elif isinstance(data, list) and data and hasattr(data[0], '__dict__'):
                    method_info["data_structure"] = {
                        "type": "list",
                        "item_attributes": {
                            k: type(v).__name__ for k, v in data[0].__dict__.items() 
                            if not k.startswith('_')
                        }
                    }
            elif hasattr(result, '__dict__'):
                method_info["data_structure"] = {
                    k: type(v).__name__ for k, v in result.__dict__.items() 
                    if not k.startswith('_')
                }
        except:
            method_info["data_structure"] = "Unable to analyze"
        
        documentation["method_details"][method_name] = method_info
    
    # Save documentation
    with open('valo_api_methods_documentation.json', 'w') as f:
        json.dump(documentation, f, indent=2)
    
    print("📄 Documentation saved to valo_api_methods_documentation.json")
    
    return documentation

def suggest_new_features(documentation):
    """Suggest new features based on available methods"""
    print(f"\n💡 Feature Suggestions Based on Available Methods")
    print("=" * 50)
    
    successful_methods = [item["method"] for item in documentation["successful_methods"]]
    
    print("🎯 New Features We Can Implement:")
    
    if any("account" in method for method in successful_methods):
        print("   ✅ Enhanced Player Profiles")
        print("      - Account creation date")
        print("      - Player level tracking")
        print("      - Account region information")
    
    if any("mmr_history" in method for method in successful_methods):
        print("   ✅ Rank Progression Tracking")
        print("      - Historical rank changes")
        print("      - RR gain/loss over time")
        print("      - Peak rank achievement dates")
    
    if any("lifetime_matches" in method for method in successful_methods):
        print("   ✅ Complete Career Statistics")
        print("      - All-time performance metrics")
        print("      - Long-term trend analysis")
        print("      - Career milestone tracking")
    
    if any("leaderboard" in method for method in successful_methods):
        print("   ✅ Competitive Leaderboards")
        print("      - Regional rankings")
        print("      - Leaderboard position tracking")
        print("      - Top player analysis")
    
    if any("store" in method for method in successful_methods):
        print("   ✅ Store Integration")
        print("      - Featured store notifications")
        print("      - Store rotation tracking")
        print("      - Skin availability alerts")
    
    if any("content" in method for method in successful_methods):
        print("   ✅ Game Content Database")
        print("      - Current game version info")
        print("      - Content updates tracking")
        print("      - Asset management")
    
    print(f"\n🚀 Implementation Priority:")
    print("   1. Enhanced player profiles with account details")
    print("   2. Historical rank progression charts")
    print("   3. Complete career statistics dashboard")
    print("   4. Leaderboard position tracking")
    print("   5. Store notification system")

def main():
    """Main function to test and document valo_api methods"""
    print("🎮 Valo-API Method Explorer")
    print("=" * 40)
    
    # Test all methods - now handles exploration internally
    try:
        test_valo_api_methods()
        print("\n🎉 Valo-API exploration completed successfully!")
        print("   Check valo_api_methods_documentation.json for details")
    except AssertionError as e:
        print(f"\n⚠️ Test failed: {e}")
    
    print("\n✅ Valo-API exploration completed!")

if __name__ == "__main__":
    main()