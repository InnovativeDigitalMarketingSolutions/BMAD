#!/usr/bin/env python3
"""
Log Redaction Utilities
- Redacteert gevoelige informatie (tokens, secrets, passwords, api keys) uit logs
- Past redactie toe op JSON strings en reguliere tekst
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict

SENSITIVE_KEYS = {
    "password", "passwd", "pass", "secret", "api_key", "apikey", "token",
    "access_token", "refresh_token", "authorization", "auth", "set-cookie",
    "client_secret", "private_key", "ssh_key",
}

BEARER_PATTERN = re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)
API_KEY_PATTERN = re.compile(r"(api[_-]?key\s*[:=]\s*)([A-Za-z0-9\-._~+/]+)", re.IGNORECASE)
OPENAI_KEY_PATTERN = re.compile(r"(sk-[A-Za-z0-9]{10,})")
GENERIC_SECRET_PATTERN = re.compile(r"([A-Za-z0-9]{24,}\.[A-Za-z0-9\-._~+/]{10,})")

REDACTED = "***REDACTED***"


def _redact_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: REDACTED if k.lower() in SENSITIVE_KEYS else _redact_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(v) for v in value]
    text = str(value)
    text = BEARER_PATTERN.sub(r"\\1" + REDACTED, text)
    text = API_KEY_PATTERN.sub(r"\\1" + REDACTED, text)
    text = OPENAI_KEY_PATTERN.sub(REDACTED, text)
    text = GENERIC_SECRET_PATTERN.sub(REDACTED, text)
    return text


def redact_text_message(message: str) -> str:
    # Probeer JSON te parsen voor key-based redaction
    try:
        obj = json.loads(message)
        redacted = _redact_value(obj)
        return json.dumps(redacted)
    except Exception:
        pass
    # Anders regex-based redaction
    text = BEARER_PATTERN.sub(r"\\1" + REDACTED, message)
    text = API_KEY_PATTERN.sub(r"\\1" + REDACTED, text)
    text = OPENAI_KEY_PATTERN.sub(REDACTED, text)
    text = GENERIC_SECRET_PATTERN.sub(REDACTED, text)
    return text


class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not os.getenv("BMAD_LOG_REDACTION_ENABLED", "1") in {"1", "true", "True"}:
            return True
        try:
            if isinstance(record.msg, str):
                record.msg = redact_text_message(record.msg)
            elif isinstance(record.msg, dict):
                record.msg = _redact_value(record.msg)
            # Also sanitize args if present
            if record.args:
                new_args = []
                for a in record.args if isinstance(record.args, (list, tuple)) else [record.args]:
                    if isinstance(a, str):
                        new_args.append(redact_text_message(a))
                    elif isinstance(a, dict):
                        new_args.append(_redact_value(a))
                    else:
                        new_args.append(a)
                record.args = tuple(new_args)
        except Exception:
            # Never break logging
            return True
        return True


def setup_security_logging(logger: logging.Logger | None = None) -> None:
    """Voegt RedactionFilter toe aan root of specifieke logger (idempotent)."""
    target = logger or logging.getLogger()
    # voorkom dubbele filters
    for f in getattr(target, "filters", []):
        if isinstance(f, RedactionFilter):
            return
    target.addFilter(RedactionFilter()) 