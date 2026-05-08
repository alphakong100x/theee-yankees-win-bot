# Baseball-GDT-Bot-GUI Compatibility Notes

Mods pointed to this repo as the likely Yankeebot base:

```text
https://github.com/avery-crudeman/Baseball-GDT-Bot-GUI
```

I reviewed the public code path and adjusted this helper so it fits that bot style.

## Compatibility finding

The public Baseball-GDT-Bot-GUI repo is a Python 2.7 project. Its README says it was written for Python 2.7 and requires `praw` and `simplejson`.

The postgame title is created in `src/main.py` with this line:

```python
posttitle = edit.generate_title(d,"post")
```

Then the bot submits that title here:

```python
sub = r.submit(self.SUBREDDIT, posttitle, edit.generate_code(d,"post"))
```

That is good for this helper because there is one narrow place to adjust the title before submission.

## What changed in this repo

`theee_title.py` is now Python 2.7 compatible.

That matters because the original helper used newer Python syntax that would not run inside the public Baseball-GDT-Bot-GUI codebase.

I also added:

```text
baseball_gdt_bot_gui_adapter.py
```

That adapter is designed to be copied next to the legacy bot's `src/main.py` and `src/editor.py`.

## Minimal integration patch

Copy these two files into the legacy bot's `src/` folder:

```text
theee_title.py
baseball_gdt_bot_gui_adapter.py
```

In `src/main.py`, add this import near the other imports:

```python
from baseball_gdt_bot_gui_adapter import apply_theee_to_postgame_title
```

Then find this existing postgame block:

```python
print "Submitting postgame thread..."
posttitle = edit.generate_title(d,"post")
sub = r.submit(self.SUBREDDIT, posttitle, edit.generate_code(d,"post"))
print "Postgame thread submitted..."
```

Change it to:

```python
print "Submitting postgame thread..."
posttitle = edit.generate_title(d,"post")
posttitle = apply_theee_to_postgame_title(d, posttitle)
sub = r.submit(self.SUBREDDIT, posttitle, edit.generate_code(d,"post"))
print "Postgame thread submitted..."
```

That is the whole install for the legacy repo path.

## Why this should not break Yankeebot

The adapter is fail-closed.

If the helper cannot confirm that the game was a Yankees win, it returns the original title.

If it cannot fetch the win streak, it returns the original title.

If the MLB API request fails, it returns the original title.

If the helper errors for any reason, it returns the original title.

So the worst likely result is that the postgame thread keeps its normal Yankeebot title.

## What it does not touch

This does not change:

```text
Reddit login
Reddit submission logic
Game thread creation
Pregame thread creation
Box score generation
Line score generation
Scoring plays
Highlights
Sticky logic
Suggested sort
Editing loop
Game final detection
Post body generation
```

It only changes `posttitle` after Yankeebot already generates it and before Reddit submission.

## Streak reset behavior

The adapter counts backward from the latest final Yankees game using the MLB Stats API.

If it sees wins, it counts them.

When it hits the first loss, it stops.

That means the E count resets naturally after a Yankees loss. No manual update is needed after every game.

## Important note

I cannot guarantee that the live r/NYYankees Yankeebot has no local custom changes beyond the public GitHub repo. This compatibility check is based on the public repo the mods sent me.

The safest handoff is still a tiny patch against the live file where `posttitle` is created.
