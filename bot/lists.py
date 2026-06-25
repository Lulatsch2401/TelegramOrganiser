import difflib
import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

LISTS_FILE = Path(os.environ.get("LISTS_FILE", str(Path(__file__).parent.parent / "lists.yaml")))

_lookup: dict[str, dict] = {}
_raw: dict[str, dict] = {}


def load_lists(path: Path | None = None) -> int:
    global _lookup, _raw
    file = path or LISTS_FILE
    with open(file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    lookup: dict[str, dict] = {}
    for key, entry in data.items():
        enriched = {"key": key, **entry}
        lookup[key.lower()] = enriched
        for alias in entry.get("aliases", []):
            lookup[alias.lower()] = enriched

    _lookup = lookup
    _raw = {k: {"key": k, **v} for k, v in data.items()}
    logger.info("Loaded %d lists (%d keywords total)", len(data), len(lookup))
    return len(data)


def get_list(keyword: str) -> dict | None:
    return _lookup.get(keyword.lower().strip())


def get_all_keywords() -> list[str]:
    return sorted(_raw.keys())


def fuzzy_match(keyword: str) -> str | None:
    kw = keyword.lower().strip()
    matches = difflib.get_close_matches(kw, _lookup.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None
