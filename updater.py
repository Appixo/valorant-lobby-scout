"""Checks GitHub for a newer version of the app (bump version.json on main to notify users)"""
import json
import os
import re

import requests

REPO_URL = "https://github.com/Appixo/valorant-lobby-scout"
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/Appixo/valorant-lobby-scout/main/version.json"
LOCAL_VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.json")


def parse_version(text):
    """'2.10.1' -> (2, 10, 1), so versions compare numerically"""
    return tuple(int(part) for part in re.findall(r"\d+", str(text or "")))


def local_version():
    try:
        with open(LOCAL_VERSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("version", "0")
    except (OSError, ValueError):
        return "0"


def check_for_update(current=None, timeout=5):
    """{'version', 'notes'} when GitHub has a newer version, else None (also when offline)"""
    current = current or local_version()
    try:
        response = requests.get(REMOTE_VERSION_URL, timeout=timeout)
        if response.status_code != 200:
            return None
        remote = response.json()
    except (requests.RequestException, ValueError):
        return None

    if parse_version(remote.get("version")) > parse_version(current):
        return {"version": str(remote["version"]), "notes": str(remote.get("notes") or "")}
    return None
