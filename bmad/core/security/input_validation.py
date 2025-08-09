#!/usr/bin/env python3
"""
Input Validation & Sanitization
- Basis validatie/sanitizatie helpers voor tool-calls en inkomende payloads
"""
from __future__ import annotations

import re
from typing import Any, Dict

SAFE_TEXT_PATTERN = re.compile(r"^[\w\s.,:;@#%&()\-_/+\[\]{}'\"!?]*$")


def sanitize_text(value: str, max_len: int = 5000) -> str:
    if not isinstance(value, str):
        return str(value)
    value = value.strip()
    if len(value) > max_len:
        value = value[:max_len]
    # rudimentary strip of control chars
    value = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", value)
    return value


def validate_text(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return bool(SAFE_TEXT_PATTERN.match(value))


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for k, v in (payload or {}).items():
        if isinstance(v, str):
            result[k] = sanitize_text(v)
        elif isinstance(v, dict):
            result[k] = sanitize_payload(v)
        elif isinstance(v, list):
            result[k] = [sanitize_text(x) if isinstance(x, str) else x for x in v]
        else:
            result[k] = v
    return result 