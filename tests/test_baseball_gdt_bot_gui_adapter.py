"""No-network tests for the Baseball-GDT-Bot-GUI adapter.

These tests run under Python 3 by shimming urllib2 before importing the
Python 2.7 adapter. The adapter itself is written to run inside the legacy bot.
"""

import importlib
import sys
import types


def load_adapter():
    urllib2 = types.ModuleType("urllib2")
    urllib2.urlopen = lambda *args, **kwargs: None
    sys.modules["urllib2"] = urllib2

    if "baseball_gdt_bot_gui_adapter" in sys.modules:
        del sys.modules["baseball_gdt_bot_gui_adapter"]

    return importlib.import_module("baseball_gdt_bot_gui_adapter")


def make_legacy_linescore(home, away, home_runs, away_runs, status="Final"):
    return {
        "data": {
            "game": {
                "home_team_name": home,
                "away_team_name": away,
                "home_team_runs": str(home_runs),
                "away_team_runs": str(away_runs),
                "status": status,
            }
        }
    }


def make_statsapi_game(date, home_id, away_id, home_score, away_score, final=True):
    return {
        "gameDate": date,
        "status": {"abstractGameState": "Final" if final else "Live"},
        "teams": {
            "home": {"team": {"id": home_id}, "score": home_score},
            "away": {"team": {"id": away_id}, "score": away_score},
        },
    }


def test_legacy_linescore_url():
    adapter = load_adapter()
    assert adapter._legacy_linescore_url("http://example/gid_1") == "http://example/gid_1/linescore.json"
    assert adapter._legacy_linescore_url("http://example/gid_1/") == "http://example/gid_1/linescore.json"


def test_legacy_yankees_win_detection_home_and_away():
    adapter = load_adapter()

    adapter._download_json = lambda url, timeout=20: make_legacy_linescore("Yankees", "Red Sox", 5, 3)
    assert adapter._legacy_game_was_yankees_win("x") is True

    adapter._download_json = lambda url, timeout=20: make_legacy_linescore("Yankees", "Red Sox", 3, 5)
    assert adapter._legacy_game_was_yankees_win("x") is False

    adapter._download_json = lambda url, timeout=20: make_legacy_linescore("Red Sox", "Yankees", 3, 5)
    assert adapter._legacy_game_was_yankees_win("x") is True

    adapter._download_json = lambda url, timeout=20: make_legacy_linescore("Red Sox", "Yankees", 5, 3)
    assert adapter._legacy_game_was_yankees_win("x") is False


def test_legacy_detection_ignores_non_final_games_and_fails_closed():
    adapter = load_adapter()

    adapter._download_json = lambda url, timeout=20: make_legacy_linescore("Yankees", "Red Sox", 5, 3, status="In Progress")
    assert adapter._legacy_game_was_yankees_win("x") is False

    def fail_download(url, timeout=20):
        raise RuntimeError("network down")

    adapter._download_json = fail_download
    assert adapter._legacy_game_was_yankees_win("x") is False


def test_win_streak_stops_at_first_loss():
    adapter = load_adapter()

    adapter._download_json = lambda url, timeout=20: {
        "dates": [
            {
                "games": [
                    make_statsapi_game("2026-05-05T01:00:00Z", 147, 111, 5, 3),
                    make_statsapi_game("2026-05-04T01:00:00Z", 111, 147, 2, 4),
                    make_statsapi_game("2026-05-03T01:00:00Z", 147, 111, 2, 3),
                    make_statsapi_game("2026-05-02T01:00:00Z", 147, 111, 8, 1),
                ]
            }
        ]
    }

    assert adapter.get_yankees_win_streak() == 2


def test_latest_loss_resets_streak_to_zero():
    adapter = load_adapter()

    adapter._download_json = lambda url, timeout=20: {
        "dates": [
            {
                "games": [
                    make_statsapi_game("2026-05-06T01:00:00Z", 147, 111, 2, 3),
                    make_statsapi_game("2026-05-05T01:00:00Z", 147, 111, 5, 3),
                ]
            }
        ]
    }

    assert adapter.get_yankees_win_streak() == 0


def test_live_game_is_ignored_for_streak():
    adapter = load_adapter()

    adapter._download_json = lambda url, timeout=20: {
        "dates": [
            {
                "games": [
                    make_statsapi_game("2026-05-06T01:00:00Z", 147, 111, 1, 9, final=False),
                    make_statsapi_game("2026-05-05T01:00:00Z", 147, 111, 5, 3),
                ]
            }
        ]
    }

    assert adapter.get_yankees_win_streak() == 1


def test_adapter_applies_only_on_confirmed_yankees_win():
    adapter = load_adapter()
    original = "IT'S WHAT YOU WANT: The Yankees defeated the Red Sox by a score of 5-3"

    adapter._legacy_game_was_yankees_win = lambda game_dir: True
    adapter.get_yankees_win_streak = lambda: 4
    assert adapter.apply_theee_to_postgame_title("dummy", original) == "THEEEE YANKEES WIN: The Yankees defeated the Red Sox by a score of 5-3"

    adapter._legacy_game_was_yankees_win = lambda game_dir: False
    assert adapter.apply_theee_to_postgame_title("dummy", original) == original


def test_adapter_fails_closed():
    adapter = load_adapter()
    original = "IT'S WHAT YOU WANT: The Yankees defeated the Red Sox by a score of 5-3"

    def raise_error(game_dir):
        raise RuntimeError("boom")

    adapter._legacy_game_was_yankees_win = raise_error
    assert adapter.apply_theee_to_postgame_title("dummy", original) == original


if __name__ == "__main__":
    test_legacy_linescore_url()
    test_legacy_yankees_win_detection_home_and_away()
    test_legacy_detection_ignores_non_final_games_and_fails_closed()
    test_win_streak_stops_at_first_loss()
    test_latest_loss_resets_streak_to_zero()
    test_live_game_is_ignored_for_streak()
    test_adapter_applies_only_on_confirmed_yankees_win()
    test_adapter_fails_closed()
    print("All Baseball-GDT-Bot-GUI adapter tests passed.")
