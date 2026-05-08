"""Python 2.7 adapter for Baseball-GDT-Bot-GUI.

Drop this file next to src/main.py and src/editor.py in the legacy bot.
The adapter is fail-closed: if anything goes wrong, return the original title.
"""

from datetime import datetime, timedelta
import urllib2

try:
    import simplejson as json
except ImportError:
    import json

from theee_title import replace_prefix_if_yankees_won

YANKEES_TEAM_ID = 147
YANKEES_TEAM_NAME = "Yankees"
DEFAULT_GAME_TYPES = "R,F,D,L,W"
STATS_API_SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"


def _download_json(url, timeout=20):
    response = urllib2.urlopen(url, timeout=timeout)
    return json.load(response)


def _legacy_linescore_url(game_dir):
    if not game_dir.endswith("/"):
        game_dir += "/"
    return game_dir + "linescore.json"


def _legacy_game_was_yankees_win(game_dir):
    """Return True only when the legacy linescore shows a final Yankees win."""
    try:
        data = _download_json(_legacy_linescore_url(game_dir), timeout=20)
        game = data.get("data", {}).get("game", {})

        status = str(game.get("status", ""))
        if status not in ("Game Over", "Final", "Completed Early"):
            return False

        home_name = game.get("home_team_name")
        away_name = game.get("away_team_name")
        home_runs = int(game.get("home_team_runs", 0))
        away_runs = int(game.get("away_team_runs", 0))

        if home_name == YANKEES_TEAM_NAME:
            return home_runs > away_runs
        if away_name == YANKEES_TEAM_NAME:
            return away_runs > home_runs
        return False
    except Exception:
        return False


def _get_score(game, side):
    return int(game.get("teams", {}).get(side, {}).get("score", 0))


def _is_final(game):
    status = game.get("status", {})
    return status.get("abstractGameState") == "Final"


def _yankees_won_statsapi_game(game, team_id):
    home_team_id = game.get("teams", {}).get("home", {}).get("team", {}).get("id")
    away_team_id = game.get("teams", {}).get("away", {}).get("team", {}).get("id")

    if home_team_id == team_id:
        return _get_score(game, "home") > _get_score(game, "away")
    if away_team_id == team_id:
        return _get_score(game, "away") > _get_score(game, "home")
    return False


def get_yankees_win_streak(team_id=YANKEES_TEAM_ID, days_back=45, game_types=DEFAULT_GAME_TYPES):
    """Count backward from the latest final Yankees game until the first loss."""
    today = datetime.utcnow().date()
    start = today - timedelta(days=days_back)

    url = (
        STATS_API_SCHEDULE_URL
        + "?sportId=1"
        + "&teamId=" + str(team_id)
        + "&startDate=" + start.strftime("%Y-%m-%d")
        + "&endDate=" + today.strftime("%Y-%m-%d")
        + "&gameTypes=" + game_types
    )

    data = _download_json(url, timeout=20)
    games = []
    for date_block in data.get("dates", []):
        for game in date_block.get("games", []):
            if _is_final(game):
                games.append(game)

    games.sort(key=lambda g: g.get("gameDate", ""), reverse=True)

    streak = 0
    for game in games:
        if _yankees_won_statsapi_game(game, team_id):
            streak += 1
        else:
            break

    return streak


def apply_theee_to_postgame_title(game_dir, posttitle):
    """
    Safe drop-in call for Baseball-GDT-Bot-GUI postgame title creation.

    Returns the original title unless the current game is confirmed as a
    final Yankees win and the current streak can be calculated.
    """
    try:
        yankees_won = _legacy_game_was_yankees_win(game_dir)
        if not yankees_won:
            return posttitle

        streak = get_yankees_win_streak()
        if streak < 1:
            return posttitle

        return replace_prefix_if_yankees_won(posttitle, streak, yankees_won=True)
    except Exception:
        return posttitle
