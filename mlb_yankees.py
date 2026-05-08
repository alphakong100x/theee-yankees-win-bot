"""MLB Stats API helper for Yankees final games and active win streak."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import requests

TEAM_ID = 147
SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"
DEFAULT_GAME_TYPES = ("R", "F", "D", "L", "W")


@dataclass(frozen=True)
class YankeesGameResult:
    game_pk: int
    opponent: str
    yankees_score: int
    opponent_score: int
    game_date: str
    game_datetime: str
    yankees_won: bool
    game_type: str


def normalize_game_types(game_types: Iterable[str] | str | None = None) -> tuple[str, ...]:
    """Return clean MLB game type codes."""
    if game_types is None:
        return DEFAULT_GAME_TYPES
    if isinstance(game_types, str):
        raw_items = game_types.split(",")
    else:
        raw_items = list(game_types)
    cleaned = tuple(item.strip().upper() for item in raw_items if item and item.strip())
    return cleaned or DEFAULT_GAME_TYPES


def fetch_recent_yankees_games(
    days_back: int = 150,
    game_types: Iterable[str] | str | None = None,
) -> list[dict[str, Any]]:
    """Fetch recent Yankees games from MLB Stats API."""
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=max(7, days_back))
    selected_game_types = normalize_game_types(game_types)

    params = {
        "sportId": 1,
        "teamId": TEAM_ID,
        "startDate": start_date.isoformat(),
        "endDate": today.isoformat(),
        "gameTypes": ",".join(selected_game_types),
        "hydrate": "team,linescore",
    }
    response = requests.get(SCHEDULE_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()

    games: list[dict[str, Any]] = []
    for day in payload.get("dates", []):
        for game in day.get("games", []):
            games.append(game)
    return games


def is_final(game: dict[str, Any]) -> bool:
    """Return true for completed MLB games."""
    status = game.get("status", {})
    return status.get("abstractGameState") == "Final" or status.get("detailedState") == "Final"


def summarize_yankees_game(game: dict[str, Any]) -> YankeesGameResult | None:
    """Convert one MLB game object into the small result this bot needs."""
    teams = game.get("teams", {})
    home = teams.get("home", {})
    away = teams.get("away", {})
    home_team = home.get("team", {})
    away_team = away.get("team", {})

    home_id = home_team.get("id")
    away_id = away_team.get("id")
    if home_id != TEAM_ID and away_id != TEAM_ID:
        return None

    yankees_side = home if home_id == TEAM_ID else away
    opponent_side = away if home_id == TEAM_ID else home

    yankees_score = int(yankees_side.get("score", 0))
    opponent_score = int(opponent_side.get("score", 0))
    opponent_name = opponent_side.get("team", {}).get("teamName") or opponent_side.get("team", {}).get("name") or "Opponent"

    return YankeesGameResult(
        game_pk=int(game.get("gamePk")),
        opponent=str(opponent_name),
        yankees_score=yankees_score,
        opponent_score=opponent_score,
        game_date=str(game.get("officialDate") or game.get("gameDate", "")[:10]),
        game_datetime=str(game.get("gameDate", "")),
        yankees_won=yankees_score > opponent_score,
        game_type=str(game.get("gameType", "")),
    )


def sorted_final_results(games: list[dict[str, Any]]) -> list[YankeesGameResult]:
    """Return completed Yankees games, newest first."""
    results: list[YankeesGameResult] = []
    for game in games:
        if not is_final(game):
            continue
        result = summarize_yankees_game(game)
        if result is not None:
            results.append(result)
    return sorted(results, key=lambda item: item.game_datetime, reverse=True)


def current_win_status(games: list[dict[str, Any]]) -> tuple[YankeesGameResult | None, int]:
    """Return latest final result and active Yankees win streak."""
    results = sorted_final_results(games)
    if not results:
        return None, 0

    latest = results[0]
    if not latest.yankees_won:
        return latest, 0

    streak = 0
    for result in results:
        if result.yankees_won:
            streak += 1
            continue
        break
    return latest, streak


def live_current_win_status(
    days_back: int = 150,
    game_types: Iterable[str] | str | None = None,
) -> tuple[YankeesGameResult | None, int]:
    """Fetch MLB data and return latest result plus active Yankees win streak."""
    games = fetch_recent_yankees_games(days_back=days_back, game_types=game_types)
    return current_win_status(games)
