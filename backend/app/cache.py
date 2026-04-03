import time
from typing import Any, Optional

_store: dict[str, tuple[Any, float]] = {}
TTL = 30 * 60  # 30 minutes


def get(key: str) -> Optional[Any]:
    if key in _store:
        value, expires_at = _store[key]
        if time.time() < expires_at:
            return value
        del _store[key]
    return None


def set(key: str, value: Any, ttl: int = TTL):
    _store[key] = (value, time.time() + ttl)
