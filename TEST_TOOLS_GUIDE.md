# 🧪 Test Tools Guide

## Available Test Tools

We've created 2 test tools so you can verify the fast stats system works correctly **without being in a game**!

---

## 1️⃣ **Quick Lookup** (Recommended for Quick Tests)

### Simple, fast player stats lookup

### Usage:

#### Command Line:
```bash
python quick_lookup.py PlayerName#TAG
```

#### Interactive Mode:
```bash
python quick_lookup.py
```
Then enter player names one at a time.

### Example:
```bash
python quick_lookup.py TenZ#SEN
```

### Output:
```
🔍 Looking up: TenZ#SEN
================================================================
📊 STATS FOR TenZ#SEN
================================================================
🎮 Level:         305
🏆 Current Rank:  Radiant (450 RR)
⭐ Peak Rank:     Radiant
💀 K/D Ratio:     1.45
🎯 Headshot %:    28.5%
🏅 Win Rate:      58.2%
📈 Matches:       127 (74W - 53L)
================================================================
✅ Stats retrieved successfully!
```

---

## 2️⃣ **Full Test Suite** (Complete Performance Testing)

### Comprehensive testing with performance benchmarks

### Usage:

#### Command Line:
```bash
python test_fast_stats.py PlayerName#TAG
```

#### Interactive Mode:
```bash
python test_fast_stats.py
```
Then enter a player name.

### Example:
```bash
python test_fast_stats.py TenZ#SEN
```

### What It Tests:

1. **Direct PD API** - Fast method using local client
2. **Cached Retrieval** - Tests cache performance
3. **Henrik's API** - Fallback comparison
4. **Cache Invalidation** - Verifies cache clearing works
5. **Performance Comparison** - Speed benchmarks

### Output:
```
🚀 TEST 1: Direct PD API (Fast Method)
⏱️  Fetch time: 0.852 seconds
📊 Player stats displayed...

🎯 TEST 2: Cached Retrieval
⏱️  Fetch time: 0.003 seconds
✅ Cache is working! (Should be < 0.1s)

📊 TEST 3: Henrik's API (Fallback)
⏱️  Fetch time: 2.145 seconds

📈 PERFORMANCE COMPARISON
Direct PD API (1st):  0.852s
Cached (2nd):         0.003s  (🚀 284.0x faster!)
Henrik's API:         2.145s

✅ Direct PD API is 2.5x faster than Henrik's API
✅ Cached retrieval is 284x faster than first load
```

---

## 🎯 Which Tool to Use?

### Use **Quick Lookup** when:
- ✅ You just want to quickly check if stats work
- ✅ You want to look up multiple players
- ✅ You don't need performance details

### Use **Full Test Suite** when:
- ✅ You want to verify the fast method is working
- ✅ You want to see cache performance
- ✅ You want to compare different methods
- ✅ You're debugging issues

---

## 🔧 Requirements

Both tools require:
1. **Valorant client running** and logged in
2. **Python packages installed** (valclient, requests, etc.)
3. **Internet connection** for API calls

---

## 📝 Testing Popular Players

Try these well-known players to test:

### Professional Players:
```bash
python quick_lookup.py TenZ#SEN
python quick_lookup.py s0m#100T
python quick_lookup.py Asuna#100T
python quick_lookup.py FNS#NRG
```

### Content Creators:
```bash
python quick_lookup.py Tarik#1337
python quick_lookup.py Shroud#9999
```

### Your Own Account:
```bash
python quick_lookup.py YourName#TAG
```

---

## 🐛 Troubleshooting

### "No stats found"
- Player name may be incorrect
- Player may have private profile
- Player may not have played competitive

### "Connection error"
- Make sure Valorant client is running
- Make sure you're logged in
- Check your internet connection

### "Module not found"
- Make sure you're in the correct directory
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### "Region error"
If you're not in EU region, edit the script and change:
```python
client = Client(region='eu')  # Change to: 'na', 'ap', 'kr'
```

---

## 📊 Expected Performance

### Quick Lookup:
- **First lookup:** 1-2 seconds
- **Cached lookup:** < 0.1 seconds

### Full Test Suite:
- **Direct PD API:** 0.5-1.5 seconds
- **Cached:** < 0.01 seconds
- **Henrik's API:** 2-3 seconds

### Speed Improvements:
- ✅ **2-3x faster** than Henrik's API alone
- ✅ **100-300x faster** with caching
- ✅ **Reliable** (fewer rate limit errors)

---

## 💡 Tips

1. **First lookup is always slower** - Building the cache
2. **Subsequent lookups are instant** - Using cached data
3. **Cache persists** until script restarts
4. **Try the same player twice** to see caching in action
5. **Check the console** for detailed API logs

---

## 🎉 What Success Looks Like

### Quick Lookup Success:
```
✅ Connected! (Region: eu)
✅ Stats retrieved successfully!
```

### Full Test Success:
```
✅ Direct PD API is 2.5x faster than Henrik's API
✅ Cached retrieval is 284x faster than first load
✅ ALL TESTS COMPLETED!
```

---

## 📞 Need Help?

If tests fail:
1. Check that Valorant is running and you're logged in
2. Verify your region setting in the script
3. Check the console for error messages
4. Try a different player name
5. Make sure all dependencies are installed

---

**Happy testing! 🚀**

Once you verify it works with these tools, your main GUI app will work the same way (but even better in actual matches)!

