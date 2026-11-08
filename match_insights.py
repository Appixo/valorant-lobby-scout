"""
Extra information about players in the current match:
parties (who queued together), smurf warning signs and earlier encounters.

Everything here works on plain data so it can be tested without the game running.
"""

import base64
import json
from datetime import datetime

RANK_TIERS = {
    "Iron 1": 3, "Iron 2": 4, "Iron 3": 5,
    "Bronze 1": 6, "Bronze 2": 7, "Bronze 3": 8,
    "Silver 1": 9, "Silver 2": 10, "Silver 3": 11,
    "Gold 1": 12, "Gold 2": 13, "Gold 3": 14,
    "Platinum 1": 15, "Platinum 2": 16, "Platinum 3": 17,
    "Diamond 1": 18, "Diamond 2": 19, "Diamond 3": 20,
    "Ascendant 1": 21, "Ascendant 2": 22, "Ascendant 3": 23,
    "Immortal 1": 24, "Immortal 2": 25, "Immortal 3": 26,
    "Radiant": 27,
}

PARTY_SYMBOLS = "①②③④⑤⑥⑦⑧⑨"


def extract_players(match_info):
    """
    Return the player entries of a pregame or in-game match, each with a TeamID.
    In agent select, players sit under AllyTeam and only the team has a TeamID.
    """
    if match_info.get('Players'):
        return match_info['Players']

    players = []
    for team in (match_info.get('AllyTeam'), match_info.get('EnemyTeam')):
        if not team:
            continue
        for player in team.get('Players', []):
            players.append({**player, 'TeamID': player.get('TeamID') or team.get('TeamID')})
    return players


# --- Parties -----------------------------------------------------------------

def decode_presence(presence):
    """Decode the base64 'private' blob of a chat presence"""
    private = presence.get('private')
    if not private:
        return {}
    try:
        return json.loads(base64.b64decode(private + '=' * (-len(private) % 4)))
    except (ValueError, TypeError):
        return {}


def presence_party_id(private):
    """Party ID from a decoded presence (supports the old flat and newer nested formats)"""
    return private.get('partyId') or (private.get('partyPresenceData') or {}).get('partyId')


def presence_parties(presences, match_puuids):
    """
    Parties visible in chat presences (only you and your friends).

    Args:
        presences: Raw response of the local /chat/v4/presences endpoint
        match_puuids: PUUIDs of the players in the current match

    Returns:
        List of sets of PUUIDs, one per party of 2 or more
    """
    match_puuids = {p.lower() for p in match_puuids}
    parties = {}
    for presence in (presences or {}).get('presences', []):
        puuid = (presence.get('puuid') or '').lower()
        if presence.get('product') != 'valorant' or puuid not in match_puuids:
            continue
        party_id = presence_party_id(decode_presence(presence))
        if party_id:
            parties.setdefault(party_id, set()).add(puuid)
    return [members for members in parties.values() if len(members) >= 2]


def number_parties(confirmed_groups, recent_links, match_puuids, my_puuid=None):
    """
    Number the parties in a match.

    Args:
        confirmed_groups: Parties known for sure (from presences)
        recent_links: (puuid, puuid) pairs that were in the same party in a recent match
        match_puuids: PUUIDs of the players in the current match
        my_puuid: Your PUUID; your party gets number 1

    Returns:
        ({puuid: party number}, set of PUUIDs whose party is confirmed)
    """
    match_puuids = {p.lower() for p in match_puuids}
    parent = {p: p for p in match_puuids}

    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def union(a, b):
        a, b = a.lower(), b.lower()
        if a in parent and b in parent:
            parent[find(a)] = find(b)

    confirmed = set()
    for group in confirmed_groups:
        group = sorted(group)
        confirmed.update(group)
        for other in group[1:]:
            union(group[0], other)
    for a, b in recent_links:
        union(a, b)

    groups = {}
    for p in match_puuids:
        groups.setdefault(find(p), []).append(p)
    parties = [sorted(members) for members in groups.values() if len(members) >= 2]
    my_puuid = (my_puuid or '').lower()
    parties.sort(key=lambda members: (my_puuid not in members, members[0]))

    numbers = {puuid: number for number, members in enumerate(parties, 1) for puuid in members}
    return numbers, confirmed & set(numbers)


def find_parties(presences, match_puuids, my_puuid=None):
    """{puuid: party number} from presences alone"""
    return number_parties(presence_parties(presences, match_puuids), [], match_puuids, my_puuid)[0]


def party_symbol(number):
    return PARTY_SYMBOLS[number - 1] if 1 <= number <= len(PARTY_SYMBOLS) else str(number)


# --- Smurf warning signs ------------------------------------------------------

