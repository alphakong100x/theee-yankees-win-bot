"""Dry-run-first Reddit bot for streak-based r/NYYankees win titles."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from mlb_yankees import YankeesGameResult, live_current_win_status, normalize_game_types
from state_store import already_posted, mark_posted
from theee_title import build_win_title

DEFAULT_SELF_TEXT = "Automated Yankees win post. Title uses the active Yankees winning streak."


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def submit_to_reddit(title: str, selftext: str) -> str:
    """Submit one Reddit text post and return its permalink."""
    import praw

    client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    username = os.getenv("REDDIT_USERNAME", "").strip()
    password = os.getenv("REDDIT_PASSWORD", "").strip()
    user_agent = os.getenv("REDDIT_USER_AGENT", "YankeesTheeeBot/1.0")
    subreddit_name = os.getenv("SUBREDDIT", "NYYankees").strip() or "NYYankees"

    missing = [
        name
        for name, value in {
            "REDDIT_CLIENT_ID": client_id,
            "REDDIT_CLIENT_SECRET": client_secret,
            "REDDIT_USERNAME": username,
            "REDDIT_PASSWORD": password,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError("Missing Reddit settings: " + ", ".join(missing))

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=user_agent,
    )
    submission = reddit.subreddit(subreddit_name).submit(title=title, selftext=selftext)
    return f"https://www.reddit.com{submission.permalink}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="r/NYYankees THEEE win title adapter")
    parser.add_argument("--post", action="store_true", help="Submit to Reddit after all checks pass")
    parser.add_argument("--dry-run", action="store_true", help="Print the title and stop")
    parser.add_argument("--state", default="state/last_posted_game.json", help="Path for duplicate-protection state")
    parser.add_argument("--days-back", type=int, default=150, help="How many past days to scan")
    parser.add_argument("--selftext", default=DEFAULT_SELF_TEXT, help="Text body for standalone Reddit posts")
    parser.add_argument("--force", action="store_true", help="Ignore duplicate state for a manual test")
    parser.add_argument("--game-types", default=os.getenv("GAME_TYPES", "R,F,D,L,W"), help="MLB game type codes to scan")
    return parser


def render_title(game: YankeesGameResult, streak: int) -> str:
    return build_win_title(
        streak=streak,
        opponent=game.opponent,
        yankees_score=game.yankees_score,
        opponent_score=game.opponent_score,
        game_date=game.game_date,
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = build_parser().parse_args(argv)
    state_path = Path(args.state)

    game_types = normalize_game_types(args.game_types)
    game, streak = live_current_win_status(days_back=args.days_back, game_types=game_types)
    if game is None:
        print("No completed Yankees game found in the scanned window.")
        return 0

    if not game.yankees_won:
        print(f"Latest final was not a Yankees win. GamePk: {game.game_pk}")
        return 0

    title = render_title(game, streak)
    print(title)
    print(f"GamePk: {game.game_pk}")
    print(f"Winning streak: {streak}")
    print(f"Game types scanned: {','.join(game_types)}")

    if already_posted(game.game_pk, state_path) and not args.force:
        print("This game is already recorded in the state file. No post made.")
        return 0

    should_post = bool(args.post or env_flag("POST_TO_REDDIT", default=False))
    if args.dry_run or not should_post:
        print("Dry run only. No Reddit post made.")
        return 0

    permalink = submit_to_reddit(title=title, selftext=args.selftext)
    mark_posted(game.game_pk, state_path)
    print(f"Posted: {permalink}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
