from mlb_yankees import current_win_status, normalize_game_types


def game(game_pk, date_time, home_id, away_id, home_score, away_score, home_name="Yankees", away_name="Opponent", game_type="R"):
    return {
        "gamePk": game_pk,
        "gameDate": date_time,
        "officialDate": date_time[:10],
        "gameType": game_type,
        "status": {"abstractGameState": "Final"},
        "teams": {
            "home": {"score": home_score, "team": {"id": home_id, "teamName": home_name}},
            "away": {"score": away_score, "team": {"id": away_id, "teamName": away_name}},
        },
    }


def test_current_win_status_counts_from_latest_until_loss():
    games = [
        game(1, "2026-05-01T23:00:00Z", 147, 111, 4, 3),
        game(2, "2026-05-02T23:00:00Z", 147, 111, 6, 2),
        game(3, "2026-05-03T23:00:00Z", 111, 147, 5, 3, home_name="Opponent", away_name="Yankees"),
        game(4, "2026-05-04T23:00:00Z", 111, 147, 1, 7, home_name="Opponent", away_name="Yankees"),
        game(5, "2026-05-05T23:00:00Z", 147, 111, 8, 1),
    ]
    latest, streak = current_win_status(games)
    assert latest is not None
    assert latest.game_pk == 5
    assert streak == 2


def test_game_type_defaults_skip_spring_training():
    assert normalize_game_types(None) == ("R", "F", "D", "L", "W")
    assert normalize_game_types("S,R") == ("S", "R")


if __name__ == "__main__":
    test_current_win_status_counts_from_latest_until_loss()
    test_game_type_defaults_skip_spring_training()
    print("All MLB tests passed.")
