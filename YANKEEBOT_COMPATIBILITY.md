# Yankeebot Compatibility Review

## What public Yankeebot posts show

Public win threads show that Yankeebot does far more than submit a title.

Observed jobs include:

```text
- win-thread title
- matchup header
- game status
- MLB Gameday link
- FanGraphs link
- Baseball Savant link
- batter tables
- pitcher tables
- game info
- scoring plays
- video highlights
- line score
- decisions
- division scoreboard
- next Yankees game
- last updated timestamp
- comment thread defaults
```

Because of that, the package should not replace Yankeebot.

## Safe install rule

Use only `theee_title.py` inside Yankeebot.

Do not install the standalone dependencies in the production Yankeebot environment.

Do not give the standalone runner posting credentials unless mods choose to use it as the poster.

## What can break

### 1. Duplicate posts

Cause: running standalone `--post` while Yankeebot already posts win threads.

Guard: use helper-only integration. Keep standalone in dry-run mode.

### 2. Dependency conflicts

Cause: installing `praw`, `requests`, or `python-dotenv` into Yankeebot's live environment.

Guard: helper-only path uses no dependencies. Standalone creates its own `.venv`.

### 3. Wrong streak source

Cause: using spring training games when the intended streak is regular season only.

Guard: standalone defaults to `R,F,D,L,W`. For spring testing, pass `--game-types S,R,F,D,L,W`.

### 4. Title formatting drift

Cause: Yankeebot changes the score text format later.

Guard: `replace_existing_prefix()` only replaces text before the first colon. The rest of the title stays as Yankeebot built it.

### 5. Bad streak value

Cause: streak is missing, zero, blank, or non-numeric.

Guard: bad values become `1`, producing `THE YANKEES WIN`.

## Senior engineer verdict

The package is safe only as a title adapter.

The standalone runner is useful for testing and proof of concept work, but it should not be the first production install path for r/NYYankees.


## Loss reset check

A Yankees loss resets the active winning streak. The MLB helper returns streak `0` when the latest final game is a Yankees loss, and the standalone runner exits without posting. For direct Yankeebot integration, the title helper should only be called on a Yankees win post, or use `replace_prefix_if_yankees_won()` so loss titles stay unchanged.
