# Yankees THEEE Bot Adapter

Small, dry-run-first ZIP for r/NYYankees mods.

The request: make the number of E characters in `THE` match the active Yankees winning streak.

```text
streak 1 -> THE YANKEES WIN
streak 2 -> THEE YANKEES WIN
streak 3 -> THEEE YANKEES WIN
streak 8 -> THEEEEEEEE YANKEES WIN
streak 19 -> THEEEEEEEEEEEEEEEEEEE YANKEES WIN
```

After a Yankees loss, the streak is 0. The next Yankees win should be passed as streak 1, which resets the title back to `THE YANKEES WIN`. The MLB helper already does this by counting backward from the latest final game and stopping at the first loss.

## Best install for the real Yankeebot

Do not replace Yankeebot.

Do not run a second live Reddit poster next to Yankeebot.

The lowest-risk install is one helper file:

```text
theee_title.py
```

Then add one import and one title replacement in the current Yankeebot win-post code:

```python
from theee_title import replace_existing_prefix

post_title = replace_existing_prefix(post_title, current_yankees_win_streak)
```

If the same code path can run after losses too, use the guarded wrapper instead:

```python
from theee_title import replace_prefix_if_yankees_won

post_title = replace_prefix_if_yankees_won(
    post_title,
    current_yankees_win_streak,
    yankees_won=latest_game_was_yankees_win,
)
```

That keeps the current bot in charge of posts, body text, game tables, links, flair, comments, locks, sticky logic, edit loops, postgame threads, game threads, and mod-only behavior.

## Why this should not break current bot jobs

`theee_title.py` has no third-party dependencies.

It does not call Reddit.

It does not call MLB.

It does not read files.

It does not write files.

It only takes an existing title string and a streak number, then swaps the prefix before the first colon.

Current Yankeebot title:

```text
IT'S WHAT YOU WANT: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT
```

After helper:

```text
THEEEEEEEE YANKEES WIN: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT
```

The rest of the title stays intact.

## Standalone test runner

The standalone runner is for preview only unless mods decide otherwise.

It has its own virtual environment and dry-run mode. It should not be installed inside Yankeebot's production environment.

### Windows PowerShell

```powershell
cd yankees-theee-bot
Set-ExecutionPolicy -Scope Process Bypass
.\INSTALL_WINDOWS.ps1
```

### Mac or Linux

```bash
cd yankees-theee-bot
./INSTALL_MAC_LINUX.sh
```

## Manual standalone preview

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m tests.test_theee_title
python -m tests.test_mlb_yankees
python -m yankees_theee_bot --dry-run
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

## Game types

Standalone mode scans regular season and postseason by default:

```text
R,F,D,L,W
```

That avoids spring training games changing the regular season streak.

For spring training tests, run:

```bash
python -m yankees_theee_bot --dry-run --game-types S,R,F,D,L,W
```

## Files

```text
theee_title.py                zero-dependency title helper
mlb_yankees.py                MLB Stats API streak helper for standalone preview
state_store.py                duplicate protection for standalone preview
yankees_theee_bot.py          dry-run-first Reddit runner
INTEGRATION_GUIDE.md          safest current-bot install path
YANKEEBOT_COMPATIBILITY.md    what was checked and what can break
MOD_REPLY.md                  Reddit reply draft
requirements.txt              standalone preview dependencies
.env.example                  standalone preview settings template
state/last_posted_game.json   standalone duplicate state
tests/                        no-network tests
examples/                     sample GitHub Actions dry-run file
```
