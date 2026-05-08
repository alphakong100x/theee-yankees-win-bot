# Integration Guide

This package has two paths.

## Path 1: title helper only

This is the recommended path for the real Yankeebot.

Copy only this file into the Yankeebot project:

```text
theee_title.py
```

Then patch the existing win-post title after Yankeebot has already built it:

```python
from theee_title import replace_existing_prefix

post_title = replace_existing_prefix(post_title, current_yankees_win_streak)
```

Example:

```python
post_title = "IT'S WHAT YOU WANT: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT"
post_title = replace_existing_prefix(post_title, 8)
```

Output:

```text
THEEEEEEEE YANKEES WIN: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT
```

This path does not add a second Reddit poster. It keeps current Yankeebot behavior in place.

## Path 2: standalone preview

Use this only to test output away from the production bot.

1. Copy `.env.example` to `.env`.
2. Keep `POST_TO_REDDIT=false`.
3. Run `python -m yankees_theee_bot --dry-run`.

Do not run standalone `--post` while Yankeebot is already creating win threads. That could create duplicate win posts.

## Streak source options

Best source: use the streak Yankeebot already has, if it has one.

Fallback source: use this package's MLB helper in standalone preview mode.

The title helper does not care where the streak comes from. It only needs a number.


## Loss reset behavior

The E count resets after a Yankees loss. The helper should only run on Yankees win posts. If the post-building path also handles losses, use this safer wrapper:

```python
from theee_title import replace_prefix_if_yankees_won

post_title = replace_prefix_if_yankees_won(
    post_title,
    current_yankees_win_streak,
    yankees_won=latest_game_was_yankees_win,
)
```

When `yankees_won` is false, the function returns the original title unchanged. When the Yankees win after a loss, pass streak `1`, and the prefix becomes `THE YANKEES WIN`.
