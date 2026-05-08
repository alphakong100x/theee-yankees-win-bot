I think I figured out a clean way to do this without making Yankeebot rewrite anything after each game.

The safest version is just a tiny title helper. Yankeebot would still build the same post it already builds, with the same body, box score, links, flairs, stickies, and update logic. The helper only changes the part before the colon.

Example:

```python
post_title = replace_existing_prefix(post_title, current_yankees_win_streak)
```

So this:

```text
IT'S WHAT YOU WANT: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT
```

becomes this on an 8-game streak:

```text
THEEEEEEEE YANKEES WIN: The Yankees defeated the Orioles by a score of 9-4 - May 02, 2026 @ 01:35 PM EDT
```

It does not replace Yankeebot, does not add a second live poster, and can be tested in dry-run mode first.

If interested, DM me and I can send the ZIP.


It resets after a loss too. The helper uses the active win streak number. If the Yankees lose, the streak goes to 0 and no win title is generated. The next win comes through as streak 1, so it goes back to `THE YANKEES WIN`.
