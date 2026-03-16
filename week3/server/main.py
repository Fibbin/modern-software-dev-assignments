# -*- coding: utf-8 -*-
from __future__ import annotations


import os
import random
import time
from typing import List, Dict, Any

import requests
from fastmcp import FastMCP


"""
Spotify MCP Server (FastMCP)

Environment variables required:
- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET
"""


mcp = FastMCP("Spotify Genre MCP Server")


SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"


_access_token: str | None = None
_token_expires_at: float | None = None


def _get_spotify_credentials() -> tuple[str, str]:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in environment."
        )
    return client_id, client_secret


def _get_access_token() -> str:
    global _access_token, _token_expires_at

    # Reuse token if still valid for at least 30 seconds
    now = time.time()
    if _access_token and _token_expires_at and now < _token_expires_at - 30:
        return _access_token

    client_id, client_secret = _get_spotify_credentials()
    resp = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=8,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed to obtain Spotify access token: {resp.status_code} {resp.text}"
        )
    data = resp.json()
    _access_token = data["access_token"]
    expires_in = data.get("expires_in", 3600)
    _token_expires_at = now + float(expires_in)
    return _access_token


def _spotify_get(path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    token = _get_access_token()
    resp = requests.get(
        f"{SPOTIFY_API_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=8,
    )

    if resp.status_code == 429:
        # Rate limited  surface a friendly error with Retry-After if present
        retry_after = resp.headers.get("Retry-After", "unknown")
        raise RuntimeError(f"Spotify rate limit exceeded. Retry after {retry_after} seconds.")

    if not resp.ok:
        raise RuntimeError(f"Spotify API error {resp.status_code}: {resp.text}")

    return resp.json()


GENRE_SEEDS: List[str] = [
    "acoustic",
    "afrobeat",
    "alt-rock",
    "alternative",
    "ambient",
    "anime",
    "black-metal",
    "bluegrass",
    "blues",
    "bossanova",
    "brazil",
    "breakbeat",
    "british",
    "cantopop",
    "chicago-house",
    "children",
    "chill",
    "classical",
    "club",
    "comedy",
    "country",
    "dance",
    "dancehall",
    "death-metal",
    "deep-house",
    "detroit-techno",
    "disco",
    "disney",
    "drum-and-bass",
    "dub",
    "dubstep",
    "edm",
    "electro",
    "electronic",
    "emo",
    "folk",
    "forro",
    "french",
    "funk",
    "garage",
    "german",
    "gospel",
    "goth",
    "grindcore",
    "groove",
    "grunge",
    "guitar",
    "happy",
    "hard-rock",
    "hardcore",
    "hardstyle",
    "heavy-metal",
    "hip-hop",
    "holidays",
    "honky-tonk",
    "house",
    "idm",
    "indian",
    "indie",
    "indie-pop",
    "industrial",
    "iranian",
    "j-dance",
    "j-idol",
    "j-pop",
    "j-rock",
    "jazz",
    "k-pop",
    "kids",
    "latin",
    "latino",
    "malay",
    "mandopop",
    "metal",
    "metal-misc",
    "metalcore",
    "minimal-techno",
    "movies",
    "mpb",
    "new-age",
    "new-release",
    "opera",
    "pagode",
    "party",
    "philippines-opm",
    "piano",
    "pop",
    "pop-film",
    "post-dubstep",
    "power-pop",
    "progressive-house",
    "psych-rock",
    "punk",
    "punk-rock",
    "r-n-b",
    "rainy-day",
    "reggae",
    "reggaeton",
    "road-trip",
    "rock",
    "rock-n-roll",
    "rockabilly",
    "romance",
    "sad",
    "salsa",
    "samba",
    "sertanejo",
    "show-tunes",
    "singer-songwriter",
    "ska",
    "sleep",
    "songwriter",
    "soul",
    "soundtracks",
    "spanish",
    "study",
    "summer",
    "swedish",
    "synth-pop",
    "tango",
    "techno",
    "trance",
    "trip-hop",
    "turkish",
    "work-out",
    "world-music",
]


@mcp.tool
def list_genres(keyword: str | None = None) -> List[str]:
    """
    Tool 3: List all available genres (optional keyword filter).

    - Does not call Spotify API; returns hardcoded official genre seeds.
    - If keyword is provided, returns only genres containing that substring (case-insensitive).
    """
    genres = sorted(GENRE_SEEDS)
    if keyword:
        k = keyword.lower()
        genres = [g for g in genres if k in g.lower()]
    return genres


@mcp.tool
def search_songs(track_name: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search songs by track name. Returns matching tracks with song name, artist name(s), and track_id.

    - Calls Spotify /v1/search with q=track_name, type=track.
    - Does not fetch artist details or genres; only returns search results.
    """
    if not track_name.strip():
        raise ValueError("track_name must not be empty.")

    data = _spotify_get(
        "/search",
        params={
            "q": track_name,
            "type": "track",
            "limit": int(limit),
        },
    )

    items = data.get("tracks", {}).get("items", [])
    tracks: List[Dict[str, Any]] = []
    for t in items:
        artists_str = ", ".join(a.get("name", "") for a in t.get("artists", []))
        tracks.append(
            {
                "track_id": t.get("id"),
                "name": t.get("name"),
                "artists": artists_str,
            }
        )

    out: Dict[str, Any] = {"query": track_name, "tracks": tracks}
    if not tracks:
        out["message"] = "No tracks found for this name."
    return out


@mcp.tool
def search_songs_by_genre(genre: str, limit: int = 10) -> Dict[str, Any]:
    """
    Tool 2: Search songs by genre.

    - Use Spotify /v1/search with q=genre:"{genre}".
    - Random offset to return up to 10 "random" tracks (if fewer than 10, return all).
    """
    if not genre.strip():
        raise ValueError("genre must not be empty.")

    normalized = genre.lower().replace(" ", "-")
    if normalized not in GENRE_SEEDS:
        # Hint: client may call list_genres first to see valid genres
        return {
            "genre": genre,
            "normalized": normalized,
            "tracks": [],
            "error": "Unsupported genre. Call list_genres first to see valid Spotify genres.",
        }

    # Spotify search allows limit up to 50; we can randomize offset in first 5 pages
    per_page = min(int(limit), 10)
    max_offset = max(0, 5 * per_page - per_page)
    offset = random.randint(0, max_offset) if max_offset > 0 else 0

    query = f'genre:"{normalized}"'
    data = _spotify_get(
        "/search",
        params={
            "q": query,
            "type": "track",
            "limit": per_page,
            "offset": offset,
        },
    )

    items = data.get("tracks", {}).get("items", []) or []
    tracks: List[Dict[str, Any]] = []
    for t in items:
        artists = ", ".join(a.get("name", "") for a in t.get("artists", []))
        tracks.append(
            {
                "id": t.get("id"),
                "name": t.get("name"),
                "artists": artists,
                "uri": t.get("uri"),
            }
        )

    return {
        "genre": genre,
        "normalized": normalized,
        "limit": per_page,
        "offset": offset,
        "tracks": tracks,
    }


if __name__ == "__main__":
    # Default to stdio transport for MCP clients like Claude / Cursor
    mcp.run()

