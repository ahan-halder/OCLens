"""Fingerprints used to match a user .cl file to PoCL's cached copy."""

from __future__ import annotations

import hashlib
from pathlib import Path


def normalize_source(text: str) -> str:
    """Normalize newlines so Windows vs Unix copies still match."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def fingerprint_text(text: str) -> str:
    payload = normalize_source(text).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def fingerprint_file(path: Path) -> str:
    return fingerprint_text(path.read_text(encoding="utf-8", errors="replace"))