def smurf_reasons(level, current_rank, peak_rank, win_rate, games, kd, recent_matches):
    """
    List the reasons an account looks like a smurf (empty list if nothing stands out).
    win_rate is a fraction (0.55); unknown values should be 0.
    """
    reasons = []
    tier = RANK_TIERS.get(current_rank, 0)
    peak_tier = RANK_TIERS.get(peak_rank, 0)

    if level and tier and ((level < 50 and tier >= RANK_TIERS["Platinum 1"]) or
                           (level < 100 and tier >= RANK_TIERS["Ascendant 1"])):
        reasons.append(f"Level {level} account already {current_rank}")

    if tier and peak_tier - tier >= 6:
        reasons.append(f"Peaked {peak_rank}, now {current_rank}")

    if games >= 15 and win_rate >= 0.70:
        reasons.append(f"Won {win_rate * 100:.0f}% of {games} games this act")

    if recent_matches >= 3 and kd >= 1.8:
        reasons.append(f"K/D {kd:.2f} over last {recent_matches} matches")

    return reasons


# --- Earlier encounters -------------------------------------------------------

def _usable_name(name):
    """False for placeholders from failed or hidden name lookups (#0000 itself is a real tag)"""
    return bool(name) and not name.startswith(('Unknown#', 'Player_'))


def build_name_ledger(history, friends=()):
    """
    {puuid: {'name', 'source', 'timestamp'}} for players you already know by name.

    Built only from your saved matches and your friends list; a player who has never
    appeared without Incognito stays unknown.
    """
    ledger = {}
    for match in sorted(history or [], key=lambda m: m.get('timestamp', '')):
        for player in match.get('players', []):
            puuid = (player.get('puuid') or '').lower()
            name = (player.get('name') or '').strip()
            if puuid and _usable_name(name):
                ledger[puuid] = {'name': name, 'source': 'match',
                                 'timestamp': match.get('timestamp', '')}

    for puuid, name in friends:
        puuid = (puuid or '').lower()
        if puuid and _usable_name(name):
            ledger[puuid] = {'name': name, 'source': 'friend', 'timestamp': ''}
    return ledger


def friend_names(friends_response):
    """(puuid, 'Riot ID#tag') pairs from the client's own friends list"""
    out = []
    for entry in (friends_response or {}).get('friends', []):
        puuid = entry.get('gameIdentifier') or entry.get('game_id') or ''
        name = entry.get('gameName') or entry.get('name') or ''
        tag = entry.get('tagLine') or entry.get('tag') or ''
        if puuid and name:
            out.append((puuid, f"{name}#{tag or '0000'}"))
    return out


def find_encounters(history, puuid, name, exclude_match_ids=(), my_puuid=None, my_name=None):
    """
    Earlier matches (newest first) from match_history.json that included this player.
    Older history entries have no PUUIDs, so those are matched by Riot ID.

    Returns:
        List of {'timestamp', 'map_name', 'agent', 'same_team'} (same_team is None when unknown)
    """
    puuid = (puuid or '').lower()
    name_key = name.lower() if _usable_name(name) else None
    encounters = []

    for match in history:
        if match.get('match_id') in exclude_match_ids:
            continue
        players = match.get('players', [])

        entry = next((p for p in players if p.get('puuid') and p['puuid'].lower() == puuid), None)
        if entry is None and name_key:
            entry = next((p for p in players if not p.get('puuid') and p.get('name', '').lower() == name_key), None)
        if entry is None:
            continue

        my_team = match.get('my_team')
        if not my_team:
            me = next((p for p in players
                       if (my_puuid and (p.get('puuid') or '').lower() == my_puuid.lower())
                       or (my_name and _usable_name(my_name) and p.get('name', '').lower() == my_name.lower())), None)
            my_team = me.get('team') if me else None

        encounters.append({
            'timestamp': match.get('timestamp', ''),
            'map_name': match.get('map_name', 'Unknown Map'),
            'agent': entry.get('agent', 'Unknown'),
            'same_team': (entry.get('team') == my_team) if my_team else None,
        })

    encounters.sort(key=lambda e: e['timestamp'], reverse=True)
    return encounters


def time_ago(timestamp, now=None):
    """'today', 'yesterday', '5 days ago', '3 months ago' for an ISO timestamp"""
    try:
        days = ((now or datetime.now()) - datetime.fromisoformat(timestamp)).days
    except (ValueError, TypeError):
        return "some time ago"
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 60:
        return f"{days} days ago"
    return f"{days // 30} months ago"


def describe_encounters(encounters):
    """One-line summary like 'Met 3× before · last 2 days ago on Lotus (teammate, Jett)'"""
    if not encounters:
        return ""
    last = encounters[0]
    side = {True: "teammate", False: "opponent"}.get(last['same_team'])
    details = ", ".join(x for x in (side, last['agent'] if last['agent'] != 'Unknown' else None) if x)
    text = f"Met {len(encounters)}× before · last {time_ago(last['timestamp'])} on {last['map_name']}"
    return f"{text} ({details})" if details else text
