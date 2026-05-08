"""Pure title helper for the r/NYYankees streak based win post."""

from __future__ import annotations

KNOWN_WIN_PREFIXES = (
    "IT'S WHAT YOU WANT",
    "THE YANKEES WIN",
    "THEE YANKEES WIN",
    "THEEE YANKEES WIN",
)


def clean_streak(streak: int | str | None) -> int:
    """Return a safe streak number. Bad values become 1."""
    try:
        value = int(streak) if streak is not None else 1
    except (TypeError, ValueError):
        return 1
    return max(1, value)


def theee_word(streak: int | str | None) -> str:
    """Return THE with E count matching the active Yankees win streak."""
    streak_num = clean_streak(streak)
    return "TH" + ("E" * streak_num)


def build_theee_prefix(streak: int | str | None) -> str:
    """Return the full streak prefix."""
    return f"{theee_word(streak)} YANKEES WIN"


def replace_existing_prefix(existing_title: str, streak: int | str | None) -> str:
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
        return f"{build_theee_prefix(streak)}: {suffix}"

    upper_title = title.upper()
    for prefix in KNOWN_WIN_PREFIXES:
        if upper_title.startswith(prefix):
            suffix = title[len(prefix) :].strip(" :-")
            if suffix:
                return f"{build_theee_prefix(streak)}: {suffix}"
            return build_theee_prefix(streak)

    return f"{build_theee_prefix(streak)}: {title}"


def replace_prefix_if_yankees_won(
    existing_title: str,
    streak: int | str | None,
    yankees_won: bool,
) -> str:
    """
    Safe wrapper for callers that run on more than win threads.

    If the latest final game was not a Yankees win, return the title unchanged.
    When the next Yankees win happens, callers should pass streak=1 and the
    title becomes THE YANKEES WIN, so the E count resets after a loss.
    """
    if not yankees_won:
        return str(existing_title or "")
    return replace_existing_prefix(existing_title, streak)


def build_win_title(
    streak: int | str | None,
    opponent: str,
    yankees_score: int | str,
    opponent_score: int | str,
    game_date: str,
) -> str:
    """Build a standalone Reddit post title."""
    score_text = f"The Yankees defeated the {opponent} {yankees_score}-{opponent_score} - {game_date}"
    return replace_existing_prefix(score_text, streak)
