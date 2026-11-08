"""
Agent and map names for Valorant.

Names are loaded from valorant-api.com so new agents/maps show up without code
changes. Results are cached in game_data_cache.json; if the API and cache are
both unavailable, the built-in lists below are used.
"""

import json
import os
import time

import requests

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_data_cache.json")
CACHE_MAX_AGE = 24 * 60 * 60  # Refresh once a day
API_TIMEOUT = 5

# Fallback lists (up to date as of November 2026)
DEFAULT_AGENTS = {
    "41fb69c1-4189-7b37-f117-bcaf1e96f1bf": "Astra",
    "5f8d3a7f-467b-97f3-062c-13acf203c006": "Breach",
    "9f0d8ba9-4140-b941-57d3-a7ad57c6b417": "Brimstone",
    "22697a3d-45bf-8dd7-4fec-84a9e28c69d7": "Chamber",
    "1dbf2edd-4729-0984-3115-daa5eed44993": "Clove",
    "117ed9e3-49f3-6512-3ccf-0cada7e3823b": "Cypher",
    "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235": "Deadlock",
    "dade69b4-4f5a-8528-247b-219e5a1facd6": "Fade",
    "e370fa57-4757-3604-3648-499e1f642d3f": "Gekko",
    "95b78ed7-4637-86d9-7e41-71ba8c293152": "Harbor",
    "ddd5a15c-4fbe-42fa-3789-11a55ca5ee04": "Hush",
    "0e38b510-41a8-5780-5e8f-568b2a4f2d6c": "Iso",
    "add6443a-41bd-e414-f6ad-e58d267f4e95": "Jett",
    "601dbbe7-43ce-be57-2a40-4abd24953621": "KAY/O",
    "1e58de9c-4950-5125-93e9-a0aee9f98746": "Killjoy",
    "7c8a4701-4de6-9355-b254-e09bc2a34b72": "Miks",
    "bb2a4828-46eb-8cd1-e765-15848195d751": "Neon",
    "8e253930-4c05-31dd-1b6c-968525494517": "Omen",
    "eb93336a-449b-9c1b-0a54-a891f7921d69": "Phoenix",
    "f94c3b30-42be-e959-889c-5aa313dba261": "Raze",
    "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc": "Reyna",
    "569fdd95-4d10-43ab-ca70-79becc718b46": "Sage",
    "6f2a04ca-43e0-be17-7f36-b3908627744d": "Skye",
    "320b2a48-4d9b-a075-30f1-1f93a9b638fa": "Sova",
    "b444168c-4e35-8076-db47-ef9bf368f384": "Tejo",
    "92eeef5d-43b5-1d4a-8d03-b3927a09034b": "Veto",
    "707eab51-4836-f488-046a-cda6bf494859": "Viper",
    "efba5359-4016-a1e5-7626-b1ae76895940": "Vyse",
    "df1cb487-4902-002e-5c17-d28e83e78588": "Waylay",
    "7f94d92c-4234-0a36-9646-3a87eb8b5c89": "Yoru",
}

# Keyed by the MapID the client reports (e.g. /Game/Maps/Jam/Jam)
DEFAULT_MAPS = {
    "/Game/Maps/Infinity/Infinity": "Abyss",
    "/Game/Maps/Ascent/Ascent": "Ascent",
    "/Game/Maps/NPEV2/NPEV2": "Basic Training",
    "/Game/Maps/Duality/Duality": "Bind",
    "/Game/Maps/Foxtrot/Foxtrot": "Breeze",
    "/Game/Maps/Rook/Rook": "Corrode",
    "/Game/Maps/HURM/HURM_Alley/HURM_Alley": "District",
    "/Game/Maps/HURM/HURM_Helix/HURM_Helix": "Drift",
    "/Game/Maps/Canyon/Canyon": "Fracture",
    "/Game/Maps/AbilityDraft/AbilityDraft": "Gauntlet",
    "/Game/Maps/HURM/HURM_HighTide/HURM_HighTide": "Glitch",
    "/Game/Maps/Triad/Triad": "Haven",
    "/Game/Maps/Port/Port": "Icebox",
    "/Game/Maps/HURM/HURM_Bowl/HURM_Bowl": "Kasbah",
    "/Game/Maps/Jam/Jam": "Lotus",
    "/Game/Maps/Pitt/Pitt": "Pearl",
    "/Game/Maps/HURM/HURM_Yard/HURM_Yard": "Piazza",
    "/Game/Maps/Duel/Duel_1/Skirmish_A": "Skirmish A",
    "/Game/Maps/Duel/Duel_2/Skirmish_B": "Skirmish B",
    "/Game/Maps/Duel/Duel_3/Skirmish_C": "Skirmish C",
    "/Game/Maps/Duel/Duel_Platform/Skirmish_D": "Skirmish D",
    "/Game/Maps/Duel/Duel_Heady/Skirmish_E": "Skirmish E",
    "/Game/Maps/Bonsai/Bonsai": "Split",
    "/Game/Maps/Plummet/Plummet": "Summit",
    "/Game/Maps/Juliett/Juliett": "Sunset",
    "/Game/Maps/Poveglia/Range": "The Range",
    "/Game/Maps/PovegliaV2/RangeV2": "The Range",
}

