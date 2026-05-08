"""Small JSON state file for duplicate protection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_STATE_PATH = Path("state/last_posted_game.json")


def load_state(path: str | Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {"posted_game_pks": []}
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"posted_game_pks": []}
    posted = data.get("posted_game_pks", [])
    if not isinstance(posted, list):
        posted = []
    return {"posted_game_pks": posted[-50:]}


def already_posted(game_pk: int, path: str | Path = DEFAULT_STATE_PATH) -> bool:
    state = load_state(path)
    return int(game_pk) in {int(item) for item in state.get("posted_game_pks", [])}


def mark_posted(game_pk: int, path: str | Path = DEFAULT_STATE_PATH) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    state = load_state(file_path)
    posted = [int(item) for item in state.get("posted_game_pks", [])]
    if int(game_pk) not in posted:
        posted.append(int(game_pk))
    file_path.write_text(
        json.dumps({"posted_game_pks": posted[-50:]}, indent=2) + "\n",
        encoding="utf-8",
    )
