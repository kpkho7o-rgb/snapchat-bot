import json
import os

ALLOWED_USERS_FILE = "allowed_users.json"


def _load() -> set:
    if not os.path.exists(ALLOWED_USERS_FILE):
        return set()
    with open(ALLOWED_USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()


def _save(users: set):
    with open(ALLOWED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)


def is_allowed(user_id: int, owner_id: int) -> bool:
    if user_id == owner_id:
        return True
    return user_id in _load()


def allow_user(user_id: int):
    users = _load()
    users.add(user_id)
    _save(users)


def revoke_user(user_id: int):
    users = _load()
    users.discard(user_id)
    _save(users)
