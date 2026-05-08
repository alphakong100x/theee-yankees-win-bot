from theee_title import build_theee_prefix, build_win_title, replace_existing_prefix, replace_prefix_if_yankees_won, theee_word


def test_theee_word_counts_e_by_streak():
    assert theee_word(1) == "THE"
    assert theee_word(2) == "THEE"
    assert theee_word(3) == "THEEE"
    assert theee_word(8) == "THEEEEEEEE"
    assert theee_word(19) == "THEEEEEEEEEEEEEEEEEEE"


def test_bad_streak_defaults_to_one():
    assert theee_word(0) == "THE"
    assert theee_word(None) == "THE"
    assert theee_word("bad") == "THE"


def test_prefix():
    assert build_theee_prefix(3) == "THEEE YANKEES WIN"


def test_replace_yankeebot_prefix_keeps_existing_suffix():
    original = "IT'S WHAT YOU WANT: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT"
    expected = "THEEEEEEEE YANKEES WIN: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT"
    assert replace_existing_prefix(original, 8) == expected


def test_full_title():
    title = build_win_title(2, "Red Sox", 5, 3, "2026-05-07")
    assert title == "THEE YANKEES WIN: The Yankees defeated the Red Sox 5-3 - 2026-05-07"


def test_safe_wrapper_does_not_change_loss_titles():
    original = "Postgame Thread: The Yankees lost to the Red Sox by a score of 5-3"
    assert replace_prefix_if_yankees_won(original, 0, yankees_won=False) == original


def test_streak_resets_to_one_after_loss_then_next_win():
    original = "IT'S WHAT YOU WANT: The Yankees defeated the Red Sox by a score of 4-2"
    assert replace_prefix_if_yankees_won(original, 1, yankees_won=True).startswith("THE YANKEES WIN:")


if __name__ == "__main__":
    test_theee_word_counts_e_by_streak()
    test_bad_streak_defaults_to_one()
    test_prefix()
    test_replace_yankeebot_prefix_keeps_existing_suffix()
    test_full_title()
    test_safe_wrapper_does_not_change_loss_titles()
    test_streak_resets_to_one_after_loss_then_next_win()
    print("All title tests passed.")
