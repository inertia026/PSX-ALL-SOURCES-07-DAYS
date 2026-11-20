"""Shared helpers: paths, config, stable JSON, hashing, polite HTTP."""
from __future__ import annotations

import hashlib
import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
RUNS_DIR = ROOT / "runs"
CACHE_DIR = ROOT / "cache"          # raw downloads + agent replay cache (git-ignored)
INPUTS_DIR = ROOT / "inputs"        # optional files you drop in by hand

USER_AGENT = "Mozilla/5.0 (compatible; psx7-research/1.0)"


@lru_cache(maxsize=1)
def settings() -> dict:
    return yaml.safe_load((CONFIG_DIR / "settings.yaml").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def holidays() -> set[str]:
    data = yaml.safe_load((CONFIG_DIR / "holidays.yaml").read_text(encoding="utf-8")) or {}
    return {str(d) for d in data.get("holidays", []) or []}


def stable_dumps(obj: Any) -> str:
    """Canonical JSON: sorted keys, fixed separators, so equal data -> equal bytes."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sha256(obj: Any) -> str:
    data = obj if isinstance(obj, (bytes, str)) else stable_dumps(obj)
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2, default=str) + "\n",
                    encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def r2(x: float | None, nd: int = 2) -> float | None:
    """Round for storage; keeps snapshots byte-stable across machines."""
    if x is None:
        return None
    try:
        if x != x:  # NaN
            return None
    except TypeError:
        return None
    return round(float(x), nd)


class Http:
    """requests wrapper with a fixed delay between calls and a few retries."""

    def __init__(self, delay: float | None = None):
        import requests

        self.s = requests.Session()
        self.s.headers.update({"User-Agent": USER_AGENT})
        self.delay = settings()["history"]["request_delay_seconds"] if delay is None else delay
        self._last = 0.0

    def get(self, url: str, **kw):
        wait = self.delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        last_exc = None
        for attempt in range(3):
            try:
                r = self.s.get(url, timeout=kw.pop("timeout", 30), **kw)
                self._last = time.monotonic()
                return r
            except Exception as e:  # network hiccup: back off and retry
                last_exc = e
                time.sleep(1.5 * (attempt + 1))
        raise last_exc  # type: ignore[misc]
