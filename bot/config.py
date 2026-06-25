import os
from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str
    allowed_user_ids: list[int]


def load_config() -> Config:
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    raw_ids = os.environ.get("ALLOWED_USER_IDS", "").strip()
    if not raw_ids:
        raise RuntimeError("ALLOWED_USER_IDS environment variable is not set")

    try:
        user_ids = [int(uid.strip()) for uid in raw_ids.split(",") if uid.strip()]
    except ValueError as e:
        raise RuntimeError(f"ALLOWED_USER_IDS must be comma-separated integers: {e}") from e

    if not user_ids:
        raise RuntimeError("ALLOWED_USER_IDS must contain at least one user ID")

    return Config(bot_token=token, allowed_user_ids=user_ids)
