"""Pure title helper for the r/NYYankees streak based win post.

This file is intentionally Python 2.7 compatible because the public
Baseball-GDT-Bot-GUI repo used by Yankeebot is a Python 2.7 codebase.

No Reddit calls. No MLB calls. No file reads. No file writes.
"""

KNOWN_WIN_PREFIXES = (
    "IT'S WHAT YOU WANT",
    "THE YANKEES WIN",
    "THEE YANKEES WIN",
    "THEEE YANKEES WIN",
)


def clean_streak(streak):
    """Return a safe streak number. Bad values become 1."""
    try:
        value = int(streak) if streak is not None else 1
    except (TypeError, ValueError):
        return 1
    return max(1, value)


def theee_word(streak):
    """Return THE with E count matching the active Yankees win streak."""
    streak_num = clean_streak(streak)
    return "TH" + ("E" * streak_num)


def build_theee_prefix(streak):
    """Return the full streak prefix."""
    return "%s YANKEES WIN" % theee_word(streak)


def replace_existing_prefix(existing_title, streak):
    """
    Swap only the text before the first colon.

    This lets Yankeebot keep its score text, date text, body, links,
    flair, sticky logic, and update loop.
    """
    title = str(existing_title or "").strip()
    if not title:
        return build_theee_prefix(streak)

    if ":" in title:
        suffix = title.split(":", 1)[1].strip()
        return "%s: %s" % (build_theee_prefix(streak), suffix)

    upper_title = title.upper()
    for prefix in KNOWN_WIN_PREFIXES:
        if upper_title.startswith(prefix):
            suffix = title[len(prefix):].strip(" :-")
            if suffix:
                return "%s: %s" % (build_theee_prefix(streak), suffix)
            return build_theee_prefix(streak)

    return "%s: %s" % (build_theee_prefix(streak), title)


def replace_prefix_if_yankees_won(existing_title, streak, yankees_won):
    """
    Safe wrapper for callers that run on more than win threads.

    If the latest final game was not a Yankees win, return the title unchanged.
    When the next Yankees win happens, callers should pass streak=1 and the
    title becomes THE YANKEES WIN, so the E count resets after a loss.
    """
    if not yankees_won:
        return str(existing_title or "")
    return replace_existing_prefix(existing_title, streak)


def build_win_title(streak, opponent, yankees_score, opponent_score, game_date):
    """Build a standalone Reddit post title."""
    score_text = "The Yankees defeated the %s %s-%s - %s" % (
        opponent,
        yankees_score,
        opponent_score,
        game_date,
    )
    return replace_existing_prefix(score_text, streak)