_data = None


def _fetch_from_api():
    """Download current agent and map names from valorant-api.com"""
    agents_resp = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true", timeout=API_TIMEOUT)
    maps_resp = requests.get("https://valorant-api.com/v1/maps", timeout=API_TIMEOUT)
    seasons_resp = requests.get("https://valorant-api.com/v1/seasons", timeout=API_TIMEOUT)
    agents_resp.raise_for_status()
    maps_resp.raise_for_status()
    seasons_resp.raise_for_status()

    agents = {a["uuid"].lower(): a["displayName"] for a in agents_resp.json()["data"]}
    maps = {m["mapUrl"]: m["displayName"] for m in maps_resp.json()["data"] if m.get("mapUrl")}
    seasons = {s["uuid"].lower(): s["startTime"] for s in seasons_resp.json()["data"] if s.get("startTime")}
    if not agents or not maps:
        raise ValueError("Empty agent or map list from API")
    return {"timestamp": time.time(), "agents": agents, "maps": maps, "seasons": seasons}


def _load():
    global _data
    if _data is not None:
        return _data

    cached = None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
    except (OSError, ValueError):
        pass

    if cached and "seasons" in cached and time.time() - cached.get("timestamp", 0) < CACHE_MAX_AGE:
        _data = cached
    else:
        try:
            _data = _fetch_from_api()
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(_data, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not update agent/map list from valorant-api.com: {e}")
            _data = cached or {"timestamp": 0, "agents": {}, "maps": {}, "seasons": {}}

    # Built-in lists fill any gaps; API/cache entries take priority
    _data["agents"] = {**DEFAULT_AGENTS, **_data.get("agents", {})}
    _data["maps"] = {**DEFAULT_MAPS, **_data.get("maps", {})}
    return _data


def get_agents():
    """Return {agent_uuid: name} for all playable agents"""
    return _load()["agents"]


def get_agent_name(agent_id, default="Unknown"):
    if not agent_id:
        return default
    return get_agents().get(agent_id.lower().strip(), default)


def get_map_name(map_id, default="Unknown Map"):
    """Convert a MapID like /Game/Maps/Jam/Jam (or codename like Jam) to its name"""
    if not map_id:
        return default
    maps = _load()["maps"]
    if map_id in maps:
        return maps[map_id]

    # Match on codename alone, e.g. "Jam" or a path with different casing
    codename = map_id.rstrip("/").split("/")[-1].lower()
    for url, name in maps.items():
        if url.split("/")[-1].lower() == codename:
            return name
    return default


# Ascendant was added in Episode 5 Act 1; before that tiers 21-24 were Immortal 1-3 and Radiant.
# valorant-api.com lists E5A1 as starting 2022-06-21T00:00:00Z, so it must not count as an old act.
ASCENDANT_RELEASE = "2022-06-21"


def normalize_tier(tier, season_id):
    """Convert a competitive tier from an old season to the current tier numbering"""
    start = _load().get("seasons", {}).get((season_id or "").lower())
    if start and start[:10] < ASCENDANT_RELEASE and tier > 20:
        return tier + 3
    return tier


def latest_season_id(season_ids):
    """Pick the most recent season from a list of season IDs (by start date)"""
    starts = _load().get("seasons", {})
    return max(season_ids, key=lambda sid: starts.get(sid.lower(), ""))
